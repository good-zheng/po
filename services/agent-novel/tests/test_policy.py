"""放行策略（policy.py）的单测——§9.3 的三态判定必须逐条能脱离模型跑。

覆盖四件事：
- 严重度 → 处置的映射：blocker 可定位走定向修补、不可定位走整章重写、轮数用尽冻结；
  major 放行但把相抵的新候选降为 disputed；minor 只记录；
- ``judge_failed`` 是第四种状态而不是「没查出问题」：它冻结，且带 ``unreviewed``；
- 编号解析的两种 source_id（库内行按 id、本轮候选按 ``pending:``，后者实体键自带冒号）；
- 回拼的三条拒收口径（空 / 与原文一致 / 长度异常），以及倒序与轮次上限。

计划闸门走 :func:`decide_plan_release`，三态是 ``pass / replan / escalate``：判据把
major 也算进「必须处理」，而轮数用尽与裁判失败都**升级给作者**而不是冻结——
停一张还没花过 token 的卡，成本与作废一章正文不在一个量级。
"""

from __future__ import annotations

from po_agent_novel.context import CanonRef, StyleContract
from po_agent_novel.gates import GateInput
from po_agent_novel.policy import (
    ReleasePolicy,
    apply_disputed,
    conflicting_keys,
    decide_plan_release,
    decide_release,
    patch_plan,
    rewrite_feedback,
    splice_patch,
)
from po_agent_novel.schemas import AssertionCandidate, ChapterExtraction, Finding
from po_agent_novel.store import CanonAssertion

TEXT = "夜色压得很低。林九拔出青铜铃，铃身却没有声音。他想起师父说过的话。"
SPAN = (7, 16)  # TEXT[7:16] == "林九拔出青铜铃"
QUOTE = TEXT[7:16]


def _assertion(
    assertion_id: str, subject_key: str, predicate: str, *, status: str = "confirmed"
) -> CanonAssertion:
    return CanonAssertion(
        id=assertion_id,
        book_id="book-1",
        kind="character",
        subject_key=subject_key,
        predicate=predicate,
        object_text="黑发",
        restatement=f"{subject_key} 的 {predicate}",
        authority="model",
        established_chapter=1,
        valid_from_chapter=1,
        valid_until_chapter=None,
        status=status,
    )


def _ref(number: int, source_id: str, kind: str = "canon") -> CanonRef:
    return CanonRef(number=number, kind=kind, source_id=source_id, text=f"设定 {number}")


def _finding(
    code: str = "attribute_conflict",
    severity: str = "blocker",
    *,
    checker: str = "rule",
    start: int | None = SPAN[0],
    end: int | None = SPAN[1],
    quote: str = QUOTE,
    refs: list[int] | None = None,
    fix: str = "把铃的来历改成为师所赠",
) -> Finding:
    return Finding(
        code=code,
        severity=severity,
        checker=checker,
        canonRefs=refs or [],
        textStart=start,
        textEnd=end,
        evidenceQuote=quote,
        explanation=f"{code} 命中",
        fixInstruction=fix,
    )


def _gate(
    *,
    extraction: ChapterExtraction | None = None,
    snapshot: tuple[CanonAssertion, ...] = (),
    refs: tuple[CanonRef, ...] = (),
) -> GateInput:
    return GateInput(
        text=TEXT,
        chapter_no=1,
        extraction=extraction,
        snapshot=snapshot,
        refs=refs,
        style=StyleContract(genre="玄幻", pov="第三人称"),
    )


def _candidate(subject_key: str, predicate: str, *, status: str = "confirmed") -> AssertionCandidate:
    return AssertionCandidate(
        kind="character",
        subjectKey=subject_key,
        predicate=predicate,
        objectText="白发",
        restatement=f"{predicate}=白发",
        evidenceQuote=QUOTE,
        status=status,
    )


# ---------- 严重度 → 处置 ----------


def test_clean_chapter_passes() -> None:
    release = decide_release(_gate(), [_finding(severity="minor")], judge_failed=False, repairs=0)
    assert release.action == "pass"
    assert release.blocking is False
    assert release.blockers == ()


def test_locatable_blocker_routes_to_patch() -> None:
    release = decide_release(_gate(), [_finding()], judge_failed=False, repairs=0)
    assert release.action == "patch"
    assert len(release.blockers) == 1
    assert release.reason  # 冻结/修补都要在事件里说清为什么


def test_chapter_level_blocker_routes_to_rewrite() -> None:
    """无 span 的 blocker（空章、字数严重失控）没有片段可指，退化为整章重写。"""
    no_span = _finding(code="length_out_of_band", start=None, end=None, quote="", fix="")
    release = decide_release(_gate(), [no_span, _finding()], judge_failed=False, repairs=0)
    assert release.action == "rewrite"


def test_mixed_blockers_choose_the_stronger_remedy() -> None:
    """混合时走整章重写：定向修补改不掉「整章都错」，两条路径互相抵消。"""
    findings = [_finding(), _finding(code="death_speaks", start=None, end=None, quote="")]
    assert decide_release(_gate(), findings, judge_failed=False, repairs=0).action == "rewrite"


def test_repairs_exhausted_freezes() -> None:
    blockers = [_finding()]
    assert (
        decide_release(_gate(), blockers, judge_failed=False, repairs=1, policy=ReleasePolicy(max_repairs=2)).action
        == "patch"
    )
    frozen = decide_release(
        _gate(), blockers, judge_failed=False, repairs=2, policy=ReleasePolicy(max_repairs=2)
    )
    assert frozen.action == "freeze"
    assert frozen.blocking is True
    assert "2 轮" in frozen.reason


def test_judge_failure_freezes_as_unreviewed() -> None:
    """裁判没跑成 ≠ 没有冲突：即使一条 Finding 都没有也必须冻结，且标记未经审查。"""
    frozen = decide_release(_gate(), [], judge_failed=True, repairs=0)
    assert frozen.action == "freeze"
    assert frozen.unreviewed is True
    assert frozen.blockers == ()


# ---------- major → disputed ----------


def test_major_only_passes_but_records_disputed_keys() -> None:
    gate = _gate(
        snapshot=(_assertion("a-1", "char:linjiu", "eye_color"),),
        refs=(_ref(1, "a-1"),),
    )
    release = decide_release(
        gate, [_finding(severity="major", refs=[1])], judge_failed=False, repairs=0
    )
    assert release.action == "pass"  # §9.3：major 允许 commit
    assert release.disputed == frozenset({("char:linjiu", "eye_color")})


def test_pending_refs_resolve_despite_colon_in_subject_key() -> None:
    """本轮候选没有库主键，source_id 是 ``pending:char:linjiu:eye_color``——两级冒号。"""
    gate = _gate(refs=(_ref(2, "pending:char:linjiu:eye_color"),))
    keys = conflicting_keys(gate, [_finding(severity="major", refs=[2])])
    assert keys == frozenset({("char:linjiu", "eye_color")})


def test_unresolvable_and_foreshadow_refs_are_ignored() -> None:
    gate = _gate(
        snapshot=(_assertion("a-9", "char:x", "y"),),
        refs=(_ref(1, "a-9"), _ref(3, "fsh-1", kind="foreshadow")),
    )
    keys = conflicting_keys(gate, [_finding(severity="major", refs=[1, 3, 7])])
    assert keys == frozenset({("char:x", "y")})  # 3 是伏笔、7 未注入：都不算冲突实体


def test_apply_disputed_only_demotes_confirmed_candidates() -> None:
    extraction = ChapterExtraction(
        assertions=[
            _candidate("char:linjiu", "eye_color"),
            _candidate("char:linjiu", "realm"),
            _candidate("char:other", "eye_color", status="todo"),
        ]
    )
    demoted, changed = apply_disputed(extraction, frozenset({("char:linjiu", "eye_color")}))
    assert changed == 1
    assert [item.status for item in demoted.assertions] == ["disputed", "confirmed", "todo"]
    # 没有命中时返回原对象：不制造「看起来改过」的新副本
    same, none_changed = apply_disputed(extraction, frozenset())
    assert same is extraction and none_changed == 0


# ---------- 定向修补 ----------


def test_patch_plan_orders_descending_and_caps_overflow() -> None:
    second = _finding(code="death_speaks", start=25, end=30, quote=TEXT[25:30])
    plan, overflow = patch_plan(TEXT, [_finding(), second], (), ReleasePolicy(max_patches=1))
    assert overflow == 1
    assert [target.start for target in plan] == [25]  # 倒序：先改后面的，前面的偏移才不失效


def test_patch_plan_windows_context_and_resolves_canon_lines() -> None:
    refs = (_ref(1, "a-1"), _ref(4, "fsh-4", kind="foreshadow"))
    plan, _ = patch_plan(
        TEXT,
        [_finding(refs=[1, 4, 9])],
        refs,
        ReleasePolicy(patch_context_chars=4),
    )
    target = plan[0]
    assert target.target == QUOTE
    assert target.before == TEXT[SPAN[0] - 4 : SPAN[0]]
    assert target.after == TEXT[SPAN[1] : SPAN[1] + 4]
    # 未注入的编号（9）不硬编成一行设定
    assert target.canon_lines == ("[canon#1] 设定 1", "[fsh#4] 设定 4")


def test_patch_plan_falls_back_to_explanation_without_instruction() -> None:
    finding = _finding(fix="")
    plan, _ = patch_plan(TEXT, [finding], (), ReleasePolicy())
    assert plan[0].instruction == finding.explanation


def test_splice_replaces_only_the_span() -> None:
    plan, _ = patch_plan(TEXT, [_finding()], (), ReleasePolicy())
    patched = splice_patch(TEXT, plan[0], "林九摸出那枚旧铃")
    assert patched == TEXT[: SPAN[0]] + "林九摸出那枚旧铃" + TEXT[SPAN[1] :]


def test_splice_rejects_empty_identical_and_oversized() -> None:
    plan, _ = patch_plan(TEXT, [_finding()], (), ReleasePolicy())
    target = plan[0]
    assert splice_patch(TEXT, target, "   ") is None
    assert splice_patch(TEXT, target, target.target) is None
    # 模型「顺手」重写整章：长度远超片段即拒收，否则没问题的段落会被一起换掉
    assert splice_patch(TEXT, target, "很长" * 60) is None
    # 略长于片段仍接受：改一句话本来就要多几个字
    assert splice_patch(TEXT, target, "林九摸出那枚师父留下的旧铃") is not None


def test_rewrite_feedback_keeps_every_blocker_visible() -> None:
    text = rewrite_feedback([_finding(fix="改 A"), _finding(code="death_speaks", fix="")])
    assert "attribute_conflict 命中：改 A" in text
    assert "death_speaks 命中" in text
    assert text.count("\n") == 1


# ---------- 计划闸门放行（decide_plan_release）----------


def test_plan_release_promotes_major_to_must_fix() -> None:
    """计划侧把 major 也算「必须处理」：一个未登记的 key 放过去就是「凭空多一个人」。"""
    release = decide_plan_release([_finding(severity="major")], judge_failed=False, attempts=0)
    assert release.action == "replan"
    assert release.blocking and len(release.blockers) == 1
    assert "第 1 轮" in release.reason


def test_plan_release_leaves_minor_to_the_record() -> None:
    """字数带偏了不违反任何已确立事实：为它重排一轮，换来的收益抵不上多一次裁判。"""
    release = decide_plan_release([_finding(severity="minor")], judge_failed=False, attempts=1)
    assert release.action == "pass"
    assert release.blockers == () and not release.blocking


def test_plan_release_exhausts_into_the_author_not_a_freeze() -> None:
    """轮数用尽 → escalate：这里停的是「还没写的一章」，作者一句话就能放行。

    正文侧同一处境是 freeze（作废的是已写成的稿子，成本不对称），两种处置不能合并。
    """
    release = decide_plan_release(
        [_finding(severity="blocker")], judge_failed=False, attempts=2, policy=ReleasePolicy()
    )
    assert release.action == "escalate"
    assert "重排 2 轮后仍有 1 条" in release.reason
    # 轮数预算与正文侧分开计：计划回炉只改十几行，不该挤掉正文修补的额度
    assert release.unreviewed is False


def test_plan_judge_failure_escalates_as_unreviewed() -> None:
    """裁判没跑成 ≠ 没有冲突：即使零判定也要升级，且标上「未经完整审查」。"""
    release = decide_plan_release([], judge_failed=True, attempts=0)
    assert release.action == "escalate" and release.unreviewed is True
    assert "不可判定" in release.reason


def test_plan_policy_repairs_are_independent_per_chapter() -> None:
    """装配层可按压测调 max_plan_repairs：判定的分母必须跟着配置走。"""
    policy = ReleasePolicy(max_plan_repairs=0)
    release = decide_plan_release(
        [_finding(severity="major")], judge_failed=False, attempts=0, policy=policy
    )
    assert release.action == "escalate"
