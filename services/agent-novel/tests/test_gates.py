"""确定性规则闸门（gates.py）的单测。

覆盖三件事，缺一件就等于闸门形同虚设：
- 每条规则的「命中 / 不命中」两侧都跑一遍——只测命中会放过那种把每次正常改写都
  报成 bug 的规则（生死翻转、可变谓词、引号内人称都是这类）；
- 证据与 span 的逐字关系（机制②）：规则引擎的证据必须能原样回到正文；
- 验收口的丢弃条件（编码未知 / 证据造假 / 该引事实却没引），并且丢弃要计数，
  不许静默。

计划闸门（``run_plan_rules``）另算一组：被检对象是场景卡而不是正文，因此坐标系换成
``scene_card_text`` 的渲染，判据换成 as-of 快照（含圣经行）。
"""

from __future__ import annotations

from po_agent_novel.context import CanonRef, StyleContract
from po_agent_novel.gates import (
    GateInput,
    GateRules,
    PlanInput,
    check_alive_conflicts,
    check_alias_drift,
    check_attribute_conflict,
    check_citations,
    check_forbidden_words,
    check_length,
    check_plan_deaths,
    check_plan_entities,
    check_plan_length,
    check_plan_payoffs,
    check_pov,
    evidence_matches_span,
    evidence_verbatim,
    mask_quotes,
    run_plan_rules,
    run_rules,
    sentence_span,
    validate_findings,
    visible_chars,
)
from po_agent_novel.prompts import scene_card_text
from po_agent_novel.schemas import (
    AliasCandidate,
    AssertionCandidate,
    ChapterExtraction,
    Finding,
    PlannedScene,
    SceneCard,
    StateChangeCandidate,
)
from po_agent_novel.store import CanonAssertion


def _assertion(
    assertion_id: str,
    subject_key: str,
    predicate: str,
    object_text: str,
    *,
    status: str = "confirmed",
    chapter: int = 1,
) -> CanonAssertion:
    return CanonAssertion(
        id=assertion_id,
        book_id="book-1",
        kind="character",
        subject_key=subject_key,
        predicate=predicate,
        object_text=object_text,
        restatement=f"{subject_key} 的 {predicate} 为 {object_text}",
        authority="model",
        established_chapter=chapter,
        valid_from_chapter=chapter,
        valid_until_chapter=None,
        status=status,
    )


def _ref(number: int, source_id: str, kind: str = "canon") -> CanonRef:
    return CanonRef(number=number, kind=kind, source_id=source_id, text=f"{kind}#{number}")


def _candidate(
    subject_key: str, predicate: str, object_text: str, evidence: str
) -> AssertionCandidate:
    return AssertionCandidate(
        kind="character",
        subjectKey=subject_key,
        predicate=predicate,
        objectText=object_text,
        restatement=f"{predicate}={object_text}",
        evidenceQuote=evidence,
        status="confirmed",
    )


def _alias(entity_key: str, alias_text: str) -> AliasCandidate:
    return AliasCandidate(entityKey=entity_key, aliasText=alias_text)


# ---------- 文本口径：字数、句区间、引号掩码 ----------


def test_visible_chars_ignores_whitespace() -> None:
    assert visible_chars("夜色压得很低，\n风里有铁锈味。\n") == 14


def test_sentence_span_covers_the_whole_sentence() -> None:
    text = "前两句话。\n他冷笑了一声，转身就走。后面还有。"
    start, end = sentence_span(text, text.index("冷笑"))
    assert text[start:end] == "他冷笑了一声，转身就走。"


def test_sentence_span_is_capped_at_evidence_limit() -> None:
    """超长单句必须截到 512：Java 侧 clip 之后证据就不等于 span 了。"""
    start, end = sentence_span("啊" * 900, 10)
    assert end - start == 512


def test_mask_quotes_keeps_length_and_blanks_interiors() -> None:
    text = "「你在说什么？」他问。"
    masked = mask_quotes(text)
    assert len(masked) == len(text)
    assert "你" not in masked and "他问" in masked


def test_mask_quotes_handles_nested_quotes() -> None:
    text = "他低声道：「她说『我先走了』，然后就没了声音。」我站在原地。"
    masked = mask_quotes(text)
    assert len(masked) == len(text)
    # 内层引号不提前结束掩码；引号外的叙述层文字原样保留
    assert "我" not in masked[: len(masked) - 6]
    assert masked.endswith("我站在原地。")


# ---------- 逐字证据 ----------


def test_evidence_verbatim_only_tolerates_whitespace() -> None:
    assert evidence_verbatim("夜色压\n得很低", "夜色压得很低，风里裹着铁锈味。")
    assert not evidence_verbatim("夜色压得很高", "夜色压得很低，风里裹着铁锈味。")
    assert not evidence_verbatim("  ", "正文")


def test_evidence_matches_span_requires_equal_normalized_text() -> None:
    text = "他数到第七块砖的时候停了下来。"
    assert evidence_matches_span("他数到第七块砖", text, 0, 7)
    # 真原文配错 span 同样是造假
    assert not evidence_matches_span("停了下来", text, 0, 7)
    assert not evidence_matches_span("他数到第七块砖", text, 5, 3)
    assert not evidence_matches_span("", text, 0, 7)


# ---------- 字数带 ----------


def test_length_in_band_is_silent() -> None:
    gate_in = GateInput(text="字" * 100, chapter_no=1)
    assert check_length(gate_in, GateRules(target_words=120)) == ([], [])


def test_length_mild_drift_is_minor_extreme_is_major() -> None:
    rules = GateRules(target_words=100)  # 允许带 60-160，硬界 35-220
    mild, _ = check_length(GateInput(text="字" * 40, chapter_no=1), rules)
    assert [f.severity for f in mild] == ["minor"]
    extreme, _ = check_length(GateInput(text="字" * 20, chapter_no=1), rules)
    assert [f.severity for f in extreme] == ["major"]
    assert extreme[0].textStart is None and not extreme[0].evidenceQuote


def test_empty_chapter_is_blocker() -> None:
    """空章没有可修补的对象：blocker 走「修补两轮不过即冻结」，正是转人工的路径。"""
    findings, _ = check_length(GateInput(text="", chapter_no=1), GateRules(target_words=100))
    assert [f.severity for f in findings] == ["blocker"]


# ---------- 禁用词 ----------


def test_forbidden_word_hits_inside_dialogue() -> None:
    text = "「那是禁术。」她低声说。"
    findings, _ = check_forbidden_words(
        GateInput(text=text, chapter_no=2), GateRules(forbidden_words=("禁术",))
    )
    assert len(findings) == 1
    assert (findings[0].code, findings[0].severity) == ("forbidden_word", "blocker")
    assert text[findings[0].textStart : findings[0].textEnd] == findings[0].evidenceQuote


def test_absent_forbidden_word_is_silent() -> None:
    findings, _ = check_forbidden_words(
        GateInput(text="夜色压得很低。", chapter_no=1), GateRules(forbidden_words=("禁术",))
    )
    assert findings == []


# ---------- 叙述人称 ----------


def _third_person() -> StyleContract:
    return StyleContract(genre="武侠", pov="第三人称限知")


def test_pov_ignores_first_person_inside_dialogue() -> None:
    gate_in = GateInput(text="「我先走了。」他没有回头。", chapter_no=1, style=_third_person())
    assert check_pov(gate_in, GateRules()) == ([], [])


def test_pov_single_hit_is_minor_and_three_hits_is_major() -> None:
    one, _ = check_pov(GateInput(text="我跟在他身后。", chapter_no=1, style=_third_person()), GateRules())
    assert [f.severity for f in one] == ["minor"]
    three, _ = check_pov(
        GateInput(text="我跟着他。我停下。我听见了。", chapter_no=1, style=_third_person()),
        GateRules(),
    )
    assert [f.severity for f in three] == ["major"] * 3
    assert all(f.code == "style_drift" for f in three)


def test_pov_needs_a_contract_and_only_checks_third_person() -> None:
    """没有文风契约、或契约本就是第一人称时，规则无从判起（不猜）。"""
    ego = GateInput(text="我跟着他。", chapter_no=1, style=StyleContract(genre="都市", pov="第一人称"))
    assert check_pov(ego, GateRules())[0] == []
    assert check_pov(GateInput(text="我跟着他。", chapter_no=1), GateRules())[0] == []


# ---------- C1 属性冲突 ----------


def test_attribute_conflict_blocks_with_injected_ref() -> None:
    """新增事实与既有断言同键不同值：blocker，且 canonRefs 用的是 [canon#N] 编号。"""
    text = "她的眼睛是红色的，像沾了血。"
    gate_in = GateInput(
        text=text,
        chapter_no=3,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "eye_color", "红", "她的眼睛是红色的")]
        ),
        snapshot=[_assertion("a1", "char:her", "eye_color", "黑", chapter=2)],
        refs=[_ref(7, "a1")],
    )
    findings, skipped = check_attribute_conflict(gate_in, GateRules())
    assert skipped == []
    assert [(f.code, f.severity, f.canonRefs) for f in findings] == [
        ("attribute_conflict", "blocker", [7])
    ]
    assert text[findings[0].textStart : findings[0].textEnd] == findings[0].evidenceQuote


def test_attribute_conflict_locates_evidence_across_newlines() -> None:
    """证据与正文只差空白时也要能定位：抽取侧按归一化空白放行，闸门不能按原文找不到就丢。"""
    text = "她的\n眼睛是红色的。"
    gate_in = GateInput(
        text=text,
        chapter_no=3,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "eye_color", "红", "她的眼睛是红色的")]
        ),
        snapshot=[_assertion("a1", "char:her", "eye_color", "黑")],
        refs=[_ref(1, "a1")],
    )
    findings, skipped = check_attribute_conflict(gate_in, GateRules())
    assert skipped == [] and len(findings) == 1
    kept, dropped = validate_findings(findings, text)
    assert dropped == 0 and len(kept) == 1


def test_attribute_conflict_pending_overlay_resolves_by_composite_key() -> None:
    """本轮 overlay 的事实没有库主键，靠 pending: 复合键也能引出编号。"""
    gate_in = GateInput(
        text="她的眼睛是红色的。",
        chapter_no=2,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "eye_color", "红", "她的眼睛是红色的")]
        ),
        snapshot=[_assertion("", "char:her", "eye_color", "黑")],
        refs=[_ref(3, "pending:char:her:eye_color")],
    )
    findings, _ = check_attribute_conflict(gate_in, GateRules())
    assert [f.canonRefs for f in findings] == [[3]]


def test_attribute_conflict_skips_when_fact_not_injected() -> None:
    """引不出编号就不报，但必须计入 no_ref：静默丢弃等于没有闸门。"""
    gate_in = GateInput(
        text="她的眼睛是红色的。",
        chapter_no=3,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "eye_color", "红", "她的眼睛是红色的")]
        ),
        snapshot=[_assertion("a1", "char:her", "eye_color", "黑")],
        refs=[],
    )
    findings, skipped = check_attribute_conflict(gate_in, GateRules())
    assert findings == [] and skipped == ["no_ref"]


def test_attribute_conflict_skips_when_evidence_not_in_chapter() -> None:
    gate_in = GateInput(
        text="夜色压得很低。",
        chapter_no=3,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "eye_color", "红", "她的眼睛是红色的")]
        ),
        snapshot=[_assertion("a1", "char:her", "eye_color", "黑")],
        refs=[_ref(1, "a1")],
    )
    findings, skipped = check_attribute_conflict(gate_in, GateRules())
    assert findings == [] and skipped == ["no_quote"]


def test_attribute_conflict_tolerates_mutable_and_compatible_values() -> None:
    cases = [
        # 可变谓词：状态推进不是冲突
        ("location_key", "苏州", "黑"),
        ("age", "十七岁", "十六岁"),
        # 值互为包含：黑 vs 黑发 是同一条事实的不同写法
        ("eye_color", "黑发", "黑"),
    ]
    for predicate, new_value, old_value in cases:
        gate_in = GateInput(
            text="她的眼睛是红色的。",
            chapter_no=3,
            extraction=ChapterExtraction(
                assertions=[_candidate("char:her", predicate, new_value, "她的眼睛是红色的")]
            ),
            snapshot=[_assertion("a1", "char:her", predicate, old_value)],
            refs=[_ref(1, "a1")],
        )
        assert check_attribute_conflict(gate_in, GateRules())[0] == [], predicate


def test_attribute_conflict_ignores_todo_gap_candidates() -> None:
    """todo 是「未知即缺口」，登记缺口不是宣称事实，不许拿去撞既有断言。"""
    gap = _candidate("char:her", "eye_color", "红", "她的眼睛是红色的").model_copy(
        update={"status": "todo"}
    )
    gate_in = GateInput(
        text="她的眼睛是红色的。",
        chapter_no=3,
        extraction=ChapterExtraction(assertions=[gap]),
        snapshot=[_assertion("a1", "char:her", "eye_color", "黑")],
        refs=[_ref(1, "a1")],
    )
    assert check_attribute_conflict(gate_in, GateRules())[0] == []


def test_attribute_conflict_skipped_entirely_without_candidates() -> None:
    """抽取失败（extraction=None）时没有可比对的增量，规则整体让路。"""
    gate_in = GateInput(
        text="她的眼睛是红色的。",
        chapter_no=3,
        snapshot=[_assertion("a1", "char:her", "eye_color", "黑")],
        refs=[_ref(1, "a1")],
    )
    assert check_attribute_conflict(gate_in, GateRules()) == ([], [])


# ---------- C2 生死 ----------


def test_dead_character_speaking_is_blocker() -> None:
    text = "沈青道：「我早就死了。」"
    gate_in = GateInput(
        text=text,
        chapter_no=4,
        extraction=ChapterExtraction(aliases=[_alias("char:shenqing", "沈青")]),
        snapshot=[_assertion("a2", "char:shenqing", "is_alive", "false", chapter=3)],
        refs=[_ref(5, "a2")],
    )
    findings, skipped = check_alive_conflicts(gate_in, GateRules())
    assert skipped == []
    assert [(f.code, f.severity, f.canonRefs) for f in findings] == [
        ("death_speaks", "blocker", [5])
    ]
    assert findings[0].evidenceQuote.startswith("沈青道：")


def test_mentioning_a_dead_character_without_speech_is_fine() -> None:
    gate_in = GateInput(
        text="沈青的坟头已经长了草。",
        chapter_no=5,
        extraction=ChapterExtraction(aliases=[_alias("char:shenqing", "沈青")]),
        snapshot=[_assertion("a2", "char:shenqing", "is_alive", "false", chapter=3)],
        refs=[_ref(5, "a2")],
    )
    assert check_alive_conflicts(gate_in, GateRules()) == ([], [])


def test_dead_character_named_only_in_dialogue_is_not_speaking() -> None:
    """名字只出现在别人的话里是转述，掩码之后不该命中。"""
    gate_in = GateInput(
        text="「沈青说过，别碰那扇门。」她压低声音。",
        chapter_no=5,
        extraction=ChapterExtraction(aliases=[_alias("char:shenqing", "沈青")]),
        snapshot=[_assertion("a2", "char:shenqing", "is_alive", "false", chapter=3)],
        refs=[_ref(5, "a2")],
    )
    assert check_alive_conflicts(gate_in, GateRules()) == ([], [])


def test_dead_without_known_name_counts_as_skipped() -> None:
    """没有姓名就没法定位正文里的这个人：计入 no_name，不假装检查过。"""
    gate_in = GateInput(
        text="沈青说他回来了。",
        chapter_no=5,
        snapshot=[_assertion("a2", "char:shenqing", "is_alive", "false", chapter=3)],
        refs=[_ref(5, "a2")],
    )
    findings, skipped = check_alive_conflicts(gate_in, GateRules())
    assert findings == [] and skipped == ["no_name"]


def test_alive_to_dead_transition_is_not_reported() -> None:
    """死亡是正常剧情：只有 false→true（无交代复活）才报。"""
    gate_in = GateInput(
        text="她倒在血泊里，再没有起来。",
        chapter_no=6,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "is_alive", "false", "她倒在血泊里")]
        ),
        snapshot=[_assertion("a1", "char:her", "is_alive", "true")],
        refs=[_ref(1, "a1")],
    )
    assert check_alive_conflicts(gate_in, GateRules()) == ([], [])


def test_resurrection_lands_both_from_assertion_and_state_snapshot() -> None:
    gate_in = GateInput(
        text="沈青从雪地里站了起来。",
        chapter_no=6,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:shenqing", "is_alive", "true", "沈青从雪地里站了起来")],
            stateChanges=[StateChangeCandidate(charKey="char:shenqing", isAlive=True)],
        ),
        snapshot=[_assertion("a2", "char:shenqing", "is_alive", "false", chapter=3)],
        refs=[_ref(5, "a2")],
    )
    findings, _ = check_alive_conflicts(gate_in, GateRules())
    assert [f.code for f in findings] == ["resurrection", "resurrection"]
    assert findings[0].textStart is not None  # 断言那条有逐字 span
    assert findings[1].textStart is None  # 状态快照是章级判定，没有片段
    assert all(f.canonRefs == [5] for f in findings)


# ---------- C3 称谓 ----------


def test_alias_pointing_to_two_entities_is_major() -> None:
    text = "沈姑娘抬起头。"
    gate_in = GateInput(
        text=text,
        chapter_no=3,
        extraction=ChapterExtraction(
            aliases=[_alias("char:a", "沈姑娘"), _alias("char:b", "沈姑娘")]
        ),
    )
    findings, _ = check_alias_drift(gate_in, GateRules())
    assert [(f.code, f.severity, f.canonRefs) for f in findings] == [("alias_drift", "major", [])]
    assert "char:a" in findings[0].explanation and "char:b" in findings[0].explanation
    assert text[findings[0].textStart : findings[0].textEnd] == findings[0].evidenceQuote


def test_one_alias_one_entity_is_fine() -> None:
    """一个人多个称谓是正常写法，只有「一个称谓多个人」才是 C3。"""
    gate_in = GateInput(
        text="沈姑娘抬起头。",
        chapter_no=3,
        extraction=ChapterExtraction(
            aliases=[_alias("char:a", "沈姑娘"), _alias("char:a", "青衫客")]
        ),
    )
    assert check_alias_drift(gate_in, GateRules()) == ([], [])


def test_historical_alias_registry_participates_in_drift() -> None:
    """跨章漂移只有合并历史登记表才看得见——本轮候选自己是干净的。"""
    gate_in = GateInput(
        text="沈姑娘抬起头。",
        chapter_no=3,
        extraction=ChapterExtraction(aliases=[_alias("char:b", "沈姑娘")]),
        known_aliases={"沈姑娘": "char:a"},
    )
    assert len(check_alias_drift(gate_in, GateRules())[0]) == 1


def test_conflicting_alias_absent_from_text_is_chapter_level() -> None:
    gate_in = GateInput(
        text="夜色压得很低。",
        chapter_no=3,
        extraction=ChapterExtraction(aliases=[_alias("char:b", "沈姑娘")]),
        known_aliases={"沈姑娘": "char:a"},
    )
    findings, _ = check_alias_drift(gate_in, GateRules())
    assert len(findings) == 1 and findings[0].textStart is None
    assert findings[0].evidenceQuote == ""


# ---------- 编号引用 ----------


def test_unknown_foreshadow_citation_is_blocker() -> None:
    gate_in = GateInput(
        text="至此，[fsh#9] 的旧账终于清了。",
        chapter_no=4,
        refs=[_ref(3, "f1", kind="foreshadow")],
    )
    findings, _ = check_citations(gate_in, GateRules())
    assert [(f.code, f.severity) for f in findings] == [("foreshadow_missing", "blocker")]


def test_unknown_canon_citation_is_major() -> None:
    gate_in = GateInput(
        text="他想起 [canon#12] 的那条规矩。", chapter_no=4, refs=[_ref(2, "a1")]
    )
    findings, _ = check_citations(gate_in, GateRules())
    assert [(f.code, f.severity) for f in findings] == [("unknown_ref", "major")]


def test_citation_of_injected_number_is_fine() -> None:
    gate_in = GateInput(
        text="他想起 [canon#2] 的规矩，又收了 [fsh#3]。",
        chapter_no=4,
        refs=[_ref(2, "a1"), _ref(3, "f1", kind="foreshadow")],
    )
    assert check_citations(gate_in, GateRules()) == ([], [])


# ---------- 验收口 ----------


def test_validate_drops_fabricated_evidence() -> None:
    finding = Finding(
        code="attribute_conflict",
        severity="blocker",
        checker="judge",
        canonRefs=[1],
        textStart=0,
        textEnd=4,
        evidenceQuote="她的眼睛是蓝色的",
    )
    assert validate_findings([finding], "她的眼睛是红色的。") == ([], 1)


def test_validate_requires_span_and_evidence_together() -> None:
    only_quote = Finding(code="style_drift", checker="rule", evidenceQuote="她的眼睛")
    only_span = Finding(code="style_drift", checker="rule", textStart=0, textEnd=4)
    assert validate_findings([only_quote, only_span], "她的眼睛是红色的。") == ([], 2)


def test_validate_drops_unknown_code_and_ungrounded_judge() -> None:
    invented = Finding(
        code="protagonist_sad",
        checker="rule",
        textStart=0,
        textEnd=4,
        evidenceQuote="她的眼睛",
    )
    judge_without_refs = Finding(code="motivation_break", checker="judge")
    assert validate_findings([invented, judge_without_refs], "她的眼睛是红色的。") == ([], 2)


def test_validate_drops_rule_conflict_without_canon_ref() -> None:
    """与既有事实相抵的规则命中若引不出编号，就是规则自己丢了证据（装配侧已计 skipped）。"""
    finding = Finding(code="death_speaks", severity="blocker", checker="rule")
    assert validate_findings([finding], "沈青道：「我回来了。」") == ([], 1)


def test_chapter_level_rule_finding_without_ref_is_kept() -> None:
    """字数/别名这类冲突的对象本就不是断言表，refs 允许为空。"""
    finding = Finding(code="length_out_of_band", severity="minor", checker="rule")
    kept, dropped = validate_findings([finding], "夜色压得很低。")
    assert kept == [finding] and dropped == 0


# ---------- run_rules 汇总 ----------


def test_run_rules_orders_by_severity_and_reports_word_count() -> None:
    text = "沈青道：「我早就死了。」\n她的眼睛是红色的，像沾了血。\n我站在原地。"
    gate_in = GateInput(
        text=text,
        chapter_no=4,
        extraction=ChapterExtraction(
            assertions=[_candidate("char:her", "eye_color", "红", "她的眼睛是红色的")],
            aliases=[_alias("char:shenqing", "沈青")],
        ),
        snapshot=[
            _assertion("a1", "char:her", "eye_color", "黑", chapter=2),
            _assertion("a2", "char:shenqing", "is_alive", "false", chapter=3),
        ],
        refs=[_ref(1, "a1"), _ref(2, "a2")],
        style=_third_person(),
    )
    report = run_rules(gate_in, GateRules(target_words=60))
    codes = [finding.code for finding in report.findings]
    assert "attribute_conflict" in codes and "death_speaks" in codes
    assert codes[0] in {"attribute_conflict", "death_speaks"}  # blocker 在前
    assert report.has_blocker and len(report.blockers) == 2
    assert report.words == visible_chars(text)
    assert report.dropped == 0 and report.skipped == {}
    assert all(
        finding.evidenceQuote == ""
        or text[finding.textStart : finding.textEnd] == finding.evidenceQuote
        for finding in report.findings
    )


def test_run_rules_caps_per_code_and_is_deterministic() -> None:
    text = "我跟着他。我停下。我听见了。我还要走。我再回头。"
    gate_in = GateInput(text=text, chapter_no=1, style=_third_person())
    rules = GateRules(target_words=20, min_ratio=0.9, max_ratio=1.1)
    first = run_rules(gate_in, rules)
    assert len(first.findings) == rules.per_code_limit + 1  # 3 条人称 + 1 条字数
    assert {f.code for f in first.findings} == {"style_drift", "length_out_of_band"}
    assert [f.model_dump() for f in first.findings] == [
        f.model_dump() for f in run_rules(gate_in, rules).findings
    ]


# ---------- 计划闸门 ----------
#
# 坐标系是 scene_card_text 的渲染而不是正文：规则命中必须能跳回「那张卡的哪一行」，
# 所以这些用例都从 prompts.scene_card_text 拿文本，而不是自己拼一句像的话——
# 模板一改，渲染与规则若漂移，这里会先红。


def _scene(goal: str, present: list[str]) -> PlannedScene:
    return PlannedScene(goal=goal, present=present, beats=[])


def _plan_in(
    card: SceneCard,
    *,
    snapshot: list[CanonAssertion] | None = None,
    refs: list[CanonRef] | None = None,
    chapter_no: int = 2,
) -> PlanInput:
    return PlanInput(
        card_text=scene_card_text(card),
        card=card,
        chapter_no=chapter_no,
        snapshot=snapshot or [],
        refs=refs or [],
    )


_ALIVE_HERO = [_assertion("a1", "char:hero", "anchor", "送信的少年", chapter=1)]
_DEAD_HERO = [
    _assertion("a1", "char:hero", "anchor", "送信的少年", chapter=1),
    _assertion("a2", "char:hero", "is_alive", "false", chapter=1),
]


def test_plan_entity_rule_needs_a_registry_to_judge() -> None:
    """一条已确立事实都没有时「未登记」没有判据：跳过并记账，而不是把开篇全判违规。"""
    card = SceneCard(entities=["char:ghost"], scenes=[_scene("雨夜敲门", ["char:ghost"])])
    findings, skipped = check_plan_entities(_plan_in(card), GateRules())
    assert (findings, skipped) == ([], ["no_registry"])

    hit, _ = check_plan_entities(
        _plan_in(card, snapshot=_ALIVE_HERO, refs=[_ref(1, "a1")]), GateRules()
    )
    assert [(f.code, f.severity) for f in hit] == [("unregistered_entity", "major")]
    # 证据是那一整行（含行末换行），不是孤零零一个 key：作者要看得见上下文
    assert hit[0].evidenceQuote.strip() == "本章实体：char:ghost"


def test_plan_entity_declared_as_new_is_not_a_violation() -> None:
    """显式写进 newEntities 的新人物是「待补设定」，不是违规——闸门不能反过来惩罚承认。"""
    card = SceneCard(
        entities=[],
        newEntities=["char:ghost"],
        scenes=[_scene("雨夜敲门", ["char:ghost"])],
    )
    assert check_plan_entities(_plan_in(card, snapshot=_ALIVE_HERO), GateRules()) == ([], [])


def test_plan_death_rule_is_blocker_and_cites_the_fact() -> None:
    """已死人物出现在 present：blocker，且必须引得出那条 is_alive 事实的编号。"""
    card = SceneCard(entities=["char:hero"], scenes=[_scene("故人重逢", ["char:hero"])])
    findings, skipped = check_plan_deaths(
        _plan_in(card, snapshot=_DEAD_HERO, refs=[_ref(1, "a1"), _ref(2, "a2")]),
        GateRules(),
    )
    assert skipped == []
    assert [(f.code, f.severity) for f in findings] == [("death_speaks", "blocker")]
    assert findings[0].canonRefs == [2]


def test_plan_death_rule_skips_when_the_fact_has_no_number() -> None:
    """编号是工作台的跳转依据：引不出编号就不许留一条指不回事实的指控。"""
    card = SceneCard(entities=["char:hero"], scenes=[_scene("故人重逢", ["char:hero"])])
    findings, skipped = check_plan_deaths(
        _plan_in(card, snapshot=_DEAD_HERO, refs=[_ref(1, "a1")]), GateRules()
    )
    assert (findings, skipped) == ([], ["no_ref"])


def test_plan_payoff_outside_the_open_list_is_blocker() -> None:
    card = SceneCard(payoffs=[7], scenes=[_scene("清账", [])])
    findings, _ = check_plan_payoffs(
        _plan_in(card, refs=[_ref(3, "f1", kind="foreshadow")]), GateRules()
    )
    assert [(f.code, f.severity) for f in findings] == [("foreshadow_missing", "blocker")]
    assert findings[0].evidenceQuote.strip() == "要收的伏笔：[fsh#7]"


def test_plan_length_band_is_minor_only() -> None:
    """字数带偏了不违反任何已确立事实：只记 minor，不该为它烧一轮重排。"""
    card = SceneCard(wordsLow=100, wordsHigh=300, scenes=[_scene("雨夜", [])])
    findings, _ = check_plan_length(_plan_in(card), GateRules(target_words=1200))
    assert [(f.code, f.severity) for f in findings] == [("length_out_of_band", "minor")]

    covering = SceneCard(wordsLow=700, wordsHigh=1900, scenes=[_scene("雨夜", [])])
    assert check_plan_length(_plan_in(covering), GateRules(target_words=1200)) == ([], [])


def test_run_plan_rules_shares_the_acceptance_gate_and_the_card_coordinates() -> None:
    """两道闸门同一个验收口：证据必须逐字等于卡文本切片，跨源冲突要计 duplicated。"""
    card = SceneCard(
        entities=["char:ghost"],
        scenes=[_scene("雨夜敲门", ["char:ghost"])],
        wordsLow=100,
        wordsHigh=300,
    )
    plan_in = _plan_in(card, snapshot=_ALIVE_HERO, refs=[_ref(1, "a1")])
    report = run_plan_rules(plan_in, GateRules(target_words=1200))
    assert {f.code for f in report.findings} == {"unregistered_entity", "length_out_of_band"}
    assert all(f.checker == "rule" for f in report.findings)
    assert all(
        plan_in.card_text[f.textStart : f.textEnd] == f.evidenceQuote
        for f in report.findings
    )
    assert report.words == visible_chars(plan_in.card_text)
    assert report.dropped == 0
