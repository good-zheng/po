"""HTTP 数据层：打 Java ``/novel/internal/**`` 的 NovelStore / CanonStore 实现。

与 ``store`` 模块的两个协议一一对应，这里只负责「线上怎么发」：
- 请求体字段用 Java DTO 的 camelCase，不做 snake_case 翻译表（多一层就多一处漂移）；
- 响应统一是 ``Result<T>`` 信封，业务失败也是 HTTP 200，所以判定看 ``success`` 不看状态码；
- 写失败按机制⑦重试：幂等键让「重试」与「重放」在库侧同义（gen_job 已 committed 的回 REPLAY，
  不会二次入库），因此这里的重试是安全的。

生产装配见 ``agent.build_novel_agent``：``NOVEL_PERSIST_ENABLED=false`` 时用
``store.MockNovelStore`` / ``store.InMemoryCanonStore``，否则用本模块。

传输层可注入（``transport``）：测试用 ``httpx.MockTransport`` 打桩，
不必为可测性把每个方法拆成「钩子 + 真实实现」两份。
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

import httpx

from po_agent_novel.actor import current_actor
from po_agent_novel.config import NovelStoreSettings
from po_agent_novel.schemas import (
    ArchivedBook,
    BookDraft,
    ChapterDraft,
    ChapterExtraction,
    CharacterProfile,
    genre_label,
    normalize_genre,
)
from po_agent_novel.store import (
    AppendOutcome,
    BookSnapshot,
    CanonAssertion,
    ChapterSnapshot,
    ExtractionSource,
    ForeshadowRecord,
    NovelStoreError,
    SceneSummary,
    StyleProfileRecord,
    SummaryRecord,
)


class _HttpChannel:
    """两个 store 共用的一条 HTTP 通道（重试 + Result 信封解包）。"""

    def __init__(
        self,
        settings: NovelStoreSettings | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings or NovelStoreSettings()
        self._transport = transport

    @property
    def _headers(self) -> dict[str, str]:
        # 令牌为空时照常发空头：Java 侧对「未配置」与「不匹配」都回 403，
        # 错误信息比在客户端提前抛更贴近真实故障现场（也避免两处判定漂移）。
        headers = {"X-Internal-Token": self.settings.internal_token}
        # 作者身份只在握手验出票据的连接上存在（见 actor 模块）。不带这个头时 Java 侧
        # 跳过归属校验——生成链路没有终端用户在场的概念，把「无身份」当错误会让一本
        # 新书在第一次归档前就写不进去。
        actor = current_actor()
        if actor is not None:
            headers["X-Actor-Uid"] = str(actor)
        return headers

    async def _call(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retriable: bool = True,
    ) -> Any:
        """发一次请求并解出 ``Result.data``，网络/5xx 错误按退避重试。"""
        url = f"{self.settings.api_base_url.rstrip('/')}{path}"
        attempts = self.settings.max_retries + 1 if retriable else 1
        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                async with httpx.AsyncClient(
                    timeout=self.settings.request_timeout_seconds,
                    transport=self._transport,
                ) as client:
                    response = await client.request(
                        method, url, params=params, json=json, headers=self._headers
                    )
                if response.status_code >= 500:
                    # 网关/服务抖动：这一类值得重试；4xx 与业务错误直接死
                    last_error = NovelStoreError(f"后端返回 {response.status_code}")
                    await self._backoff(attempt, attempts)
                    continue
                response.raise_for_status()
                return self._unwrap(response.json())
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                await self._backoff(attempt, attempts)
        raise NovelStoreError(f"{method} {path} 调用失败：{last_error}") from last_error

    async def _backoff(self, attempt: int, attempts: int) -> None:
        if attempt + 1 >= attempts:
            return
        await asyncio.sleep(self.settings.retry_backoff_seconds * (2**attempt))

    @staticmethod
    def _unwrap(body: Any) -> Any:
        if not isinstance(body, dict):
            raise NovelStoreError("后端返回结构异常：顶层不是对象")
        if not body.get("success", False):
            raise NovelStoreError(f"后端业务错误：{body.get('message') or '未知错误'}")
        return body.get("data")


class HttpNovelStore(_HttpChannel):
    """成稿读写实现：复用 Java novel 模块的 BookService / ChapterService / CharacterService。

    章节与角色是「一条一个请求」：内部通道沿用管理端的单资源接口形状，
    归档一次几十条的量级犯不上再建批量端点。
    读侧只有 ``load_book`` 一条，且只带一章——正文按对话需要单点取，不整本过网。
    """

    async def save_book(self, draft: BookDraft) -> str:
        data = await self._call(
            "POST",
            "/novel/internal/books",
            params={"authorId": self.settings.author_id},
            json={
                "title": draft.title,
                # 两份文本同源：summary 是 Tier-0 世界观摘要（注入用），
                # description 是对外简介（书架展示用）。作者在工作台把它们改开之前，
                # 让两者同源好过只写一个——少写的那个会一直是 null
                "summary": draft.summary,
                "description": draft.summary,
                # 服务端只收 NovelGenres 的十个 value，中文原话会被 requireKnownGenre
                # 整本打回（实测：三章写完、闸门全过，死在最后一步的「无效的小说类型」）。
                "genre": normalize_genre(draft.genre),
            },
        )
        return str(self._require_id(data, "book"))

    async def save_chapters(self, book_id: str, chapters: list[ChapterDraft]) -> list[str]:
        book = self._as_int(book_id, "book_id")
        created: list[str] = []
        # 顺序而非并发：chapterIndex 缺省时服务端按「当前最大序号+1」分配，
        # 并发写会让序号撞车。
        for chapter in chapters:
            data = await self._call(
                "POST",
                f"/novel/internal/books/{book}/chapters",
                json={
                    "title": chapter.title,
                    "content": chapter.content,
                    "chapterIndex": chapter.index,
                },
            )
            created.append(str(self._require_id(data, "chapter")))
        return created

    async def save_characters(
        self, book_id: str, characters: list[CharacterProfile]
    ) -> None:
        book = self._as_int(book_id, "book_id")
        for item in characters:
            await self._call(
                "POST",
                f"/novel/internal/books/{book}/characters",
                json={
                    "name": item.name,
                    # book_character 没有 role 列：定位词并进 description，
                    # 拆列属于建表变更，不该由数据层单方面决定
                    "description": f"{item.role}｜{item.description}",
                },
            )

    async def list_books(self) -> list[ArchivedBook]:
        # GET /books 在 SecurityConfig 里对游客开放（读者端书架），不必带内部令牌。
        # 计数恒为 0：book 表没有聚合列，列表接口也就带不出 chapterCount/characterCount
        # （真要计数得走 /books/{id}/chapters 的分页 total，逐本请求不划算）。
        # 当前无运行时调用方——回溯续写（N3+）需要时，应在管理端列表 DTO 上补聚合字段。
        data = await self._call("GET", "/books", params={"page": 0, "size": 50})
        records = data.get("content") if isinstance(data, dict) else data
        return [
            ArchivedBook(
                book_id=str(item["id"]),
                title=item.get("title") or "",
                # 库里存的是 value（fantasy），提示词与卡片要的是中文：过一道 genre_label
                genre=genre_label(item.get("genre") or ""),
                summary=item.get("description") or "",
                chapter_count=0,
                character_count=0,
            )
            for item in (records or [])
            if isinstance(item, dict) and item.get("id") is not None
        ]

    async def load_book(self, book_id: str, *, chapter_id: str | None = None) -> BookSnapshot:
        params: dict[str, Any] = {"bookId": self._as_int(book_id, "book_id")}
        if chapter_id is not None:
            params["chapterId"] = self._as_int(chapter_id, "chapter_id")
        data = await self._call("GET", "/novel/internal/books/detail", params=params)
        if not isinstance(data, dict) or data.get("bookId") is None:
            raise NovelStoreError(f"书本读回结构异常：{data!r}")
        raw = data.get("chapter")
        if isinstance(raw, dict):
            if raw.get("chapterId") is None or raw.get("chapterIndex") is None:
                # 这里不像 _words 那样退化：缺字段只能读成 chapter=None，
                # 而 None 的形状是「这本书没有这一章」——把坏载荷说成书不存在，
                # 模型就会照着一份它以为不存在的正文谈设定。
                raise NovelStoreError(f"参照章结构异常：{raw!r}")
            chapter: ChapterSnapshot | None = ChapterSnapshot(
                chapter_id=str(raw["chapterId"]),
                index=int(raw["chapterIndex"]),
                title=raw.get("title") or "",
                content=raw.get("content") or "",
            )
        else:
            chapter = None
        return BookSnapshot(
            book_id=str(data["bookId"]),
            title=data.get("title") or "",
            genre=genre_label(data.get("genre") or ""),
            summary=data.get("summary") or "",
            chapter_count=int(data.get("chapterCount") or 0),
            chapter=chapter,
        )

    def _require_id(self, data: Any, what: str) -> int:
        if not isinstance(data, dict) or data.get("id") is None:
            raise NovelStoreError(f"{what} 入库回执缺少 id")
        return int(data["id"])

    @staticmethod
    def _as_int(value: str, name: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise NovelStoreError(f"{name} 不是合法的后端 ID：{value!r}") from exc


class HttpCanonStore(_HttpChannel):
    """正典层实现：写只走内部通道，读一律带 as-of 章号。"""

    async def append_assertions(
        self,
        book_id: str,
        as_of_chapter: int,
        extraction: ChapterExtraction,
        source: ExtractionSource,
    ) -> AppendOutcome:
        payload = build_append_request(book_id, as_of_chapter, extraction, source)
        data = await self._call(
            "POST", "/novel/internal/assertions:append", json=payload
        )
        result = data if isinstance(data, dict) else {}
        # 回执不带断言 id：id 由 load_snapshot 按实体键取回，
        # 写侧回读等于多一次往返，而调用方本来就有快照这条读路径
        return AppendOutcome(
            applied=bool(result.get("applied", False)),
            inserted=int(
                int(result.get("assertionsInserted") or 0)
                + int(result.get("foreshadowsWritten") or 0)
                + int(result.get("aliasesWritten") or 0)
                + int(result.get("stateChangesWritten") or 0)
            ),
            skipped=int(result.get("skipped") or 0),
        )

    async def close_assertion_range(
        self, assertion_id: str, until_chapter: int, reason: str
    ) -> None:
        await self._call(
            "POST",
            "/novel/internal/assertions:close",
            json={
                "assertionId": HttpNovelStore._as_int(assertion_id, "assertion_id"),
                "untilChapter": until_chapter,
                "reason": reason,
            },
        )

    async def load_snapshot(
        self,
        book_id: str,
        as_of_chapter: int,
        entities: list[str] | None = None,
        kinds: list[str] | None = None,
    ) -> list[CanonAssertion]:
        params: dict[str, Any] = {
            "bookId": HttpNovelStore._as_int(book_id, "book_id"),
            "asOf": as_of_chapter,
        }
        if entities:
            params["entities"] = ",".join(entities)
        if kinds:
            params["kinds"] = ",".join(kinds)
        data = await self._call("GET", "/novel/internal/canon/snapshot", params=params)
        return [
            CanonAssertion(
                id=str(item["id"]),
                book_id=str(item["bookId"]),
                kind=item.get("kind") or "",
                subject_key=item.get("subjectKey") or "",
                predicate=item.get("predicate") or "",
                object_text=item.get("objectText") or "",
                restatement=item.get("restatement") or "",
                authority=item.get("authority") or "model",
                established_chapter=item.get("establishedChapter"),
                valid_from_chapter=int(item.get("validFromChapter") or as_of_chapter),
                valid_until_chapter=item.get("validUntilChapter"),
                status=item.get("status") or "confirmed",
            )
            for item in (data or [])
            if isinstance(item, dict) and item.get("id") is not None
        ]

    async def load_open_foreshadows(
        self, book_id: str, as_of_chapter: int
    ) -> list[ForeshadowRecord]:
        data = await self._call(
            "GET",
            "/novel/internal/canon/foreshadows/open",
            params={
                "bookId": HttpNovelStore._as_int(book_id, "book_id"),
                "asOf": as_of_chapter,
            },
        )
        return [
            ForeshadowRecord(
                id=str(item["id"]),
                book_id=str(item["bookId"]),
                planted_chapter=int(item.get("plantedChapter") or 0),
                content=item.get("content") or "",
                due_by_arc=item.get("dueByArc"),
            )
            for item in (data or [])
            if isinstance(item, dict) and item.get("id") is not None
        ]

    async def save_findings(
        self, chapter_id: str, findings: list[dict[str, object]], idempotency_key: str
    ) -> None:
        await self._call(
            "POST",
            "/novel/internal/findings",
            json={
                "chapterId": HttpNovelStore._as_int(chapter_id, "chapter_id"),
                "idempotencyKey": idempotency_key,
                "findings": findings,
            },
        )

    async def save_chapter_summaries(
        self,
        book_id: str,
        chapter_id: str,
        chapter_no: int,
        scenes: list[SceneSummary],
        digest: str | None = None,
    ) -> None:
        del book_id, chapter_no  # 服务端按章节行推导 book 与覆盖区间，客户端传了也不可信
        chapter = HttpNovelStore._as_int(chapter_id, "chapter_id")
        if scenes:
            await self._call(
                "POST",
                "/novel/internal/summaries",
                json={
                    "chapterId": chapter,
                    "level": "scene",
                    "scenes": [
                        {"sceneNo": s.scene_no, "content": s.content, "tokens": s.tokens}
                        for s in scenes
                    ],
                },
            )
        if digest:
            # 章级摘要没有场景序号，用 0 占位（与 Java 侧「该级 scene_no 恒 0」同口径）
            await self._call(
                "POST",
                "/novel/internal/summaries",
                json={
                    "chapterId": chapter,
                    "level": "chapter",
                    "scenes": [{"sceneNo": 0, "content": digest, "tokens": None}],
                },
            )

    async def save_arc_summary(
        self, book_id: str, arc_no: int, from_chapter: int, to_chapter: int, content: str
    ) -> None:
        # arc 级没有章节行可推导，区间由调用方给（服务端只校验 1 <= from <= to）
        await self._call(
            "POST",
            "/novel/internal/summaries",
            json={
                "bookId": HttpNovelStore._as_int(book_id, "book_id"),
                "level": "arc",
                "arcNo": arc_no,
                "fromChapter": from_chapter,
                "toChapter": to_chapter,
                "scenes": [{"sceneNo": arc_no, "content": content, "tokens": None}],
            },
        )

    async def load_summaries(
        self,
        book_id: str,
        upto_chapter: int,
        levels: Sequence[str] = ("scene", "chapter"),
        limit: int = 24,
    ) -> list[SummaryRecord]:
        data = await self._call(
            "GET",
            "/novel/internal/canon/summaries",
            params={
                "bookId": HttpNovelStore._as_int(book_id, "book_id"),
                "upto": upto_chapter,
                "levels": ",".join(levels),
                "limit": limit,
            },
        )
        return [
            SummaryRecord(
                id=str(item["id"]),
                level=item.get("level") or "scene",
                chapter_no=item.get("chapterNo"),
                scene_no=item.get("sceneNo"),
                content=item.get("content") or "",
                tokens=item.get("tokens"),
            )
            for item in (data or [])
            if isinstance(item, dict) and item.get("id") is not None
        ]

    async def load_style_profile(self, book_id: str) -> StyleProfileRecord | None:
        data = await self._call(
            "GET",
            "/novel/internal/canon/style",
            params={"bookId": HttpNovelStore._as_int(book_id, "book_id")},
        )
        if not isinstance(data, dict):
            # null 是「这本书还没定过契约」，不是错误：装配侧据此保留派生契约
            return None
        return StyleProfileRecord(
            person=data.get("person"),
            tense=data.get("tense"),
            sentence_len_min=data.get("sentenceLenMin"),
            sentence_len_max=data.get("sentenceLenMax"),
            chapter_words_min=data.get("chapterWordsMin"),
            chapter_words_max=data.get("chapterWordsMax"),
            forbidden_words=_words(data.get("forbiddenWords")),
            tics=_words(data.get("tics")),
            taboo=_words(data.get("taboo")),
        )


def _words(value: Any) -> tuple[str, ...]:
    """把契约里的词表读成字符串元组。

    容忍 ``None`` 与非列表：Java 侧存的是 JSON 文本，读回来坏掉时应该退化成「这一项没表态」，
    而不是让整次装配炸在解析上——装配是生成路径，炸在这里就等于一章都写不了。
    """
    if not isinstance(value, list):
        return ()
    return tuple(str(word) for word in value if word not in (None, ""))


def build_append_request(
    book_id: str,
    as_of_chapter: int,
    extraction: ChapterExtraction,
    source: ExtractionSource,
) -> dict[str, Any]:
    """把候选增量拼成 ``InternalAssertionAppendRequest`` 的 JSON 形状。

    单独成函数是为了让「线上载荷长什么样」可被直接断言——测试若只走
    MockTransport 的响应侧，字段名写错照样全绿。
    """
    return {
        "bookId": HttpNovelStore._as_int(book_id, "book_id"),
        "asOfChapter": as_of_chapter,
        "idempotencyKey": source.idempotency_key,
        "chapterId": HttpNovelStore._as_int(source.chapter_id, "chapter_id"),
        "assertions": [
            {
                "kind": a.kind,
                "subjectKey": a.subjectKey,
                "predicate": a.predicate,
                "objectText": a.objectText,
                "restatement": a.restatement,
                "confidence": a.confidence,
                "establishedChapter": as_of_chapter,
                "validFromChapter": as_of_chapter,
                "sourceChapterId": HttpNovelStore._as_int(source.chapter_id, "chapter_id"),
                "evidenceQuote": a.evidenceQuote,
                "promptVersion": source.prompt_version,
                "model": source.model,
                "status": a.status or "confirmed",
            }
            for a in extraction.assertions
        ],
        # 抽取只产「埋」：收束要按 id 关闭，而 id 只有 L1 注入的未收清单里有
        "foreshadows": [
            {
                "op": "open",
                "plantedChapter": as_of_chapter,
                "content": f.content,
                "dueByArc": f.dueByArc,
            }
            for f in extraction.foreshadows
        ],
        "aliases": [
            {
                "entityKey": a.entityKey,
                "aliasText": a.aliasText,
                "firstSeenChapter": as_of_chapter,
                "isPrimary": a.isPrimary,
            }
            for a in extraction.aliases
        ],
        "stateChanges": [
            {
                "charKey": s.charKey,
                "asOfChapter": as_of_chapter,
                "isAlive": s.isAlive,
                "locationKey": s.locationKey,
                "knows": s.knows,
                "holds": s.holds,
                "mood": s.mood,
                "lastSeenChapter": as_of_chapter,
            }
            for s in extraction.stateChanges
        ],
    }


__all__ = [
    "HttpCanonStore",
    "HttpNovelStore",
    "NovelStoreError",
    "build_append_request",
]
