"""语义裁判（PRD §9.2）：一次 LLM 调用，产物走与规则引擎**同一个**验收口。

规则闸门判不了的那部分（世界规则被无代价违反、动机矛盾、叙述时态/腔调漂移）只能交给
模型。但模型自己也会幻读，所以裁判的输出不比抽取宽松：`gates.validate_findings` 要求
逐字证据 + 可解析的 canon 编号，缺一即整条作废——**裁判与被审者不同源 ≠ 裁判可以无证**。

本模块在 §9.2 的字面要求之外多收紧三条，都是为了让「台账里的每一条都能跳到正文的一处」：

1. ``checker`` 强制归位为 ``"judge"``。模型把自报判定标成 ``rule`` 就能绕开
   「裁判必须引编号」那条判定（:func:`gates.validate_findings` 按 checker 分档），
   来源标签不该由被检查的一方填写。
2. 没有证据的判定直接丢弃。§9.2 只要求「证据与 span 不一致 → 作废」，但一条
   既无片段又无引文的「动机矛盾」到了工作台就是一条无法复核的指控，
   留着它等于教作者不信任闸门（§14 的误报风险）。
3. span 由证据反推，不信模型自报的字符偏移。LLM 数中文字符不可靠，而
   「证据逐字出现在正文」是它擅长的；偏移错了就把整条好判定扔掉是白丢证据。
   反推成功后 ``evidenceQuote`` 改写为 ``text[start:end]``：原文切片才是权威证据，
   模型那份只是定位用的副本（可能与原文差着空白）。

裁判失败**不等于没有冲突**（§8-⑧ 不静默降级）：解析失败/网络异常时
:class:`JudgeOutcome.failed` 为真且计数为 ``judge_failed``，由 N4c 的放行策略按
「闸门不可判定」处置，而不是当成绿灯通过。
"""

from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel

from po_agent_novel.context import CanonRef
from po_agent_novel.gates import GateInput, PlanInput, locate_quote, validate_findings
from po_agent_novel.prompts import judge_prompt, plan_judge_prompt
from po_agent_novel.schemas import ChapterOutline, Finding, FindingList

logger = logging.getLogger(__name__)

# 丢弃原因，全部计入 GateReport 侧可观测的计数：静默丢弃等于没有闸门。
_DROP_NO_EVIDENCE = "no_evidence"
_DROP_UNLOCATABLE = "unlocatable"
_DROP_INVALID = "invalid_finding"
_DROP_FAILED = "judge_failed"


@dataclass(frozen=True, slots=True)
class JudgeOutcome:
    """一次裁判的结果。

    :param findings: 已过验收口的 Finding（``checker`` 恒为 ``judge``）
    :param dropped: 各丢弃原因的计数（含验收口作废的 ``invalid_finding``）
    :param relocated: 由证据反推、与模型自报 span 不一致的条数——这个数偏高就说明
        提示词的偏移口径该改，或该换一家更会数数的模型
    :param model_tag: ``_llm_type``，供事件与日志标识「这章是谁审的」；Finding 表没有
        这一维（§15.3 偏差 #1），所以它只活在运行期
    :param failed: 裁判本身没跑成（违约 / 网络 / 无结构化输出能力）。**必须**与
        「跑成了但没查出问题」区分开，否则 §8-⑨ 的假绿灯换个位置又回来了
    """

    findings: list[Finding] = field(default_factory=list)
    dropped: dict[str, int] = field(default_factory=dict)
    relocated: int = 0
    model_tag: str = ""
    failed: bool = False

    @property
    def dropped_total(self) -> int:
        return sum(self.dropped.values())


def ref_lines(refs: Sequence[CanonRef]) -> list[str]:
    """编号表 → 提示词里的设定清单。

    渲染格式与 ``context.compile_context`` 写进注入块的那一行**同构**（前缀按 kind
    区分 canon / fsh）：裁判读到的编号必须与写作者当时看到的同一份，否则「裁判引的
    编号」在工作台上指向另一条事实。
    """
    return [
        f"[{'fsh' if ref.kind == 'foreshadow' else 'canon'}#{ref.number}] {ref.text}"
        for ref in refs
    ]


def _model_tag(model: BaseChatModel) -> str:
    return str(getattr(model, "_llm_type", "") or type(model).__name__)


def prepare_findings(
    findings: Sequence[Finding], text: str
) -> tuple[list[Finding], Counter[str], int]:
    """归位 checker、按证据反推 span，并统计各类丢弃。

    在 :func:`gates.validate_findings` **之前**跑：验收口只管「证据与 span 是否自洽」，
    而这里负责「让自洽成为可能」——先定位再验收，才不会把一批只是数错了偏移的
    真冲突整片作废。
    """
    kept: list[Finding] = []
    dropped: Counter[str] = Counter()
    relocated = 0
    for finding in findings:
        if not finding.evidenceQuote:
            dropped[_DROP_NO_EVIDENCE] += 1
            continue
        span = locate_quote(text, finding.evidenceQuote)
        if span is None:
            dropped[_DROP_UNLOCATABLE] += 1
            continue
        start, end = span
        if (finding.textStart, finding.textEnd) != (start, end):
            relocated += 1
        kept.append(
            finding.model_copy(
                update={
                    "checker": "judge",
                    "textStart": start,
                    "textEnd": end,
                    "evidenceQuote": text[start:end],
                }
            )
        )
    return kept, dropped, relocated


async def _collect(
    model: BaseChatModel, prompt: str, subject_no: int, text: str, tag: str
) -> JudgeOutcome:
    """调用 + 归一 + 验收的公共段（两道语义闸门只在提示词与坐标系上不同）。

    失败口径留在这里而不是各调用点重写：「裁判没跑成」必须与「跑成了但没查出问题」
    分成两种结果（§8-⑧），两种写法各写一半就会只有一种被正确处理。
    """
    try:
        # method 必须显式写 function_calling：缺省时 langchain 走 json_schema
        # response_format，DeepSeek 直接 400（真机现象：两道闸门每次都「裁判未完成」，
        # 于是每一章都带着未经语义审查的计划/正文归档）。
        raw: Any = await model.with_structured_output(
            FindingList, method="function_calling"
        ).ainvoke(prompt)
    except Exception as exc:  # 裁判失败不是「无冲突」，见模块 docstring
        logger.error("第 %s 章语义裁判调用失败：%s", subject_no, exc)
        return JudgeOutcome(dropped={_DROP_FAILED: 1}, model_tag=tag, failed=True)

    if not isinstance(raw, FindingList):
        logger.error(
            "第 %s 章语义裁判返回类型异常（%s），整轮按失败处置",
            subject_no,
            type(raw).__name__,
        )
        return JudgeOutcome(dropped={_DROP_FAILED: 1}, model_tag=tag, failed=True)

    prepared, dropped, relocated = prepare_findings(list(raw.findings), text)
    kept, invalid = validate_findings(prepared, text)
    if invalid:
        dropped[_DROP_INVALID] = invalid
    return JudgeOutcome(
        findings=kept, dropped=dict(dropped), relocated=relocated, model_tag=tag, failed=False
    )


async def run_judge(
    model: BaseChatModel,
    gate_in: GateInput,
    *,
    chapter: ChapterOutline | None = None,
    rule_codes: Sequence[str] = (),
) -> JudgeOutcome:
    """跑一次正文语义裁判（§9.2）。

    :param chapter: 本章大纲；``None`` 时提示词不带大纲段
    :param rule_codes: 规则引擎本轮已命中的编码，写进提示词要求裁判不重复报——
        同一处冲突占两条台账名额，``per_code_limit`` 就白烧了

    入参用 :class:`gates.GateInput` 而不是重新拼一份：正文、编号表、文风契约、章号
    四项与规则闸门同源，两条闸门对「本章是什么」的认定必须完全一致。
    """
    prompt = judge_prompt(
        gate_in.chapter_no,
        gate_in.text,
        ref_lines(gate_in.refs),
        chapter=chapter,
        style_pov=gate_in.style.pov if gate_in.style else None,
        rule_codes=list(rule_codes),
    )
    return await _collect(
        model, prompt, gate_in.chapter_no, gate_in.text, _model_tag(model)
    )


async def run_plan_judge(
    model: BaseChatModel,
    plan_in: PlanInput,
    *,
    chapter: ChapterOutline | None = None,
    style_pov: str | None = None,
    rule_codes: Sequence[str] = (),
) -> JudgeOutcome:
    """跑一次**计划**语义裁判（§7 的 gate_plan 语义段）：被检对象是场景卡。

    与正文裁判共用 :func:`prepare_findings` 与 :func:`gates.validate_findings`，
    只把坐标系换成 ``plan_in.card_text``：「每条判定都能跳回被检对象的一处」这条要求
    对计划同样成立，否则工作台拿到的是一条指不到东西的指控。

    产物**不进 ``review_finding``**：那张表的 span 语义是「章节正文的字符区间」，
    把卡文本坐标写进去，作者点过去会落在正文的别处——悬空出处比少一条记录更有害
    （PRD §15.6 登记）。它只上浮进事件与归档卡片。
    """
    prompt = plan_judge_prompt(
        plan_in.chapter_no,
        plan_in.card_text,
        ref_lines(plan_in.refs),
        chapter=chapter,
        style_pov=style_pov,
        rule_codes=list(rule_codes),
    )
    return await _collect(
        model, prompt, plan_in.chapter_no, plan_in.card_text, _model_tag(model)
    )
