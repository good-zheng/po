"""数据层单测：锁定 NovelStore / CanonStore 两个协议的语义。

``MockNovelStore`` 与 ``InMemoryCanonStore`` 是 HTTP 实现（http_store）的
行为基线——协议里写下的语义（章节 id 回执、幂等重放、唯一冲突跳过、as-of 过滤）
必须在两边一致，否则「换数据源不改子图」这条分层承诺就是空的。
"""

from __future__ import annotations

import pytest

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
    InMemoryCanonStore,
    MockNovelStore,
    NovelStoreError,
    content_hash,
)


def _draft() -> BookDraft:
    return BookDraft(title="云海孤鸿", genre="玄幻", summary="少年偶得上古残卷。")


def _assertion(subject: str = "char:linwan", quote: str = "他数到第七块砖") -> AssertionCandidate:
    return AssertionCandidate(
        kind="character",
        subjectKey=subject,
        predicate="eye_color",
        objectText="金色",
        restatement="林晚的眼睛是金色的。",
        evidenceQuote=quote,
    )


def _source(chapter_id: str = "1", text: str = "正文") -> ExtractionSource:
    return ExtractionSource(
        chapter_id=chapter_id,
        content_hash=content_hash(text),
        prompt_version="v1",
        model="deepseek-chat",
    )


# ---------- 成稿协议 ----------


async def test_save_and_list_roundtrip() -> None:
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    assert book_id.startswith("book-")

    await store.save_chapters(
        book_id,
        [
            ChapterDraft(index=1, title="启程", content="夜色压得很低。"),
            ChapterDraft(index=2, title="暗流", content="看似平静。"),
        ],
    )
    await store.save_characters(
        book_id, [CharacterProfile(name="林晚", role="主角", description="少年")]
    )

    books = await store.list_books()
    assert len(books) == 1
    book = books[0]
    assert book.book_id == book_id
    assert book.title == "云海孤鸿"
    assert book.chapter_count == 2
    assert book.character_count == 1


async def test_save_chapters_returns_one_id_per_chapter_in_order() -> None:
    """章节 id 回执是正典溯源的前提：数量与顺序都必须与入参一致。"""
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    chapters = [
        ChapterDraft(index=1, title="启程", content="一"),
        ChapterDraft(index=2, title="暗流", content="二"),
        ChapterDraft(index=3, title="裂隙", content="三"),
    ]
    ids = await store.save_chapters(book_id, chapters)
    assert len(ids) == len(chapters)
    assert len(set(ids)) == len(ids)  # 互不相同，否则正典会把三章混成同一出处


async def test_unknown_book_id_raises() -> None:
    store = MockNovelStore()
    with pytest.raises(KeyError):
        await store.save_chapters("book-missing", [])


async def test_books_are_isolated_per_id() -> None:
    store = MockNovelStore()
    first = await store.save_book(_draft())
    second = await store.save_book(_draft())
    await store.save_chapters(first, [ChapterDraft(index=1, title="启程", content="一")])
    await store.save_chapters(second, [])
    books = {b.book_id: b for b in await store.list_books()}
    assert books[first].chapter_count == 1
    assert books[second].chapter_count == 0


async def test_load_book_returns_meta_plus_named_reference_chapter() -> None:
    """对话装配要的是「这本书 + 我点的那一章」，不是整本正文。"""
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    ids = await store.save_chapters(
        book_id,
        [
            ChapterDraft(index=1, title="启程", content="夜色压得很低。"),
            ChapterDraft(index=2, title="暗流", content="看似平静。"),
        ],
    )
    snap = await store.load_book(book_id, chapter_id=ids[1])
    assert (snap.book_id, snap.title, snap.genre, snap.summary) == (
        book_id,
        "云海孤鸿",
        "玄幻",
        "少年偶得上古残卷。",
    )
    assert snap.chapter_count == 2
    assert snap.chapter is not None
    assert (snap.chapter.chapter_id, snap.chapter.index, snap.chapter.title) == (
        ids[1],
        2,
        "暗流",
    )
    assert snap.chapter.content == "看似平静。"


async def test_load_book_without_reference_chapter_is_not_an_error() -> None:
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    await store.save_chapters(book_id, [ChapterDraft(index=1, title="启程", content="一")])
    snap = await store.load_book(book_id)
    assert snap.chapter is None
    assert snap.chapter_count == 1


async def test_load_book_ignores_chapter_of_another_book() -> None:
    """别书的章号打进来只能读成「这本书没有这一章」，绝不能拿那一章凑数。"""
    store = MockNovelStore()
    first = await store.save_book(_draft())
    second = await store.save_book(_draft())
    first_ids = await store.save_chapters(
        first, [ChapterDraft(index=1, title="启程", content="一")]
    )
    await store.save_chapters(second, [ChapterDraft(index=1, title="另一本", content="二")])
    snap = await store.load_book(second, chapter_id=first_ids[0])
    assert snap.chapter is None


async def test_blank_placeholder_chapter_is_not_counted_as_written() -> None:
    """管理端留空的「待写占位」不算写过：游标数的是有正文的章，不是章节行数。

    按行数计游标会让续写跳过这一章往后写，于是它永久空着，而衔接用的「上一章结尾」
    恰好读成这个空串——两处同时错，且错得很安静。
    """
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    ids = await store.save_chapters(
        book_id,
        [
            ChapterDraft(index=1, title="第一章", content="正文一"),
            ChapterDraft(index=2, title="", content=""),
        ],
    )
    assert (await store.load_book(book_id)).chapter_count == 1
    assert (await store.list_books())[0].chapter_count == 1

    # 占位行本身仍可被点名读出来——它是排期，不是不存在
    snap = await store.load_book(book_id, chapter_id=ids[1])
    assert snap.chapter is not None
    assert (snap.chapter.index, snap.chapter.content) == (2, "")

    # 续写填掉它：行 id 不变（正典断言按 chapter_id 溯源），计数才往前走
    [refilled] = await store.save_chapters(
        book_id, [ChapterDraft(index=2, title="第二章", content="正文二")]
    )
    assert refilled == ids[1]
    assert (await store.load_book(book_id)).chapter_count == 2


async def test_refill_of_a_written_chapter_is_refused() -> None:
    """同号写入只在「那一行还空着」时被允许：已定稿的正文绝不被静默改写。"""
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    [chapter_id] = await store.save_chapters(
        book_id, [ChapterDraft(index=1, title="第一章", content="正文一")]
    )
    with pytest.raises(NovelStoreError):
        await store.save_chapters(book_id, [ChapterDraft(index=1, title="改名", content="重写")])
    snap = await store.load_book(book_id, chapter_id=chapter_id)
    assert snap.chapter is not None and snap.chapter.content == "正文一"


async def test_load_book_of_unknown_book_raises() -> None:
    store = MockNovelStore()
    with pytest.raises(KeyError):
        await store.load_book("book-missing")


# ---------- 正典协议 ----------


async def test_append_then_snapshot() -> None:
    canon = InMemoryCanonStore()
    outcome = await canon.append_assertions(
        "1", 3, ChapterExtraction(assertions=[_assertion()]), _source("11")
    )
    assert outcome.applied is True
    assert outcome.inserted == 1
    snapshot = await canon.load_snapshot("1", 3)
    assert [e.subject_key for e in snapshot] == ["char:linwan"]
    # 权威级由服务端判定：模型自证最高只到 model
    assert snapshot[0].authority == "model"
    assert snapshot[0].established_chapter == 3


async def test_replay_of_same_key_does_not_duplicate() -> None:
    """退出条件「重放不重复」的内存侧对应：同幂等键第二次写入不产新记录。"""
    canon = InMemoryCanonStore()
    extraction = ChapterExtraction(assertions=[_assertion()])
    source = _source("11", "同一版正文")
    first = await canon.append_assertions("1", 3, extraction, source)
    replay = await canon.append_assertions("1", 3, extraction, source)
    assert first.applied is True
    assert replay.applied is False
    assert replay.inserted == 0
    assert len(await canon.load_snapshot("1", 3)) == 1


async def test_different_content_hash_is_not_replay() -> None:
    """正文改过就不是重放：修订后重跑抽取应当入库，否则闸门永远补不上。"""
    canon = InMemoryCanonStore()
    extraction = ChapterExtraction(assertions=[_assertion()])
    await canon.append_assertions("1", 3, extraction, _source("11", "旧稿"))
    newer = await canon.append_assertions("1", 3, extraction, _source("11", "新稿"))
    assert newer.applied is True


async def test_idempotency_key_covers_all_four_dimensions() -> None:
    """幂等键必须同时含章号/正文摘要/提示词版本/模型：缺任一项都会互相屏蔽。"""
    base = _source("11", "正文")
    assert base.idempotency_key == f"11:{content_hash('正文')[:16]}:v1:deepseek-chat"
    for other in (
        _source("12", "正文"),
        _source("11", "别的正文"),
        ExtractionSource("11", content_hash("正文"), "v2", "deepseek-chat"),
        ExtractionSource("11", content_hash("正文"), "v1", "qwen-max"),
    ):
        assert other.idempotency_key != base.idempotency_key


async def test_snapshot_filters_by_as_of_chapter() -> None:
    """as-of 是正典读取的硬要求：第 5 章才成立的事实不能注入第 3 章。"""
    canon = InMemoryCanonStore()
    await canon.append_assertions(
        "1", 5, ChapterExtraction(assertions=[_assertion()]), _source("55")
    )
    assert await canon.load_snapshot("1", 3) == []
    assert len(await canon.load_snapshot("1", 5)) == 1


async def test_closed_range_stops_matching_after_until_chapter() -> None:
    """闭区间：until 当章仍成立，之后不再注入（而非删除记录）。"""
    canon = InMemoryCanonStore()
    outcome = await canon.append_assertions(
        "1", 2, ChapterExtraction(assertions=[_assertion()]), _source("22")
    )
    await canon.close_assertion_range(outcome.assertion_ids[0], 6, "第 7 章双眼变色")
    assert len(await canon.load_snapshot("1", 6)) == 1
    assert await canon.load_snapshot("1", 7) == []
    # 记录仍在：as-of 早于闭合点的查询照旧答得出来
    assert len(await canon.load_snapshot("1", 3)) == 1


async def test_todo_status_is_not_injected() -> None:
    """机制③：缺口登记为 todo，只用来提示作者补设定，绝不作为事实注入提示词。"""
    canon = InMemoryCanonStore()
    gap = _assertion(subject="rule:mengui")
    gap.status = "todo"
    await canon.append_assertions("1", 1, ChapterExtraction(assertions=[gap]), _source("1"))
    assert await canon.load_snapshot("1", 1) == []
    assert len(await canon.load_snapshot("1", 1, entities=["rule:mengui"])) == 0


async def test_duplicate_alias_is_skipped_not_overwritten() -> None:
    """一个称谓指向两个实体属 C3 冲突：跳过而非后写覆盖，裁定权在作者。"""
    canon = InMemoryCanonStore()
    alias = ChapterExtraction(aliases=[AliasCandidate(entityKey="char:linwan", aliasText="沈师兄")])
    await canon.append_assertions("1", 1, alias, _source("1"))
    conflict = ChapterExtraction(
        aliases=[AliasCandidate(entityKey="char:other", aliasText="沈师兄")]
    )
    outcome = await canon.append_assertions("1", 1, conflict, _source("2"))
    assert outcome.applied is True
    assert outcome.skipped == 1


async def test_append_also_records_foreshadows_and_states() -> None:
    """计数口径与 Java 回执一致：断言 + 伏笔 + 称谓 + 状态四类都算 inserted。"""
    canon = InMemoryCanonStore()
    extraction = ChapterExtraction(
        assertions=[_assertion()],
        foreshadows=[ForeshadowPlantCandidate(content="残卷缺的一页去了哪", dueByArc=2)],
        stateChanges=[StateChangeCandidate(charKey="char:linwan", isAlive=True)],
        aliases=[AliasCandidate(entityKey="char:linwan", aliasText="少年", isPrimary=True)],
    )
    outcome = await canon.append_assertions("1", 4, extraction, _source("44"))
    assert outcome.inserted == 4
    open_items = await canon.load_open_foreshadows("1", 4)
    assert [f.content for f in open_items] == ["残卷缺的一页去了哪"]
    # 尚未埋下的章不该看到这条伏笔
    assert await canon.load_open_foreshadows("1", 3) == []


# ---------- 冲突台账（review_finding）----------


def _finding_row(
    code: str = "attribute_conflict",
    start: int | None = 12,
    checker: str = "rule",
) -> dict[str, object]:
    return {
        "code": code,
        "severity": "blocker",
        "checker": checker,
        "canonRefs": [1],
        "textStart": start,
        "textEnd": None if start is None else start + 6,
        "evidenceQuote": "",
        "explanation": "同一主体的同一谓词出现了两个值。",
        "fixInstruction": "",
    }


async def test_ledger_replay_collapses_on_the_content_key() -> None:
    """重放同一处冲突只留一行，且**幂等键不参与判定**。

    Java 侧的查重条件是 (chapterId, revision, code, checker, textStart)，
    内存实现照抄：换一把 idempotencyKey 重投照样不该写双份，否则改一次提示词版本
    或换一个抽取模型就把整本台账刷成双倍。
    """
    canon = InMemoryCanonStore()
    await canon.save_findings("1", [_finding_row()], "1:hashA:findings")
    await canon.save_findings("1", [_finding_row()], "1:hashB:findings")
    assert len(canon._findings) == 1


async def test_ledger_null_span_rows_dedupe_too() -> None:
    """无 span 的章级行按「NULL 也算重复」去重（Java 用的是 isNull，不是忽略该条件）。

    最容易写错的一种：若 NULL 不参与查重，每轮重放都会给整章级冲突（字数越带）
    多添一行，而它恰恰是唯一没有位置的编码。
    """
    canon = InMemoryCanonStore()
    await canon.save_findings("1", [_finding_row("length_out_of_band", None)], "k1")
    await canon.save_findings("1", [_finding_row("length_out_of_band", None)], "k2")
    assert len(canon._findings) == 1


async def test_ledger_keeps_rows_from_both_checkers() -> None:
    """同一处冲突，规则与裁判各留一行：互查的痕迹不许被去重抹平。

    不同落点（textStart 不同）同理都留——per_code_limit 是闸门口径，不是库口径。
    """
    canon = InMemoryCanonStore()
    await canon.save_findings("1", [_finding_row(start=10)], "k")
    await canon.save_findings("1", [_finding_row(start=20)], "k")
    await canon.save_findings("1", [_finding_row(start=10, checker="judge")], "k")
    assert len(canon._findings) == 3


async def test_ledger_rejects_rows_without_code_or_checker() -> None:
    """缺 code 或 checker 直接抛，与 CanonTxWriter 同一条硬失败。

    内存实现吞下它 = 单测绿、线上 500：这两列一个是「哪件事」，一个是「谁说的」，
    缺任意一条的台账行在工作台上无法复核也无法分派。
    """
    canon = InMemoryCanonStore()
    with pytest.raises(ValueError, match="缺少"):
        await canon.save_findings("1", [{**_finding_row(), "code": ""}], "k")
    with pytest.raises(ValueError, match="缺少"):
        await canon.save_findings("1", [{**_finding_row(), "checker": ""}], "k")
    assert canon._findings == []


async def test_ledger_clips_code_and_checker_to_the_column_width() -> None:
    """入列前按列宽截断（code 32 / checker 16），且截断值同时用于去重键。

    不去重键一起截的话：两条超长但前 32 字相同的编码在库里撞成一行、在内存里是两行，
    「测试绿、线上少一行」又回来了。
    """
    canon = InMemoryCanonStore()
    long_code = "x" * 60
    await canon.save_findings("1", [_finding_row(code=long_code), _finding_row(code=long_code)], "k")
    assert [row["code"] for row in canon._findings] == ["x" * 32]
    assert canon._findings[0]["chapterId"] == "1"
