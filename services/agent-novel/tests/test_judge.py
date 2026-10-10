"""语义裁判（judge.py）的单测。

裁判与被审者不同源 ≠ 裁判可以无证，所以这里盯的四件事：
- 编号渲染与 L1 注入块同构：裁判引的 ``[canon#N]`` 必须与作者在工作台看到的那一份
  指向同一条事实，否则台账不可复核；
- span 由证据反推、``checker`` 强制归位为 judge：模型自报的字符偏移不可信，
  来源标签也不该由被检查的一方填写；
- 丢弃要计数：无证据、定位失败、验收口作废三类各归各的桶，静默丢弃等于没有闸门；
- **调用失败与「查不出冲突」是两件事**（§8-⑧/⑨）：failed 必须为真且不带任何结论，
  下游（N4c 的放行策略）才不至于一句「闸门没报」就放行。

计划裁判（``run_plan_judge``）与正文裁判走同一条处理链，只有坐标系换成场景卡：
一条跳不回被检对象的指控，在工作台上就是噪声。
"""

from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.runnables import RunnableLambda

from po_agent_novel.context import CanonRef, StyleContract
from po_agent_novel.gates import GateInput, PlanInput
from po_agent_novel.judge import prepare_findings, ref_lines, run_judge, run_plan_judge
from po_agent_novel.prompts import scene_card_text
from po_agent_novel.schemas import (
    ChapterOutline,
    Finding,
    FindingList,
    PlannedScene,
    SceneCard,
)

# 正文取一小段：足够定位，又不至于让断言里出现「不知道数没数对」的偏移。
TEXT = "夜色压得很低。林九拔出青铜铃，铃身却没有声音。"
QUOTE = "铃身却没有声音"


def _finding(
    *,
    code: str = "world_rule_break",
    quote: str = QUOTE,
    start: int | None = None,
    end: int | None = None,
    refs: list[int] | None = None,
    checker: str = "judge",
) -> Finding:
    return Finding(
        code=code,
        severity="major",
        checker=checker,  # type: ignore[arg-type]
        canonRefs=refs if refs is not None else [1],
        textStart=start,
        textEnd=end,
        evidenceQuote=quote,
        explanation="青铜铃在设定里必然有声，这里无端安静。",
        fixInstruction="补出它此刻无声的代价或缘由。",
    )


def _gate(refs: list[CanonRef] | None = None) -> GateInput:
    return GateInput(
        text=TEXT,
        chapter_no=2,
        refs=refs
        if refs is not None
        else [
            CanonRef(number=1, kind="canon", source_id="canon-1", text="青铜铃 · 特性 = 必鸣"),
            CanonRef(number=2, kind="foreshadow", source_id="fsh-1", text="铃声的代价"),
        ],
        style=StyleContract(genre="玄幻", pov="第三人称"),
    )


class _ScriptedJudge:
    """只实现 run_judge 用到的那一面：``with_structured_output(FindingList).ainvoke``。

    不装成真的 BaseChatModel：裁判的行为边界就是这一次结构化调用，
    多包一层离线模型只会把「谁在调用」和「返回了什么」两件事糊在一起。
    """

    _llm_type = "scripted-judge"

    def __init__(self, result: Any = None, *, error: Exception | None = None) -> None:
        self._result = result
        self._error = error
        self.prompts: list[str] = []
        self.schemas: list[type] = []

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        async def run(prompt: str | list) -> Any:
            self.prompts.append(str(prompt))
            if self._error is not None:
                raise self._error
            return self._result

        self.schemas.append(schema)
        return RunnableLambda(func=run)  # type: ignore[arg-type]


# ---------- 编号渲染 ----------


def test_ref_lines_are_the_same_lines_the_writer_saw() -> None:
    """前缀按 kind 区分、编号原样带出：裁判提示词里的清单必须与注入块逐字同构。"""
    assert ref_lines(_gate().refs) == [
        "[canon#1] 青铜铃 · 特性 = 必鸣",
        "[fsh#2] 铃声的代价",
    ]


def test_empty_ref_lines_stay_empty() -> None:
    """没有编号表时出空列表：提示词那边会换成「本章无相关已登记设定」，不在这里编文案。"""
    assert ref_lines([]) == []


# ---------- 证据反推 span ----------


def test_model_payload_without_checker_still_parses() -> None:
    """省略 checker 是 DeepSeek 的常态（它把恒定值字段省掉），不该让整份判定作废。

    真机现象：一次 7 条「missing: checker」把 FindingList 整体打回，闸门只能报
    「裁判未完成」——查出的冲突越多，丢得越干净。
    """
    parsed = FindingList.model_validate(
        {
            "findings": [
                {
                    "code": "world_rule_break",
                    "severity": "major",
                    "canonRefs": [1],
                    "evidenceQuote": QUOTE,
                    "explanation": "青铜铃在设定里必然有声，这里无端安静。",
                }
            ]
        }
    )
    assert [finding.checker for finding in parsed.findings] == ["judge"]
    kept, dropped, _ = prepare_findings(parsed.findings, TEXT)
    assert len(kept) == 1 and dropped == {}


def test_prepare_relocates_from_evidence_and_forces_checker() -> None:
    # 模型给的偏移是错的（它还自称 rule），证据本身却是逐字摘自正文的
    finding = _finding(start=999, end=1000, checker="rule")
    kept, dropped, relocated = prepare_findings([finding], TEXT)
    start, end = TEXT.index(QUOTE), TEXT.index(QUOTE) + len(QUOTE)
    assert relocated == 1
    assert kept[0].textStart == start and kept[0].textEnd == end
    assert kept[0].evidenceQuote == TEXT[start:end]
    assert kept[0].checker == "judge"
    assert dropped == {}


def test_prepare_keeps_an_already_correct_span_without_relocating() -> None:
    start = TEXT.index(QUOTE)
    kept, _, relocated = prepare_findings([_finding(start=start, end=start + len(QUOTE))], TEXT)
    assert relocated == 0
    assert kept[0].textStart == start


def test_prepare_tolerates_whitespace_only_in_quote() -> None:
    """模型把正文里的换行排成空格时仍然定位得到，且证据改写回原文切片。"""
    text = "夜色压得很低。\n铃身却没有声音。"
    kept, dropped, relocated = prepare_findings([_finding(quote="夜色压得很低。 铃身却没有声音。")], text)
    assert dropped == {} and relocated == 1
    assert kept[0].evidenceQuote == text[0 : kept[0].textEnd]


def test_prepare_drops_quoteless_verdicts() -> None:
    """无证据的判定不进台账：到了工作台就是一条无法复核的指控。"""
    kept, dropped, _ = prepare_findings([_finding(quote="")], TEXT)
    assert kept == []
    assert dropped["no_evidence"] == 1


def test_prepare_drops_unlocatable_quotes() -> None:
    kept, dropped, _ = prepare_findings([_finding(quote="铃声响彻山谷")], TEXT)
    assert kept == []
    assert dropped["unlocatable"] == 1


# ---------- 一次裁判调用 ----------


async def test_run_judge_success_path() -> None:
    model = _ScriptedJudge(FindingList(findings=[_finding(start=0, end=1)]))
    outcome = await run_judge(model, _gate(), rule_codes=["length"])
    assert outcome.failed is False
    assert [f.code for f in outcome.findings] == ["world_rule_break"]
    # 偏移由证据反推，model_tag 留下「这章是谁审的」
    assert outcome.relocated == 1
    assert outcome.model_tag == "scripted-judge"
    assert model.schemas == [FindingList]


async def test_run_judge_call_failure_is_not_an_empty_ledger() -> None:
    """网络/违约失败：failed 为真、计数为 judge_failed，且 findings 空不等于「审查通过」。"""
    model = _ScriptedJudge(error=RuntimeError("上游 503"))
    outcome = await run_judge(model, _gate())
    assert outcome.failed is True
    assert outcome.findings == []
    assert outcome.dropped == {"judge_failed": 1}
    assert outcome.dropped_total == 1


async def test_run_judge_rejects_a_non_findinglist_return() -> None:
    """结构化违约（返回 dict / 别的类型）整轮按失败处置，不静默当成空集。"""
    outcome = await run_judge(_ScriptedJudge({"findings": []}), _gate())
    assert outcome.failed is True
    assert outcome.dropped == {"judge_failed": 1}


async def test_run_judge_drops_verdicts_without_refs() -> None:
    """裁判必须引编号：证据齐全但 canonRefs 空 → 验收口作废并计入 invalid_finding。"""
    outcome = await run_judge(_ScriptedJudge(FindingList(findings=[_finding(refs=[])])), _gate())
    assert outcome.failed is False
    assert outcome.findings == []
    assert outcome.dropped["invalid_finding"] == 1


async def test_run_judge_empty_list_is_a_legit_verdict() -> None:
    outcome = await run_judge(_ScriptedJudge(FindingList()), _gate())
    assert (outcome.failed, outcome.findings, outcome.dropped) == (False, [], {})


def test_prompt_carries_numbers_outline_and_rule_hits() -> None:
    """提示词只给编号表（不给全库），并告知规则已命中的编码以免重复占台账名额。"""
    model = _ScriptedJudge(FindingList())
    asyncio.run(
        run_judge(
            model,
            _gate(),
            chapter=ChapterOutline(index=2, title="无声之铃", summary="林九发现青铜铃失灵"),
            rule_codes=["attribute_conflict", "pov_drift"],
        )
    )
    prompt = model.prompts[0]
    assert "[canon#1] 青铜铃 · 特性 = 必鸣" in prompt
    assert "[fsh#2] 铃声的代价" in prompt
    assert "林九发现青铜铃失灵" in prompt
    assert "attribute_conflict、pov_drift" in prompt
    assert TEXT in prompt
    assert "第三人称" in prompt


# ---------- 计划裁判（run_plan_judge）----------
#
# 与正文裁判共用 prepare_findings 与验收口，只把坐标系换成卡文本：
# 「每条判定都能跳回被检对象的一处」对计划同样成立，否则工作台拿到的是一条
# 指不到东西的指控。


CARD = SceneCard(
    entities=["char:hero"],
    scenes=[PlannedScene(goal="雨夜敲门，故人重逢", present=["char:hero"], beats=["铃无人鸣"])],
)
CARD_TEXT = scene_card_text(CARD)
CARD_QUOTE = "铃无人鸣"


def _plan_in() -> PlanInput:
    return PlanInput(
        card_text=CARD_TEXT,
        card=CARD,
        chapter_no=2,
        refs=[CanonRef(number=1, kind="canon", source_id="canon-1", text="青铜铃 · 特性 = 必鸣")],
    )


async def test_plan_judge_locates_on_the_card_not_the_prose() -> None:
    finding = _finding(quote=CARD_QUOTE, start=0, end=1)
    model = _ScriptedJudge(FindingList(findings=[finding]))
    outcome = await run_plan_judge(model, _plan_in(), rule_codes=["length_out_of_band"])
    assert outcome.failed is False and outcome.relocated == 1
    kept = outcome.findings[0]
    assert CARD_TEXT[kept.textStart : kept.textEnd] == kept.evidenceQuote
    assert kept.checker == "judge"
    # 被检对象是那张卡，提示词里不许出现「正文」坐标系
    assert "场景卡（你唯一的被检对象）：" in model.prompts[0]
    assert CARD_TEXT in model.prompts[0]
    assert "length_out_of_band" in model.prompts[0]


async def test_plan_judge_drops_evidence_that_is_not_on_the_card() -> None:
    """拿正文句子来指控计划：定位不到即丢弃并计数，不留一条跳不过去的判定。"""
    outcome = await run_plan_judge(
        _ScriptedJudge(FindingList(findings=[_finding(quote=QUOTE)])), _plan_in()
    )
    assert outcome.findings == []
    assert outcome.dropped["unlocatable"] == 1


async def test_plan_judge_failure_is_unreviewed_at_the_plan_gate_too() -> None:
    """裁判没跑成 → failed：由 decide_plan_release 换成 escalate + unreviewed，而不是绿灯。"""
    outcome = await run_plan_judge(_ScriptedJudge(error=RuntimeError("上游 503")), _plan_in())
    assert outcome.failed is True and outcome.dropped == {"judge_failed": 1}
