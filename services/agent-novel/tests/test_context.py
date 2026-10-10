"""L1 上下文编译器的约束测试（PRD §6 的四条装配规则 + 退出条件）。

这里锁的是「注入预算与书长无关」和「回溯续写不泄漏后文」两条铁律——
它们都是编译器的结构性保证，一旦回归就是长篇质量整体崩，不是单章写坏。
断言口径刻意用「块里看不看得到」而非「调用了几次 store」：前者是作者与模型
真正消费的东西，后者重构一下就白掉一片。
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from po_agent_novel.context import (
    Budgets,
    CompiledContext,
    StyleContract,
    approx_tokens,
    compile_context,
)
from po_agent_novel.schemas import (
    AssertionCandidate,
    BookIdea,
    ChapterDraft,
    ChapterExtraction,
    ChapterOutline,
    ForeshadowPlantCandidate,
)
from po_agent_novel.store import (
    CanonAssertion,
    ChapterSnapshot,
    ExtractionSource,
    InMemoryCanonStore,
    SceneSummary,
    StyleProfileRecord,
    SummaryRecord,
)

BOOK = "11"
_IDEA = BookIdea(title="云海孤鸿", genre="玄幻", summary="少年偶得残卷，卷入两宗百年恩怨。")
_OUTLINE = [
    ChapterOutline(title="启程", summary="主角离开熟悉的环境。"),
    ChapterOutline(title="暗流", summary="各方势力开始试探。"),
    ChapterOutline(title="裂隙", summary="真相撕开一角。"),
]
_EVIDENCE = "她抬眼，墨绿色的瞳仁映着灯。"


def _assertion(subject: str, predicate: str, value: str) -> AssertionCandidate:
    return AssertionCandidate(
        kind="character",
        subjectKey=subject,
        predicate=predicate,
        objectText=value,
        restatement=f"{subject} 的 {predicate} 是 {value}。",
        evidenceQuote=_EVIDENCE,
    )


async def _seed(
    store: InMemoryCanonStore, chapter: int, assertions: list[AssertionCandidate]
) -> None:
    """按章追加一批候选：幂等键含 chapter_id，因此逐章调用不会互相屏蔽。"""
    await store.append_assertions(
        BOOK,
        chapter,
        ChapterExtraction(assertions=assertions),
        ExtractionSource(
            chapter_id=str(chapter),
            content_hash=f"hash-{chapter}",
            prompt_version="v1",
            model="test-model",
        ),
    )


def _chapters(count: int, *, tail: str = "灯下他终于看清那半枚虎符的裂纹。") -> list[ChapterDraft]:
    return [
        ChapterDraft(index=n, title=f"第{n}章", content=f"第{n}章正文。" + tail)
        for n in range(1, count + 1)
    ]


async def _compile(
    store: InMemoryCanonStore, index: int, **kwargs: object
) -> CompiledContext:
    kwargs.setdefault("chapters", _chapters(index))
    return await compile_context(
        store,
        book_id=BOOK,
        idea=_IDEA,
        outline=_OUTLINE,
        index=index,
        **kwargs,  # type: ignore[arg-type]
    )


# ---------- 开篇：没有库可读时也要给出可用的块 ----------


async def test_first_chapter_compiles_without_any_store_read() -> None:
    """book_id=None（本轮尚未归档）+ index=0：Tier-1/2 整段跳过，不拿假 id 打后端。"""

    class _NoReads(InMemoryCanonStore):
        def __init__(self) -> None:
            super().__init__()
            self.reads = 0

        async def load_snapshot(self, *a: object, **kw: object) -> list[CanonAssertion]:
            self.reads += 1
            return await super().load_snapshot(*a, **kw)  # type: ignore[arg-type]

        async def load_summaries(self, *a: object, **kw: object) -> list[SummaryRecord]:
            self.reads += 1
            return await super().load_summaries(*a, **kw)  # type: ignore[arg-type]

        async def load_open_foreshadows(self, *a: object, **kw: object) -> list[CanonAssertion]:
            self.reads += 1
            return await super().load_open_foreshadows(*a, **kw)  # type: ignore[arg-type]

        async def load_style_profile(self, *a: object, **kw: object) -> StyleProfileRecord | None:
            # 文风契约也是库读：书还没归档时拿 None 去打后端，会和摘要一样先炸在这里
            self.reads += 1
            return await super().load_style_profile(*a, **kw)  # type: ignore[arg-type]

    store = _NoReads()
    compiled = await compile_context(
        store,
        book_id=None,
        idea=_IDEA,
        outline=_OUTLINE,
        index=0,
        chapters=[],
    )
    assert store.reads == 0
    assert compiled.counts["tier1"] == 0
    assert "（无登记）" in compiled.block
    assert "本章大纲：《启程》" in compiled.block


async def test_second_chapter_sees_first_chapter_facts() -> None:
    store = InMemoryCanonStore()
    await _seed(store, 1, [_assertion("char:shenqing", "eye_color", "墨绿")])

    compiled = await _compile(store, 1)
    assert "[canon#1] char:shenqing · eye_color = 墨绿" in compiled.block
    assert compiled.refs[0].number == 1
    assert compiled.refs[0].source_id == "canon-1"
    assert compiled.counts["tier1"] == 1


# ---------- 退出条件：回溯续写不泄漏后文 ----------


async def test_backwriting_hides_facts_established_later() -> None:
    """重写第 12 章时，第 20 章才成立的事实与第 20 章才埋的伏笔都不该进块。"""
    store = InMemoryCanonStore()
    await _seed(store, 5, [_assertion("char:shenqing", "eye_color", "墨绿")])
    await _seed(store, 20, [_assertion("char:shenqing", "eye_color_after", "失明")])
    await store.append_assertions(
        BOOK,
        20,
        ChapterExtraction(foreshadows=[ForeshadowPlantCandidate(content="后文才埋的引线")]),
        ExtractionSource(
            chapter_id="f20", content_hash="f20", prompt_version="v1", model="test-model"
        ),
    )
    await store.save_arc_summary(BOOK, arc_no=2, from_chapter=15, to_chapter=24, content="跨越后文的弧")
    await store.save_chapter_summaries(
        BOOK, "ch20", 20, [SceneSummary(scene_no=1, content="第 20 章的场景")]
    )

    compiled = await _compile(store, 12)
    assert "失明" not in compiled.block
    assert "后文才埋的引线" not in compiled.block
    assert "跨越后文的弧" not in compiled.block
    assert "第 20 章的场景" not in compiled.block
    # 已知的事实照常可见（区间相交语义）
    assert "char:shenqing · eye_color = 墨绿" in compiled.block


async def test_arc_reaching_past_as_of_is_not_injected() -> None:
    store = InMemoryCanonStore()
    await store.save_arc_summary(BOOK, arc_no=1, from_chapter=1, to_chapter=10, content="前十章的弧")

    compiled = await _compile(store, 5)
    assert "前十章的弧" not in compiled.block

    later = await _compile(store, 10)
    assert "主线进度（自第 1 章的弧）：前十章的弧" in later.block


# ---------- 退出条件：预算与书长无关 ----------


async def test_injection_never_exceeds_the_budget() -> None:
    """400 条断言 + 300 条场景摘要：块仍必须夹在 4000 token 内并留下裁剪账。"""
    store = InMemoryCanonStore()
    long_value = "墨绿色的瞳仁里映着灯，灯下是一枚缺了角的虎符。" * 4
    for chapter in range(1, 21):
        await _seed(
            store,
            chapter,
            [_assertion(f"char:e{chapter}", f"trait_{chapter}_{n}", long_value) for n in range(20)],
        )
    for chapter in range(1, 21):
        await store.save_chapter_summaries(
            BOOK,
            f"ch{chapter}",
            chapter,
            [SceneSummary(scene_no=n, content=long_value) for n in range(1, 6)],
            digest=long_value,
        )

    compiled = await _compile(store, 20)
    assert compiled.tokens <= Budgets().total
    assert compiled.counts["dropped"] > 0
    assert approx_tokens(compiled.block) == compiled.tokens


async def test_empty_block_fits_small_budgets() -> None:
    store = InMemoryCanonStore()
    await _seed(store, 1, [_assertion("char:shenqing", "eye_color", "墨绿")])

    compiled = await _compile(store, 1, budgets=Budgets(tier1=1, tier2=1))
    assert compiled.tokens <= Budgets(tier1=1, tier2=1).total
    assert compiled.counts["tier1"] == 1  # 抽到了，但注入不下——记账要如实分开
    assert "[canon#1]" not in compiled.block


# ---------- Tier-2：原文尾段最后才被动 ----------


async def test_previous_tail_survives_when_summaries_overrun() -> None:
    store = InMemoryCanonStore()
    long_value = "夜色压得很低，风里裹着一点铁锈味。" * 30
    for chapter in (18, 19, 20):
        await store.save_chapter_summaries(
            BOOK,
            f"ch{chapter}",
            chapter,
            [SceneSummary(scene_no=n, content=long_value) for n in range(1, 6)],
        )
    tail = "天亮之前还有三个时辰，够他把最后一步棋走完。"

    compiled = await _compile(store, 20, chapters=_chapters(20, tail=tail))
    assert tail in compiled.block
    assert compiled.counts["tier2"] > 0
    assert compiled.tokens <= Budgets().total


async def test_recent_chapter_window_only() -> None:
    store = InMemoryCanonStore()
    for chapter in (1, 2, 17, 18, 19, 20):
        await store.save_chapter_summaries(
            BOOK, f"ch{chapter}", chapter, [SceneSummary(scene_no=1, content=f"第{chapter}章场景")]
        )

    compiled = await _compile(store, 20, recent_chapters=3)
    assert "第 20 章" in compiled.block and "第 18 章" in compiled.block
    assert "第17章场景" not in compiled.block
    assert "第1章场景" not in compiled.block


async def test_chapter_digest_only_fills_in_for_sceneless_chapter() -> None:
    """同章有场景摘要时章级摘要不再重复注入；缺场景拆解时章级顶上。"""
    store = InMemoryCanonStore()
    await store.save_chapter_summaries(
        BOOK, "ch9", 9, [SceneSummary(scene_no=1, content="第九章场景一")], digest="第九章全章"
    )
    await store.save_chapter_summaries(BOOK, "ch10", 10, [], digest="第十章全章")

    compiled = await _compile(store, 10)
    assert "第九章场景一" in compiled.block
    assert "第九章全章" not in compiled.block
    assert "第十章全章" in compiled.block


async def test_in_session_digests_fill_tier2_before_archive() -> None:
    """摘要与正典同样迟于归档才落库：本轮 digests 不顶上，连续写作时 Tier-2 恒空。"""
    store = InMemoryCanonStore()
    pending = [
        SummaryRecord(id="", level="scene", chapter_no=2, scene_no=1, content="第二章场景一"),
        SummaryRecord(id="", level="scene", chapter_no=2, scene_no=2, content="第二章场景二"),
        SummaryRecord(id="", level="chapter", chapter_no=2, scene_no=0, content="第二章整章"),
    ]

    compiled = await _compile(store, 2, digests=pending)
    assert "第二章场景一" in compiled.block and "第二章场景二" in compiled.block
    assert "第二章整章" not in compiled.block
    assert compiled.counts["tier2"] == 2


async def test_current_round_digest_beats_the_stored_one() -> None:
    store = InMemoryCanonStore()
    await store.save_chapter_summaries(
        BOOK, "ch3", 3, [SceneSummary(scene_no=1, content="旧版第三章场景")]
    )
    fresh = SummaryRecord(id="", level="scene", chapter_no=3, scene_no=1, content="重写后的第三章场景")

    compiled = await _compile(store, 3, digests=[fresh])
    assert "重写后的第三章场景" in compiled.block
    assert "旧版第三章场景" not in compiled.block


# ---------- overlay：本轮已抽未入库的事实 ----------


def _pending(subject: str, predicate: str, value: str, *, chapter: int) -> CanonAssertion:
    return CanonAssertion(
        id="",
        book_id=BOOK,
        kind="character",
        subject_key=subject,
        predicate=predicate,
        object_text=value,
        restatement="",
        authority="model",
        established_chapter=chapter,
        valid_from_chapter=chapter,
        valid_until_chapter=None,
        status="confirmed",
    )


async def test_overlay_fills_the_gap_left_by_deferred_writes() -> None:
    store = InMemoryCanonStore()
    compiled = await _compile(
        store,
        2,
        overlay=[_pending("char:shenqing", "eye_color", "墨绿", chapter=1)],
    )
    assert "[canon#1] char:shenqing · eye_color = 墨绿" in compiled.block
    # 未入库的候选没有库主键，用 pending: 前缀保住「可回指」这条契约
    assert compiled.refs[0].source_id == "pending:char:shenqing:eye_color"


async def test_overlay_uses_the_same_as_of_and_dedupe_rules() -> None:
    store = InMemoryCanonStore()
    await _seed(store, 1, [_assertion("char:shenqing", "eye_color", "墨绿")])
    overlay = [
        _pending("char:shenqing", "eye_color", "琥珀", chapter=1),  # 与库内同键：不重复编号
        _pending("char:linwan", "secret", "她读过禁卷", chapter=30),  # as-of 之后：丢弃
    ]

    compiled = await _compile(store, 2, overlay=overlay)
    assert compiled.counts["tier1"] == 1
    assert "琥珀" not in compiled.block and "她读过禁卷" not in compiled.block
    assert "墨绿" in compiled.block


async def test_pending_todo_is_not_injected() -> None:
    """机制③的缺口登记（status=todo）不参与注入：读侧只认 confirmed。"""
    gap = replace(_pending("rule:menngui", "undefined", "正文提到门规但没有条目", chapter=1), status="todo")
    compiled = await _compile(InMemoryCanonStore(), 2, overlay=[gap])
    assert compiled.counts["tier1"] == 0


# ---------- 实体清单 / 文风契约 ----------


async def test_entities_narrow_tier1() -> None:
    store = InMemoryCanonStore()
    await _seed(
        store,
        1,
        [_assertion("char:shenqing", "eye_color", "墨绿"), _assertion("place:yunjian", "ruler", "柳氏")],
    )

    compiled = await _compile(store, 1, entities=["char:shenqing"])
    assert compiled.counts["tier1"] == 1
    assert "place:yunjian" not in compiled.block


async def test_style_contract_line_is_present() -> None:
    compiled = await _compile(
        InMemoryCanonStore(), 1, style=StyleContract(genre="玄幻", pov="第一人称", tense="现在时")
    )
    assert "文风契约：玄幻｜第一人称｜现在时。" in compiled.block
    assert "世界观与主线：" in compiled.block


async def test_stored_style_profile_beats_derived_contract() -> None:
    """作者手改的契约盖在世界观派生值之上——词表只能由人手收紧（§5.5）。"""
    store = InMemoryCanonStore()
    store.put_style_profile(
        BOOK,
        StyleProfileRecord(
            person="第三人称限知",
            forbidden_words=("禁术", "血祭"),
            chapter_words_min=2200,
            chapter_words_max=3200,
        ),
    )

    compiled = await _compile(
        store, 1, style=StyleContract(genre="玄幻", pov="第一人称", tense="现在时")
    )
    assert compiled.style is not None
    assert compiled.style.pov == "第三人称限知"
    assert compiled.style.forbidden_words == ("禁术", "血祭")
    assert "文风契约：玄幻｜第三人称限知｜现在时" in compiled.block
    assert "禁用词：禁术、血祭" in compiled.block
    assert "单章 2200-3200 字" in compiled.block


async def test_partial_profile_keeps_untouched_derived_fields() -> None:
    """只定字数带时人称照旧：未表态（None）不等于表态为空。"""
    store = InMemoryCanonStore()
    store.put_style_profile(BOOK, StyleProfileRecord(chapter_words_min=1000, chapter_words_max=1500))

    compiled = await _compile(
        store, 1, style=StyleContract(genre="玄幻", pov="第一人称", tense="现在时")
    )
    assert compiled.style is not None
    assert compiled.style.pov == "第一人称"
    assert compiled.style.chapter_words_max == 1500
    assert "禁用词" not in compiled.block


async def test_long_word_list_does_not_eat_the_contract_line() -> None:
    """词表只列前若干项：整行落不进 Tier-0 时丢的是**整条文风契约**，不是少看几个词。"""
    store = InMemoryCanonStore()
    store.put_style_profile(
        BOOK, StyleProfileRecord(forbidden_words=tuple(f"词{i}" for i in range(30)))
    )

    compiled = await _compile(store, 1)
    line = next(row for row in compiled.block.splitlines() if "文风契约" in row)
    assert "词11" in line
    assert "词12" not in line
    assert "共 30 项" in line

    # 截断是为了让这一行留在块里：预算刚好等于「世界观行 + 截断后的契约行」时它仍在，
    # 而全量列出 30 个词的那一行比这份预算更贵，会被 _fit 整行裁掉
    head = approx_tokens(f"世界观与主线：{_IDEA.summary}")
    full = line.replace(
        "词0、词1、词2、词3、词4、词5、词6、词7、词8、词9、词10、词11（共 30 项）",
        "、".join(f"词{i}" for i in range(30)),
    )
    assert approx_tokens(full) > head + approx_tokens(line)

    # 11 = _with_framing 给段落标题留的 10 个 token + 刚好装下这一行的 1 个
    kept = await _compile(store, 1, budgets=Budgets(tier0=head + approx_tokens(line) + 11))
    assert "文风契约" in kept.block


# ---------- 对话侧装配：task_chapter（§10.3「同一份上下文」） ----------


def _reference(index: int = 3, *, content: str = "她终于承认，那半枚虎符是她自己砸的。") -> ChapterSnapshot:
    return ChapterSnapshot(
        chapter_id=str(20 + index), index=index, title="裂隙", content=content
    )


async def test_task_chapter_writes_the_reference_chapter_not_an_outline() -> None:
    """对话没有「下一章大纲」，任务区要说清谈的是哪一章；尾段也跟着这一章走。"""
    store = InMemoryCanonStore()
    compiled = await _compile(store, 3, chapters=(), task_chapter=_reference(3))

    assert "当前参照章：《裂隙》（第 3 章，已定稿）" in compiled.block
    assert "本章大纲" not in compiled.block
    # 参照章就是当前章，标成「上一章」会让模型把正在讨论的章当过去式谈
    assert "当前参照章结尾原文：" in compiled.block
    assert "上一章结尾原文" not in compiled.block


async def test_task_chapter_tail_beats_the_draft_list() -> None:
    """两个来源都给了的时候以参照章为准：对话传 chapters 是调用方弄错了对象。"""
    store = InMemoryCanonStore()
    compiled = await _compile(
        store,
        3,
        chapters=_chapters(3, tail="这一段属于生成侧的草稿。"),
        task_chapter=_reference(3, content="这一段属于参照章。"),
    )
    assert "这一段属于参照章。" in compiled.block
    assert "生成侧的草稿" not in compiled.block


async def test_task_chapter_later_than_as_of_is_rejected() -> None:
    """as-of 是唯一支点：晚于它的参照章会把未定稿正文从近因漏进来，宁可炸也不过滤。"""
    store = InMemoryCanonStore()
    with pytest.raises(ValueError, match="漏后文"):
        await _compile(store, 3, chapters=(), task_chapter=_reference(5))


async def test_task_chapter_keeps_the_same_as_of_filters() -> None:
    """参照章不改写 Tier-1 的口径：as-of 之后成立的事实照样看不见。"""
    store = InMemoryCanonStore()
    await _seed(store, 2, [_assertion("char:linwan", "eye_color", "墨绿")])
    await _seed(store, 6, [_assertion("char:linwan", "sword", "青霜")])

    compiled = await _compile(store, 3, chapters=(), task_chapter=_reference(3))
    assert "墨绿" in compiled.block
    assert "青霜" not in compiled.block
    assert "截至第 3 章" in compiled.block
