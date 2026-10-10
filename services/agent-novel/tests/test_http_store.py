"""HTTP 数据层单测：用 ``httpx.MockTransport`` 打桩，不发真实请求。

覆盖的是「线上怎么发」这几件事，缺一条就会在真机上线时才暴露：
- 载荷字段名与 Java DTO 一致（camelCase、幂等键、as-of 字段）；
- ``Result`` 信封看 ``success`` 而非状态码；
- 只有 5xx 与传输错误值得重试，业务错误一次即死；
- 重放（applied=false）与失败要各自归位，不能混成「写了」；
- 作者身份（``X-Actor-Uid``）活在任务上下文而不是 store 实例上——后者会让并发连接串读。
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
import pytest

from po_agent_novel.actor import reset_actor, set_actor
from po_agent_novel.config import NovelStoreSettings
from po_agent_novel.http_store import (
    HttpCanonStore,
    HttpNovelStore,
    build_append_request,
)
from po_agent_novel.schemas import (
    AliasCandidate,
    AssertionCandidate,
    BookDraft,
    ChapterDraft,
    ChapterExtraction,
    CharacterProfile,
    ForeshadowPlantCandidate,
    StateChangeCandidate,
)
from po_agent_novel.store import (
    ExtractionSource,
    NovelStoreError,
    SceneSummary,
    content_hash,
)

BOOK = "11"


class _Backend:
    """按脚本应答的假后端：记录每个请求，脚本用尽后重复最后一条。"""

    def __init__(self, *replies: httpx.Response | Exception) -> None:
        self.requests: list[httpx.Request] = []
        self._replies = list(replies)

    @property
    def transport(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            reply = self._replies.pop(0) if len(self._replies) > 1 else self._replies[0]
            if isinstance(reply, Exception):
                raise reply
            return reply

        return httpx.MockTransport(handle)

    def body(self, index: int = 0) -> dict[str, Any]:
        return json.loads(self.requests[index].content)

    def query(self, index: int = 0) -> dict[str, str]:
        return dict(httpx.QueryParams(self.requests[index].url.query))


def _settings(**overrides: Any) -> NovelStoreSettings:
    # retry_backoff_seconds=0：重试语义照测，但不让单测真的等退避
    return NovelStoreSettings(
        _env_file=None,
        api_base_url="http://backend/api",
        internal_token="tk-internal",
        author_id=7,
        max_retries=2,
        retry_backoff_seconds=0.0,
        **overrides,
    )


def _ok(data: Any) -> httpx.Response:
    return httpx.Response(200, json={"code": 200, "success": True, "data": data})


def _biz_fail(message: str) -> httpx.Response:
    """业务失败在 Java 侧也是 HTTP 200：判定必须看 success 字段。"""
    return httpx.Response(200, json={"code": 500, "success": False, "message": message})


def _extraction() -> ChapterExtraction:
    return ChapterExtraction(
        assertions=[
            AssertionCandidate(
                kind="character",
                subjectKey="char:linwan",
                predicate="eye_color",
                objectText="墨绿",
                restatement="林晚的眼睛是墨绿色。",
                evidenceQuote="她抬眼，墨绿色的瞳仁映着灯。",
                confidence=0.9,
            )
        ],
        aliases=[AliasCandidate(entityKey="char:linwan", aliasText="沈师兄", isPrimary=True)],
        stateChanges=[
            StateChangeCandidate(charKey="char:linwan", isAlive=False, locationKey="place:yunjian")
        ],
        foreshadows=[ForeshadowPlantCandidate(content="残卷缺的一页", dueByArc=2)],
    )


def _source(chapter_id: str = "21") -> ExtractionSource:
    return ExtractionSource(
        chapter_id=chapter_id,
        content_hash=content_hash("正文"),
        prompt_version="v1",
        model="qwen-max",
    )


def _receipt(**fields: Any) -> httpx.Response:
    return _ok({"applied": True, "skipped": 0, **fields})


# ---------- 成稿入库 ----------


async def test_save_book_posts_to_internal_channel_with_token() -> None:
    backend = _Backend(_ok({"id": 11}))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    assert await store.save_book(BookDraft(title="云海孤鸿", genre="玄幻", summary="梗概")) == "11"
    request = backend.requests[0]
    assert request.method == "POST"
    assert str(request.url).endswith("/api/novel/internal/books?authorId=7")
    assert request.headers["X-Internal-Token"] == "tk-internal"
    # summary 是 Tier-0 注入用的世界观摘要，description 是书架对外简介：同源双写；
    # genre 发的是字典 value（服务端 requireKnownGenre 只收这十个串，中文 label 整本打回）
    assert backend.body() == {
        "title": "云海孤鸿",
        "summary": "梗概",
        "description": "梗概",
        "genre": "fantasy",
    }


async def test_save_book_sends_value_even_for_compound_genre() -> None:
    backend = _Backend(_ok({"id": 11}))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    await store.save_book(
        BookDraft(title="代码封神", genre="都市科幻（都市异能+赛博救世）", summary="梗概")
    )
    # 实测死过一次：构思给的是复合中文，归档 POST 被「无效的小说类型」打回
    # （BookServiceImpl.requireKnownGenre），三章正文与全部正典就此不落库。
    # 归一放在客户端——服务端刻意保持严格，宽容匹配等于让脏值继续在库里漂。
    assert backend.body()["genre"] == "scifi"


async def test_save_chapters_is_sequential_and_returns_ids_in_order() -> None:
    backend = _Backend(_ok({"id": 21}), _ok({"id": 22}), _ok({"id": 23}))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    chapters = [ChapterDraft(index=i, title=f"第{i}章", content=f"正文{i}") for i in (1, 2, 3)]
    assert await store.save_chapters(BOOK, chapters) == ["21", "22", "23"]
    assert [req.url.path for req in backend.requests] == [
        "/api/novel/internal/books/11/chapters"
    ] * 3
    assert [backend.body(i)["chapterIndex"] for i in range(3)] == [1, 2, 3]


async def test_save_characters_folds_role_into_description() -> None:
    backend = _Backend(_ok({"id": 31}))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    await store.save_characters(BOOK, [CharacterProfile(name="林晚", role="主角", description="剑修")])
    # book_character 没有 role 列：定位词并进 description，不私拆新字段
    assert backend.body() == {"name": "林晚", "description": "主角｜剑修"}


async def test_missing_id_in_receipt_raises_store_error() -> None:
    backend = _Backend(_ok({"title": "云海孤鸿"}))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError, match="缺少 id"):
        await store.save_book(BookDraft(title="t", genre="g", summary="s"))
    assert len(backend.requests) == 1  # 结构契约错误不该重试


# ---------- 成稿读回 ----------


async def test_load_book_sends_params_and_maps_reference_chapter() -> None:
    backend = _Backend(
        _ok(
            {
                "bookId": 11,
                "title": "云海孤鸿",
                "genre": "fantasy",
                "summary": "少年偶得上古残卷。",
                "chapterCount": 37,
                "chapter": {
                    "chapterId": 21,
                    "chapterIndex": 37,
                    "title": "裂隙",
                    "content": "她抬眼，墨绿色的瞳仁映着灯。",
                },
            }
        )
    )
    store = HttpNovelStore(_settings(), transport=backend.transport)

    snap = await store.load_book(BOOK, chapter_id="21")
    request = backend.requests[0]
    assert request.method == "GET"
    assert request.url.path.endswith("/novel/internal/books/detail")
    assert backend.query(0) == {"bookId": "11", "chapterId": "21"}
    assert request.headers["X-Internal-Token"] == "tk-internal"

    assert (snap.title, snap.genre, snap.summary, snap.chapter_count) == (
        "云海孤鸿",
        "玄幻",
        "少年偶得上古残卷。",
        37,
    )
    assert snap.chapter is not None
    # chapterIndex 就是对话侧的 as-of：层号错位会正典泄漏，必须原样传回
    assert (snap.chapter.chapter_id, snap.chapter.index, snap.chapter.content) == (
        "21",
        37,
        "她抬眼，墨绿色的瞳仁映着灯。",
    )


async def test_load_book_without_chapter_id_omits_param_and_reads_null_reference() -> None:
    backend = _Backend(_ok({"bookId": 11, "title": "云海孤鸿", "chapterCount": 0, "chapter": None}))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    snap = await store.load_book(BOOK)
    assert backend.query(0) == {"bookId": "11"}
    assert snap.chapter is None
    assert snap.chapter_count == 0


async def test_load_book_with_malformed_reference_chapter_fails_loud() -> None:
    """参照章缺字段不能读成 chapter=None：那是「这本书没有这一章」的说法形状，

    把坏载荷说成书不存在，模型就会照着一份它以为不存在的正文谈设定。
    """
    backend = _Backend(
        _ok({"bookId": 11, "chapterCount": 2, "chapter": {"chapterId": 21, "title": "裂隙"}})
    )
    store = HttpNovelStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError, match="参照章结构异常"):
        await store.load_book(BOOK, chapter_id="21")
    assert len(backend.requests) == 1


async def test_load_book_of_missing_book_is_a_store_error() -> None:
    backend = _Backend(_biz_fail("书籍不存在"))
    store = HttpNovelStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError, match="书籍不存在"):
        await store.load_book(BOOK)
    assert len(backend.requests) == 1  # 业务错误一次即死，重试只是打爆后端


# ---------- 正典载荷 ----------


def test_append_request_matches_java_dto_shape() -> None:
    source = _source()
    payload = build_append_request(BOOK, 4, _extraction(), source)

    assert set(payload) == {
        "bookId",
        "asOfChapter",
        "idempotencyKey",
        "chapterId",
        "assertions",
        "foreshadows",
        "aliases",
        "stateChanges",
    }
    assert payload["bookId"] == 11 and payload["chapterId"] == 21
    assert payload["idempotencyKey"] == source.idempotency_key

    (assertion,) = payload["assertions"]
    assert assertion["evidenceQuote"] == "她抬眼，墨绿色的瞳仁映着灯。"
    assert assertion["status"] == "confirmed"
    # 建立章与生效起点都由「本轮抽取的 as-of」决定，模型无权指定
    assert assertion["establishedChapter"] == 4 and assertion["validFromChapter"] == 4
    assert assertion["sourceChapterId"] == 21
    assert assertion["promptVersion"] == "v1" and assertion["model"] == "qwen-max"

    # 抽取只产「埋」：收束要按 id 关闭，而 id 只有 L1 注入的未收清单里有
    assert payload["foreshadows"] == [
        {"op": "open", "plantedChapter": 4, "content": "残卷缺的一页", "dueByArc": 2}
    ]
    assert payload["aliases"][0]["firstSeenChapter"] == 4
    assert payload["stateChanges"][0]["asOfChapter"] == 4
    assert payload["stateChanges"][0]["lastSeenChapter"] == 4


def test_non_numeric_id_is_rejected_before_any_request() -> None:
    """离线 store 的 `book-xxxx` 短主键不该变成一次注定 400 的网络请求。"""
    backend = _Backend(_ok({}))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError, match="合法的后端 ID"):
        build_append_request("book-abc01234567", 1, _extraction(), _source())
    assert backend.requests == []


# ---------- 正典写入回执 ----------


async def test_append_inserted_sums_all_four_categories() -> None:
    backend = _Backend(
        _receipt(
            assertionsInserted=3,
            foreshadowsWritten=1,
            aliasesWritten=2,
            stateChangesWritten=1,
        )
    )
    store = HttpCanonStore(_settings(), transport=backend.transport)

    outcome = await store.append_assertions(BOOK, 4, _extraction(), _source())
    assert (outcome.applied, outcome.inserted, outcome.skipped) == (True, 7, 0)
    assert outcome.assertion_ids == []  # 回执不带 id，读回走 snapshot


async def test_replay_is_reported_not_as_failure() -> None:
    """幂等命中在 Java 侧是成功应答（REPLAY），客户端必须原样表达「没写但没失败」。"""
    backend = _Backend(_receipt(assertionsInserted=0, applied=False))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    outcome = await store.append_assertions(BOOK, 4, _extraction(), _source())
    assert outcome.applied is False and outcome.inserted == 0


# ---------- 重试与错误 ----------


async def test_5xx_retries_until_exhausted_then_terminal_error() -> None:
    backend = _Backend(httpx.Response(503, json={}))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError, match="503"):
        await store.append_assertions(BOOK, 4, _extraction(), _source())
    # max_retries=2 ⇒ 首提 + 2 次重试 = 3 次请求，然后进入终态而不是无限重试
    assert len(backend.requests) == 3


async def test_transient_failure_then_success_does_not_raise() -> None:
    backend = _Backend(
        httpx.Response(500, json={}),
        _receipt(assertionsInserted=1),
    )
    store = HttpCanonStore(_settings(), transport=backend.transport)

    outcome = await store.append_assertions(BOOK, 4, _extraction(), _source())
    assert outcome.applied is True and len(backend.requests) == 2


async def test_transport_error_is_retried() -> None:
    backend = _Backend(httpx.ConnectError("boom"), _receipt(assertionsInserted=1))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    outcome = await store.append_assertions(BOOK, 4, _extraction(), _source())
    assert outcome.applied is True


async def test_business_error_fails_fast_without_retry() -> None:
    """403（令牌不匹配）之类重试只会掩盖配置错误，必须一次即死并带上后端原因。"""
    backend = _Backend(_biz_fail("内部令牌无效"))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError, match="内部令牌无效"):
        await store.append_assertions(BOOK, 4, _extraction(), _source())
    assert len(backend.requests) == 1


async def test_non_json_body_fails_as_store_error() -> None:
    backend = _Backend(httpx.Response(200, text="<html>gateway</html>"))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    with pytest.raises(NovelStoreError):
        await store.append_assertions(BOOK, 4, _extraction(), _source())


# ---------- 读侧 ----------


async def test_snapshot_sends_as_of_and_entity_filters() -> None:
    backend = _Backend(
        _ok(
            [
                {
                    "id": 91,
                    "bookId": 11,
                    "kind": "character",
                    "subjectKey": "char:linwan",
                    "predicate": "eye_color",
                    "objectText": "墨绿",
                    "restatement": "林晚的眼睛是墨绿色。",
                    "status": "confirmed",
                    "validFromChapter": 4,
                    "validUntilChapter": None,
                }
            ]
        )
    )
    store = HttpCanonStore(_settings(), transport=backend.transport)

    entries = await store.load_snapshot(BOOK, 6, entities=["char:linwan"], kinds=["character"])
    request = backend.requests[0]
    assert request.method == "GET"
    assert backend.query(0) == {"bookId": "11", "asOf": "6", "entities": "char:linwan", "kinds": "character"}
    assert request.headers["X-Internal-Token"] == "tk-internal"

    (entry,) = entries
    assert entry.id == "91" and entry.status == "confirmed"
    assert entry.authority == "model"  # 抽取来源恒为 model，写侧闸门之外没有别的权限
    assert entry.valid_until_chapter is None


async def test_open_foreshadows_and_close_range_round_trip() -> None:
    backend = _Backend(_ok([{"id": 5, "bookId": 11, "plantedChapter": 2, "content": "残卷缺的一页"}]), _ok(None))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    records = await store.load_open_foreshadows(BOOK, 3)
    assert [(r.id, r.planted_chapter, r.content) for r in records] == [
        ("5", 2, "残卷缺的一页")
    ]

    await store.close_assertion_range("91", until_chapter=7, reason="第 8 章失明")
    assert backend.body(1) == {"assertionId": 91, "untilChapter": 7, "reason": "第 8 章失明"}


# ---------- 层级摘要树（scene / chapter / arc 三级同一条通道） ----------


async def test_chapter_summaries_send_scene_and_chapter_levels() -> None:
    backend = _Backend(_ok(None), _ok(None))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    await store.save_chapter_summaries(
        BOOK,
        "21",
        3,
        [SceneSummary(scene_no=1, content="林晚入城", tokens=12), SceneSummary(scene_no=2, content="夜访旧档房")],
        digest="林晚入城并夜访旧档房。",
    )
    # 一次调用两次请求：scene 级批量、chapter 级单条（章级摘要的 scene_no 恒 0）
    assert backend.body(0) == {
        "chapterId": 21,
        "level": "scene",
        "scenes": [
            {"sceneNo": 1, "content": "林晚入城", "tokens": 12},
            {"sceneNo": 2, "content": "夜访旧档房", "tokens": None},
        ],
    }
    assert backend.body(1) == {
        "chapterId": 21,
        "level": "chapter",
        "scenes": [{"sceneNo": 0, "content": "林晚入城并夜访旧档房。", "tokens": None}],
    }


async def test_chapter_summaries_without_digest_skips_chapter_level() -> None:
    backend = _Backend(_ok(None))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    await store.save_chapter_summaries(BOOK, "21", 3, [SceneSummary(scene_no=1, content="入城")])
    assert len(backend.requests) == 1
    assert backend.body(0)["level"] == "scene"

    await store.save_chapter_summaries(BOOK, "21", 3, [])
    assert len(backend.requests) == 1  # 空场景不空打后端


async def test_arc_summary_carries_span_and_uses_book_id() -> None:
    backend = _Backend(_ok(None))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    await store.save_arc_summary(BOOK, arc_no=2, from_chapter=6, to_chapter=10, content="旧档房一线收束。")
    # arc 级没有章节行可推导，区间与 bookId 必须由客户端给（Java 侧只校验 1<=from<=to）
    assert backend.body() == {
        "bookId": 11,
        "level": "arc",
        "arcNo": 2,
        "fromChapter": 6,
        "toChapter": 10,
        "scenes": [{"sceneNo": 2, "content": "旧档房一线收束。", "tokens": None}],
    }


async def test_load_summaries_sends_upto_and_level_list() -> None:
    backend = _Backend(
        _ok(
            [
                {"id": 71, "level": "chapter", "chapterNo": 3, "sceneNo": 0, "content": "全章摘要", "tokens": 20},
                {"id": 72, "level": "scene", "chapterNo": 3, "sceneNo": 1, "content": "场景摘要", "tokens": 8},
            ]
        )
    )
    store = HttpCanonStore(_settings(), transport=backend.transport)

    rows = await store.load_summaries(BOOK, 3, levels=("scene", "chapter"), limit=6)
    assert backend.query(0) == {"bookId": "11", "upto": "3", "levels": "scene,chapter", "limit": "6"}
    assert [(r.id, r.level, r.chapter_no, r.scene_no) for r in rows] == [
        ("71", "chapter", 3, 0),
        ("72", "scene", 3, 1),
    ]


async def test_style_profile_maps_camel_case_dto() -> None:
    backend = _Backend(
        _ok(
            {
                "id": 3,
                "bookId": 11,
                "person": "第三人称限知",
                "tense": "过去时",
                "sentenceLenMin": 12,
                "sentenceLenMax": 40,
                "chapterWordsMin": 2200,
                "chapterWordsMax": 3200,
                "forbiddenWords": ["禁术", "血祭"],
                "tics": ["不由得"],
                "taboo": [],
            }
        )
    )
    store = HttpCanonStore(_settings(), transport=backend.transport)

    row = await store.load_style_profile(BOOK)
    assert backend.query(0) == {"bookId": "11"}
    assert row is not None
    assert (row.person, row.chapter_words_min, row.chapter_words_max) == ("第三人称限知", 2200, 3200)
    assert row.forbidden_words == ("禁术", "血祭")
    # 空数组是作者明确「这一项清空」，读回来必须是空而不是 None
    assert row.taboo == ()


async def test_missing_style_profile_reads_as_none() -> None:
    """``data:null`` = 这本书没定过契约，装配侧要保留派生值而不是覆盖成空契约。"""
    backend = _Backend(_ok(None))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    assert await store.load_style_profile(BOOK) is None


async def test_corrupt_word_list_degrades_to_untouched() -> None:
    """Java 侧词表是 JSON 文本：坏掉时退化成「这一项没表态」，不能让一章都写不了。"""
    backend = _Backend(
        _ok({"bookId": 11, "person": "第一人称", "forbiddenWords": "禁术", "tics": None})
    )
    store = HttpCanonStore(_settings(), transport=backend.transport)

    row = await store.load_style_profile(BOOK)
    assert row is not None
    assert row.forbidden_words == ()
    assert row.tics == ()
    assert row.person == "第一人称"


# ---------- 作者作用域（X-Actor-Uid） ----------


async def test_actor_header_is_carried_once_an_actor_is_bound() -> None:
    backend = _Backend(_ok([]))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    token = set_actor(7)
    try:
        await store.load_snapshot(BOOK, 3)
    finally:
        reset_actor(token)

    assert backend.requests[0].headers["X-Actor-Uid"] == "7"


async def test_actor_header_absent_when_no_actor_is_bound() -> None:
    """生成链路没有终端用户在场的概念：不带这个头，Java 侧就跳过归属校验。

    这里断言「头不存在」而不是「头为空」：空头在 Java 侧会走「非数字→400」那条分支，
    等于把内部调用全打死。
    """
    backend = _Backend(_ok([]))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    await store.load_snapshot(BOOK, 3)

    assert "X-Actor-Uid" not in backend.requests[0].headers


async def test_actor_bindings_do_not_leak_between_connections() -> None:
    """store 是装配期建一次、所有连接共享的：身份必须活在任务上下文里而不是实例上。

    两个并发任务各绑一位作者读同一本书，若实现把 uid 存成 store 字段，
    后绑的那个会盖掉前一个，两位作者的读口就串了。
    """
    backend = _Backend(*([_ok([])] * 2))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    async def read_as(uid: int) -> None:
        token = set_actor(uid)
        try:
            await store.load_snapshot(BOOK, 3)
        finally:
            reset_actor(token)

    await asyncio.gather(read_as(7), read_as(8))

    assert sorted(request.headers["X-Actor-Uid"] for request in backend.requests) == ["7", "8"]


async def test_reset_restores_the_previous_actor() -> None:
    """连接关掉后必须回到「无身份」：否则同一任务里下一个匿名请求顶着上一个作者的身份。"""
    backend = _Backend(_ok([]), _ok([]))
    store = HttpCanonStore(_settings(), transport=backend.transport)

    token = set_actor(7)
    reset_actor(token)
    await store.load_snapshot(BOOK, 3)

    assert "X-Actor-Uid" not in backend.requests[0].headers
