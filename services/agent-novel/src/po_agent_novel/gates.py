"""确定性规则闸门（PRD §9.1）：零 LLM、零网络，只比对「本章文本」与「已登记事实」。

存在的理由：语义裁判自己也会幻读，所以 C1/C2/C3 里凡是能变成机器可判定比对的
都不该交给模型。本模块每条规则都只读入参、不猜测——规则命中即事实；规则没命中
**不代表没问题**（判不了的那部分交给 N4b 的裁判）。

三条贯穿全模块的口径：

1. **逐字证据**（机制②）：带 span 的 Finding，其 ``evidenceQuote`` 必须逐字等于
   ``text[textStart:textEnd]``，只容忍空白差异（:func:`evidence_verbatim` 与抽取侧是
   同一份实现，因此「放行的证据」与「台账里的证据」不会各说各话）。规则引擎按 span
   取原文生成证据，因此天然成立；:func:`validate_findings` 真正守的是裁判产物，放在
   同一处是为了让两种 checker 走同一个验收口。
2. **引用即编号**：Finding 的 ``canonRefs`` 用 L1 注入的 ``[canon#N]`` 编号而非库
   主键——作者在工作台看到的编号必须与模型当时看到的那一份对得上。拿不到编号的
   命中**不静默丢弃**，计入 ``GateReport.skipped``（静默等于没有闸门）。
3. **区间可空**：整章级规则（字数越带、状态翻转）没有可指向的片段，
   ``textStart`` / ``textEnd`` 留空。Java ``review_finding.text_start`` 允许 NULL，
   且服务层按「NULL 也算重复」显式查重，重放不会写双份。无 span 的 Finding 到了
   N4c 会退化为整章重写——定向修补喂不出「整章都错」的上下文，这是刻意的分派。

严重度映射（§9.3 的三档各对应一类可执行的处置）：

- ``blocker``：改文本就能解决，且不解决就不能 commit（属性冲突、死者发言、无交代
  复活、禁用词、回收了不存在的伏笔、空章）。
- ``major``：机器无权判定谁对，要作者裁定（别名一对多、视角整体漂移、字数严重失控、
  引用了未注入的设定编号）。
- ``minor``：记录不阻断，供 §12 评测与风格调优（零星第一人称、轻度偏离字数带）。

本模块住两道闸门：**正文闸门**（:func:`run_rules`，判已成稿的章节）与**计划闸门**
（:func:`run_plan_rules`，判还没花掉写作 token 的场景卡，§7 的 gate_plan）。
两者共用同一套编码、同一个验收口与同一份取舍口径，只是坐标系不同——正文闸门的 span
落在章节正文上，计划闸门的 span 落在 :func:`prompts.scene_card_text` 的稳定渲染上。
分成两个入参而不是复用 :class:`GateInput` 加一个标志位，是因为判据真的不一样：
计划里没有「正文逐字证据」可言，硬套会让正文规则在卡文本上空转并报出假冲突。
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, get_args

from po_agent_novel.context import CanonRef, StyleContract
from po_agent_novel.schemas import (
    ChapterExtraction,
    Finding,
    FindingCode,
    FindingSeverity,
    SceneCard,
)
from po_agent_novel.store import CanonAssertion

# 证据与 span 的硬上限：与 Java ``clip(evidenceQuote, 512)`` 同值。Python 侧先收敛，
# 服务端才不会静默截断——被裁短的证据跟 span 原文不再逐字相等，落库产物会过不了
# 这条闸门自己定的校验。
_EVIDENCE_LIMIT = 512

_WHITESPACE = re.compile(r"\s+")

# 引号对：对话与题内的「我」不算叙述者人称，被引的人物发言不算死者行动。
_QUOTE_PAIRS = (("「", "」"), ("『", "』"), ("\u201c", "\u201d"), ("\u2018", "\u2019"))
_QUOTE_MASK = "\x00"

# 句末标点：定位证据片段时按句取，既保证片段自然完整，也把证据长度压在预算内。
_SENTENCE_ENDS = "。！？；\n"

# 发言动词：与人名同现才算「这个人在说话」，只出现名字不构成发言。
_SPEECH_VERBS = (
    "说", "道", "问", "答", "喊", "叫", "笑", "叹", "念", "喝", "吼", "语", "嘟囔", "哼",
)

# 允许随剧情变化的谓词：这些属性的「新旧不一致」是剧情推进而不是冲突，该由断言区间
# （valid_from/valid_until）表达，不该由闸门报出来。
_MUTABLE_PREDICATES = frozenset(
    {
        "location",
        "location_key",
        "mood",
        "holds",
        "knows",
        "health",
        "injury",
        "age",
        "realm",
        "cultivation",
        "power_level",
        "companions",
        "allies",
    }
)

# 生死谓词单独走 check_alive_conflicts：true→false 是正常死亡，只有 false→true 才是
# 「无交代复活」，用通用属性冲突表达会把每一次死亡都报成 bug。
_ALIVE_PREDICATE = "is_alive"

_FALSY = frozenset({"false", "no", "none", "null", "0", "dead", "否", "无", "已死", "殁", "死"})
_TRUTHY = frozenset({"true", "yes", "alive", "1", "是", "存活", "在世", "活着"})

# 必须带 canon 引用的编码：这类冲突的定义就是「与某条已登记事实相抵」，
# 引不出事实条目就说明规则自己丢了证据。其余（字数 / 禁用词 / 别名 / 引用编号）
# 冲突对象本就不是断言表，允许 refs 为空。
_REF_REQUIRED_CODES = frozenset(
    {
        "attribute_conflict",
        "death_speaks",
        "resurrection",
        "knowledge_leak",
        "timeline_break",
        "world_rule_break",
        "motivation_break",
    }
)

# 收下的编码全集：schemas.FindingCode 是唯一维护点。未知编码走「作废」而不是
# 抛 ValidationError——闸门作废一条记录是可观测的（dropped 计数），
# 而结构化输出违约会让整轮运行终止。
_KNOWN_CODES = frozenset(get_args(FindingCode))

_CITATION = re.compile(r"\[(canon|fsh)#(\d+)\]")

_SEVERITY_ORDER: dict[str, int] = {"blocker": 0, "major": 1, "minor": 2}

RuleResult = tuple[list[Finding], list[str]]


def evidence_verbatim(quote: str, text: str) -> bool:
    """机制②「证据强制」：证据必须逐字摘自正文，否则整条作废。

    只归一化空白（模型常把正文里的换行排成空格），不做大小写/标点/省略号等任何
    「宽松匹配」——一旦放宽，这条闸门就退化成又一个软措辞，而它是
    「正文里确实写了」与「模型觉得应该如此」之间唯一的硬分界。

    原先住在 graph.py，迁入本模块是为了让抽取侧与闸门侧共用同一份口径：两道闸门
    对「证据」的定义不一致时，被抽验收到的断言可能在台账里被判伪造。
    """
    normalized_quote = _WHITESPACE.sub("", quote)
    return bool(normalized_quote) and normalized_quote in _WHITESPACE.sub("", text)


def evidence_matches_span(quote: str, text: str, start: int, end: int) -> bool:
    """证据必须等于它自己声明的那一段原文（同样只容忍空白差异）。

    §9.2「``evidence_quote`` 与 ``text_span`` 原文完全一致，否则该 Finding 作废」的
    落点：裁判可以给一段真原文却把 span 挪到别处，也可以给对的 span 配一句改写过的
    「原文」，两种都是编造证据，只有逐字相等能同时挡住。
    """
    if not 0 <= start < end <= len(text):
        return False
    if not quote:
        return False
    return _WHITESPACE.sub("", quote) == _WHITESPACE.sub("", text[start:end])


def mask_quotes(text: str) -> str:
    """把引号内的字符替换成占位符，**长度与位置保持不变**。

    保长度是关键：规则在掩码文本上定位，再回到原文取证据。一旦压缩长度，span 就与
    原文错位，逐字校验会把自己写的规则判死。
    """
    out = list(text)
    pending: list[str] = []
    for index, char in enumerate(text):
        if pending:
            out[index] = _QUOTE_MASK
            if char == pending[-1]:
                pending.pop()
            else:
                for opener, closer in _QUOTE_PAIRS:
                    if char == opener:
                        pending.append(closer)
                        break
            continue
        for opener, closer in _QUOTE_PAIRS:
            if char == opener:
                out[index] = _QUOTE_MASK
                pending.append(closer)
                break
    return "".join(out)


def sentence_span(text: str, pos: int) -> tuple[int, int]:
    """取包含 ``pos`` 的句子区间（``[start, end)``，含句末标点）。"""
    start = 0
    for index in range(pos - 1, -1, -1):
        if text[index] in _SENTENCE_ENDS:
            start = index + 1
            break
    end = len(text)
    for index in range(pos, len(text)):
        if text[index] in _SENTENCE_ENDS:
            end = index + 1
            break
    while start < end and text[start].isspace():
        start += 1
    if end - start > _EVIDENCE_LIMIT:
        end = start + _EVIDENCE_LIMIT
    return start, end


def visible_chars(text: str) -> int:
    """正文字数（不计空白）：中文网文的「字数」口径，与含换行的字符数不同。"""
    return sum(1 for char in text if not char.isspace())


class _Locator:
    """按「去空白」口径把候选证据定位回原文区间。

    抽取侧的证据校验只归一化空白（见 :func:`evidence_verbatim`），所以
    ``evidenceQuote`` 与正文可能差着换行；直接 ``text.find(quote)`` 会把合法证据当成
    定位失败，于是「正文里跨行的那处冲突」在台账里静默消失。
    """

    __slots__ = ("_joined", "_starts", "_text")

    def __init__(self, text: str) -> None:
        chars: list[str] = []
        starts: list[int] = []
        for index, char in enumerate(text):
            if not char.isspace():
                chars.append(char)
                starts.append(index)
        self._text = text
        self._joined = "".join(chars)
        self._starts = starts

    def locate(self, needle: str) -> tuple[int, int] | None:
        stripped = _WHITESPACE.sub("", needle)
        if not stripped:
            return None
        pos = self._joined.find(stripped)
        if pos < 0:
            return None
        stop = min(pos + len(stripped), len(self._starts))
        start = self._starts[pos]
        end = self._starts[stop - 1] + 1
        if end - start > _EVIDENCE_LIMIT:
            end = start + _EVIDENCE_LIMIT
        return start, end


def locate_quote(text: str, quote: str) -> tuple[int, int] | None:
    """证据 → 原文区间（与 :func:`evidence_verbatim` 同一份「去空白」口径，取首个落点）。

    :func:`evidence_verbatim` 判「正文里确实有这句」，本函数补「在哪一句」。两者必须
    同口径，否则出现「证据合法但定位失败」的第三种状态——而语义裁判的 span 全靠它反推
    （模型自报的字符偏移不可信，见 judge.py）。
    """
    return _Locator(text).locate(quote)


@dataclass(frozen=True, slots=True)
class GateRules:
    """规则口径（缺省即 PRD 的要求，装配层可按书覆盖）。

    字数带用比值而非绝对值：目标 1200 字的章与目标 3000 字的章要同一套判据。
    越过 ``hard_*`` 才升格——「比目标长三成」既不是幻觉也不值得烧一轮修补，只记
    ``minor``。
    """

    target_words: int = 1200
    min_ratio: float = 0.6
    max_ratio: float = 1.6
    hard_min_ratio: float = 0.35
    hard_max_ratio: float = 2.2
    narrator_ego: tuple[str, ...] = ("我", "俺", "咱")
    pov_major_hits: int = 3
    forbidden_words: tuple[str, ...] = ()
    speech_window: int = 12
    # 每个编码最多留几条：一处系统性漂移会在同一章命中十几条，台账被同一件事刷屏
    # 之后就没人看，宁可在报告里如实记数。
    per_code_limit: int = 3


@dataclass(frozen=True, slots=True)
class GateInput:
    """一次检视的输入：正文 + 已成立事实 + 本章候选 + L1 编号。

    :param text: 本章定稿正文（所有 span 的坐标系）
    :param chapter_no: 1 基章号，只用于解释文案
    :param extraction: 本章 extract 产出；``None`` 表示抽取失败，此时依赖候选的规则
        整体跳过——没有候选就没有可比对的增量
    :param snapshot: as-of 已确认断言（库内 + 本轮 overlay 合并后的读侧视图）。
        必须与 ``refs`` 同源：闸门只在「模型当时看得见」的事实上做判定
    :param refs: L1 装配产物里的编号表，用于把断言换成 ``[canon#N]``
    :param known_aliases: 历史称谓登记表（aliasText → entityKey）。本轮候选之外的
        别名漂移只能靠它比对，会话内累积的 overlay 与 N5b 的读侧都填这个口子
    :param style: 文风契约；``None`` 时不做视角检查（没有契约就没有违规可言）
    """

    text: str
    chapter_no: int
    extraction: ChapterExtraction | None = None
    snapshot: Sequence[CanonAssertion] = ()
    refs: Sequence[CanonRef] = ()
    known_aliases: Mapping[str, str] = field(default_factory=lambda: MappingProxyType({}))
    style: StyleContract | None = None


@dataclass(frozen=True, slots=True)
class GateReport:
    """规则闸门的结果：收下的 Finding + 两类「没收下」的计数。"""

    findings: list[Finding] = field(default_factory=list)
    dropped: int = 0
    skipped: dict[str, int] = field(default_factory=dict)
    words: int = 0

    @property
    def blockers(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "blocker"]

    @property
    def majors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "major"]

    @property
    def minors(self) -> list[Finding]:
        return [finding for finding in self.findings if finding.severity == "minor"]

    @property
    def has_blocker(self) -> bool:
        return any(finding.severity == "blocker" for finding in self.findings)


@dataclass(frozen=True, slots=True)
class PlanInput:
    """一次**计划**检视的输入：场景卡 + as-of 事实 + L1 编号。

    与 :class:`GateInput` 分开的理由不是形式：两者的坐标系不同（卡文本 vs 章节正文）、
    被检对象不同（还没花掉写作 token 的意图 vs 已成稿的事实），合成一个入参会让
    「正文规则在计划上跑」这种误用变成可能——计划里没有逐字证据，正文规则会整片空转。

    :param card_text: :func:`prompts.scene_card_text` 的稳定渲染，**所有 span 的坐标系**
    :param card: 同一张卡的结构体（规则读字段而不是解析文本，避免模板一改规则就哑）
    :param chapter_no: 1 基章号，只用于解释文案
    :param snapshot: 计划时那次装配拿到的 as-of 快照（**不按 entities 收窄**：
        判「这个实体存不存在」的口径必须比检索口径更宽，否则每个新实体都是违规）
    :param refs: 与 ``snapshot`` 同源的编号表；``foreshadow`` 行即「可回收的伏笔」全集
    """

    card_text: str
    card: SceneCard
    chapter_no: int
    snapshot: Sequence[CanonAssertion] = ()
    refs: Sequence[CanonRef] = ()


def _numbers_for(refs: Sequence[CanonRef], assertion: CanonAssertion) -> list[int]:
    """断言 → 注入编号。库内行按 ``id`` 命中，本轮 overlay 按 ``pending:`` 复合键命中。

    两种键都试：compile_context 给 overlay 行的 source_id 拼的是
    ``pending:{subject}:{predicate}``（那些行没有库主键），只按 id 找会让本轮新事实
    永远引不出编号，于是「与上一章刚抽出的事实冲突」反而报不出来。
    """
    keys = {assertion.id, f"pending:{assertion.subject_key}:{assertion.predicate}"}
    return sorted({ref.number for ref in refs if ref.source_id in keys})


def _normalize_value(value: str) -> str:
    return _WHITESPACE.sub("", value or "").strip("。！!，,；;").lower()


def _is_falsy(value: str) -> bool:
    return _normalize_value(value) in _FALSY


def _is_truthy(value: str) -> bool:
    return _normalize_value(value) in _TRUTHY


def _values_agree(left: str, right: str) -> bool:
    """两个取值是否相容：完全相同、互为包含，或同为真/同为假。

    互为包含是刻意放宽：「黑发」与「黑」不该判成冲突，而「黑」与「白」仍会命中。
    放宽只发生在**同一谓词的值**上，不影响「证据必须逐字」那条硬线。
    """
    a, b = _normalize_value(left), _normalize_value(right)
    if not a or not b:
        return True
    if a == b or a in b or b in a:
        return True
    return (_is_falsy(a) and _is_falsy(b)) or (_is_truthy(a) and _is_truthy(b))


def _established_rows(snapshot: Sequence[CanonAssertion]) -> dict[tuple[str, str], CanonAssertion]:
    """(实体键, 谓词) → 最早确立的那条已确认断言（生死谓词除外）。

    取首条而非末条：冲突要指向「先立起来的那一条」，后写的区间覆盖是剧情推进的正常
    痕迹，拿它当被违反的事实会把每一次正常改写都报成 bug。
    """
    rows: dict[tuple[str, str], CanonAssertion] = {}
    for assertion in snapshot:
        if assertion.status != "confirmed" or assertion.predicate == _ALIVE_PREDICATE:
            continue
        rows.setdefault((assertion.subject_key, assertion.predicate), assertion)
    return rows


def _names_by_entity(gate_in: GateInput) -> dict[str, set[str]]:
    """实体键 → 可用姓名集合（本轮称谓候选 + 历史登记表）。

    没有姓名就无法在正文里定位这个人：``char:shenqing`` 这类键是拼音 slug，正文里
    不会出现它。取不到名字的死者计入 ``skipped["no_name"]``，不假装检查过。
    """
    names: dict[str, set[str]] = {}
    for alias_text, entity_key in gate_in.known_aliases.items():
        names.setdefault(entity_key, set()).add(alias_text)
    if gate_in.extraction is not None:
        for alias in gate_in.extraction.aliases:
            names.setdefault(alias.entityKey, set()).add(alias.aliasText)
    return {key: {name for name in values if name} for key, values in names.items()}


def _spanned(gate_in: GateInput, start: int, end: int, **fields: Any) -> Finding:
    """按 span 从原文取证据再构造 Finding——规则引擎的证据只能是原文本身。

    写成「先取切片再传参」而不是把 quote 交给调用方：任何一处手抖（误用掩码文本、
    误用候选里的复述）都会让 Finding 过不了自己的逐字校验，而这个构造点只有一条
    路径可走。
    """
    return Finding(evidenceQuote=gate_in.text[start:end], textStart=start, textEnd=end, **fields)


def check_length(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """章节字数越带（§9.1「章节字数越带」）。"""
    used = visible_chars(gate_in.text)
    low = int(rules.target_words * rules.min_ratio)
    high = int(rules.target_words * rules.max_ratio)
    if low <= used <= high:
        return [], []
    extreme = used < int(rules.target_words * rules.hard_min_ratio) or used > int(
        rules.target_words * rules.hard_max_ratio
    )
    short = used < low
    severity: FindingSeverity = "blocker" if used == 0 else ("major" if extreme else "minor")
    return (
        [
            Finding(
                code="length_out_of_band",
                # 只有空章才是 blocker：非空的越带只能整章重写，给 blocker 等于让
                # 「定向修补」去做整章重写，两条路径互相抵消。空章没有片段可指，
                # 放行策略据此起整章重写那一支（policy.decide_release），轮数用尽才冻结。
                severity=severity,
                checker="rule",
                explanation=f"第 {gate_in.chapter_no} 章 {used} 字，越出目标带 {low}-{high}。",
                fixInstruction=(
                    f"重写本章至 {rules.target_words} 字左右（允许带 {low}-{high}）："
                    + ("补足场景与细节。" if short else "压缩冗余描写。")
                ),
            )
        ],
        [],
    )


def check_forbidden_words(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """命中禁用词（§9.1 ``forbidden_words``）。

    引号内也算命中：违禁词是平台红线，出现在人物台词里一样过不了审。
    """
    findings: list[Finding] = []
    for word in rules.forbidden_words:
        if not word:
            continue
        position = gate_in.text.find(word)
        if position < 0:
            continue
        start, end = sentence_span(gate_in.text, position)
        findings.append(
            _spanned(
                gate_in,
                start,
                end,
                code="forbidden_word",
                severity="blocker",
                checker="rule",
                explanation=f"第 {gate_in.chapter_no} 章命中禁用词「{word}」。",
                fixInstruction=f"改写该句，去掉「{word}」，不改变句意。",
            )
        )
    return findings, []


def check_pov(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """叙述人称漂移（§9.1「人称/时态违反 style_profile」的人称一半）。

    只判「契约要求第三人称、叙述层出现第一人称代词」这一个方向：中文没有时态变位，
    「了/过/着」是体貌不是时态，时态漂移判不了（交语义裁判）；反过来要求第一人称时
    也无法可靠检出「他」，硬检就是把每段第三人称叙述都报成违规。

    零星命中记 ``minor``（口语、无引号的心理活动都会带「我」），累计到
    ``pov_major_hits`` 才认定整章换了视角，升 ``major`` 进台账。
    """
    style = gate_in.style
    if style is None or "第三人称" not in style.pov or not rules.narrator_ego:
        return [], []
    masked = mask_quotes(gate_in.text)
    pattern = re.compile("|".join(re.escape(marker) for marker in rules.narrator_ego))
    hits = [match.start() for match in pattern.finditer(masked)]
    if not hits:
        return [], []
    severity: FindingSeverity = "major" if len(hits) >= rules.pov_major_hits else "minor"
    findings = [
        _spanned(
            gate_in,
            *sentence_span(gate_in.text, position),
            code="style_drift",
            severity=severity,
            checker="rule",
            explanation=(
                f"文风契约要求「{style.pov}」，叙述层出现第一人称（本章共 {len(hits)} 处）。"
            ),
            fixInstruction="把这句叙述改回契约约定的视角；人物内心可用对话或引号内的想法表达。",
        )
        for position in hits[: rules.per_code_limit]
    ]
    return findings, []


def check_attribute_conflict(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """C1 属性漂移：本章新增事实与 as-of 区间内已确立的同一谓词相抵。

    只比对 ``confirmed`` 候选：``todo`` 是「未知即缺口」，登记缺口不是宣称事实，拿它
    去撞既有断言等于把机制③当成违规。生死谓词由 check_alive_conflicts 处理。
    """
    extraction = gate_in.extraction
    if extraction is None or not gate_in.snapshot:
        return [], []
    established = _established_rows(gate_in.snapshot)
    locator = _Locator(gate_in.text)
    findings: list[Finding] = []
    skipped: list[str] = []
    for candidate in extraction.assertions:
        if candidate.status != "confirmed" or candidate.predicate == _ALIVE_PREDICATE:
            continue
        if candidate.predicate in _MUTABLE_PREDICATES:
            continue
        old = established.get((candidate.subjectKey, candidate.predicate))
        if old is None or _values_agree(old.object_text, candidate.objectText):
            continue
        numbers = _numbers_for(gate_in.refs, old)
        if not numbers:
            skipped.append("no_ref")
            continue
        span = locator.locate(candidate.evidenceQuote)
        if span is None:
            # 证据落不回原文就没有可定位的冲突，计一条 skipped 而不是丢掉：
            # 「抽取侧按归一化空白收下、闸门侧按原文找不到」是两套口径打架的信号。
            skipped.append("no_quote")
            continue
        findings.append(
            _spanned(
                gate_in,
                *span,
                code="attribute_conflict",
                severity="blocker",
                checker="rule",
                canonRefs=numbers,
                explanation=(
                    f"{candidate.subjectKey} · {candidate.predicate} 已确立为"
                    f"「{old.object_text}」（第 "
                    f"{old.established_chapter or old.valid_from_chapter} 章起），"
                    f"本章写成「{candidate.objectText}」。"
                ),
                fixInstruction=(
                    f"改回既有设定：{old.restatement}；若剧情确实要它变化，"
                    "需在正文里显式交代变化的来由。"
                ),
            )
        )
    return findings, skipped


def _death_speaks(
    gate_in: GateInput, name: str, entity_key: str, dead: CanonAssertion, position: int
) -> Finding:
    numbers = _numbers_for(gate_in.refs, dead)
    return _spanned(
        gate_in,
        *sentence_span(gate_in.text, position),
        code="death_speaks",
        severity="blocker",
        checker="rule",
        canonRefs=numbers,
        explanation=(
            f"「{name}」（{entity_key}）在第 "
            f"{dead.established_chapter or dead.valid_from_chapter} 章起已死亡，"
            "本章让其发言。"
        ),
        fixInstruction="去掉该人物的发言，改为他人转述、回忆或遗言文本，不要在场景里让死者直接开口。",
    )


def check_alive_conflicts(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """C2 生死：死者在本章发言，或被重新记为存活。

    两条都从「as-of 快照里 ``is_alive`` 为假」出发：发言看文本（姓名与发言动词同现
    才算，只出现名字不算说话——旁人提到死者是很正常的写法），存活状态看本章候选。
    引号内的名字不算发言：那通常是旁人转述死者生前之言。
    """
    dead = {
        assertion.subject_key: assertion
        for assertion in gate_in.snapshot
        if assertion.predicate == _ALIVE_PREDICATE
        and assertion.status == "confirmed"
        and _is_falsy(assertion.object_text)
    }
    if not dead:
        return [], []
    names = _names_by_entity(gate_in)
    masked = mask_quotes(gate_in.text)
    findings: list[Finding] = []
    skipped: list[str] = []
    for entity_key, assertion in sorted(dead.items()):
        if not _numbers_for(gate_in.refs, assertion):
            skipped.append("no_ref")
            continue
        if entity_key not in names:
            skipped.append("no_name")
            continue
        for name in sorted(names[entity_key], key=len, reverse=True):
            position = _speech_hit(masked, name, rules.speech_window)
            if position is None:
                continue
            findings.append(_death_speaks(gate_in, name, entity_key, assertion, position))
            break
    extraction = gate_in.extraction
    if extraction is None:
        return findings, skipped
    locator = _Locator(gate_in.text)
    for candidate in extraction.assertions:
        if (
            candidate.predicate != _ALIVE_PREDICATE
            or candidate.status != "confirmed"
            or not _is_truthy(candidate.objectText)
            or candidate.subjectKey not in dead
        ):
            continue
        span = locator.locate(candidate.evidenceQuote)
        if span is None:
            skipped.append("no_quote")
            continue
        findings.append(
            _spanned(
                gate_in,
                *span,
                code="resurrection",
                severity="blocker",
                checker="rule",
                canonRefs=_numbers_for(gate_in.refs, dead[candidate.subjectKey]),
                explanation=f"{candidate.subjectKey} 已登记为死亡，本章又将其记为存活。",
                fixInstruction="删除该状态变化，或在正文里写清复活的代价与依据。",
            )
        )
    for change in extraction.stateChanges:
        if change.isAlive is not True or change.charKey not in dead:
            continue
        findings.append(
            Finding(
                code="resurrection",
                severity="blocker",
                checker="rule",
                canonRefs=_numbers_for(gate_in.refs, dead[change.charKey]),
                explanation=f"{change.charKey} 本章结束时的状态快照又标记为存活。",
                fixInstruction="核对生死：确需复活则补写依据，否则把该人物的 isAlive 改回死亡。",
            )
        )
    return findings, skipped


def _speech_hit(masked: str, name: str, window: int) -> int | None:
    """返回「``name`` 与发言动词同现」的首个位置，找不到返回 ``None``。"""
    position = masked.find(name)
    while position >= 0:
        surround = masked[max(0, position - window) : position + len(name) + window]
        if any(verb in surround for verb in _SPEECH_VERBS):
            return position
        position = masked.find(name, position + 1)
    return None


def check_alias_drift(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """C3 称谓：一个称谓在本轮候选或历史登记里指向了多个实体。

    反向（一个实体多个称谓）是正常写法，不报。严重度取 ``major`` 而非 ``blocker``：
    「沈姑娘」到底指谁不是文本能自证的，机器改哪一处都可能改错，必须进台账等人裁定。
    """
    merged: dict[str, set[str]] = {}
    for alias_text, entity_key in gate_in.known_aliases.items():
        merged.setdefault(alias_text, set()).add(entity_key)
    if gate_in.extraction is not None:
        for alias in gate_in.extraction.aliases:
            merged.setdefault(alias.aliasText, set()).add(alias.entityKey)
    masked = mask_quotes(gate_in.text)
    findings: list[Finding] = []
    for alias_text in sorted(merged):
        owners = merged[alias_text]
        if len(owners) < 2:
            continue
        detail = f"称谓「{alias_text}」同时指向 {'、'.join(sorted(owners))}。"
        position = masked.find(alias_text)
        if position < 0:
            # 登记了冲突称谓但本章没写过它：冲突属正典层而非文本层，整章级记录。
            findings.append(
                Finding(
                    code="alias_drift",
                    severity="major",
                    checker="rule",
                    explanation=detail,
                    fixInstruction="在正典里为该称谓指定唯一实体，或给两个实体分别改用其他称谓。",
                )
            )
            continue
        findings.append(
            _spanned(
                gate_in,
                *sentence_span(gate_in.text, position),
                code="alias_drift",
                severity="major",
                checker="rule",
                explanation=detail,
                fixInstruction="在本章把该称谓换成具体实体名，避免同一称谓被读成两个人。",
            )
        )
    return findings, []


def check_citations(gate_in: GateInput, rules: GateRules) -> RuleResult:
    """正文引用了未注入的编号（§9.1「本章声明回收的 foreshadow_id 不存在」）。

    本规则是「注入即编号」在**文本侧**的落点：模型只该引用 ``[canon#N]`` /
    ``[fsh#N]`` 里真实存在过的编号，凭空造一个就是在认领一条不存在的设定。判据是
    refs 全集而非「实际注入成功的行」——被预算裁掉的编号仍是合法编号，只是模型当时
    没看见，报成冲突反而误导裁定。

    提示词不要求写作者在正文里标注回收编号（回收声明在场景卡的 ``payoffs`` 里，
    由 :func:`check_plan_payoffs` 校验），因此本规则只在模型自己模仿注入格式时命中；
    它是那条改动的安全网，不是死代码。
    """
    by_kind: dict[str, set[int]] = {"canon": set(), "foreshadow": set()}
    for ref in gate_in.refs:
        by_kind.setdefault(ref.kind, set()).add(ref.number)
    findings: list[Finding] = []
    for match in _CITATION.finditer(gate_in.text):
        prefix, number = match.group(1), int(match.group(2))
        kind = "foreshadow" if prefix == "fsh" else "canon"
        if number in by_kind[kind]:
            continue
        findings.append(
            _spanned(
                gate_in,
                *sentence_span(gate_in.text, match.start()),
                code="foreshadow_missing" if kind == "foreshadow" else "unknown_ref",
                # 伏笔编号不存在意味着本章「收了」一条从未埋下的线，落进台账就是悬空
                # 引用，所以 blocker；设定编号不存在多半只是文里带了一句编号样式，
                # 先 major 进台账，别为格式问题烧修补轮次。
                severity="blocker" if kind == "foreshadow" else "major",
                checker="rule",
                explanation=f"正文引用了未注入的 [{prefix}#{number}]。",
                fixInstruction="删去该编号引用，或把它改为上方清单里真实存在的编号。",
            )
        )
    return findings, []


_RULES = (
    check_length,
    check_forbidden_words,
    check_pov,
    check_attribute_conflict,
    check_alive_conflicts,
    check_alias_drift,
    check_citations,
)


# ---------- 计划闸门（§9.1 的计划侧：在正文写下第一个字之前判掉「必然冲突的计划」） ----------


def _plan_span(plan_in: PlanInput, needle: str) -> tuple[int, int] | None:
    """在卡文本里定位一个键/编号，返回它所在**整行**的区间。

    取整行而不是只取那个键：``fixInstruction`` 要落到「改这一行」，而证据只截一个
    ``char:x`` 的话，作者在工作台看到的片段没有上下文，等于又要他去猜。
    """
    if not needle:
        return None
    position = plan_in.card_text.find(needle)
    if position < 0:
        return None
    return sentence_span(plan_in.card_text, position)


def _plan_spanned(plan_in: PlanInput, start: int, end: int, **fields: Any) -> Finding:
    """按计划文本取证据再构造 Finding（与 :func:`_spanned` 同一条硬线，只是坐标系不同）。"""
    return Finding(
        evidenceQuote=plan_in.card_text[start:end], textStart=start, textEnd=end, **fields
    )


def _plan_keys(plan_in: PlanInput) -> set[str]:
    """计划里声明过的全部实体键：entities ∪ 各场景 present ∪ locationKey。

    ``newEntities`` 也算「声明过」——它是作者可见的待补清单，不是违规；
    真正的违规是**没声明就用了**（出现在 present 里却既不在 entities 也不在待补清单）。
    """
    keys = set(plan_in.card.entities)
    keys.update(plan_in.card.newEntities)
    for scene in plan_in.card.scenes:
        keys.update(scene.present)
        if scene.locationKey:
            keys.add(scene.locationKey)
    return keys


def _registered_keys(plan_in: PlanInput) -> set[str]:
    """as-of 快照里已经存在的实体键（含圣经行，见 context.compile_context 的 world）。"""
    return {assertion.subject_key for assertion in plan_in.snapshot}


def check_plan_entities(plan_in: PlanInput, rules: GateRules) -> RuleResult:
    """C3 计划侧：场景用到了一条已登记事实都指不出的实体。

    取 ``major`` 而非 ``blocker``：「这个人是新角色」与「这个 key 打错了」机器分不开，
    而前者是合法写法（正文允许出现新人，只是他此刻还没有任何设定）。所以处置是
    「把它显式写进 newEntities，或换回登记过的 key」，由重规划一轮解决。
    """
    registered = _registered_keys(plan_in)
    if not registered:
        # 一书一条事实都没有（圣经与抽取都还没产出）：此时「未登记」没有判据，
        # 报出来就是把开篇每一章都判成违规，宁可跳过并记账。
        return [], ["no_registry"]
    findings: list[Finding] = []
    for key in sorted(_plan_keys(plan_in) - registered):
        if key in set(plan_in.card.newEntities):
            continue
        span = _plan_span(plan_in, key)
        if span is None:
            continue
        findings.append(
            _plan_spanned(
                plan_in,
                *span,
                code="unregistered_entity",
                severity="major",
                checker="rule",
                explanation=f"第 {plan_in.chapter_no} 章计划使用了未登记实体「{key}」。",
                fixInstruction=(
                    f"把「{key}」换回已登记实体，或显式写进 newEntities 交给作者补设定；"
                    "不要在计划里默认一个没有出处的人物。"
                ),
            )
        )
    return findings, []


def check_plan_deaths(plan_in: PlanInput, rules: GateRules) -> RuleResult:
    """C2 计划侧：把已死人物排进了在场名单。

    这一条正是「计划闸门存在的理由」：正文里死者发言要烧一整章的 token 才发现，
    而在这里只需改一行 present。严重度取 blocker——在场名单是硬约束，
    照卡写出来的正文必然违规，没有「作者其实想让他说话」的第三种解释。
    """
    dead = {
        assertion.subject_key: assertion
        for assertion in plan_in.snapshot
        if assertion.predicate == _ALIVE_PREDICATE
        and assertion.status == "confirmed"
        and _is_falsy(assertion.object_text)
    }
    findings: list[Finding] = []
    skipped: list[str] = []
    present = {key for scene in plan_in.card.scenes for key in scene.present}
    for entity_key in sorted(present & set(dead)):
        assertion = dead[entity_key]
        numbers = _numbers_for(plan_in.refs, assertion)
        if not numbers:
            skipped.append("no_ref")
            continue
        span = _plan_span(plan_in, entity_key)
        if span is None:
            skipped.append("no_line")
            continue
        findings.append(
            _plan_spanned(
                plan_in,
                *span,
                code="death_speaks",
                severity="blocker",
                checker="rule",
                canonRefs=numbers,
                explanation=(
                    f"第 {plan_in.chapter_no} 章计划让 {entity_key} 在场，但它自第 "
                    f"{assertion.established_chapter or assertion.valid_from_chapter} 章起已死亡。"
                ),
                fixInstruction=(
                    "把该人物从在场名单里去掉，改为回忆、遗言文本或他人转述；"
                    "确需复活，先在正典里给它一条有交代的复活事实。"
                ),
            )
        )
    return findings, skipped


def check_plan_payoffs(plan_in: PlanInput, rules: GateRules) -> RuleResult:
    """C6 计划侧：本章声明回收的伏笔编号不在未收清单里（§5.3）。

    判据是 refs 里的 ``foreshadow`` 全集而非「实际进注入块的行」，与
    :func:`check_citations` 同口径：被预算裁掉的编号仍是合法编号。
    blocker 的理由与正文侧一致——收一条没埋过的线，落进台账就是悬空引用。
    """
    open_numbers = {ref.number for ref in plan_in.refs if ref.kind == "foreshadow"}
    findings: list[Finding] = []
    for number in plan_in.card.payoffs:
        if number in open_numbers:
            continue
        token = f"[fsh#{number}]"
        span = _plan_span(plan_in, token)
        if span is None:
            # 编号来自结构化字段，卡文本里理应有；找不到时退回整章级记录，
            # 不许静默丢弃（那是 §8-⑧ 禁的降级）。
            findings.append(
                Finding(
                    code="foreshadow_missing",
                    severity="blocker",
                    checker="rule",
                    explanation=f"第 {plan_in.chapter_no} 章计划回收 [{number}]，但它不在未收清单里。",
                    fixInstruction="删去该回收声明，或改为清单里真实存在的编号。",
                )
            )
            continue
        findings.append(
            _plan_spanned(
                plan_in,
                *span,
                code="foreshadow_missing",
                severity="blocker",
                checker="rule",
                explanation=f"第 {plan_in.chapter_no} 章计划回收 {token}，但它不在未收清单里。",
                fixInstruction="删去该回收声明，或改为清单里真实存在的编号。",
            )
        )
    return findings, []


def check_plan_length(plan_in: PlanInput, rules: GateRules) -> RuleResult:
    """C6 计划侧：卡的字数带容不下本章的目标字数。

    只看「带与目标是否相交」，不看目标本身合不合理（那是装配参数的事）。
    取 ``minor``：字数带偏了不违反任何已确立事实，把它送进重规划回路只是白烧一轮，
    正文侧的 :func:`check_length` 才是真正管住字数的那道闸门。
    """
    low, high = plan_in.card.wordsLow, plan_in.card.wordsHigh
    if low <= rules.target_words <= high:
        return [], []
    explanation = (
        f"第 {plan_in.chapter_no} 章计划的字数带 {low}-{high} 容不下目标 {rules.target_words} 字。"
    )
    fix = f"把字数带改为覆盖 {rules.target_words} 的区间（建议 {low}-{high} 上下放扩）。"
    span = _plan_span(plan_in, f"{low}-{high}")
    if span is None:
        # 带值来自结构化字段，卡文本里理应有；找不到时退回整章级记录，不许静默丢弃。
        return (
            [
                Finding(
                    code="length_out_of_band",
                    severity="minor",
                    checker="rule",
                    explanation=explanation,
                    fixInstruction=fix,
                )
            ],
            [],
        )
    return (
        [
            _plan_spanned(
                plan_in,
                *span,
                code="length_out_of_band",
                severity="minor",
                checker="rule",
                explanation=explanation,
                fixInstruction=fix,
            )
        ],
        [],
    )


_PLAN_RULES = (
    check_plan_deaths,
    check_plan_entities,
    check_plan_payoffs,
    check_plan_length,
)


def run_plan_rules(plan_in: PlanInput, rules: GateRules | None = None) -> GateReport:
    """跑完计划侧确定性规则：与正文闸门同一个验收口、同一份取舍口径。

    共用 :func:`validate_findings` 与 :func:`_cap_per_code` 是刻意的：两道闸门产的是
    同一种记录（同一套编码、同一份逐字证据要求），分两套校验就会有两套松紧，
    而「计划闸门的证据标准更松」正是让假冲突混进台账的入口。
    坐标系统一用 ``card_text``——台账里的 span 指向那张卡，不指向还没写出来的正文。
    """
    config = rules or GateRules()
    findings: list[Finding] = []
    skipped: list[str] = []
    for rule in _PLAN_RULES:
        produced, reasons = rule(plan_in, config)
        findings.extend(produced)
        skipped.extend(reasons)
    kept, dropped = validate_findings(findings, plan_in.card_text)
    return GateReport(
        findings=_cap_per_code(kept, config.per_code_limit),
        dropped=dropped,
        skipped=dict(Counter(skipped)),
        words=visible_chars(plan_in.card_text),
    )


def validate_findings(findings: Iterable[Finding], text: str) -> tuple[list[Finding], int]:
    """§9.2 的落地校验：编码已知、证据与 span 自洽、该引事实的必须引。

    作废条件（任一）：
    - 编码不在 ``FindingCode`` 全集内（裁判自造编码不许进台账）；
    - span 与证据只有一边存在，或区间越界／起终点颠倒；
    - 证据与 ``text[start:end]`` 去空白后不相等（编造证据的一眼假防线）；
    - ``checker == 'judge'`` 却没引任何 canon 编号（裁判不许无据报告）；
    - 规则命中了「与既有事实相抵」这类冲突却引不出编号。
    """
    kept: list[Finding] = []
    dropped = 0
    for finding in findings:
        if finding.code not in _KNOWN_CODES:
            dropped += 1
            continue
        start, end = finding.textStart, finding.textEnd
        has_span = start is not None and end is not None
        if has_span != bool(finding.evidenceQuote):
            dropped += 1
            continue
        if has_span and not evidence_matches_span(finding.evidenceQuote, text, start, end):
            dropped += 1
            continue
        needs_ref = finding.checker == "judge" or finding.code in _REF_REQUIRED_CODES
        if needs_ref and not finding.canonRefs:
            dropped += 1
            continue
        kept.append(finding)
    return kept, dropped


def _sort_key(finding: Finding) -> tuple[int, str, int]:
    """严重度优先，其次编码，最后 span 起点。

    span 起点用 -1 表示「整章级」，让它排在同严重度同编码的片段级记录之前：
    没有位置的记录覆盖范围更大，读台账的人要先看到它。
    """
    start = finding.textStart if finding.textStart is not None else -1
    return (_SEVERITY_ORDER[finding.severity], finding.code, start)


def _cap_per_code(findings: Sequence[Finding], limit: int) -> list[Finding]:
    """同一编码只留前 ``limit`` 条，且按严重度优先留。

    排序键里带上起点，是为了让「本章第一处冲突」而不是「最后一次命中」进台账——
    作者顺着 span 跳过去时，最想看到的是问题的起始位置。
    """
    buckets: dict[str, list[Finding]] = {}
    for finding in sorted(findings, key=_sort_key):
        bucket = buckets.setdefault(finding.code, [])
        if len(bucket) < limit:
            bucket.append(finding)
    return sorted((finding for bucket in buckets.values() for finding in bucket), key=_sort_key)


def run_rules(gate_in: GateInput, rules: GateRules | None = None) -> GateReport:
    """跑完全部确定性规则，再统一过验收口。

    先收齐再校验（而非逐条校验）：``per_code_limit`` 要在证据合规之后按严重度取舍，
    否则一条编造证据的记录会挤掉真冲突的位置。
    """
    config = rules or GateRules()
    findings: list[Finding] = []
    skipped: list[str] = []
    for rule in _RULES:
        produced, reasons = rule(gate_in, config)
        findings.extend(produced)
        skipped.extend(reasons)
    kept, dropped = validate_findings(findings, gate_in.text)
    return GateReport(
        findings=_cap_per_code(kept, config.per_code_limit),
        dropped=dropped,
        skipped=dict(Counter(skipped)),
        words=visible_chars(gate_in.text),
    )


__all__ = [
    "GateInput",
    "GateReport",
    "GateRules",
    "PlanInput",
    "check_alive_conflicts",
    "check_alias_drift",
    "check_attribute_conflict",
    "check_citations",
    "check_forbidden_words",
    "check_length",
    "check_plan_deaths",
    "check_plan_entities",
    "check_plan_length",
    "check_plan_payoffs",
    "check_pov",
    "evidence_matches_span",
    "evidence_verbatim",
    "locate_quote",
    "mask_quotes",
    "run_plan_rules",
    "run_rules",
    "sentence_span",
    "validate_findings",
    "visible_chars",
]
