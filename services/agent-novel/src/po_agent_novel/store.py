"""小说数据层：持久层协议 + 进程内实现。

两个协议对应两类不同的数据，因此分开：
- ``NovelStore``：成稿本体（书 / 章 / 角色），沿用旧协议；
- ``CanonStore``：L0 正典层（断言 / 状态 / 称谓 / 伏笔 / Finding / 摘要）。
  正典是「会约束后续生成的东西」，写入语义与成稿不同——只追加、靠闭区间演进、
  读侧必须带 as-of 章号，塞进同一个协议里凑合就会丢掉这三个性质。

生产实现见 ``po_agent_novel.http_store``（打 Java 的 /novel/internal/**）；
本模块的内存实现服务于单测与无后端环境（``NOVEL_PERSIST_ENABLED=false``）。

协议是结构性子类型（typing.Protocol）：实现方无需继承，只要方法签名匹配即可
被子图使用；方法声明为 async 是为了让 HTTP 实现与内存实现在调用侧完全同形。

调用方：``graph.archive_node``（用户在 interrupt 处确认归档之后）与
``graph.extract_node``（只产候选，不直接写库——写库统一留在 interrupt 之后，
防 resume 重放把正典写成双份）。
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from typing import Protocol
from uuid import uuid4

from po_agent_novel.schemas import (
    ArchivedBook,
    AssertionCandidate,
    BookDraft,
    ChapterDraft,
    ChapterExtraction,
    CharacterProfile,
)


class NovelStore(Protocol):
    """成稿数据层协议（归档写入 + 书目查询）。

    方法粒度对齐 Java novel 模块的资源划分（book / chapter / character）。

    book_id 是三种资源之间的唯一关联键：save_book 先建书目并返回 id，
    章节与角色再按该 id 写入（调用顺序见 graph.archive_node）。
    """

    async def save_book(self, draft: BookDraft) -> str:
        """保存书稿元数据，返回 book_id。"""
        ...

    async def save_chapters(self, book_id: str, chapters: list[ChapterDraft]) -> list[str]:
        """批量保存章节正文，按入参顺序返回各章 id。

        返回值是本轮新加的：断言溯源（canon_entry.source_chapter_id）与幂等键
        都要引用章节 id，而章节 id 只在落库之后才存在，不返回就没法给正典标出处。
        语义仍是「整体写入」而非增量追加。
        """
        ...

    async def save_characters(
        self, book_id: str, characters: list[CharacterProfile]
    ) -> None:
        """保存角色档案（整体写入，来源为归档前的角色提取结果）。"""
        ...

    async def list_books(self) -> list[ArchivedBook]:
        """列出已归档书目（回溯续写的数据入口）。"""
        ...

    async def load_book(self, book_id: str, *, chapter_id: str | None = None) -> BookSnapshot:
        """读回书目元数据 + 参照章（对话装配用，§10.3-②「同一份上下文」）。

        只带单章正文：L1 编译器对已定稿章节的全部需求是参照章的标题与末尾原文，
        其余都在摘要树里。整本正文不过网，一次对话的开销才不随书长增长。
        """
        ...


@dataclass(frozen=True, slots=True)
class ChapterSnapshot:
    """参照章（``load_book`` 的子记录）。"""

    chapter_id: str
    index: int
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class BookSnapshot:
    """一本书的装配输入：Tier-0 的背景 + 任务区的参照章。

    ``chapter`` 为 ``None`` 表示没点到参照章（或那一章不属于这本书）：此时任务区
    只有「这本书还不存在第 N 章」这一种诚实说法，编译器不许拿别的章凑数。
    """

    book_id: str
    title: str
    genre: str
    summary: str
    chapter_count: int
    chapter: ChapterSnapshot | None


class NovelStoreError(RuntimeError):
    """数据层不可用：网络失败、后端业务错误或返回结构异常。

    定义在协议模块而不是 HTTP 模块，是为了让 graph 只依赖 ``store``：
    捕获数据层失败不该把 httpx 拉进子图的导入链。
    """


@dataclass(frozen=True, slots=True)
class ExtractionSource:
    """一次抽取的来源标识，同时是幂等键的原料。

    ``content_hash`` + ``prompt_version`` + ``model`` 三者齐备才构成
    「同一章、同一版正文、同一份抽取」；缺任一项，重放就只能靠猜。
    """

    chapter_id: str
    content_hash: str
    prompt_version: str
    model: str

    @property
    def idempotency_key(self) -> str:
        return f"{self.chapter_id}:{self.content_hash[:16]}:{self.prompt_version}:{self.model}"


@dataclass(frozen=True, slots=True)
class CanonAssertion:
    """正典断言（读侧视图）。"""

    id: str
    book_id: str
    kind: str
    subject_key: str
    predicate: str
    object_text: str
    restatement: str
    authority: str
    established_chapter: int | None
    valid_from_chapter: int
    valid_until_chapter: int | None
    status: str


@dataclass(frozen=True, slots=True)
class ForeshadowRecord:
    """未收伏笔（读侧视图）。"""

    id: str
    book_id: str
    planted_chapter: int
    content: str
    due_by_arc: int | None


@dataclass(frozen=True, slots=True)
class SceneSummary:
    """一个场景的摘要（写侧载荷，L1 编译器消费）。"""

    scene_no: int
    content: str
    tokens: int | None = None


@dataclass(frozen=True, slots=True)
class SummaryRecord:
    """层级摘要树的一节（读侧视图）。

    ``chapter_no`` 是该节覆盖区间的**起始章号**：scene/chapter 级就是它那一章，
    arc 级是弧的第一章（区间终点由服务端参与过滤，不回传——读侧拿到手的
    永远是「整段都已知」的摘要，客户端不需要再判一次）。
    """

    id: str
    level: str
    chapter_no: int | None
    scene_no: int | None
    content: str
    tokens: int | None = None


@dataclass(slots=True)
class AppendOutcome:
    """写入结果：把「重放被识别」与「真的写了」区分开。"""

    applied: bool
    assertion_ids: list[str] = field(default_factory=list)
    inserted: int = 0
    skipped: int = 0


@dataclass(frozen=True, slots=True)
class StyleProfileRecord:
    """文风契约（``style_profile`` 表）的读侧视图。

    全字段可选是有意的：作者是逐条收紧契约的，一次只定「人称 + 字数带」是常态。
    ``None`` 表示这一项作者没表态，装配侧要保留派生值而不是当成空串覆盖上去。

    这里没有 ``genre``：书的类型属于 ``book`` 行，契约只覆写文风维度。
    """

    person: str | None = None
    tense: str | None = None
    sentence_len_min: int | None = None
    sentence_len_max: int | None = None
    chapter_words_min: int | None = None
    chapter_words_max: int | None = None
    forbidden_words: tuple[str, ...] = ()
    tics: tuple[str, ...] = ()
    taboo: tuple[str, ...] = ()


class CanonStore(Protocol):
    """L0 正典层协议。

    读侧一律带 ``as_of_chapter``：不带章号的正典读取等于把后文剧透给正在写
    第 N 章的模型，回溯重写时会把第 30 章的事实写进第 12 章。

    写侧只有追加与闭区间，没有「删除断言」：旧事实是 as-of 查询的地基。
    """

    async def append_assertions(
        self,
        book_id: str,
        as_of_chapter: int,
        extraction: ChapterExtraction,
        source: ExtractionSource,
    ) -> AppendOutcome:
        """把一章的候选增量入库；幂等键命中已提交记录时返回未生效的重放。"""
        ...

    async def close_assertion_range(
        self, assertion_id: str, until_chapter: int, reason: str
    ) -> None:
        """关闭断言有效期：``until_chapter`` 是该断言最后仍然成立的章号（含端点）。"""
        ...

    async def load_snapshot(
        self,
        book_id: str,
        as_of_chapter: int,
        entities: list[str] | None = None,
        kinds: list[str] | None = None,
    ) -> list[CanonAssertion]:
        """读取截至该章仍成立的已确认断言（disputed 与 todo 不参与注入）。"""
        ...

    async def load_open_foreshadows(
        self, book_id: str, as_of_chapter: int
    ) -> list[ForeshadowRecord]:
        """读取截至该章已埋未收的伏笔。"""
        ...

    async def save_findings(
        self, chapter_id: str, findings: list[dict[str, object]], idempotency_key: str
    ) -> None:
        """冲突台账入库（闸门产物，N4 起才有真实调用方）。

        去重靠**内容键** ``(chapter_id, code, checker, text_start)``，与
        ``CanonTxWriter.persistFindings`` 的查重条件一致；``idempotency_key`` 只是
        随请求带上、服务端不看。两套实现都不许改这个口径：闸门每章都会重跑，
        按调用键去重等于「换个提示词版本就翻倍台账」。
        """
        ...

    async def save_chapter_summaries(
        self,
        book_id: str,
        chapter_id: str,
        chapter_no: int,
        scenes: list[SceneSummary],
        digest: str | None = None,
    ) -> None:
        """写一章的场景摘要，``digest`` 非空时同时写该章的章级摘要。

        签名里既有 ``chapter_id``（服务端定位行、取正文版本）又有 ``chapter_no``
        （区间过滤的键）：Java 侧能从章节行推出章号，内存实现没有表可查，
        两个都收才能让两套实现落在同一个 as-of 语义上。
        """
        ...

    async def save_arc_summary(
        self, book_id: str, arc_no: int, from_chapter: int, to_chapter: int, content: str
    ) -> None:
        """写弧级摘要（跨章区间）。

        只从章级摘要合成，绝不做「摘要的摘要再摘要」——套娃是记忆污染的放大器
        （§6-4）。同一弧号重复写按覆盖处理。
        """
        ...

    async def load_summaries(
        self,
        book_id: str,
        upto_chapter: int,
        levels: Sequence[str] = ("scene", "chapter"),
        limit: int = 24,
    ) -> list[SummaryRecord]:
        """读取「整段区间都 ≤ upto_chapter」的摘要，新的在前。

        与 :meth:`load_snapshot` 的 as-of 语义**不同**：断言按区间与 as-of 相交
        过滤（那条事实在第 N 章仍然成立就该看见），摘要按整段已知过滤——
        一段覆盖 11~20 章的弧摘要里含着第 20 章的剧情，写第 12 章时按相交注入
        就是剧透。
        """
        ...

    async def load_style_profile(self, book_id: str) -> StyleProfileRecord | None:
        """读取作者定的文风契约；``None`` 表示这本书还没定过契约。

        只有读侧没有写侧：契约的写入方是管理端（作者手改），模型与生成链路都不许
        写这张表——「作者收紧的禁用词」如果 agent 也能改，闸门读的词表就成了模型自己
        写的，§10.5-② 那条提权路径只是换了张表。
        """
        ...


def content_hash(text: str) -> str:
    """正文的 sha256 摘要，幂等键的组成部分。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pending_assertions(
    book_id: str, as_of_chapter: int, extraction: ChapterExtraction
) -> list[CanonAssertion]:
    """把「本轮已抽、尚未入库」的候选转成读侧视图，供 L1 编译器当 overlay 用。

    正典写入刻意留在归档确认之后（resume 重放会把入库写成双份），于是连续写多章时
    第 2 章从库里读不到第 1 章的事实。id 留空：它没有库主键，编译器会以
    ``pending:`` 前缀补上可回指的标识。
    """
    return [_to_record("", book_id, as_of_chapter, item) for item in extraction.assertions]


class MockNovelStore:
    """进程内成稿实现：uuid 主键、列表保存、重启即失。

    仅用于开发与测试；换真实实现时按 NovelStore 协议提供 HTTP 版本即可。
    """

    def __init__(self) -> None:
        # 三张表按 book_id 关联，对应协议里的三类资源。
        self._meta: dict[str, BookDraft] = {}
        self._chapters: dict[str, list[ChapterDraft]] = {}
        self._characters: dict[str, list[CharacterProfile]] = {}
        # 章节 id → 章：load_book 按 id 点名单章，没有这张表就只能靠列表序号猜，
        # 而 save_chapters 返回的 id 顺序正是调用方唯一知道的东西。
        self._chapter_ids: dict[str, dict[str, ChapterDraft]] = {}

    async def save_book(self, draft: BookDraft) -> str:
        # 短主键（12 位十六进制）足够避免碰撞，且便于在日志与用户回执中辨识。
        book_id = f"book-{uuid4().hex[:12]}"
        self._meta[book_id] = draft
        # 先把章节/角色表初始化为空列表，list_books 的聚合计数无需再判 None。
        self._chapters[book_id] = []
        self._characters[book_id] = []
        self._chapter_ids[book_id] = {}
        return book_id

    async def save_chapters(self, book_id: str, chapters: list[ChapterDraft]) -> list[str]:
        self._require(book_id)
        # 复制一份入参列表：调用方后续若改动自己的列表，不影响已归档数据。
        self._chapters[book_id] = list(chapters)
        ids = [f"chapter-{uuid4().hex[:12]}" for _ in chapters]
        self._chapter_ids[book_id] = dict(zip(ids, self._chapters[book_id]))
        return ids

    async def save_characters(
        self, book_id: str, characters: list[CharacterProfile]
    ) -> None:
        self._require(book_id)
        self._characters[book_id] = list(characters)

    async def list_books(self) -> list[ArchivedBook]:
        # 以书目表为基准遍历，章节/角色计数缺失时按 0 处理（防御式取默认值）。
        return [
            ArchivedBook(
                book_id=book_id,
                title=draft.title,
                genre=draft.genre,
                summary=draft.summary,
                chapter_count=len(self._chapters.get(book_id, [])),
                character_count=len(self._characters.get(book_id, [])),
            )
            for book_id, draft in self._meta.items()
        ]

    async def load_book(self, book_id: str, *, chapter_id: str | None = None) -> BookSnapshot:
        self._require(book_id)
        draft = self._meta[book_id]
        chosen = self._chapter_ids[book_id].get(chapter_id) if chapter_id else None
        return BookSnapshot(
            book_id=book_id,
            title=draft.title,
            genre=draft.genre,
            summary=draft.summary,
            chapter_count=len(self._chapters[book_id]),
            chapter=None
            if chosen is None
            else ChapterSnapshot(
                chapter_id=str(chapter_id),
                index=chosen.index,
                title=chosen.title,
                content=chosen.content,
            ),
        )

    def _require(self, book_id: str) -> None:
        """校验 book_id 已存在：把真实数据层的外键约束在 mock 里显式化。"""
        if book_id not in self._meta:
            raise KeyError(f"book 不存在：{book_id}")


class InMemoryCanonStore:
    """正典层内存实现：给单测与无后端环境用，行为对齐 Java 侧语义。

    刻意复刻四处库约束，否则会出现「测试过了线上照样错」：
    幂等键重放不重复入库、(book, aliasText) 唯一、as-of 区间过滤、
    台账按内容键去重（``idempotencyKey`` 不参与，见 :meth:`save_findings`）。
    """

    def __init__(self) -> None:
        self._entries: list[CanonAssertion] = []
        self._foreshadows: list[ForeshadowRecord] = []
        self._alias_keys: set[tuple[str, str]] = set()
        # 正典协议里没有「读角色状态」的方法（状态只作为 as-of 快照的服务端拼接依据），
        # 这里只保写入记录，保证 inserted 的口径与 Java 回执的四类计数一致。
        self._state_changes: list[dict[str, object]] = []
        self._findings: list[dict[str, object]] = []
        # 与 _findings 同步维护的内容键集合：Java 用唯一索引查重，这里用 set 顶替索引
        self._finding_keys: set[tuple[str, str, str, object]] = set()
        # 摘要行按 dict 存（要就地覆盖）：与 _state_changes 同理，读侧再转 SummaryRecord
        self._summaries: list[dict[str, object]] = []
        # 文风契约按书一份：写入方是管理端，内存里由测试与本地装配塞入
        self._styles: dict[str, StyleProfileRecord] = {}
        self._committed: set[str] = set()
        self._seq = 0

    async def append_assertions(
        self,
        book_id: str,
        as_of_chapter: int,
        extraction: ChapterExtraction,
        source: ExtractionSource,
    ) -> AppendOutcome:
        if source.idempotency_key in self._committed:
            return AppendOutcome(applied=False)
        self._committed.add(source.idempotency_key)

        outcome = AppendOutcome(applied=True)
        for item in extraction.assertions:
            assertion_id = self._next_id("canon")
            self._entries.append(_to_record(assertion_id, book_id, as_of_chapter, item))
            outcome.assertion_ids.append(assertion_id)
            outcome.inserted += 1
        for plant in extraction.foreshadows:
            self._foreshadows.append(
                ForeshadowRecord(
                    id=self._next_id("foreshadow"),
                    book_id=book_id,
                    planted_chapter=as_of_chapter,
                    content=plant.content,
                    due_by_arc=plant.dueByArc,
                )
            )
            outcome.inserted += 1
        for alias in extraction.aliases:
            key = (book_id, alias.aliasText)
            if key in self._alias_keys:
                # 一个称谓指向两个实体属于 C3 冲突，裁定权在作者，这里只跳过不覆盖
                outcome.skipped += 1
                continue
            self._alias_keys.add(key)
            outcome.inserted += 1
        for change in extraction.stateChanges:
            self._state_changes.append({**change.model_dump(), "bookId": book_id})
            outcome.inserted += 1
        return outcome

    async def close_assertion_range(
        self, assertion_id: str, until_chapter: int, reason: str
    ) -> None:
        for position, entry in enumerate(self._entries):
            if entry.id == assertion_id:
                # 闭区间而非删除：旧事实留在库里，as-of 才答得出「第 N 章时已知什么」
                self._entries[position] = replace(entry, valid_until_chapter=until_chapter)
                return
        raise KeyError(f"断言不存在：{assertion_id}")

    async def load_snapshot(
        self,
        book_id: str,
        as_of_chapter: int,
        entities: list[str] | None = None,
        kinds: list[str] | None = None,
    ) -> list[CanonAssertion]:
        wanted_entities = set(entities or ())
        wanted_kinds = set(kinds or ())
        return [
            entry
            for entry in self._entries
            if entry.book_id == book_id
            and entry.status == "confirmed"
            and entry.valid_from_chapter <= as_of_chapter
            and (entry.valid_until_chapter is None or entry.valid_until_chapter >= as_of_chapter)
            and (not wanted_entities or entry.subject_key in wanted_entities)
            and (not wanted_kinds or entry.kind in wanted_kinds)
        ]

    async def load_open_foreshadows(
        self, book_id: str, as_of_chapter: int
    ) -> list[ForeshadowRecord]:
        return [
            record
            for record in self._foreshadows
            if record.book_id == book_id and record.planted_chapter <= as_of_chapter
        ]

    async def save_findings(
        self, chapter_id: str, findings: list[dict[str, object]], idempotency_key: str
    ) -> None:
        del idempotency_key  # 服务端不看这把键（台账去重靠内容键），内存实现也不能拿它兜底
        for finding in findings:
            row = {
                **finding,
                "chapterId": chapter_id,
                "code": _clip_field(finding.get("code"), 32),
                "checker": _clip_field(finding.get("checker"), 16),
            }
            if not row["code"] or not row["checker"]:
                # 与 CanonTxWriter 同一条抛出：缺 code 或 checker 的行既查重不了，
                # 也回答不了「哪个检查器在说哪件事」。内存实现吞下它 = 单测绿灯、线上 500。
                raise ValueError("Finding 缺少 code 或 checker")
            dedupe_key = _finding_key(row)
            if dedupe_key in self._finding_keys:
                continue
            self._finding_keys.add(dedupe_key)
            self._findings.append(row)

    async def save_chapter_summaries(
        self,
        book_id: str,
        chapter_id: str,
        chapter_no: int,
        scenes: list[SceneSummary],
        digest: str | None = None,
    ) -> None:
        del chapter_id  # 内存实现按章号定位行；Java 侧才需要章节行去取正文版本
        for scene in scenes:
            self._upsert_summary(
                book_id, "scene", chapter_no, chapter_no, scene.scene_no,
                scene.content, scene.tokens,
            )
        if digest:
            # 章级摘要没有场景序号（与 Java 侧「scene_no 留 0 表示该级无序号」同口径）
            self._upsert_summary(book_id, "chapter", chapter_no, chapter_no, 0, digest, None)

    async def save_arc_summary(
        self, book_id: str, arc_no: int, from_chapter: int, to_chapter: int, content: str
    ) -> None:
        if not 1 <= from_chapter <= to_chapter:
            raise ValueError(f"弧区间非法：{from_chapter}-{to_chapter}")
        self._upsert_summary(book_id, "arc", from_chapter, to_chapter, arc_no, content, None)

    async def load_summaries(
        self,
        book_id: str,
        upto_chapter: int,
        levels: Sequence[str] = ("scene", "chapter"),
        limit: int = 24,
    ) -> list[SummaryRecord]:
        wanted = set(levels)
        rows = [
            row
            for row in self._summaries
            if row["book_id"] == book_id
            and row["level"] in wanted
            # 整段已知：区间终点也要 ≤ upto，否则弧摘要会把 upto 之后的剧情带进注入
            and row["from_chapter"] <= upto_chapter
            and row["to_chapter"] <= upto_chapter
        ]
        rows.sort(key=lambda row: (-row["from_chapter"], row["scene_no"] or 0))
        return [
            SummaryRecord(
                id=row["id"],
                level=row["level"],
                chapter_no=row["from_chapter"],
                scene_no=row["scene_no"],
                content=row["content"],
                tokens=row["tokens"],
            )
            for row in rows[:limit]
        ]

    async def load_style_profile(self, book_id: str) -> StyleProfileRecord | None:
        return self._styles.get(book_id)

    def put_style_profile(self, book_id: str, record: StyleProfileRecord) -> None:
        """内存侧的契约写入：真实写入方是管理端 PUT，这里只给测试与本地装配用。"""
        self._styles[book_id] = record

    def _upsert_summary(
        self,
        book_id: str,
        level: str,
        from_chapter: int,
        to_chapter: int,
        scene_no: int | None,
        content: str,
        tokens: int | None,
    ) -> None:
        """按 (book, level, 定位键) 覆盖写：摘要可重算，正典不可重写，两者的写语义不同。"""
        for row in self._summaries:
            if row["book_id"] != book_id or row["level"] != level:
                continue
            # arc 级按弧号定位（跨章区间会变），scene/chapter 级按起始章号定位
            if level == "arc":
                same = row["scene_no"] == scene_no
            else:
                same = row["from_chapter"] == from_chapter and row["scene_no"] == scene_no
            if same:
                row["to_chapter"] = to_chapter
                row["content"] = content
                row["tokens"] = tokens
                return
        self._summaries.append(
            {
                "id": self._next_id("summary"),
                "book_id": book_id,
                "level": level,
                "from_chapter": from_chapter,
                "to_chapter": to_chapter,
                "scene_no": scene_no,
                "content": content,
                "tokens": tokens,
            }
        )

    def _next_id(self, prefix: str) -> str:
        self._seq += 1
        return f"{prefix}-{self._seq}"


def _clip_field(value: object, limit: int) -> str:
    """与 CanonTxWriter.clip 同口径的入列截断：库里的 code/checker 可能是超长的模型输出。"""
    return str(value or "")[:limit]


def _finding_key(finding: dict[str, object]) -> tuple[str, str, str, object]:
    """台账的内容唯一键，逐项对齐 CanonTxWriter 的查重条件。

    两处容易看漏：``revision`` 来自章节行而非 Finding 本身（内存实现没有表可查，
    同章改写后的新台账会撞在这里，代价已记进 PRD §15.3）；``textStart`` 为空时
    Java 走 ``isNull`` 而不是忽略，所以章级发现（无 span 的那些）在同一章里只会落一条。
    """
    return (
        str(finding.get("chapterId") or ""),
        str(finding.get("code") or ""),
        str(finding.get("checker") or ""),
        finding.get("textStart"),
    )


def _to_record(
    assertion_id: str, book_id: str, as_of_chapter: int, item: AssertionCandidate
) -> CanonAssertion:
    return CanonAssertion(
        id=assertion_id,
        book_id=book_id,
        kind=item.kind,
        subject_key=item.subjectKey,
        predicate=item.predicate,
        object_text=item.objectText,
        restatement=item.restatement,
        # 权威级由服务端判定，模型自证最高只到 model
        authority="model",
        established_chapter=as_of_chapter,
        valid_from_chapter=as_of_chapter,
        valid_until_chapter=None,
        status=item.status or "confirmed",
    )


__all__ = [
    "AppendOutcome",
    "BookSnapshot",
    "CanonAssertion",
    "CanonStore",
    "ChapterSnapshot",
    "ExtractionSource",
    "ForeshadowRecord",
    "InMemoryCanonStore",
    "MockNovelStore",
    "NovelStore",
    "NovelStoreError",
    "SceneSummary",
    "StyleProfileRecord",
    "SummaryRecord",
    "content_hash",
    "pending_assertions",
]
