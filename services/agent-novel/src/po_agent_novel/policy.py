"""放行策略（PRD §9.3）：把闸门产物映射为「放行 / 修补 / 冻结」三态。

纯函数、零 LLM、零网络——判据必须能脱离模型逐条单测，否则「闸门判得准不准」与
「放行处置对不对」两件事的回归会在同一次改动里搅在一起。

三态与严重度的对应：

- ``blocker``：本章事实不许 commit。能定位到片段的走**定向修补**（只喂
  ``[span ± 上下文] + fixInstruction + 相关 canon``，返回片段并原位回拼），
  定位不了的（整章级：空章、字数严重失控）走**整章重写**；两轮仍不过即**冻结**转人工。
  两种修补分开是因为成本与漂移：整章重写会把没问题的段落一起洗掉，而 §12 的黄金集
  要统计的正是「闸门指出的那一处有没有被改掉」。
- ``major``：允许 commit，但与之相抵的那条**新候选断言**降级为 ``disputed``。
  只降新事实、不动已确立断言（那是作者确认过的既有设定），因为「先注入再纠错」的
  代价是后面每一章都按错的设定写；被降级的行读侧不注入（``load_snapshot`` 只给
  confirmed），等工作台裁定。
- ``minor``：只记录（供 §12 评测与风格调优）。

``judge_failed`` 单独占一格：它既不是「查出冲突」也不是「没有冲突」，而是**不可判定**。
没有 ``fixInstruction`` 可喂修补，也不能当绿灯放行（§8-⑨），所以直接冻结。

计划闸门（§7 的 gate_plan）走 :func:`decide_plan_release`，三态是
``pass / replan / escalate``：判据把 major 也算进「必须处理」（计划里一个未登记的 key
放过去就是「正文凭空多出没有设定的人」），轮数用尽或裁判没跑成都**升级给作者**而不是
冻结——这里冻结的是「还没写的一章」，用户一句「照这张卡写」就能放行，成本不对称。
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Literal

from po_agent_novel.context import CanonRef
from po_agent_novel.gates import GateInput
from po_agent_novel.schemas import ChapterExtraction, Finding

ReleaseAction = Literal["pass", "patch", "rewrite", "freeze"]
PlanReleaseAction = Literal["pass", "replan", "escalate"]

# 本轮候选在 L1 编号表里的 source_id 前缀（见 context.compile_context）：
# 它没有库主键，只能按 ``pending:{subject}:{predicate}`` 反解出冲突对象。
_PENDING_PREFIX = "pending:"


@dataclass(frozen=True, slots=True)
class ReleasePolicy:
    """放门口径（装配层可按书覆盖）。

    :param max_repairs: 一章最多修补几轮，用尽仍有 blocker 即冻结转人工（§9.3 的「2 轮」）
    :param max_patches: 一轮最多打几个片段。同一章十几处同源漂移会在第一轮就把
        整章洗成另一篇稿子，而闸门要的是「那一处改掉没有」——留到下一轮重检更可信
    :param patch_context_chars: 片段两侧各带多少上下文进提示词。太短会导致改出来的
        句子接不上前后文，太长等于整章重写
    :param max_plan_repairs: 一张场景卡最多重排几轮。与 ``max_repairs`` 分开计是必要的：
        重排只改十几行计划，代价与「改一千二百字正文」不在一个量级，
        合并计数会让计划问题挤掉正文修补的轮次预算
    """

    max_repairs: int = 2
    max_patches: int = 3
    patch_context_chars: int = 160
    max_plan_repairs: int = 2


@dataclass(frozen=True, slots=True)
class Release:
    """一次放行判定。

    :param action: 三态加一格 ``rewrite``（整章级 blocker 的修补形态）
    :param blockers: 触发判定的 blocker（``patch``/``rewrite`` 的输入，也是冻结时给人
        看的清单）
    :param disputed: 与 major 相抵的 ``(subject_key, predicate)``，入库前据此降级候选
    :param unreviewed: 语义裁判没跑成——**这章没有经过完整审查**，与「审查通过」必须
        在事件、台账和回执里都区分得开
    :param reason: 一句话结论，直接进 THINKING 事件与归档回执
    """

    action: ReleaseAction = "pass"
    blockers: tuple[Finding, ...] = ()
    disputed: frozenset[tuple[str, str]] = frozenset()
    unreviewed: bool = False
    reason: str = ""

    @property
    def blocking(self) -> bool:
        return self.action in ("patch", "rewrite", "freeze")


def _has_span(finding: Finding) -> bool:
    return (
        finding.textStart is not None
        and finding.textEnd is not None
        and finding.textStart < finding.textEnd
    )


def conflicting_keys(gate_in: GateInput, majors: Sequence[Finding]) -> frozenset[tuple[str, str]]:
    """major 的 ``canonRefs`` → 冲突所在的 ``(实体键, 谓词)``。

    编号是「模型当时看到的那一份」（``[canon#N]``），所以解析只能在注入表里做，
    不能拿编号去查库——查到的可能是另一行。两种 source_id 都要认：库内行按 ``id``
    反查快照，本轮候选按 ``pending:`` 前缀反解。
    """
    wanted = {number for finding in majors for number in finding.canonRefs}
    if not wanted:
        return frozenset()
    by_number = {ref.number: ref for ref in gate_in.refs}
    by_id = {assertion.id: assertion for assertion in gate_in.snapshot if assertion.id}
    keys: set[tuple[str, str]] = set()
    for number in sorted(wanted):
        ref = by_number.get(number)
        if ref is None or ref.kind != "canon":
            continue
        if ref.source_id.startswith(_PENDING_PREFIX):
            # rpartition 而非 split：实体键自身带冒号（char:linwan），谓词不带。
            subject, _, predicate = ref.source_id[len(_PENDING_PREFIX) :].rpartition(":")
            if subject and predicate:
                keys.add((subject, predicate))
            continue
        assertion = by_id.get(ref.source_id)
        if assertion is not None:
            keys.add((assertion.subject_key, assertion.predicate))
    return frozenset(keys)


def apply_disputed(extraction: ChapterExtraction, keys: frozenset[tuple[str, str]]) -> tuple[ChapterExtraction, int]:
    """把与 major 相抵的本章候选降为 ``disputed``，返回（新候选, 降级条数）。

    只动 ``confirmed``：``todo`` 本来就是缺口，不注入也不参与比对。
    刻意就地改写 ``entry["extraction"]`` 而非等到写库那一刻——L1 的 overlay 视图与
    入库载荷必须同源，否则「本轮后面几章照样注入这条被怀疑的事实」，等归档才降级就晚了。
    """
    if not keys:
        return extraction, 0
    updated: list[Finding] = []
    changed = 0
    for item in extraction.assertions:
        if item.status == "confirmed" and (item.subjectKey, item.predicate) in keys:
            updated.append(item.model_copy(update={"status": "disputed"}))
            changed += 1
        else:
            updated.append(item)
    if not changed:
        return extraction, 0
    return extraction.model_copy(update={"assertions": updated}), changed


@dataclass(frozen=True, slots=True)
class PatchTarget:
    """一处定向修补：片段、上下文、指令与相关设定。"""

    start: int
    end: int
    target: str
    before: str
    after: str
    instruction: str
    explanation: str
    canon_lines: tuple[str, ...] = ()


def patch_plan(
    text: str, blockers: Sequence[Finding], refs: Sequence[CanonRef], policy: ReleasePolicy
) -> tuple[list[PatchTarget], int]:
    """blocker → 修补清单（按起点**倒序**），返回（清单, 被丢弃条数）。

    倒序回拼是为了让偏移不失效：每打一个补丁，它之后的坐标都会整体平移。
    超出 ``max_patches`` 的留在下一轮——闸门每轮都会重跑，漏掉的会再次命中，
    比一次改十几处再无从归因要好。
    """
    by_number = {ref.number: ref for ref in refs}
    usable = [finding for finding in blockers if _has_span(finding)]
    overflow = len(usable) - policy.max_patches
    ordered = sorted(usable, key=lambda finding: finding.textStart or 0, reverse=True)[
        : policy.max_patches
    ]
    plan: list[PatchTarget] = []
    for finding in ordered:
        start, end = finding.textStart or 0, finding.textEnd or 0
        plan.append(
            PatchTarget(
                start=start,
                end=end,
                target=text[start:end],
                before=text[max(0, start - policy.patch_context_chars) : start],
                after=text[end : end + policy.patch_context_chars],
                instruction=finding.fixInstruction or finding.explanation,
                explanation=finding.explanation,
                canon_lines=tuple(
                    f"[{'fsh' if by_number[n].kind == 'foreshadow' else 'canon'}#{n}] "
                    f"{by_number[n].text}"
                    for n in sorted(set(finding.canonRefs))
                    if n in by_number
                ),
            )
        )
    return plan, max(0, overflow)


def splice_patch(text: str, target: PatchTarget, fragment: str) -> str | None:
    """把模型返回的片段原位回拼；不可信时返回 ``None``（调用方记数，不静默接受）。

    三条拒收口径都指向同一个失败模式——模型「顺手」把整章重写了一遍：
    空片段、与原文一致（等于没改）、以及长度远超片段本身。第三种最危险，
    因为它会静默通过并把没问题的段落一起换掉。
    """
    cleaned = fragment.strip()
    if not cleaned or cleaned == target.target:
        return None
    limit = max(len(target.target) * 3, 60) + 40
    if len(cleaned) > limit:
        return None
    return text[: target.start] + cleaned + text[target.end :]


def rewrite_feedback(blockers: Sequence[Finding]) -> str:
    """整章级 blocker → 审稿意见文本（喂给整章重写）。"""
    lines = [
        f"- {finding.explanation or finding.code}"
        + (f"：{finding.fixInstruction}" if finding.fixInstruction else "")
        for finding in blockers
    ]
    return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class PlanRelease:
    """一次计划放行判定（§7 的 gate_plan 出口）。

    :param action: ``pass`` 放行去写正文 / ``replan`` 回 plan_scene 重排 /
        ``escalate`` 交作者拍板（图内 interrupt）
    :param blockers: 触发判定的 blocker+major（replan 的意见来源，也是升级时给人看的清单）。
        与正文侧不同，这里把 major 也算进「必须处理」：计划里一个未登记的 key
        不值得烧一轮正文修补，但**必须**在卡上说清楚——它是 newEntities 少填了一格，
        放过去就会变成「正文凭空多出一个没有设定的人」
    :param unreviewed: 计划裁判没跑成——这张卡**没有经过完整审查**，与「审查通过」
        必须在事件与归档卡片上区分得开（§8-⑨）
    :param reason: 一句话结论，直接进 THINKING 事件与 interrupt 卡片
    """

    action: PlanReleaseAction = "pass"
    blockers: tuple[Finding, ...] = ()
    unreviewed: bool = False
    reason: str = ""

    @property
    def blocking(self) -> bool:
        return self.action in ("replan", "escalate")


def decide_plan_release(
    findings: Sequence[Finding],
    *,
    judge_failed: bool,
    attempts: int,
    policy: ReleasePolicy | None = None,
) -> PlanRelease:
    """计划闸门产物 → 三态处置。

    判据只看 blocker/major（``minor`` 一律只记录）：场景卡是「还没花 token 的意图」，
    为一条字数带偏了的重排一轮，换来的收益抵不上多一轮 plan_scene + 裁判的开销。

    两条与正文侧刻意相反的取向，都是「成本不对称」的结果：
    - 裁判没跑成 → **escalate** 而不是 freeze：这里冻结的是「计划」，用户一句
      「照这张卡写」就能放行；而正文侧的冻结作废的是已写成的稿子，没有轻处置可言；
    - 轮数用尽 → **escalate** 而不是继续硬拦：一张反复改不平的卡通常是设定本身有洞
      （世界规则互相矛盾），继续自动重排只会把卡越改越绕，该由作者裁定而不是机器再猜一轮。
    """
    config = policy or ReleasePolicy()
    hard = tuple(
        finding for finding in findings if finding.severity in ("blocker", "major")
    )
    if judge_failed:
        return PlanRelease(
            action="escalate",
            blockers=hard,
            unreviewed=True,
            reason="计划裁判未完成，这张卡的冲突不可判定",
        )
    if not hard:
        return PlanRelease(action="pass", blockers=())
    if attempts >= config.max_plan_repairs:
        return PlanRelease(
            action="escalate",
            blockers=hard,
            reason=f"重排 {attempts} 轮后仍有 {len(hard)} 条计划冲突",
        )
    return PlanRelease(
        action="replan",
        blockers=hard,
        reason=f"{len(hard)} 条计划冲突 → 回炉重排（第 {attempts + 1} 轮）",
    )


def decide_release(
    gate_in: GateInput,
    findings: Sequence[Finding],
    *,
    judge_failed: bool,
    repairs: int,
    policy: ReleasePolicy | None = None,
) -> Release:
    """一次放行判定。

    :param findings: 双闸门**合并后**的 Finding（与入库台账同一份，避免「按 A 判定、
        按 B 记账」）
    :param repairs: 本章已用修补轮数
    """
    config = policy or ReleasePolicy()
    blockers = tuple(finding for finding in findings if finding.severity == "blocker")
    disputed = conflicting_keys(gate_in, [finding for finding in findings if finding.severity == "major"])
    if judge_failed:
        return Release(
            action="freeze",
            blockers=blockers,
            disputed=disputed,
            unreviewed=True,
            reason="语义裁判未完成，本章冲突不可判定",
        )
    if not blockers:
        return Release(action="pass", disputed=disputed)
    if repairs >= config.max_repairs:
        return Release(
            action="freeze",
            blockers=blockers,
            disputed=disputed,
            reason=f"修补 {repairs} 轮后仍有 {len(blockers)} 条 blocker",
        )
    action: ReleaseAction = "patch" if all(_has_span(finding) for finding in blockers) else "rewrite"
    return Release(
        action=action,
        blockers=blockers,
        disputed=disputed,
        reason=f"{len(blockers)} 条 blocker → {'定向修补' if action == 'patch' else '整章重写'}",
    )


__all__ = [
    "PatchTarget",
    "PlanRelease",
    "PlanReleaseAction",
    "Release",
    "ReleaseAction",
    "ReleasePolicy",
    "apply_disputed",
    "conflicting_keys",
    "decide_plan_release",
    "decide_release",
    "patch_plan",
    "rewrite_feedback",
    "splice_patch",
]
