"""小说创作子图（PRD §7 的目标拓扑）。

主干：conceive → worldbuild → outline → plan_scene ⇄ gate_plan → write → extract
→ gate_text ⇄ revise → commit_and_next →（下一章 plan_scene ｜ archive）。
三条回环各判一件事且互不缠绕：

- **计划回环**（plan_scene ⇄ gate_plan）判「这张卡照写会不会报废」，出口是
  放行 / 重排 / 交作者拍板；
- **正文回环**（gate_text ⇄ revise ⇄ extract）判「这一处冲突改掉没有」（闸门客观命中，
  旧版由 reflect 自评的「这稿好不好」已按 §8-⑨ 废除）；
- **章节推进**（commit_and_next）判「全书写完没有」。

「先计划再动笔」是这条拓扑存在的理由：正文一旦写出，在场名单、要收的伏笔、用到的实体
就全被既成事实绑住了，那时才发现「让已死的人开口」要烧一整章重写的 token；
而计划只有十几行，改它几乎免费——所以计划闸门把 major 也算进必须处理（policy 里
登记了这条与正文侧刻意相反的取向）。

领域状态全部放在 ``artifacts["novel"]`` 命名空间（supervisor 不解释），
子图状态 schema 直接复用 CoreState——禁止向 CoreState 添加领域字段。

章节生命周期（``index`` 与 ``chapters`` 的关系是最容易写错的一处）：
``index`` 是 0 基的**正在写**章号，``chapters`` 只收已定稿章，故写第 N 章时
``len(chapters) == N - 1 == index``。draft（当前稿）在 commit_and_next 之前**不进**
chapters，所以 extract/gate_text/revise 三段一律读 ``ns["draft"]``、章号取
``index + 1``——它们跑在定稿之前，早期版本那种「``index - 1`` 回看 ``chapters``」
的口径会随定稿时机一起失效。

归档前 ``interrupt`` 挂起等待用户确认，确认后经 NovelStore 写入成稿、再按章节 id 把
extract 攒下的候选增量连同**书级圣经**一起交给 CanonStore（正典层）。
所有写库都排布在 interrupt 之后，且带幂等键：resume 会让 archive 节点从头重放，
写侧不幂等就会把正典写成双份。gate_plan 的升级确认点同理，只是它重放的是
「规则 + 裁判」这两段只读判定（没有写库，代价是一次判定重跑，不是双份记录）。

节点进度经 ``get_stream_writer`` 发布 thinking / plan 领域事件，
由 AgentRunner 的 custom 流翻译透传。

分阶段模型：节点在**装配期**按 ``NODE_MODEL_ROLES`` 声明的角色从 ``stage_models`` 取
模型——构思、圣经、大纲、场景卡与抽取用规划脑（plan），正文与重写用写作脑（write），
两道闸门的裁判与归档抽取用审稿脑（judge）。三者可以是同一个模型实例（单模型部署），
也可以各配各的（见 agent-core 的 ``AGENT_CORE_LLM_ROLES__*``）。
**计划闸门刻意与 write 异源**：同一颗脑排的计划自己审，就是 §14 登记的
「盲区一致，假绿灯」。

运行位置与状态归属（两处易错点）：
- 本图被 ``supervisor.build_supervisor_graph`` 以 ``builder.add_node(name, graph)``
  的方式挂为子图节点，因此运行时是「父图内的一个节点」；
- 本图的 checkpointer 由父图统一供给（compile() 不挂 saver）：interrupt 的挂起
  状态与 resume 计数都写在父图线程的 checkpoint 上，thread_id 即 conversation_id。
  若子图自行挂 saver，反倒会在父图 checkpoint 之外产生第二份状态，破坏恢复语义。
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt
from pydantic import BaseModel

from po_agent_core.config import ModelRole
from po_agent_core.events import EventType
from po_agent_core.supervisor.state import CoreState
from po_agent_novel.context import CompiledContext, StyleContract, compile_context
from po_agent_novel.gates import (
    GateInput,
    GateRules,
    PlanInput,
    evidence_verbatim,
    run_plan_rules,
    run_rules,
)
from po_agent_novel.judge import ref_lines, run_judge, run_plan_judge
from po_agent_novel.policy import (
    PlanRelease,
    Release,
    ReleasePolicy,
    apply_disputed,
    decide_plan_release,
    decide_release,
    patch_plan,
    rewrite_feedback,
    splice_patch,
)
from po_agent_novel.prompts import (
    PROMPT_VERSION,
    conceive_prompt,
    extract_characters_prompt,
    extract_prompt,
    outline_prompt,
    patch_prompt,
    plan_scene_prompt,
    revise_prompt,
    scene_card_text,
    summarize_arc_prompt,
    summarize_chapter_prompt,
    worldbuild_prompt,
    write_chapter_prompt,
)
from po_agent_novel.schemas import (
    AliasCandidate,
    ArcDigest,
    AssertionCandidate,
    BookDraft,
    BookIdea,
    ChapterDigest,
    ChapterDraft,
    ChapterExtraction,
    ChapterOutline,
    CharacterList,
    Finding,
    Outline,
    SceneCard,
    WorldBible,
    WorldRuleEntry,
)
from po_agent_novel.store import (
    CanonAssertion,
    CanonStore,
    ExtractionSource,
    InMemoryCanonStore,
    NovelStore,
    NovelStoreError,
    SceneSummary,
    SummaryRecord,
    content_hash,
    pending_assertions,
)

logger = logging.getLogger(__name__)

# artifacts 命名空间键：必须与插槽名 agent.NOVEL_AGENT_NAME 一致，
# 否则宿主/其他垂直 Agent 无法按名定位本 Agent 的领域数据。
NOVEL_KEY = "novel"

# 节点名常量：同时会作为 Runner STEP 事件 payload 的 ``node`` 字段上浮，
# 前端按此展示节点级进度，改动即影响前端展示口径。
CONCEIVE_NODE = "conceive"
WORLDBUILD_NODE = "worldbuild"
OUTLINE_NODE = "outline"
PLAN_NODE = "plan_scene"
GATE_PLAN_NODE = "gate_plan"
WRITE_NODE = "write"
EXTRACT_NODE = "extract"
GATE_NODE = "gate_text"
REVISE_NODE = "revise"
COMMIT_NODE = "commit_and_next"
ARCHIVE_NODE = "archive"

# 节点 → 模型角色：阶段换模型的唯一维护点。
# 节点在装配期按这张表从传入的 stage_models 里取模型，因此「哪个阶段用哪个模型」
# 是子图自己声明的领域知识，配置侧（AGENT_CORE_LLM_ROLES__*）只需按角色名覆盖，
# 无需知道子图内部有哪些节点。改这张表即改阶段归属，记得同步 STAGE_ROLES 的调用方说明。
NODE_MODEL_ROLES: dict[str, ModelRole] = {
    CONCEIVE_NODE: ModelRole.PLAN,  # 构思：结构化抽取，属规划类
    WORLDBUILD_NODE: ModelRole.PLAN,  # 书级圣经：与构思/大纲同为「先定义」的一路
    OUTLINE_NODE: ModelRole.PLAN,  # 大纲：与构思同角色（同一颗「规划脑」）
    PLAN_NODE: ModelRole.PLAN,  # 场景卡：挑实体、排场景，仍是规划
    # 计划裁判：必须与 plan_scene/write 异源（§7 同源约束）。它审的是「照这张卡写
    # 会不会出事」，与写正文那颗脑的判断维度重叠时，两道闸门会一起瞎。
    GATE_PLAN_NODE: ModelRole.JUDGE,
    WRITE_NODE: ModelRole.WRITE,  # 正文：长文生成，成本与质量的主战场
    # 正典抽取用规划脑而非审稿脑：抽取者与被审者同源会有盲区一致性
    # （自己写歪的事实自己抽不出问题），所以刻意与两道闸门分角色。
    EXTRACT_NODE: ModelRole.PLAN,
    # 正文闸门的语义裁判：判定类，且必须与 write/extract 异源（§9.2 的「异源互查」）
    GATE_NODE: ModelRole.JUDGE,
    # 定向修补与整章重写都是「写字」，与正文同一个写作脑：换一颗脑来改句子会把
    # 语气改掉，而 §12 黄金集要比对的是「同一处的前后两版」。
    REVISE_NODE: ModelRole.WRITE,
    ARCHIVE_NODE: ModelRole.JUDGE,  # 归档内的角色抽取：同为结构化判定类
}

# commit_and_next 刻意不在这张表里：它是纯状态搬运（定稿、推进游标），一次 LLM 调用都没有。
# 声明一个用不上的角色只会在装配期多建一颗模型，并让人以为定稿有模型参与。

# 本图需要的全部角色（去重、保持声明顺序，取字符串形态即 stage_models 的键）：
# 装配层据此逐个建模型，也是「缺哪个角色就报哪个名字」的校验清单。
STAGE_ROLES: tuple[str, ...] = tuple(dict.fromkeys(NODE_MODEL_ROLES.values()))

# 归档确认的「肯定」词表：WS 上行帧里 resume 值是用户输入的字符串（如 yes），
# 因此需要做字符串归一化；小写化 + strip 以兼容 "Yes" / " 确认 "。
_APPROVE_WORDS = {"yes", "true", "1", "ok", "确认", "同意", "是"}

# 命名空间里以 pydantic 模型存放的键：interrupt 之后必须重新装配（见 _hydrate）。
_NS_MODELS: dict[str, type[BaseModel]] = {
    "idea": BookIdea,
    "bible": WorldBible,
    "plan": SceneCard,
}
_NS_MODEL_LISTS: dict[str, type[BaseModel]] = {"outline": ChapterOutline}
_ENTRY_MODELS: dict[str, type[BaseModel]] = {"extraction": ChapterExtraction}


def _unwrap_constructors(value: Any) -> Any:
    """把 LangChain 的 constructor 信封还原成普通 dict/list。

    递归是必须的：信封会套信封（``SceneCard`` 的每个 ``PlannedScene`` 各带一份），
    只拆最外层会让内层字段揣着 ``lc``/``type``/``id`` 这些与模型无关的键进校验。
    """
    if isinstance(value, dict):
        if value.get("type") == "constructor" and "kwargs" in value:
            return _unwrap_constructors(value["kwargs"])
        return {key: _unwrap_constructors(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_unwrap_constructors(item) for item in value]
    return value


def _as_model(value: Any, model: type[BaseModel]) -> Any:
    """一个命名空间取值 → 模型实例；已经是实例或不是 dict 时原样返回。"""
    if isinstance(value, model):
        return value
    if not isinstance(value, dict):
        return value
    return model.model_validate(_unwrap_constructors(value))


def _as_models(value: Any, model: type[BaseModel]) -> Any:
    return [_as_model(item, model) for item in value] if isinstance(value, list) else value


def _hydrate(ns: dict[str, Any]) -> dict[str, Any]:
    """resume 之后把领域模型重新装配回实例（就地于副本，调用方已拿到拷贝）。

    真机翻车现场：第 1 章计划闸门 escalate、作者回 yes 之后，下一个节点报
    ``'dict' object has no attribute 'wordsLow'``。过 checkpointer（真机默认 redis）时
    pydantic 模型被存成 LangChain 的 constructor 信封、取回来不再是实例，而冻结
    dataclass（style / chapters / world_rows / plan_view）原样回来了——所以要复原的
    只有模型这一类。每个节点都经 :func:`_ns` 读命名空间，修在这一处即可；
    对从未挂起的常规运行是空操作（``isinstance`` 命中就直接返回）。
    """
    for key, model in _NS_MODELS.items():
        if key in ns:
            ns[key] = _as_model(ns[key], model)
    for key, model in _NS_MODEL_LISTS.items():
        if key in ns:
            ns[key] = _as_models(ns[key], model)
    if "extractions" in ns:
        entries = []
        for entry in ns["extractions"] or []:
            if isinstance(entry, dict):
                entry = {
                    key: _as_model(value, _ENTRY_MODELS[key]) if key in _ENTRY_MODELS else value
                    for key, value in entry.items()
                }
            entries.append(entry)
        ns["extractions"] = entries
    return ns


def _ns(state: CoreState) -> dict[str, Any]:
    """读取本 Agent 的领域命名空间，返回浅拷贝副本（模型已复原）。"""
    # 返回副本而非原引用：节点在副本上就地修改后整体回写，
    # 避免直接改写父图传入 state 中的同一 dict 造成隐式共享写。
    artifacts = state.get("artifacts") or {}
    namespace = artifacts.get(NOVEL_KEY)
    # 首次进入（conceive 之前）命名空间不存在，此时按空字典处理。
    return _hydrate(dict(namespace)) if isinstance(namespace, dict) else {}


def _update(ns: dict[str, Any]) -> dict[str, Any]:
    """节点返回值：整体替换 novel 命名空间（merge_artifacts 后写胜出）。

    CoreState.artifacts 以 merge_artifacts 归并（浅合并、同名顶层键整体替换），
    因此每次回写都必须给出全量领域数据，且必须带 NOVEL_KEY 这一层——
    只返回子字段的「补丁式」更新既会丢字段也无法被合并。
    """
    return {"artifacts": {NOVEL_KEY: ns}}


def _emit(event_type: EventType, content: str, payload: dict[str, Any] | None = None) -> None:
    """发布一条领域进度事件（custom 流），由宿主 AgentRunner 翻译为前端帧。

    :param event_type: 事件类型，本图只用 THINKING / PLAN 两种进度语义
    :param content: 面向用户的一句话进度描述
    :param payload: 结构化附加信息，约定含 ``stage`` 字段供前端区分阶段
    """
    try:
        writer = get_stream_writer()
    except RuntimeError:  # 无流上下文（节点被直接调用）时静默跳过
        return
    # 帧结构须与 AgentRunner.translate_custom 的解析约定一致（type/content/payload）：
    # type 合法才会被原样透传为对应事件，否则会被包成 STEP 兜底。
    writer({"type": event_type.value, "content": content, "payload": payload or {}})


def _last_user_text(state: CoreState) -> str:
    """取最近一条用户消息文本，作为本轮委托的原始需求（构思输入）。"""
    # supervisor 是单轮委托语义、messages 由 add_messages 满载归并，
    # 因此逆序遇到的第一条 HumanMessage 即本轮输入；
    # content 可能是多模态列表，统一转 str 才能安全拼进提示词。
    for message in reversed(state.get("messages") or []):
        if isinstance(message, HumanMessage):
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


def _approved(value: Any) -> bool:
    """确认解析：resume 值为 WS 字符串（如 ``yes``），也兼容布尔。

    interrupt 恢复时本节点会从头重放，``interrupt(...)`` 的返回值即宿主
    ``Command(resume=value)`` 传入的值——经 WS 上行帧到达时是 str，
    直连调用/测试时可以是 bool，故这里统一归一化。
    归档确认与计划升级确认共用这一份词表：两处「同意」必须是同一个意思，
    否则用户学会了按 yes 归档，却在计划卡片上按 yes 停笔。
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _APPROVE_WORDS
    return bool(value)


def _chapter_heading(index: int, title: str) -> str:
    """拼装章节标题；title 已带「第N章」前缀时不重复添加。"""
    prefix = f"第{index}章"
    # 提示词要求模型只输出正文、不带标题，序号与标题在此统一生成，
    # 避免模型自拟标题导致各章标题格式不一致。
    return title if title.startswith(prefix) else f"{prefix} {title}"


def _book_text(idea: BookIdea, chapters: list[ChapterDraft]) -> str:
    """拼装「书名 + 题材 + 梗概 + 各章正文」的完整书稿文本。

    归档成功与用户选择暂不归档两种回执共用：无论是否入库，
    用户都能在本轮回复里拿到成稿全文。
    """
    parts = [f"《{idea.title}》（{idea.genre}）\n{idea.summary}"]
    parts.extend(f"\n{_chapter_heading(c.index, c.title)}\n{c.content}" for c in chapters)
    return "\n".join(parts)


def _release_label(release: Release, repairs: int) -> str:
    """正文放行结论的一句话文案：既是事件内容，也是工作台的状态标签口径。

    把「为什么放行/冻结」写在文案里而不是只放 payload：用户在 WS 上看到的这一行
    往往就是唯一的解释机会（``unreviewed`` 这类布尔值没人会去点开看）。
    """
    if release.action == "pass":
        return "放行"
    if release.action == "freeze":
        return f"冻结转人工（{release.reason}）"
    kind = "定向修补" if release.action == "patch" else "整章重写"
    return f"{kind}（第 {repairs + 1} 轮）"


def _plan_label(release: PlanRelease, attempts: int) -> str:
    """计划放行结论的一句话文案（口径与 :func:`_release_label` 一致）。"""
    if release.action == "pass":
        return "放行"
    if release.action == "replan":
        return f"回炉重排（第 {attempts + 1} 轮）"
    return f"转作者拍板（{release.reason}）"


def bible_extraction(bible: WorldBible) -> ChapterExtraction:
    """书级圣经 → 正典写入载荷（复用 ``append_assertions``，不需要新的库接口）。

    三条映射口径都有刻意的理由，改任何一条都要回来看这段：

    - 规则行原样转断言，``evidenceQuote`` 用「书级圣经：{restatement}」。机制② 的
      「必须逐字摘自正文」约束的是**抽取**——设定是动笔前的作者约定，此刻还没有正文
      可引，硬要它自证出处等于要求作者先写一章才能定设定；
    - 人物 → ``anchor`` 断言 + 一条主别名（正文里出现的中文名 ↔ 实体键，
      plan_scene 与生死规则全靠它认人）；**只有 ``alive=False`` 才额外写 ``is_alive``**：
      漏记「活人」不会造成任何违规，漏记「死人」则会让死者在全书每一章都合法地开口，
      这类不对称就是只写一边的理由；
    - 关系 → 主语键取复合键 ``rel:{from}:{to}``，一条关系一行。挂在人物键上会让同一个人
      的两条关系在闸门侧撞成「同一谓词两个值」，那是我们自己造的假冲突。
    """
    assertions: list[AssertionCandidate] = []
    for rule in bible.rules:
        assertions.append(
            AssertionCandidate(
                kind=rule.kind,
                subjectKey=rule.subjectKey,
                predicate=rule.predicate,
                objectText=rule.objectText,
                restatement=rule.restatement,
                evidenceQuote=f"书级圣经：{rule.restatement}",
                # status 原样透传：todo 即作者自己标的缺口，不许在这里替他确认为事实
                status=rule.status or "confirmed",
            )
        )
    aliases: list[AliasCandidate] = []
    for character in bible.characters:
        assertions.append(
            AssertionCandidate(
                kind="character",
                subjectKey=character.key,
                predicate="anchor",
                objectText=f"{character.role}｜{character.anchor}",
                restatement=f"{character.name}（{character.role}）：{character.anchor}",
                evidenceQuote=f"书级圣经：{character.name}",
                status="confirmed",
            )
        )
        aliases.append(
            AliasCandidate(entityKey=character.key, aliasText=character.name, isPrimary=True)
        )
        if not character.alive:
            assertions.append(
                AssertionCandidate(
                    kind="character",
                    subjectKey=character.key,
                    predicate="is_alive",
                    objectText="false",
                    restatement=f"{character.name}在开篇即已死亡，此后不许直接发言",
                    evidenceQuote=f"书级圣经：{character.name}",
                    status="confirmed",
                )
            )
    for relation in bible.relations:
        assertions.append(
            AssertionCandidate(
                kind="relation",
                subjectKey=f"rel:{relation.fromKey}:{relation.toKey}",
                predicate="relation_to",
                objectText=relation.relation,
                restatement=relation.restatement,
                evidenceQuote=f"书级圣经：{relation.relation}",
                status="confirmed",
            )
        )
    return ChapterExtraction(assertions=assertions, aliases=aliases)


def gap_bible(idea: BookIdea, reason: str) -> WorldBible:
    """世界构建问不出结果时的兜底圣经：一条 ``todo`` 缺口，零「已确立设定」。

    形状与离线占位圣经一致（读侧只注入 ``confirmed``，所以这一本不会把任何编造的
    规则喂给后续章节），区别只在 ``restatement`` 写的是**真实失败原因**：归档卡片
    要能告诉作者「这本书的世界没定下来，是因为 X」，而不是留一个看不出缘由的空。
    """
    sentence = f"世界构建未取得可用结果（{reason}），本书暂时按「设定全是缺口」继续。"
    return WorldBible(
        logline=f"《{idea.title}》：{idea.summary}",
        rules=[
            WorldRuleEntry(
                subjectKey="rule:worldbuild_failed",
                predicate="build_failed",
                objectText=reason,
                restatement=sentence,
                status="todo",
            )
        ],
        openQuestions=[sentence, "请在工作台补齐世界规则、人物与关系，或重跑 worldbuild。"],
    )


def filter_extraction(
    extraction: ChapterExtraction, content: str
) -> tuple[ChapterExtraction, int]:
    """丢弃证据不在正文中的断言，返回（收敛后的候选, 被丢弃条数）。

    单独成函数是为了让闸门可被直接单测；逐字口径住在 gates.evidence_verbatim——
    抽取侧与 N4 的双闸门必须共用同一份实现，否则「放行的证据」与「台账里的证据」
    会各说各话，被抽验收到的断言反而在冲突台账里被判伪造。
    状态变迁/称谓/伏笔不做证据校验：它们没有 evidence 字段，正确性由
    「实体键必须能对上已登记断言或别名」约束（gates.py 的别名与生死规则先覆盖一部分）。
    """
    kept = [a for a in extraction.assertions if evidence_verbatim(a.evidenceQuote, content)]
    dropped = len(extraction.assertions) - len(kept)
    if not dropped:
        return extraction, 0
    return extraction.model_copy(update={"assertions": kept}), dropped


def _arc_spans(
    outline: Sequence[ChapterOutline], total: int, arc_chapters: int
) -> list[tuple[int, int]]:
    """弧级摘要的章区间划分（1 基闭区间），返回 ``[(start, end), ...]``。

    优先按大纲点名的 ``arc`` 分组：连续同名即一段弧，作者换了弧名就是换了一段剧情，
    这时**不再**受 ``arc_chapters`` 跨度约束——把作者明确的分组硬切成两半，
    Tier-0 的进度线会告诉他「弧在中间断了」，那是假信息。
    弧名为空的章视作延续当前弧（模型常常只在弧的第一章写名字）；整段都没点名时
    退回按 ``arc_chapters`` 等分，保证长书仍有分辨率。

    ``save_arc_summary`` 没有承载弧名的列，所以标题只影响切分、不落库
    （PRD §15.6 登记的偏差之一）。
    """
    if total <= 0 or arc_chapters <= 0:
        return []
    titles = [(chapter.arc or "").strip() for chapter in outline[:total]]
    groups: list[tuple[str, int, int]] = []
    start = 1
    title = titles[0]
    for pos in range(2, total + 1):
        current = titles[pos - 1]
        if current and current != title:
            groups.append((title, start, pos - 1))
            start, title = pos, current
        elif current and not title:
            title = current
    groups.append((title, start, total))

    spans: list[tuple[int, int]] = []
    for group_title, group_start, group_end in groups:
        if group_title:
            spans.append((group_start, group_end))
            continue
        cursor = group_start
        while cursor <= group_end:
            stop = min(cursor + arc_chapters - 1, group_end)
            spans.append((cursor, stop))
            cursor = stop + 1
    return spans


def merge_gate_rules(
    base: GateRules, bible: Any, style: StyleContract | None
) -> GateRules:
    """按书合并规则口径：禁用词先取本轮圣经，再被作者手改的文风契约覆盖。

    旧实现里 ``GateRules.forbidden_words`` 恒空——没有任何一处产出禁用词，
    §9.1 的这条规则其实是死代码。worldbuild 交出 ``forbidden`` 之后它才真的生效，
    而合并点必须只有这一处：两道闸门各读一份词表，就会出现
    「计划里没禁、正文里被禁」这种无法归因的分裂。

    ``style`` 传的是**那一次装配**用的契约（``compiled.style``，作者库内的
    ``style_profile`` 已盖在派生值之上）：作者赢过圣经，因为词表只能由人手收紧——
    模型产出的清单与它要遵守的清单若是两份，「谁定的禁用词」就又漂移了。
    """
    forbidden = tuple(getattr(bible, "forbidden", ()) or ())
    if style is not None and style.forbidden_words:
        forbidden = style.forbidden_words
    rules = replace(base, forbidden_words=forbidden) if forbidden else base
    if style is not None and style.chapter_words_min and style.chapter_words_max:
        # 作者给了绝对字数带，就按带换算比例：目标取中点，允许带正好是那一段。
        # 留两套判据（比值 + 绝对值）会让「越带」在两边算出不同的严重度。
        middle = (style.chapter_words_min + style.chapter_words_max) // 2
        rules = replace(
            rules,
            target_words=middle,
            min_ratio=style.chapter_words_min / middle,
            max_ratio=style.chapter_words_max / middle,
        )
    return rules


def build_novel_graph(
    stage_models: Mapping[str, BaseChatModel],
    store: NovelStore,
    *,
    canon_store: CanonStore | None = None,
    chapter_count: int = 3,
    chapter_words: int = 1200,
    max_repairs: int = 2,
    max_plan_repairs: int = 2,
    arc_chapters: int = 10,
) -> CompiledStateGraph:
    """编译小说创作子图。

    不挂 checkpointer：作为 supervisor 子节点运行时由父图统一供给
    （interrupt 挂起 / resume 续跑依赖父图的线程 checkpoint）。
    也正因如此，本函数不接收 saver / thread_id 参数，单测可用
    ``graph.ainvoke(state, config=...)`` 直连驱动。

    拓扑（固定边 + 三条条件边）：

    - START → conceive → worldbuild → outline → plan_scene → gate_plan；
    - gate_plan 条件边：**pass** 去 write、**replan** 回 plan_scene（意见随提示词带回）、
      **escalate** 在节点内 interrupt 交作者拍板——按 yes 继续写并把本章标记为
      「计划未经完整审查」，按其他回复即停笔并直接进 archive（强制停，不是强制过）；
    - write → extract → gate_text；gate_text 条件边：blocker 走 revise（定向修补或
      整章重写，改完回 extract 重抽），其余进 commit_and_next；
    - commit_and_next 条件边：还有下一章回 plan_scene，全书写完进 archive；archive → END。

    修补回环必须回到 extract：正文变了，候选断言的逐字证据可能已经失效
    （旧事实配新正文＝闸门自己造了条假证据）。
    两轮修补仍不过即**冻结该章**：正文照常成稿，但它的事实与摘要一律不入库
    （§9.3「blocker 不 commit」），冲突台账照写——那正是人工要裁定的东西。

    :param stage_models: 角色 → 模型实例，键取 ``ModelRole``（见 NODE_MODEL_ROLES）。
        每个节点在**装配期**按角色取定模型并绑进闭包，运行期不再查表——
        因此换模型只需改配置后重启，运行中的图不会中途换脑。
    :param store: 成稿数据层（NovelStore 协议），仅 archive 节点使用
    :param canon_store: 正典数据层（CanonStore 协议）；缺省 ``InMemoryCanonStore``
        （进程内、重启即失）。生产装配由 agent 层显式传入 HTTP 实现
    :param chapter_count: 大纲章数，写入 outline_prompt 的规划要求
    :param chapter_words: 每章目标字数，写进计划/正文提示词，也是两道闸门的字数带基准
    :param max_repairs: 单章最大正文修补轮数（§9.3 的「2 轮不过冻结转人工」）
    :param max_plan_repairs: 单张场景卡最大重排轮数，用尽即升级给作者。与
        ``max_repairs`` 分开计是必要的：重排只改十几行计划，正文修补要改一千二百字，
        合并计数会让计划问题挤掉正文修补的轮次预算
    :param arc_chapters: 弧级摘要的默认跨度（未被大纲 arc 点名分组的章节按此等分）；
        设为 0 或负值则不产 arc 摘要
    :return: 已编译子图（CompiledStateGraph），状态 schema 为 CoreState
    """
    missing = [role for role in STAGE_ROLES if role not in stage_models]
    if missing:
        # 缺角色即刻报错而不是回落到某个已有模型：静默回落会得到「真模型正文 +
        # 占位审稿」这类混合链路，比整体降级更难排查（离线降级交给装配层决定）。
        names = ", ".join(missing)
        raise ValueError(f"缺少阶段模型：{names}（本图需要 {'/'.join(STAGE_ROLES)}）")
    # 缺省用进程内正典而非拒绝装配：正典写入是「有则落库、无则留在本轮 artifacts」，
    # 单测与无后端环境都要能跑完整链路（与 NovelStore 必须显式传入不同）。
    canon_store = canon_store or InMemoryCanonStore()
    # 结构化输出绑定是「LLM 调用契约」：schema 即输出约束（见 schemas 模块），
    # 与 prompts 的「输出格式」节互为双保险。此处不做任何模型差异分支——
    # 真实模型与离线模型（OfflineNovelModel.with_structured_output）接口一致。
    # method 显式指定 function calling：langchain-openai 1.x 的默认方法是发
    # json_schema 型 response_format，而 DeepSeek / DashScope 兼容端点不支持，
    # 会直接 400（This response_format type is unavailable now）；工具调用是各
    # OpenAI 兼容端点的最大公约数，OpenAI 侧同样支持。
    conceiver = stage_models[NODE_MODEL_ROLES[CONCEIVE_NODE]].with_structured_output(
        BookIdea, method="function_calling"
    )
    worldbuilder = stage_models[NODE_MODEL_ROLES[WORLDBUILD_NODE]].with_structured_output(
        WorldBible, method="function_calling"
    )
    outliner = stage_models[NODE_MODEL_ROLES[OUTLINE_NODE]].with_structured_output(
        Outline, method="function_calling"
    )
    planner = stage_models[NODE_MODEL_ROLES[PLAN_NODE]].with_structured_output(
        SceneCard, method="function_calling"
    )
    writer = stage_models[NODE_MODEL_ROLES[WRITE_NODE]]
    plan_model = stage_models[NODE_MODEL_ROLES[EXTRACT_NODE]]
    extractor = plan_model.with_structured_output(
        ChapterExtraction, method="function_calling"
    )
    # 摘要与抽取同一颗「规划脑」（PLAN）：两者都是「读正文 → 结构化压缩」，
    # 且都不做判定——把摘要交给审稿脑只会让它和闸门抢活。
    # 不新增节点：摘要跟着定稿走，与 extract 同生命周期，拆开只是多一次状态搬运。
    digester = plan_model.with_structured_output(ChapterDigest, method="function_calling")
    arc_digester = plan_model.with_structured_output(ArcDigest, method="function_calling")
    character_extractor = stage_models[NODE_MODEL_ROLES[ARCHIVE_NODE]].with_structured_output(
        CharacterList, method="function_calling"
    )
    # 两道语义裁判都不在装配期绑 structured_output：run_*_judge 自己绑 FindingList——
    # 裁判的「调用失败」要被归到闸门的失败计数上（JudgeOutcome.failed），绑在这里
    # 就只能把异常一路抛穿节点，等于把「查不出」与「没查成」混成一个。
    plan_judge_model = stage_models[NODE_MODEL_ROLES[GATE_PLAN_NODE]]
    judge_model = stage_models[NODE_MODEL_ROLES[GATE_NODE]]
    # 规则闸门口径：装配期只有 chapter_words 可给；禁用词来自本轮圣经（worldbuild 产出），
    # 所以合并点在 :func:`merge_gate_rules`（节点内只留一层 _rules_for 取值），
    # 两道闸门共用同一份词表。
    gate_rules = GateRules(target_words=chapter_words)
    # 放行口径同样留在装配期：一封 blocker 该修几轮、一轮修几处，是按书（甚至按平台）
    # 调的参数，不该散落在节点判断里。
    release_policy = ReleasePolicy(max_repairs=max_repairs, max_plan_repairs=max_plan_repairs)
    # 幂等键要记录「哪个模型抽的」：换模型后同一章的抽取结果本就该重算，
    # 名字比对即可，不必存实例。取不到 model_name（本地包装类）时退回类名。
    extractor_name = str(
        getattr(plan_model, "model_name", None) or type(plan_model).__name__
    )

    def _world_rows(ns: dict[str, Any]) -> tuple[CanonAssertion, ...]:
        """圣经行（读侧视图）：worldbuild 生成一次，后续每章装配都带同一份。"""
        return tuple(ns.get("world_rows") or ())

    def _rules_for(ns: dict[str, Any], style: StyleContract | None = None) -> GateRules:
        return merge_gate_rules(gate_rules, ns.get("bible"), style)

    def _pending_rows(ns: dict[str, Any]) -> tuple[list[CanonAssertion], list[SummaryRecord]]:
        """把本轮攒下的候选正典与层级摘要转成 L1 编译器的 overlay 形态。

        正典与摘要都刻意迟于归档才落库（写侧不幂等会被 resume 重放写成双份），
        于是连续写多章时库里什么都没有——overlay 补的就是这段本轮内存视图。
        缺了它，第 2 章起 Tier-1/Tier-2 恒空，L1 装配反而在最需要它的长写作会话里失效。
        """
        assertions: list[CanonAssertion] = []
        summaries: list[SummaryRecord] = []
        for entry in ns.get("extractions") or []:
            if not isinstance(entry, dict) or entry.get("extraction") is None:
                continue
            chapter_no = int(entry["chapter"])
            assertions.extend(pending_assertions("", chapter_no, entry["extraction"]))
            for scene in entry.get("scenes") or []:
                summaries.append(
                    SummaryRecord(
                        id="",
                        level="scene",
                        chapter_no=chapter_no,
                        scene_no=scene.scene_no,
                        content=scene.content,
                        tokens=scene.tokens,
                    )
                )
            if entry.get("digest"):
                summaries.append(
                    SummaryRecord(
                        id="",
                        level="chapter",
                        chapter_no=chapter_no,
                        scene_no=0,
                        content=entry["digest"],
                    )
                )
        return assertions, summaries

    async def _compile(
        ns: dict[str, Any],
        *,
        entities: list[str] | None,
        stage: str,
        fail_stage: str,
        chapter_no: int,
    ) -> CompiledContext | None:
        """按「当前章」装配注入块；读取失败即返回 ``None`` 并留痕。

        plan_scene 与 write 各装配一次，且两次**故意不同**：
        - 计划那次 ``entities=None``（全量 as-of 视图）。判「这个实体登记过没有」的口径
          必须比检索口径更宽——拿即将挑中的那份清单先过滤一遍，每个新实体都会同时是
          「未登记」与「查不到」，闸门就废了；
        - 写作那次按场景卡的 ``entities`` 收窄（§6-1「先抽实体再检索」），
          这正是注入预算与书长解耦的落点。
        两份产物分别存进 ``plan_view`` / ``gate_view``：编号是按那一次装配的
        行集发的，混用会让裁判引着一个指向另一份事实的编号。

        :param stage: 成功事件的 stage 名（计划侧 plan_compiled / 正文侧 context_compiled，
            后者沿用旧名，成本监控与回归断言都认它）
        :param fail_stage: 失败留痕的 stage 名，与 ``stage`` 分开，
            这样「正文装配失败」与「计划装配失败」在事件流里是两个数
        """
        try:
            overlay_rows, digest_rows = _pending_rows(ns)
            compiled = await compile_context(
                canon_store,
                book_id=ns.get("book_id") or None,
                idea=ns["idea"],
                outline=ns["outline"],
                index=ns["index"],
                chapters=ns["chapters"],
                entities=entities,
                world=_world_rows(ns),
                overlay=overlay_rows,
                digests=digest_rows,
                style=ns.get("style"),
            )
        except Exception as exc:
            # 记忆读取失败不阻断本节：这一章宁可看不见正典，也不要让整条链路停在读取上。
            # 但必须留痕——注入缺位造成的设定漂移，事后只能靠这条日志定位到章。
            logger.error("第 %s 章 L1 装配失败（%s），本节不带正典注入：%s", chapter_no, stage, exc)
            _emit(
                EventType.THINKING,
                f"第 {chapter_no} 章记忆装配失败，本节不带正典注入",
                {"stage": fail_stage, "chapter": chapter_no},
            )
            return None
        # token 与裁剪计数上浮：N6 的成本监控按这条统计「P95 注入 ≤ 4k」是否成立。
        # entities / narrowed / tier1_empty_by_entities 是 §8-⑧ 要的收窄遥测：
        # 「按场景卡实体检索」命中空集时，读者看到的是「设定 0 条」，
        # 而真实原因可能是 key 打错而不是这本书真的没有相关设定——不记这一笔就无法区分。
        _emit(
            EventType.THINKING,
            f"第 {chapter_no} 章注入 {compiled.tokens} token（设定 {compiled.counts['tier1']} 条 / "
            f"圣经 {compiled.counts['world']} 条 / 近因 {compiled.counts['tier2']} 条 / "
            f"裁剪 {compiled.counts['dropped']} 条）",
            {
                "stage": stage,
                "chapter": chapter_no,
                **compiled.counts,
                "tokens": compiled.tokens,
                "entities": list(entities or ()),
                "narrowed": bool(entities),
                "tier1_empty_by_entities": bool(entities) and compiled.counts["tier1"] == 0,
            },
        )
        return compiled

    async def _digest_chapter(
        idea: BookIdea, chapter: ChapterOutline, index: int, content: str
    ) -> dict[str, Any]:
        """产出一章的场景级摘要与章级摘要（写侧候选，随正典一起在归档后落库）。

        与 extract 同一次定稿触发、同一颗 PLAN 脑：正文此刻就在上下文里，分成两次
        调用就是同一章付两遍 token，而且第二遍吃第一遍的输出——那是 §6-4 明令禁止的
        「摘要的摘要」。

        失败只让这一章缺近因，不影响正典入库：摘要是提示词质量项，正典是一致性项。
        """
        try:
            digest: ChapterDigest = await digester.ainvoke(
                summarize_chapter_prompt(idea, chapter, index, content)
            )
        except Exception as exc:
            logger.error("第 %s 章摘要失败，该章不产层级摘要：%s", index + 1, exc)
            _emit(
                EventType.THINKING,
                f"第 {index + 1} 章摘要失败（不影响正典入库）",
                {"stage": "digest_failed", "chapter": index + 1},
            )
            return {"scenes": [], "digest": ""}
        return {
            "scenes": [
                SceneSummary(scene_no=scene.sceneNo, content=scene.content)
                for scene in digest.scenes
            ],
            "digest": digest.digest,
        }

    async def conceive_node(state: CoreState) -> dict[str, Any]:
        """构思节点（图入口）：一句话想法 → 结构化 BookIdea，并初始化领域状态。"""
        brief = _last_user_text(state)
        idea: BookIdea = await conceiver.ainvoke(conceive_prompt(brief))
        # 首次写入整个 novel 命名空间：下列字段即后续所有节点共享的状态契约。
        # index 是 0 基的「正在写」章游标；draft 是当前章稿（定稿前不进 chapters）。
        ns: dict[str, Any] = {
            "brief": brief,
            "idea": idea,
            # bible：书级圣经（WorldBible）；world_rows：它派生的读侧断言行（进 Tier-0）；
            # style：由圣经落成的文风契约——三者都在 worldbuild 一次写定。
            "bible": None,
            "world_rows": [],
            "style": None,
            "outline": [],
            "chapters": [],
            "index": 0,
            "draft": "",
            "action": "",
            "book_id": "",
            # plan：当前章的场景卡；plan_view：计划那次装配的产物；
            # plan_repairs/plan_feedback/plan_action：计划回环的轮数、退回意见与路由键；
            # plan_stats：最近一次计划闸门的判据快照（只上浮，不落 review_finding 表）；
            # plan_unreviewed：作者拍板「照这张卡写」的章号（1 基），归档卡片要显式交代；
            # plan_new：历轮场景卡自报的新实体（只上浮给作者，永不进正典）；
            # halted_at：计划冲突未获放行而停笔的那一章。
            "plan": None,
            "plan_view": None,
            "plan_repairs": 0,
            "plan_action": "",
            "plan_feedback": "",
            "plan_stats": None,
            "plan_unreviewed": [],
            "plan_new": [],
            "halted_at": None,
            # extractions：各章候选正典增量（键为 1 基章号），只攒不写，
            # 写库统一留到 archive 的 interrupt 之后。
            "extractions": [],
            # entity_keys：已登记的实体键（圣经 + 历轮抽取），回灌给 plan_scene 的可选
            # 清单与下一章的抽取提示词，压制「同一人物第二个 key」。
            "entity_keys": [],
            # gate_repairs：当前章已用正文修补轮数（放行策略的硬上限，闸门每轮自行归零
            # 或累加，故不在此处重置）；gate_action：正文侧路由键（条件边唯一判据）；
            # gate_view：写这稿时那一次 L1 装配的产物，闸门沿用它以保持「模型看见的事实」
            # 与「闸门据以判定的事实」同源，修补轮不覆写；
            # frozen：修补用尽仍未过闸门的章号（1 基），归档时显式告知用户哪些章的
            # 事实没有入库。
            "gate_repairs": 0,
            "gate_action": "",
            "gate_view": None,
            "frozen": [],
        }
        _emit(
            EventType.THINKING,
            f"构思完成：《{idea.title}》（{idea.genre}）",
            {"stage": "conceived", "title": idea.title, "genre": idea.genre},
        )
        return _update(ns)

    async def worldbuild_node(state: CoreState) -> dict[str, Any]:
        """书级圣经节点：动笔之前先把世界钉死（机制①「先定义再动笔」）。

        一份产出喂四处，因此它必须发生在 outline 之前、且必须在任何一次 L1 装配之前：
        - 文风契约（pov/tense）→ :class:`context.StyleContract`，``check_pov`` 自此有基准；
        - 禁用词 → :class:`gates.GateRules`（``merge_gate_rules`` 按书合并）；
        - 实体键全集 → plan_scene 的「只能从这些里挑」清单；
        - 规则/人物/关系 → Tier-0 的编号世界行，并作为 ``snapshot`` 的一部分进两道闸门。

        这里**不写库**：圣经要等 book_id 与章节 id 才落得下去（§8-⑦ 写后置，
        与 extract 候选同一批，见 :func:`write_canon` 的种子段）。
        也刻意不加 interrupt：归档确认卡片已经带上了 openQuestions，
        多一次挂起只是把同一批设定问两遍。

        失败策略（§7 的表）在这里落地：问不出可用结果就**重问一次**，再不行降级为
        :func:`gap_bible`（全缺口、零已确立设定）并显式发 ``worldbuild_failed``。
        降级可见是硬线（§8-⑧）——「圣经没建起来」与「这本书没有设定」在后续章节的
        表现完全一样，区别只能靠这一条事件留下。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        prompt = worldbuild_prompt(idea)
        bible: WorldBible | None = None
        reason = ""
        for attempt in (1, 2):
            try:
                produced = await worldbuilder.ainvoke(prompt)
                if not isinstance(produced, WorldBible):
                    raise TypeError(f"返回类型异常（{type(produced).__name__}）")
                bible = produced
                break
            except Exception as exc:  # 违约 / 网络都按「问不出」处理，不冒到 Runner
                logger.error("书级圣经第 %s 次未取得可用结果：%s", attempt, exc)
                # 重问一次再降级：结构化违约多为偶发，一次抖动就丢掉整本设定太贵
                reason = str(exc) or type(exc).__name__
        degraded = bible is None
        if bible is None:
            bible = gap_bible(idea, reason)
        ns["bible"] = bible
        # as_of=1：开篇前就成立的设定，其有效起点是第 1 章，因此后续每章的 as-of 都看得见。
        ns["world_rows"] = pending_assertions("", 1, bible_extraction(bible))
        ns["style"] = StyleContract(genre=idea.genre, pov=bible.pov, tense=bible.tense)
        ns["entity_keys"] = sorted({row.subject_key for row in ns["world_rows"]})
        if degraded:
            # 单独一帧而不是塞进 worldbuilt 的文案里：N6 的成本与质量门禁要按 stage 计数，
            # 「降级发生的次数」是判断该换模型还是该改提示词的第一个数。
            _emit(
                EventType.THINKING,
                f"书级圣经两次都没问出可用结果，本书按「设定全是缺口」继续：{reason}",
                {"stage": "worldbuild_failed", "reason": reason},
            )
        _emit(
            EventType.THINKING,
            f"书级圣经：{len(bible.rules)} 条规则 / {len(bible.characters)} 个人物 / "
            f"{len(bible.relations)} 段关系（禁用词 {len(bible.forbidden)} 个，"
            f"未决 {len(bible.openQuestions)} 条）",
            {
                "stage": "worldbuilt",
                "rules": len(bible.rules),
                "characters": len(bible.characters),
                "relations": len(bible.relations),
                "forbidden": len(bible.forbidden),
                # 缺口要看得见才算机制③：静默补全是这套系统失败的主要方式之一
                "open_questions": list(bible.openQuestions),
                "degraded": degraded,
            },
        )
        return _update(ns)

    async def outline_node(state: CoreState) -> dict[str, Any]:
        """大纲节点：按 chapter_count 规划全书章节，覆写 ns["outline"]。"""
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: Outline = await outliner.ainvoke(outline_prompt(idea, chapter_count))
        # 只取 chapters 列表入状态：章节序号由列表下标隐含（见 schemas.ChapterOutline），
        # 因此这里不额外存 index 字段。arc（剧情弧名）随章走，弧级摘要按它分组。
        ns["outline"] = list(outline.chapters)
        titles = [chapter.title for chapter in outline.chapters]
        # PLAN 事件区别于 THINKING：前端用它渲染「全书规划」类进度卡片。
        _emit(
            EventType.PLAN,
            "大纲：" + " / ".join(titles),
            {
                "stage": "outlined",
                "chapters": titles,
                "arcs": [chapter.arc for chapter in outline.chapters],
            },
        )
        return _update(ns)

    async def plan_scene_node(state: CoreState) -> dict[str, Any]:
        """场景卡节点：写正文之前先交出「这一章打算怎么写」。

        重排回环（gate_plan 判 replan）与初排共用本节点，靠 ``plan_feedback`` 区分：
        退回意见逐字进提示词（``plan_scene_prompt`` 的 instruction 段），
        而不是新设一个 replan 节点——两条路径都是「出一张卡」，分开只是多一次状态搬运。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter = outline[index]
        # 计划时的装配不带 entities：判「这个 key 登记过没有」要先看得见全量事实。
        view = await _compile(
            ns,
            entities=None,
            stage="plan_compiled",
            fail_stage="plan_context_failed",
            chapter_no=index + 1,
        )
        ns["plan_view"] = view
        # 契约取「那一次装配」的版本：作者手改的 style_profile 已经盖在派生值上，
        # 拿 ns["style"] 会让同一个模型在同一次调用里读到两份人称口径（提示词 vs 注入块）。
        style: StyleContract | None = getattr(view, "style", None) or ns.get("style")
        card: SceneCard = await planner.ainvoke(
            plan_scene_prompt(
                idea,
                chapter,
                index,
                total=len(outline),
                registered=list(ns.get("entity_keys") or []),
                foreshadows=ref_lines(
                    [ref for ref in (view.refs if view else ()) if ref.kind == "foreshadow"]
                ),
                chapter_words=chapter_words,
                pov=style.pov if style else "",
                prev_tail=ns["chapters"][-1].content[-200:] if ns["chapters"] else "",
                instruction=str(ns.get("plan_feedback") or ""),
            )
        )
        ns["plan"] = card
        # 自报的新实体只上浮：计划不是出处，进了 alias 表下一章它就成了「书里已成立」
        new_keys = set(ns.get("plan_new") or []) | set(card.newEntities)
        ns["plan_new"] = sorted(new_keys)
        _emit(
            EventType.THINKING,
            f"第 {index + 1} 章场景卡：{len(card.entities)} 个实体 / {len(card.scenes)} 个场景 / "
            f"收 {len(card.payoffs)} 条伏笔（{card.wordsLow}-{card.wordsHigh} 字）",
            {
                "stage": "planned",
                "chapter": index + 1,
                "entities": len(card.entities),
                "new_entities": list(card.newEntities),
                "scenes": len(card.scenes),
                "payoffs": list(card.payoffs),
                "words_low": card.wordsLow,
                "words_high": card.wordsHigh,
                "replan": bool(ns.get("plan_feedback")),
            },
        )
        return _update(ns)

    async def gate_plan_node(state: CoreState) -> dict[str, Any]:
        """计划闸门节点（§7 的 gate_plan）：规则 + 异源裁判，判**还没写**的那张卡。

        与正文闸门同构（规则在前、裁判在后、合并去重、策略判定），三点不同：
        - 坐标系是 :func:`prompts.scene_card_text` 的稳定渲染，不是章节正文；
        - 处置是 pass / replan / escalate（交作者），而不是 patch / rewrite / freeze；
        - 产物**不落 ``review_finding``**：那张表的 span 语义是「正文字符区间」，
          把卡文本坐标写进去，作者点过去会落在正文的别处——悬空出处比少一条记录更有害。
          它只上浮进事件与归档卡片。

        escalate 在本节点内 interrupt：计划冲突反复改不平通常是设定本身有洞，
        该由作者裁定而不是机器再猜一轮。按 yes 继续写就把本章记进
        ``plan_unreviewed``（「照这张卡写」是作者的授权，不是审查通过，归档卡片必须
        这么交代）；按其他回复则 ``halted_at`` 定章并直接进 archive——
        强制停，不是强制过。
        """
        ns = _ns(state)
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter_no = index + 1
        card: SceneCard = ns["plan"]
        chapter = outline[index]
        view = ns.get("plan_view")
        card_text = scene_card_text(card, chapter)
        plan_in = PlanInput(
            card_text=card_text,
            card=card,
            chapter_no=chapter_no,
            snapshot=tuple(getattr(view, "snapshot", ()) or ()),
            refs=tuple(getattr(view, "refs", ()) or ()),
        )
        report = run_plan_rules(plan_in, _rules_for(ns, getattr(view, "style", None)))
        # 计划裁判的视角基准同样取装配那次的契约（与上面的注入块同一份）
        style: StyleContract | None = getattr(view, "style", None) or ns.get("style")
        outcome = await run_plan_judge(
            plan_judge_model,
            plan_in,
            chapter=chapter,
            style_pov=style.pov if style else None,
            rule_codes=[finding.code for finding in report.findings],
        )
        seen = {(finding.code, finding.textStart, finding.textEnd) for finding in report.findings}
        extra = [
            finding
            for finding in outcome.findings
            if (finding.code, finding.textStart, finding.textEnd) not in seen
        ]
        findings = [*report.findings, *extra]
        attempts = int(ns.get("plan_repairs") or 0)
        release = decide_plan_release(
            findings,
            judge_failed=outcome.failed,
            attempts=attempts,
            policy=release_policy,
        )
        stats = {
            "rule": len(report.findings),
            "judge": len(outcome.findings),
            "duplicated": len(outcome.findings) - len(extra),
            "dropped": report.dropped + outcome.dropped_total,
            "skipped": {**report.skipped, **outcome.dropped},
            "judge_failed": outcome.failed,
            "blockers": sum(1 for f in findings if f.severity == "blocker"),
            "majors": sum(1 for f in findings if f.severity == "major"),
            "release": release.action,
            "unreviewed": release.unreviewed,
        }
        ns["plan_action"] = release.action
        ns["plan_stats"] = {**stats, "findings": [f.model_dump() for f in findings]}
        if release.action == "replan":
            ns["plan_repairs"] = attempts + 1
            ns["plan_feedback"] = rewrite_feedback(release.blockers)
        else:
            ns["plan_repairs"] = 0
            ns["plan_feedback"] = ""
        if release.action == "escalate":
            # 卡片必须带 card_text：作者要看的不是「有几条冲突」而是「那张卡长什么样」，
            # 没有卡文本的批准等于闭眼放行。
            answer = interrupt(
                {
                    "stage": "plan_approval",
                    "question": (
                        f"第 {chapter_no} 章的场景卡有 {len(release.blockers)} 条未平的冲突"
                        f"（{release.reason}）。照这张卡继续写请回复 yes"
                        "（本章会标注为「计划未经完整审查」），其他回复视为停笔并转归档。"
                    ),
                    "chapter": chapter_no,
                    "card_text": card_text,
                    "blockers": [finding.model_dump() for finding in release.blockers],
                    "unreviewed": release.unreviewed,
                    "reason": release.reason,
                    "hint": "照计划继续请回复 yes，其他回复视为停笔",
                }
            )
            if _approved(answer):
                # 批准 ≠ 通过：把章号记进 plan_unreviewed，归档回执与事件都要说清
                # 「这一章按计划写了，但计划没走完审查」，否则 §8-⑨ 的假绿灯
                # 就从这道人工口又溜回来了。
                ns["plan_action"] = "pass"
                ns["plan_unreviewed"] = sorted({*list(ns.get("plan_unreviewed") or []), chapter_no})
            else:
                ns["plan_action"] = "halt"
                ns["halted_at"] = chapter_no
                ns["action"] = "archive"
            stats["approved"] = _approved(answer)
        _emit(
            EventType.THINKING,
            f"第 {chapter_no} 章计划闸门：规则 {stats['rule']} 条 / 裁判 {len(extra)} 条 / "
            f"待处理 {len(release.blockers)} → {_plan_label(release, attempts)}",
            {"stage": "plan_gated", "chapter": chapter_no, **stats},
        )
        return _update(ns)

    async def write_node(state: CoreState) -> dict[str, Any]:
        """正文节点：按场景卡产出「当前章」初稿。

        整章重写与定向修补都在 revise 节点——本节点只有一条路径（写初稿），
        因此不再需要「靠 feedback 是否为空分岔」那种共用形态，提示词也就不会
        在同一段里既讲创作又讲修补。

        进本节点先按场景卡的 entities 做 L1 装配（§6-1），再装配一次才拼提示词：
        装配按 as-of=当前游标取数，重写第 12 章时不会看到第 30 章的事实。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter = outline[index]
        card: SceneCard | None = ns.get("plan")
        # entities 为空即「本轮没有实体清单」：退回全量 as-of 快照而不是猜实体（§6-1）。
        entities = list(card.entities) if card is not None and card.entities else None
        compiled = await _compile(
            ns,
            entities=entities,
            stage="context_compiled",
            fail_stage="context_failed",
            chapter_no=index + 1,
        )
        # 闸门视图随本轮装配落进状态：gate_text 必须在「这稿写作者当时看得见的事实」
        # 上判定，所以它复用 compiled 的 refs/snapshot/style，而不是自己再读一次库
        # （自读会得到另一份视图，于是「闸门报的冲突模型没看见」无从归因）。
        # 修补轮不回覆写它——正文被改过但没重新装配，视图仍是「写这稿时那一份」，
        # 这正是 revise → extract → gate 重跑时该沿用的引用序列。
        # 装配失败时存 None：闸门照跑，只是引不出编号（计入 skipped），不静默跳过。
        ns["gate_view"] = compiled
        block = compiled.block if compiled is not None else None
        # 初稿路径：取上一章定稿末尾 200 字做衔接参考；开篇无上文则传空串，
        # 由提示词切换为「铺开世界观」的开篇要求。
        # 有注入块时这段尾部已在 Tier-2 里（且更长），prev_tail 会被提示词忽略。
        prev_tail = ns["chapters"][-1].content[-200:] if ns["chapters"] else ""
        prompt = write_chapter_prompt(
            idea, outline, index, prev_tail, chapter_words, context=block, card=card
        )
        response = await writer.ainvoke(prompt)
        # 正文走 WRITE 角色模型。提示词要求「直接输出正文」，此处不做清洗，只做类型
        # 归一化（个别模型会返回内容块列表而非纯字符串）。
        draft = response.content if isinstance(response.content, str) else str(response.content)
        # 写入 draft 但不入 chapters：只有过了正文闸门才由 commit_and_next 定稿，
        # 未定稿的稿子下一轮会被修补结果覆盖。
        ns["draft"] = draft
        _emit(
            EventType.THINKING,
            f"第 {index + 1} 章《{chapter.title}》初稿完成（约 {len(draft)} 字）",
            {
                "stage": "drafted",
                "chapter": index + 1,
                "scenes": len(card.scenes) if card else 0,
            },
        )
        return _update(ns)

    def _put_entry(ns: dict[str, Any], entry: dict[str, Any]) -> None:
        """按章号写入 extract 条目（同章覆盖而非追加）。

        修补回环会让同一章重跑 extract：正文换了，旧候选的逐字证据可能已经不在新正文里。
        追加会得到两条同章候选，而 ``write_canon`` 与 ``_pending_rows`` 都按章号取用，
        结果是「闸门用的是新候选、入库用的是旧候选」这类无法归因的分叉。
        """
        kept = [
            item
            for item in (ns.get("extractions") or [])
            if not (isinstance(item, dict) and item.get("chapter") == entry["chapter"])
        ]
        ns["extractions"] = [*kept, entry]

    def _entry_slot(ns: dict[str, Any], chapter_no: int) -> tuple[list[Any], int | None]:
        """本章的 extract 条目（列表 + 下标），找不到时下标为 ``None``。

        反向取最近的一条：同章条目按覆盖写，正常只有一条；倒着找让「重复条目」
        在链路里也稳定命中最新那次，而不是最旧那次。
        """
        entries = list(ns.get("extractions") or [])
        for position in range(len(entries) - 1, -1, -1):
            if isinstance(entries[position], dict) and entries[position].get("chapter") == chapter_no:
                return entries, position
        return entries, None

    async def extract_node(state: CoreState) -> dict[str, Any]:
        """正典抽取节点：从「当前章这一稿」抽候选增量，只攒不写。

        放在正文闸门之前、修补回环之内：闸门要比对「本章新增事实 vs 已确立事实」，
        所以候选必须先于闸门产出；而 revise 改完正文会重跑本节点——旧候选的逐字证据
        可能已经不在新正文里，不回 extract 就是让闸门拿假证据记账。
        本节点不写库：写库要等 book_id 与章节 id，而它们只在 archive 的 interrupt
        之后才存在。

        两道机制在这里落地：
        - 机制②证据强制：``filter_extraction`` 丢弃 evidenceQuote 不在正文中的断言，
          丢弃条数作为事件上浮（静默丢弃等于没有闸门）；
        - 机制③未知即缺口：正文引用未定义设定时由提示词登记 status="todo"，
          这里原样透传，不替它填空。
        抽取成功后顺手产出本章的层级摘要（``_digest_chapter``）：此刻正文就在上下文里，
        与抽取同批产完最省 token，摘要与候选一起攒着，等归档之后才落库。
        解析失败（模型不守契约 / 网络异常）时本章记为 None：该章不 commit 新事实。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter_no = index + 1
        content: str = ns["draft"]
        chapter_draft = ChapterDraft(index=chapter_no, title=outline[index].title, content=content)
        entry: dict[str, Any] = {
            "chapter": chapter_no,
            "content_hash": content_hash(content),
            "extraction": None,
            "dropped": 0,
        }
        try:
            extraction: ChapterExtraction = await extractor.ainvoke(
                extract_prompt(
                    idea,
                    outline[index],
                    index,
                    content,
                    known_entities=list(ns.get("entity_keys") or []),
                )
            )
        except Exception as exc:  # 结构化输出违约 / 调用失败：宁缺毋滥
            # 记 error 级而非 warning：这一章的事实将永久缺席，直到人工补录，
            # 是长程一致性上的真实损失，必须能在日志里被追到。
            logger.error("第 %s 章正典抽取失败，本章不入库新事实：%s", chapter_no, exc)
            _emit(
                EventType.THINKING,
                f"第 {chapter_no} 章正典抽取失败，本章不入库新事实（待人工补录）",
                {"stage": "extract_failed", "chapter": chapter_no},
            )
            _put_entry(ns, entry)
            return _update(ns)

        extraction, dropped = filter_extraction(extraction, chapter_draft.content)
        entry["extraction"] = extraction
        entry["dropped"] = dropped
        entry.update(await _digest_chapter(idea, outline[index], index, content))
        if dropped:
            _emit(
                EventType.THINKING,
                f"第 {chapter_no} 章丢弃 {dropped} 条无逐字证据的断言",
                {"stage": "extract_filtered", "chapter": chapter_no, "dropped": dropped},
            )
        # 累积实体键供下一章复用（谓词级去重，顺序保留便于复现）。
        keys = set(ns.get("entity_keys") or ())
        keys.update(a.subjectKey for a in extraction.assertions)
        keys.update(a.entityKey for a in extraction.aliases)
        keys.update(s.charKey for s in extraction.stateChanges)
        ns["entity_keys"] = sorted(keys)
        _put_entry(ns, entry)
        counts = {
            "assertions": len(extraction.assertions),
            "stateChanges": len(extraction.stateChanges),
            "aliases": len(extraction.aliases),
            "foreshadows": len(extraction.foreshadows),
        }
        _emit(
            EventType.THINKING,
            f"第 {chapter_no} 章正典抽取：{counts['assertions']} 条断言 / "
            f"{counts['stateChanges']} 项状态 / {counts['aliases']} 个称谓 / "
            f"{counts['foreshadows']} 处伏笔",
            {"stage": "extracted", "chapter": chapter_no, **counts},
        )
        return _update(ns)

    def _known_aliases(ns: dict[str, Any]) -> dict[str, str]:
        """本轮已登记的称谓表（称谓 → 实体键），供跨章别名漂移比对。

        圣经人物的中文名先入表（那是全书最早的一份称谓），其后是各章抽取候选。
        用 ``setdefault`` 而不是覆盖：保留**最早**那次认定，后来的章若把同一称谓
        指给别的实体，两份都在 merged 集合里，``check_alias_drift`` 才报得出来；
        覆盖会让漂移自我抹平（最坏的那种：越写越像没问题）。
        """
        table: dict[str, str] = {}
        for character in getattr(ns.get("bible"), "characters", ()) or ():
            table.setdefault(character.name, character.key)
        for entry in ns.get("extractions") or []:
            if not isinstance(entry, dict) or entry.get("extraction") is None:
                continue
            for alias in entry["extraction"].aliases:
                table.setdefault(alias.aliasText, alias.entityKey)
        return table

    async def gate_text_node(state: CoreState) -> dict[str, Any]:
        """正文双闸门节点（§9）：对「当前章这一稿」跑规则引擎 + 语义裁判。

        规则在前、裁判在后，两个理由：
        - 规则命中即事实，不必再让模型判一遍；把已命中的编码写进裁判提示词，
          省下的正是台账名额（同一处冲突两条来源各占一行，``per_code_limit`` 白烧）；
        - 规则零成本、裁判要烧 token，先用免费的挑明显问题（§9.1/§9.2 的分工
          本来就是按成本切的）。

        产物挂在**本章的 extract 条目**上（``findings``），与候选正典一起在归档后落库：
        Finding 的定位键是 chapter_id，而它只在 archive 的 interrupt 之后才存在
        （§8-⑦ 写后置）。

        闸门之后接放行策略（§9.3，判定本身在 :mod:`po_agent_novel.policy`，零 LLM）：
        blocker 可修补则回环到 revise，轮数用尽即冻结本章；major 把相抵的新候选降为
        ``disputed``；minor 只记录。判据与记账读同一份合并后的 ``findings``，
        不允许「按 A 判定、按 B 记账」。
        """
        ns = _ns(state)
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter_no = index + 1
        content: str = ns["draft"]
        entries, slot = _entry_slot(ns, chapter_no)
        current = entries[slot] if slot is not None else None
        view = ns.get("gate_view")
        gate_in = GateInput(
            text=content,
            chapter_no=chapter_no,
            extraction=(current or {}).get("extraction"),
            # 闸门视图取自本章写作者那一次装配：行集与编号都是那一次分给模型的这一份，
            # 不让节点自己再读一遍库（两份视图之间的差值会被当成冲突报出来，无法归因）。
            snapshot=tuple(getattr(view, "snapshot", ()) or ()),
            refs=tuple(getattr(view, "refs", ()) or ()),
            known_aliases=_known_aliases(ns),
            style=getattr(view, "style", None),
        )
        report = run_rules(gate_in, _rules_for(ns, gate_in.style))
        outcome = await run_judge(
            judge_model,
            gate_in,
            chapter=outline[index],
            rule_codes=[finding.code for finding in report.findings],
        )
        seen = {(finding.code, finding.textStart, finding.textEnd) for finding in report.findings}
        # 裁判重复报出规则已命中的同一处：留一条（来源取规则，因为它更便宜且不会变），
        # 否则台账里同一件事两行，作者会怀疑闸门坏了。
        extra = [
            finding
            for finding in outcome.findings
            if (finding.code, finding.textStart, finding.textEnd) not in seen
        ]
        findings = [*report.findings, *extra]
        repairs = int(ns.get("gate_repairs") or 0)
        release = decide_release(
            gate_in,
            findings,
            judge_failed=outcome.failed,
            repairs=repairs,
            policy=release_policy,
        )
        demoted = 0
        if current is not None and release.disputed and current.get("extraction") is not None:
            # 就地改写本章候选：L1 的 overlay 视图（_pending_rows）与入库载荷读的是同一份
            # 条目，等归档才降级会让后面几章照常注入这条被怀疑的事实。
            fresh, demoted = apply_disputed(current["extraction"], release.disputed)
            current = {**current, "extraction": fresh}
        if current is not None and release.action == "freeze":
            # 冻结＝本章事实不 commit。层级摘要一并作废：它与断言是「同一份已发生剧情」
            # 的两种载体，留摘要等于换条路把未经裁定的剧情注入后续章节。
            current = {**current, "extraction": None, "scenes": [], "digest": ""}
        gate_stats = {
            "rule": len(report.findings),
            "judge": len(outcome.findings),
            "duplicated": len(outcome.findings) - len(extra),
            "dropped": report.dropped + outcome.dropped_total,
            "skipped": {**report.skipped, **outcome.dropped},
            "words": report.words,
            "judge_failed": outcome.failed,
            "blockers": len(release.blockers),
            "majors": sum(1 for finding in findings if finding.severity == "major"),
            "disputed": demoted,
            "release": release.action,
            "unreviewed": release.unreviewed,
        }
        if current is None:
            # gate_text 只跑在 extract 之后，本章必有条目；走到这里说明链路自己坏了。
            # 不放行策略介入（没有条目可挂 blocker 与台账），但必须留 error 痕迹——
            # 静默放行正是 §8-⑧ 禁止的那种降级。
            logger.error("第 %s 章缺少 extract 条目，放行策略跳过本章（未拦截）", chapter_no)
            _emit(
                EventType.THINKING,
                f"第 {chapter_no} 章缺少抽取条目，闸门未拦截",
                {"stage": "gate_orphan", "chapter": chapter_no, **gate_stats},
            )
            return _update(ns)
        # 只改写本章那一条：extract 条目是 write_canon 的遍历依据（按章号对齐
        # chapter_ids），把台账挂在这里，落库时就与正典同批、同幂等口径。
        entries[slot] = {
            **current,
            "gate": gate_stats,
            "blockers": [finding.model_dump() for finding in release.blockers],
            # findings 在 extract 失败时是 None 之外的唯一残留：冻结章也要写台账，
            # 那正是人工要裁定的东西，不许随事实一起作废。
            "findings": [finding.model_dump() for finding in findings],
        }
        ns["extractions"] = entries
        ns["gate_repairs"] = repairs + 1 if release.action in ("patch", "rewrite") else 0
        # 条件边只读这一个键：路由判据留在闸门（有完整上下文的地方），
        # 而不是让 after_gate 去 entries 里翻 gate 字典。
        ns["gate_action"] = release.action
        if release.action == "freeze":
            ns["frozen"] = [*ns.get("frozen", []), chapter_no]
        _emit(
            EventType.THINKING,
            f"第 {chapter_no} 章闸门：规则 {gate_stats['rule']} 条 / "
            f"裁判 {len(extra)} 条 / blocker {gate_stats['blockers']} → {_release_label(release, repairs)}",
            {
                "stage": "gated",
                "chapter": chapter_no,
                "blockers": gate_stats["blockers"],
                "findings": len(findings),
                **gate_stats,
            },
        )
        return _update(ns)

    async def revise_node(state: CoreState) -> dict[str, Any]:
        """正文修补节点（§9.3）：只改闸门点出的片段，改完回 extract 重抽、回闸门重检。

        不整章重写是这条路径存在的全部理由：整章重写会把没问题的段落一起洗掉，既多烧
        token 又无从归因——§12 黄金集要统计的正是「闸门指出的那一处改掉没有」。
        整章级 blocker（空章、字数严重失控）没有片段可指，退化为一次整章重写，但**仍走
        本节点**：这样「修补」在链路里只有一个入口、一个计数点，轮数用尽后由闸门判冻结，
        不会出现两条路径各自数到一半。

        改的是 ``ns["draft"]`` 而不是 ``ns["chapters"]`` 里的那一章：定稿由
        commit_and_next 完成，此刻本章还没进成稿列表，回写按章号 splice 反而会写错位置。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter_no = index + 1
        entries, slot = _entry_slot(ns, chapter_no)
        current = entries[slot] if slot is not None else None
        blockers = [
            Finding.model_validate(row) for row in list((current or {}).get("blockers") or [])
        ]
        if current is None or not blockers:
            # gate_text 只在放行策略判 blocker 时才把路由指向本节点，且那时 blocker 已落进
            # 条目。走到这里说明状态被外部改写：不做任何猜测式修补，让 extract → gate
            # 重跑一遍自行收敛，但要留下 error 痕迹（静默跳章＝§8-⑧ 禁的降级）。
            logger.error("第 %s 章修补节点缺少 blocker 清单，跳过修补", chapter_no)
            _emit(
                EventType.THINKING,
                f"第 {chapter_no} 章跳过修补（缺 blocker 清单）",
                {"stage": "repaired", "chapter": chapter_no, "patched": 0, "skipped": True},
            )
            return _update(ns)
        text = ns["draft"]
        action = str((current.get("gate") or {}).get("release") or "rewrite")
        view = ns.get("gate_view")
        stats = {"patched": 0, "rejected": 0, "failed": 0, "overflow": 0}
        if action == "patch":
            plan, overflow = patch_plan(
                text, blockers, tuple(getattr(view, "refs", ()) or ()), release_policy
            )
            stats["overflow"] = overflow
            for target in plan:
                try:
                    response = await writer.ainvoke(
                        patch_prompt(
                            idea,
                            outline[index],
                            index,
                            before=target.before,
                            target=target.target,
                            after=target.after,
                            instruction=target.instruction or target.explanation,
                            canon_lines=list(target.canon_lines),
                        )
                    )
                except Exception as exc:
                    # 单个片段失败不影响其余片段：本轮少修一处，下一轮闸门会再次命中。
                    logger.error("第 %s 章片段修补调用失败：%s", chapter_no, exc)
                    stats["failed"] += 1
                    continue
                fragment = (
                    response.content if isinstance(response.content, str) else str(response.content)
                )
                patched = splice_patch(text, target, fragment)
                if patched is None:
                    # 空返回 / 与原文一致 / 长度异常（模型把整章重写了一遍）一律拒收：
                    # 收下它等于用「假装修好了」换掉一段没问题的正文。
                    stats["rejected"] += 1
                    continue
                text = patched
                stats["patched"] += 1
        else:
            try:
                response = await writer.ainvoke(
                    revise_prompt(
                        idea,
                        outline[index],
                        index,
                        text,
                        rewrite_feedback(blockers),
                        chapter_words,
                        context=getattr(view, "block", None),
                    )
                )
            except Exception as exc:
                logger.error("第 %s 章整章重写失败：%s", chapter_no, exc)
                stats["failed"] = 1
            else:
                rewritten = (
                    response.content if isinstance(response.content, str) else str(response.content)
                ).strip()
                # 整章重写只守「非空」这一条：字数越带归闸门下一轮判，在这里再设阈值
                # 就等于把放行判据抄进修补节点，两处会各说各话。
                if rewritten:
                    text = rewritten
                    stats["patched"] = 1
        ns["draft"] = text
        kind = "定向修补" if action == "patch" else "整章重写"
        _emit(
            EventType.THINKING,
            f"第 {chapter_no} 章{kind}：改写 {stats['patched']} 处 / "
            f"拒收 {stats['rejected']} 处 / 失败 {stats['failed']} 处",
            {"stage": "repaired", "chapter": chapter_no, "action": action, **stats},
        )
        return _update(ns)

    async def commit_node(state: CoreState) -> dict[str, Any]:
        """定稿节点（零 LLM）：把过闸的 draft 落成 ChapterDraft 并推进游标。

        旧版这一段长在 reflect 节点里，定稿判据与评分混在一起；§8-⑨ 废掉自评之后，
        「能不能定稿」只由 gate_text 的产物决定，于是定稿本身退化成一个纯状态搬运步骤。
        单独成节点是为了让**章号始终连续**：``index`` 只会 +1，不会出现「跳一章」
        而让 ``chapters`` 下标与 ``chapter_ids`` 对齐错位（那是 write_canon 的溯源键）。

        修补用尽而冻结的章也照走这里：正文是作者要看的成果，作废的是它的事实与摘要
        （gate_text 已把本章条目清成 extraction=None），不是稿子本身。
        """
        ns = _ns(state)
        outline: list[ChapterOutline] = ns["outline"]
        index: int = ns["index"]
        chapter = outline[index]
        content: str = ns["draft"]
        ns["chapters"] = [
            *ns["chapters"],
            # ChapterDraft.index 是 1 基（对外展示口径），此处完成 0 基 → 1 基转换。
            ChapterDraft(index=index + 1, title=chapter.title, content=content),
        ]
        ns["draft"] = ""
        ns["index"] = index + 1
        # action 只区分「是否收尾」：章节推进与归档两条路，判据留在这里一处。
        ns["action"] = "next" if ns["index"] < len(outline) else "archive"
        _, slot = _entry_slot(ns, index + 1)
        entry = (ns.get("extractions") or [])[slot] if slot is not None else {}
        _emit(
            EventType.THINKING,
            f"第 {index + 1} 章定稿（{(entry.get('gate') or {}).get('release', 'pass')}，"
            f"约 {len(content)} 字）",
            {
                "stage": "chapter_done",
                "chapter": index + 1,
                "release": (entry.get("gate") or {}).get("release", "pass"),
                "frozen": index + 1 in list(ns.get("frozen") or []),
                "advanced": ns["index"],
            },
        )
        return _update(ns)

    async def archive_node(state: CoreState) -> dict[str, Any]:
        """归档节点：人在环确认点——先 interrupt 等用户拍板，再决定是否落库。

        interrupt 会让整个图在此挂起（父图 checkpoint 记录断点），宿主把
        INTERRUPT 事件推给前端；用户回复后宿主以 ``Command(resume=value)``
        续跑，本节点从头重放，``interrupt(...)`` 返回 resume 值。
        因此 interrupt 之前的代码必须是无副作用的纯读取（这里只有 _ns），
        全部写库动作都排在它之后——重放一次就是一次真实写入，靠幂等键兜住。
        """
        ns = _ns(state)
        idea: BookIdea = ns["idea"]
        chapters: list[ChapterDraft] = ns["chapters"]
        # 冻结章在确认卡片上就要露头：这些章的正文会入库、事实不会，用户若在看完整本
        # 之后才知道「第 7 章的设定其实没被系统记住」，那是一本书最坏的一种意外。
        frozen = [int(no) for no in (ns.get("frozen") or [])]
        frozen_note = (
            f"第 {'、'.join(str(no) for no in frozen)} 章有未裁定的 blocker："
            "正文照常入库，但其设定与摘要不入库，冲突已进台账等你裁定。"
            if frozen
            else ""
        )
        unreviewed = [int(no) for no in (ns.get("plan_unreviewed") or [])]
        unreviewed_note = (
            f"第 {'、'.join(str(no) for no in unreviewed)} 章按计划写了，"
            "而那张计划卡没走完审查（你当时批准了继续）。"
            if unreviewed
            else ""
        )
        halted = ns.get("halted_at")
        halted_note = (
            f"第 {halted} 章的场景卡未获放行，全书在此停笔。" if halted else ""
        )
        if not chapters:
            # 一章都没定稿（开篇那张卡就被判停）：不挂确认点，也不建空书——
            # 0 章的书目会占住 book_id 并让后续 as-of 查询从一条空区间起步。
            _emit(EventType.THINKING, "计划停笔于第一章之前，全书未定稿，未归档", {"stage": "halted"})
            return {
                "artifacts": {NOVEL_KEY: ns},
                "messages": [
                    AIMessage(
                        content=f"《{idea.title}》未能开工：{halted_note or '第 1 章的计划未获放行。'}"
                        "已定稿章节为空，故不入库；构思与圣经仍保留在当前会话中。"
                    )
                ],
            }
        # 载荷即前端确认卡片的展示内容，必须可 JSON 序列化（会写进 checkpoint）；
        # question/hint 属协议约定字段：Runner 取 question 作为事件摘要，
        # hint 告知用户什么回复算「确认」（词表见 _APPROVE_WORDS）。
        approval = interrupt(
            {
                "question": (
                    f"《{idea.title}》共 {len(chapters)} 章已完稿"
                    + (f"（{len(frozen)} 章待人工裁定），是否归档入库？" if frozen else "，是否归档入库？")
                ),
                "title": idea.title,
                "genre": idea.genre,
                "chapter_count": len(chapters),
                "frozen": frozen,
                "frozen_note": frozen_note,
                # 计划侧的两类留痕也进卡片：停笔与「批准过的未审查章」都会在书里留下
                # 长期影响（缺章 / 没有计划依据的正文），只进事件流等于不给作者看。
                "plan_unreviewed": unreviewed,
                "unreviewed_note": unreviewed_note,
                "halted_at": halted,
                "halted_note": halted_note,
                "open_questions": list(getattr(ns.get("bible"), "openQuestions", ()) or ()),
                "hint": "确认归档请回复 yes，其他回复视为暂不归档",
            }
        )
        # 无论是否归档都拼出成稿全文，两种回执都能让用户直接读到结果。
        book_text = _book_text(idea, chapters)
        if _approved(approval):
            # 先抽角色再落库；save_book 返回的 book_id 是后续两次写入的外键，
            # 三者顺序不可调换，对应 Java novel 模块 book/chapter/character 的资源划分。
            extracted: CharacterList = await character_extractor.ainvoke(
                extract_characters_prompt(idea.title, chapters)
            )
            try:
                book_id = await store.save_book(
                    BookDraft(title=idea.title, genre=idea.genre, summary=idea.summary)
                )
                # 章节 id 是正典的溯源键（source_chapter_id）与幂等键的一部分，
                # 所以必须先拿到才能写正典。
                chapter_ids = await store.save_chapters(book_id, chapters)
                await store.save_characters(book_id, extracted.characters)
            except NovelStoreError as exc:
                # 成稿入库失败（重试已用尽）：把全文还给用户并说明原因，
                # 让他另起一次归档——正典尚未写入，重投不会双写。
                logger.error("成稿入库失败：%s", exc)
                _emit(EventType.THINKING, f"入库失败：{exc}", {"stage": "archive_failed"})
                reply = f"{book_text}\n\n入库失败（{exc}），成稿仍保留在当前会话中，请稍后重试归档。"
            else:
                canon_summary = await write_canon(
                    idea,
                    ns["outline"],
                    ns.get("bible"),
                    book_id,
                    chapters,
                    chapter_ids,
                    ns.get("extractions") or [],
                )
                # book_id 回写命名空间：便于中断恢复后的观测与后续续写引用。
                ns["book_id"] = book_id
                _emit(
                    EventType.THINKING,
                    f"已归档：{book_id}",
                    {
                        "stage": "archived",
                        "book_id": book_id,
                        "frozen": frozen,
                        "plan_unreviewed": unreviewed,
                        **canon_summary,
                    },
                )
                reply = (
                    f"{book_text}\n\n已归档入库（{book_id}，共 {len(chapters)} 章、"
                    f"{len(extracted.characters)} 名角色）。{canon_summary['canon_line']}"
                    + (f"\n\n{frozen_note}" if frozen_note else "")
                    + (f"\n\n{unreviewed_note}" if unreviewed_note else "")
                    + (f"\n\n{halted_note}" if halted_note else "")
                )
        else:
            # 暂不归档只是不落库：正文照样回给用户，作品仍留在本会话的 checkpoint 中。
            _emit(EventType.THINKING, "用户选择暂不归档", {"stage": "declined"})
            reply = f"{book_text}\n\n按你的要求暂不归档，本作保留在当前会话中。"
        # 本节点是子图中唯一向 messages 追加内容的节点（给用户最终回执），
        # 因此这里不走 _update，而是同时返回 artifacts 与 messages 两部分。
        return {"artifacts": {NOVEL_KEY: ns}, "messages": [AIMessage(content=reply)]}

    async def write_canon(
        idea: BookIdea,
        outline: list[ChapterOutline],
        bible: WorldBible | None,
        book_id: str,
        chapters: list[ChapterDraft],
        chapter_ids: list[str],
        extractions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """把书级圣经与 extract 攒下的候选增量、层级摘要逐章入库，返回一行用户可见的统计。

        圣经排在各章候选**之前**：它是后面每一章要比对的基线，而幂等键按章级发放，
        种子与增量互不遮挡。种子沿用 ``append_assertions``（as_of=1）而不是新开接口，
        Java 侧因此**不需要**任何协议改动（§15.6）。

        一章一次 append 是刻意的粒度：幂等键是「章级」的（chapter_id + 正文摘要），
        整本书一个键会让任何一章的修订把全书抽取结果一起判为重放。
        摘要走同一批 chapter_ids：它的 as-of 区间端点由服务端从章节行推导，
        因此也必须等章节 id 存在才写得进去。

        单章失败不终止归档：成稿已经落库，回滚反而丢掉用户已确认的成果；
        失败章记进 pending 上浮，交由人工重驱（同一键重投即命中幂等，不会双写）。
        """
        by_chapter = {
            entry.get("chapter"): entry
            for entry in extractions
            if isinstance(entry, dict)
        }
        inserted = skipped = 0
        summary_rows = 0
        finding_rows = 0
        pending: list[int] = []
        replayed: list[int] = []
        findings_failed: list[int] = []
        seed_rows = 0
        seed_failed = ""
        seed_replayed = False
        # 台账与正典的遍历域不同：冻结章与抽取失败章没有候选，但**必须**有台账——
        # 那张单子正是人工要裁定的东西，让它跟着事实一起作废就等于没人能裁定（§9.3）。
        if bible is not None and chapter_ids:
            seed = bible_extraction(bible)
            seed_source = ExtractionSource(
                chapter_id=chapter_ids[0],
                content_hash=content_hash(bible.model_dump_json()),
                prompt_version=PROMPT_VERSION,
                model=extractor_name,
            )
            try:
                outcome = await canon_store.append_assertions(
                    book_id, 1, seed, seed_source
                )
            except Exception as exc:
                # 种子失败不中断各章增量：圣经缺的是基线设定，各章事实照旧成立，
                # 但必须说给作者听——没有基线，后面每一章的比对口径都悄悄变松了。
                logger.error("书级圣经入库失败，本书缺正典基线：%s", exc)
                seed_failed = str(exc)
            else:
                seed_rows = outcome.inserted
                inserted += outcome.inserted
                skipped += outcome.skipped
                if not outcome.applied:
                    seed_replayed = True
        for position, chapter in enumerate(chapters):
            entry = by_chapter.get(chapter.index)
            # 章节 id 与正文按位置对齐；数据层返回的 id 数少于章节数属契约破坏，
            # 宁可跳过正典也不要把 id 猜错（猜错会写成别的章的溯源）。
            if entry is None or position >= len(chapter_ids):
                continue
            source = ExtractionSource(
                chapter_id=chapter_ids[position],
                content_hash=str(entry.get("content_hash") or content_hash(chapter.content)),
                prompt_version=PROMPT_VERSION,
                model=extractor_name,
            )
            payload = list(entry.get("findings") or [])
            if payload:
                # 台账排在正典之前：两者互不依赖，而正典失败会 continue 掉本章余下的写入，
                # 排在后面就等于「正典越不稳，台账越缺」——恰与裁定闭环的需要相反。
                try:
                    await canon_store.save_findings(
                        chapter_ids[position],
                        payload,
                        f"{chapter_ids[position]}:{source.content_hash}:findings",
                    )
                except Exception as exc:
                    # 台账缺章单独记账：它既不该拖正典的重驱（断言已入库），也不能默默
                    # 吞掉——没有台账的 blocker 等于没人裁定的冲突，§10 的裁定闭环无从开始。
                    logger.error("第 %s 章冲突台账入库失败：%s", chapter.index, exc)
                    findings_failed.append(chapter.index)
                else:
                    finding_rows += len(payload)
            if entry.get("extraction") is None:
                continue
            try:
                outcome = await canon_store.append_assertions(
                    book_id, chapter.index, entry["extraction"], source
                )
            except Exception as exc:
                logger.error("第 %s 章正典入库失败，待人工重驱：%s", chapter.index, exc)
                pending.append(chapter.index)
                continue
            inserted += outcome.inserted
            skipped += outcome.skipped
            # 幂等命中（applied=False）不是失败，但必须留痕：它意味着这一章的
            # 抽取此前已入库过（重放 / 重复归档），本次什么都没写。
            if not outcome.applied:
                logger.info(
                    "第 %s 章正典写入命中幂等键，未重复入库：%s",
                    chapter.index,
                    source.idempotency_key,
                )
                replayed.append(chapter.index)
            scenes = list(entry.get("scenes") or [])
            digest = entry.get("digest") or None
            try:
                await canon_store.save_chapter_summaries(
                    book_id, chapter_ids[position], chapter.index, scenes, digest
                )
            except Exception as exc:
                # 摘要入库失败不进 pending：它缺的是近因质量，不是事实一致性，
                # 重驱正典时不该把已经写好的断言再推一遍。
                logger.error("第 %s 章层级摘要入库失败：%s", chapter.index, exc)
            else:
                summary_rows += len(scenes) + (1 if digest else 0)
        arcs = await _write_arcs(book_id, idea, outline, len(chapters), by_chapter)
        line = f"正典入库 {inserted} 条"
        if seed_rows:
            line += f"（含书级圣经基线 {seed_rows} 条）"
        if seed_failed:
            line += f"；圣经基线入库失败（{seed_failed}），本书缺正典基线"
        if skipped:
            line += f"（{skipped} 条因唯一冲突跳过）"
        if summary_rows:
            line += f"；层级摘要 {summary_rows} 行" + (f"、弧级 {arcs} 段" if arcs else "")
        if finding_rows:
            line += f"；冲突台账 {finding_rows} 条"
        if findings_failed:
            line += f"；第 {'、'.join(str(p) for p in findings_failed)} 章台账入库失败，待重驱"
        if replayed or seed_replayed:
            labels = [f"第 {no} 章" for no in replayed]
            if seed_replayed:
                labels.insert(0, "圣经基线")
            line += f"；{'、'.join(labels)}为重放，未重复入库"
        if pending:
            line += f"；第 {'、'.join(str(p) for p in pending)} 章入库失败，待重驱"
        return {
            "canon_inserted": inserted,
            "canon_skipped": skipped,
            "canon_replayed": replayed,
            "canon_failed": pending,
            "seed_rows": seed_rows,
            "seed_failed": seed_failed,
            "seed_replayed": seed_replayed,
            "summary_rows": summary_rows,
            "arc_count": arcs,
            "finding_rows": finding_rows,
            "findings_failed": findings_failed,
            "canon_line": line,
        }

    async def _write_arcs(
        book_id: str,
        idea: BookIdea,
        outline: list[ChapterOutline],
        total_chapters: int,
        by_chapter: dict[Any, dict[str, Any]],
    ) -> int:
        """按大纲 arc 分组（缺名时按 ``arc_chapters`` 等分）合成弧级摘要，返回成功段数。

        输入只有章级摘要（正文一律不看）——arc 按定义就是「章摘要往上升一层」，
        再高就没有下一层可吃了，因此这里不存在套娃路径。
        跨度不越过已知最后一章，尾段不足一整弧照样合成：
        否则尾部章节永远进不了 Tier-0 的进度线，而 Tier-0 是唯一与书长无关的进度载体。
        """
        written = 0
        for arc_no, (start, end) in enumerate(
            _arc_spans(outline, total_chapters, arc_chapters), start=1
        ):
            pairs = [
                (no, by_chapter[no].get("digest"))
                for no in range(start, end + 1)
                if isinstance(by_chapter.get(no), dict) and by_chapter[no].get("digest")
            ]
            if not pairs:
                continue
            try:
                arc: ArcDigest = await arc_digester.ainvoke(
                    summarize_arc_prompt(idea, pairs, arc_no)
                )
                await canon_store.save_arc_summary(book_id, arc_no, start, end, arc.content)
            except Exception as exc:
                logger.error("第 %s 段弧摘要失败（第 %s-%s 章）：%s", arc_no, start, end, exc)
                continue
            written += 1
        return written

    def after_plan(state: CoreState) -> str:
        """gate_plan 后的条件边：放行策略的三态在这里落地。

        与 after_gate 的分工：这里判「这张打算怎么写的设计会不会报废」，那里判
        「已经写出来的这稿冲突改掉没有」。escalate 分支的 ``halt`` 不新增终点——
        它把 ``action`` 写成 archive 后走归档：已定稿的章是成果，停笔不等于失败，
        把它们交出去比挂在这里等一个回复更负责。
        """
        ns = _ns(state)
        action = ns.get("plan_action")
        if action == "replan":
            return PLAN_NODE
        if action == "halt":
            return ARCHIVE_NODE
        return WRITE_NODE

    def after_gate(state: CoreState) -> str:
        """gate_text 之后的条件边：正文放行策略的三态在这里落地。

        只有 patch/rewrite 多出一个分支去 revise；freeze 不新增终点——它已经由 gate_text
        作废了本章事实，链路照常进 commit_and_next，剩下的裁定发生在归档卡片
        和工作台上，而不是把整条链路挂在这里等一个回复。
        """
        if _ns(state).get("gate_action") in ("patch", "rewrite"):
            return REVISE_NODE
        return COMMIT_NODE

    def after_commit(state: CoreState) -> str:
        """commit_and_next 后的条件边：还有下一章就回到计划，全书写完进归档。"""
        return ARCHIVE_NODE if _ns(state).get("action") == "archive" else PLAN_NODE

    builder: StateGraph = StateGraph(CoreState)
    builder.add_node(CONCEIVE_NODE, conceive_node)
    builder.add_node(WORLDBUILD_NODE, worldbuild_node)
    builder.add_node(OUTLINE_NODE, outline_node)
    builder.add_node(PLAN_NODE, plan_scene_node)
    builder.add_node(GATE_PLAN_NODE, gate_plan_node)
    builder.add_node(WRITE_NODE, write_node)
    builder.add_node(EXTRACT_NODE, extract_node)
    builder.add_node(GATE_NODE, gate_text_node)
    builder.add_node(REVISE_NODE, revise_node)
    builder.add_node(COMMIT_NODE, commit_node)
    builder.add_node(ARCHIVE_NODE, archive_node)
    # 主干固定边：先定义（conceive → worldbuild → outline），再计划（plan_scene → gate_plan）。
    builder.add_edge(START, CONCEIVE_NODE)
    builder.add_edge(CONCEIVE_NODE, WORLDBUILD_NODE)
    builder.add_edge(WORLDBUILD_NODE, OUTLINE_NODE)
    builder.add_edge(OUTLINE_NODE, PLAN_NODE)
    builder.add_edge(PLAN_NODE, GATE_PLAN_NODE)
    # 计划闸门的三态：放行去写正文，重排回 plan_scene，停笔直接进归档。
    builder.add_conditional_edges(
        GATE_PLAN_NODE, after_plan, [WRITE_NODE, PLAN_NODE, ARCHIVE_NODE]
    )
    # 正文 → 抽正典 → 闸门是固定串行的三段：闸门必须在抽取之后（§8-①
    # 「只有 gate_text 通过的抽取才进正典」），而抽取的产物正是它的输入。
    builder.add_edge(WRITE_NODE, EXTRACT_NODE)
    builder.add_edge(EXTRACT_NODE, GATE_NODE)
    builder.add_conditional_edges(GATE_NODE, after_gate, [REVISE_NODE, COMMIT_NODE])
    # 修补回环（gate_text → revise → extract）：正文换了就重抽候选，
    # 旧候选的逐字证据在新正文里可能已经不存在——不回 extract 就是让闸门拿假证据记账。
    builder.add_edge(REVISE_NODE, EXTRACT_NODE)
    # 章节推进：定稿后下一章**从计划重新开始**（新章要新的场景卡，不是新的正文）。
    builder.add_conditional_edges(COMMIT_NODE, after_commit, [PLAN_NODE, ARCHIVE_NODE])
    builder.add_edge(ARCHIVE_NODE, END)
    return builder.compile()


__all__ = [
    "ARCHIVE_NODE",
    "COMMIT_NODE",
    "CONCEIVE_NODE",
    "EXTRACT_NODE",
    "GATE_NODE",
    "GATE_PLAN_NODE",
    "NODE_MODEL_ROLES",
    "NOVEL_KEY",
    "OUTLINE_NODE",
    "PLAN_NODE",
    "REVISE_NODE",
    "STAGE_ROLES",
    "WORLDBUILD_NODE",
    "WRITE_NODE",
    "bible_extraction",
    "build_novel_graph",
    "filter_extraction",
    "merge_gate_rules",
]
