"""一致性黄金集门禁（PRD §12.1）：阈值、覆盖台账与语料自洽。

阈值直接抄 PRD 的原话，不放宽：闸门召回 ≥ 90%（blocker 类 100%）、误报 ≤ 15%；
抽取新事实召回 ≥ 85%、误采 ≤ 10%；别名归一准确率 ≥ 95%。换模型 / 改提示词 / 改阈值
都必须跑这一套（CI 里是一条独立 step，见 ``.github/workflows/ci.yml``）。

三类测试各有用途，别混着看：

- **阈值测试**：跑 :func:`run_golden_set`，断言六个指标。失败时要看
  :meth:`GoldenReport.diagnostics` 的逐条漏报与误报，聚合值本身不指位置；
- **覆盖台账测试**：证明语料真的把 C1–C6 都埋了（每类 ≥ 8 处），并且四类「只有语义
  裁判能判」的编码在规则侧**应当零命中**——哪天补了确定性规则，这个测试会红，
  那是在提醒重算基线，不是 bug；
- **语料自洽测试**：标注必须逐字指在正文里、反例不能同时是标注、字数带必须自洽。
  这三条任何一条塌了，上面两组数字就全在自欺——「召回 100%」也可能只是标注漏写了。
"""

from __future__ import annotations

from typing import get_args

from po_agent_novel.gates import GateRules, visible_chars
from po_agent_novel.prompts import scene_card_text
from po_agent_novel.schemas import FindingCode

from golden.book import (
    BIBLE,
    CHAPTERS,
    CONFLICT_CLASSES,
    EXTRACTION_FAILED_CHAPTERS,
    HARD_HIGH,
    HARD_LOW,
    JUDGE_ONLY_CODES,
    OUTLINE,
    PLAN_CASES,
    RULES,
    SOFT_HIGH,
    SOFT_LOW,
)
from golden.score import GoldenReport, run_golden_set

# ---------- PRD §12.1 的验收线 ----------

GATE_RECALL_FLOOR = 0.90
BLOCKER_RECALL_FLOOR = 1.0
FALSE_POSITIVE_CEILING = 0.15
NEW_FACT_RECALL_FLOOR = 0.85
FALSE_CAPTURE_CEILING = 0.10
ALIAS_ACCURACY_FLOOR = 0.95
CLASS_MARK_FLOOR = 8

MARKED_CODES = frozenset(get_args(FindingCode))

_REPORT: GoldenReport | None = None


async def report() -> GoldenReport:
    """整份黄金集只跑一次：六个阈值测的是同一次运行的不同侧面。

    各测试拿到的是同一份纯数据结果，跨 pytest-asyncio 的函数级事件循环复用是安全的
    （打分器里没有任何与循环绑定的对象）。
    """
    global _REPORT
    if _REPORT is None:
        _REPORT = await run_golden_set()
    return _REPORT


def _fail(summary: str, loaded: GoldenReport) -> None:
    raise AssertionError(f"{summary}\n\n{loaded.diagnostics()}")


# ---------- 阈值 ----------


async def test_gate_recall_meets_prd_floor() -> None:
    loaded = await report()
    assert loaded.recall >= GATE_RECALL_FLOOR, _fail(
        f"闸门召回 {loaded.recall:.3f} < {GATE_RECALL_FLOOR}", loaded
    )


async def test_blocker_recall_is_exact() -> None:
    loaded = await report()
    assert loaded.blocker_recall == BLOCKER_RECALL_FLOOR, _fail(
        f"blocker 召回 {loaded.blocker_recall:.3f} ≠ 1.0", loaded
    )


async def test_false_positive_rate_within_ceiling() -> None:
    loaded = await report()
    assert loaded.fp_rate <= FALSE_POSITIVE_CEILING, _fail(
        f"误报率 {loaded.fp_rate:.3f} > {FALSE_POSITIVE_CEILING}", loaded
    )


async def test_decoys_are_never_reported() -> None:
    """反例不许有命中：比聚合误报率更严。

    聚合值会把「一处反例误报」摊进几十条命中里显得无害，而反例的作用恰恰是钉住
    「规则没有多做判」——引号内的死者转述、可变谓词的正常改写、包含关系的取值。
    """
    loaded = await report()
    assert not loaded.prose.decoy_hits, _fail(
        f"正文反例被报出 {len(loaded.prose.decoy_hits)} 条", loaded
    )


async def test_severity_labels_match_the_rules() -> None:
    """严重度也是判据：blocker/major/minor 走三条不同的处置分支（§9.3），报错档等于改放行。"""
    loaded = await report()
    assert not loaded.prose.severity_errors and not loaded.plan.severity_errors, _fail(
        "严重度标注与规则实得分档不符", loaded
    )


async def test_new_fact_recall_meets_prd_floor() -> None:
    loaded = await report()
    assert loaded.extraction.recall >= NEW_FACT_RECALL_FLOOR, _fail(
        f"新事实召回 {loaded.extraction.recall:.3f} < {NEW_FACT_RECALL_FLOOR}", loaded
    )


async def test_false_capture_rate_within_ceiling() -> None:
    loaded = await report()
    assert loaded.extraction.false_capture_rate <= FALSE_CAPTURE_CEILING, _fail(
        f"误采 {loaded.extraction.false_capture_rate:.3f} > {FALSE_CAPTURE_CEILING}", loaded
    )


async def test_hallucinated_evidence_is_blocked_entirely() -> None:
    """逐字证据闸门是「误采」唯一的确定性测法：证据不在正文里的候选必须一条不留。"""
    loaded = await report()
    extraction = loaded.extraction
    assert extraction.hallucinated > 0, _fail(
        "语料里没有幻觉候选，误采指标没有判据", loaded
    )
    assert extraction.block_rate == 1.0, _fail(
        f"幻觉候选漏放行：拦住 {extraction.blocked}/{extraction.hallucinated}", loaded
    )


async def test_alias_normalization_accuracy() -> None:
    loaded = await report()
    assert loaded.aliases.accuracy >= ALIAS_ACCURACY_FLOOR, _fail(
        f"别名归一准确率 {loaded.aliases.accuracy:.3f} < {ALIAS_ACCURACY_FLOOR}", loaded
    )
    assert not loaded.aliases.mismatched_chapters, _fail(
        "库的别名处置与「首次认定优先」不符", loaded
    )


# ---------- 覆盖台账 ----------


async def test_every_conflict_class_is_marked() -> None:
    """每类冲突都埋够 8 处（PRD §12.1「各埋 8–15 处」的下限）。

    只钉下限：C2 与 C6 的实际标注数超出 15（生死与文风是规则面最容易叠的地方），
    多标不是缺陷，少标才是——少标会让某类冲突的召回率失去意义。
    """
    loaded = await report()
    counts = loaded.class_counts()
    assert set(counts) == set(CONFLICT_CLASSES)
    thin = {cls: n for cls, n in counts.items() if n < CLASS_MARK_FLOOR}
    assert not thin, _fail(f"以下冲突类别标注不足 {CLASS_MARK_FLOOR} 处：{thin}", loaded)


async def test_judge_only_codes_are_invisible_to_the_rules() -> None:
    """C4/C5/knows/动机四类只有语义裁判能判：规则侧对它们零命中。

    这不是「规则做得差」的免责条款，而是台账：一旦有人给这四类补了确定性规则，
    本测试转红并要求重算召回基线（原先算作漏报的标注会变成命中，基线虚高）。
    """
    loaded = await report()
    assert not loaded.prose.judge_blind_spots, _fail(
        "规则侧命中了 judge-only 标注，基线需要重算", loaded
    )
    assert not loaded.plan.judge_blind_spots, _fail(
        "计划闸门命中了 judge-only 标注，基线需要重算", loaded
    )


async def test_judge_only_classes_have_labels() -> None:
    """四类 judge 标注每类都得有语料，否则上一条测试是空跑。"""
    loaded = await report()
    assert set(loaded.judge_labels) == set(JUDGE_ONLY_CODES), (
        f"judge 标注覆盖 {sorted(loaded.judge_labels)} ≠ {sorted(JUDGE_ONLY_CODES)}"
    )
    assert all(count >= CLASS_MARK_FLOOR for count in loaded.judge_labels.values()), (
        f"judge 标注不足：{loaded.judge_labels}"
    )


async def test_plan_side_pays_off_a_real_foreshadow_number() -> None:
    """payoff 反例必须真的拿到过未收编号：没有编号时「不报」不等于「不越界」。"""
    loaded = await report()
    decoys = sum(1 for case in PLAN_CASES if case.payoff_decoy)
    assert decoys >= 1
    assert loaded.payoff_decoys_injected == decoys, (
        f"{decoys} 张反例卡里只有 {loaded.payoff_decoys_injected} 张注入了真实编号"
    )


# ---------- 语料自洽 ----------


def test_marks_point_at_verbatim_prose() -> None:
    """每条标注的片段必须逐字在它那一章的正文里（整章级标注除外）。

    标注与正文共用同一份字面量本来就该成立，这条是防 ``at`` 下标写错——下标错了，
    「召回」就变成在比对一段根本不存在的文本。
    """
    for case in CHAPTERS:
        for mark in case.marks:
            fragment = case.locate(mark)
            if mark.at < 0:
                assert fragment == "", f"第 {case.no} 章整章级标注却给了下标 {mark.at}"
                continue
            assert fragment in case.text, f"第 {case.no} 章标注片段不在正文里：{fragment!r}"
            assert fragment not in {case.parts[i] for i in case.decoys}, (
                f"第 {case.no} 章同一片段既是标注又是反例：{fragment!r}"
            )


def test_plan_needles_appear_in_the_rendered_card() -> None:
    """needle 指在 ``scene_card_text`` 的渲染里：模板改语义时这条会红，而不是静默漏报。"""
    by_no = {case.no: case for case in PLAN_CASES}
    for case in CHAPTERS:
        plan = by_no[case.no]
        rendered = scene_card_text(plan.card, OUTLINE[case.no - 1])
        for mark in plan.marks:
            needle = plan.locate(mark)
            assert needle in rendered, (
                f"第 {case.no} 章计划标注 needle {needle!r} 不在卡文本里"
            )


def test_decoy_indices_are_in_range() -> None:
    for case in CHAPTERS:
        for index in case.decoys:
            assert 0 <= index < len(case.parts), f"第 {case.no} 章反例下标 {index} 越界"


def test_word_band_is_self_computing() -> None:
    """字数带必须由 ``_pad`` 自己保证：只有标了 ``length_out_of_band`` 的章才许越带。

    否则长度规则会污染别的标注——一章因为语料写短了被判长度违规，那条 Finding 在
    误报列表里，而它其实是「语料没垫够字」，不是闸门的问题。
    """
    for case in CHAPTERS:
        words = visible_chars(case.text)
        marked = any(mark.code == "length_out_of_band" for mark in case.marks)
        if marked:
            assert not SOFT_LOW <= words <= SOFT_HIGH, (
                f"第 {case.no} 章标了越带，实际 {words} 字落在软带 {SOFT_LOW}-{SOFT_HIGH} 内"
            )
            if words:
                beyond_hard = not HARD_LOW <= words <= HARD_HIGH
                expected = "blocker" if words == 0 else ("major" if beyond_hard else "minor")
                severity = next(
                    mark.severity
                    for mark in case.marks
                    if mark.code == "length_out_of_band"
                )
                assert severity == expected, f"第 {case.no} 章长度标注严重度应为 {expected}"
            continue
        assert SOFT_LOW <= words <= SOFT_HIGH, (
            f"第 {case.no} 章 {words} 字越出软带 {SOFT_LOW}-{SOFT_HIGH}，需要 _pad 补字"
        )


def test_mark_codes_are_declared() -> None:
    """标注里的编码必须是 :data:`FindingCode` 的成员：拼错的编码永远配不上 Finding。"""
    for case in CHAPTERS:
        for mark in case.marks:
            assert mark.code in MARKED_CODES, f"第 {case.no} 章未知编码 {mark.code}"
    for plan in PLAN_CASES:
        for mark in plan.marks:
            assert mark.code in MARKED_CODES, f"计划第 {plan.no} 章未知编码 {mark.code}"


def test_chapter_and_plan_sides_are_one_to_one() -> None:
    """两侧都是同样的 20 章：as-of 支点错开一位的话，两道闸门的召回根本不可比。"""
    assert len(CHAPTERS) == 20
    assert [case.no for case in CHAPTERS] == list(range(1, 21))
    assert [plan.no for plan in sorted(PLAN_CASES, key=lambda p: p.no)] == list(range(1, 21))
    assert len({case.title for case in CHAPTERS}) == 20
    assert EXTRACTION_FAILED_CHAPTERS, "语料里要有抽取失败的章，否则候选侧规则的跳过分支没被测到"


def test_rules_match_the_corpus_assumptions() -> None:
    """语料的严重度标注是按这组参数写死的：改参数必须回来核对带宽与视角阈值。

    ``target_words=160`` 刻意偏离生产缺省（1200）：黄金集要的是「同一套判据」而不是
    「像真书」，每章两千字会把语料撑成无法逐字标注的篇幅。
    """
    assert RULES.target_words != GateRules().target_words
    assert RULES.forbidden_words == tuple(BIBLE.forbidden)
    assert SOFT_LOW == int(RULES.target_words * RULES.min_ratio)
    assert SOFT_HIGH == int(RULES.target_words * RULES.max_ratio)
    assert HARD_LOW == int(RULES.target_words * RULES.hard_min_ratio)
    assert HARD_HIGH == int(RULES.target_words * RULES.hard_max_ratio)


def test_every_rule_mark_is_sane_about_detector() -> None:
    """``detector`` 只能是 rule/judge，且 judge 标注不许要求严重度（裁判不产分档契约）。"""
    for case in CHAPTERS:
        for mark in case.marks:
            assert mark.detector in {"rule", "judge"}, f"第 {case.no} 章 {mark.detector}"
            if mark.detector == "judge":
                assert mark.code in JUDGE_ONLY_CODES, (
                    f"第 {case.no} 章把规则可判的 {mark.code} 标成了 judge"
                )
            else:
                assert mark.code not in JUDGE_ONLY_CODES, (
                    f"第 {case.no} 章把只有裁判能判的 {mark.code} 标成了规则"
                )
    for plan in PLAN_CASES:
        assert all(mark.detector == "rule" for mark in plan.marks), (
            f"计划第 {plan.no} 章有 judge 标注：计划闸门是纯规则的"
        )
