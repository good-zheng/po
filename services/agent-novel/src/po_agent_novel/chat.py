"""对话面板子图（§10.3 右栏）：读正典讨论设定，唯一产出是提议卡事件。

与 novel 插槽的分工是两条刻意分开的线：生成链路会写库、会产正文，本模块两者都不做。
它是「第二条通往记忆的路」（§1.2-⑤ 的头号污染形态），所以能力边界写在结构上而不是
只写在提示词里：

- **只读**：全程只调 ``NovelStore.load_book`` 与 ``CanonStore`` 的四个 ``load_*``，
  一次写库调用都没有（§12.4-1 的 ``test_chat_cannot_write_canon`` 用一个「写方法一律
  抛错」的哨兵 store 钉住这条）；
- **不产正文**（§10.3 约定 3）：确定性守门 :func:`_wants_prose` 拦掉明显的代写请求，
  语义边界（「把第 3 章那段改冷一点的说法」这类谈改法）仍由提示词负责；
- **不触发生成**：本图没有任何路径能启动 novel 子图，也不写 ``interrupt``。

设定结论以 ``PROPOSAL`` 事件上浮（payload 即 Java ``ProposalRequest`` 的字段名，
前端原样转发 ``POST /novel/proposals``）。**编排侧不写这张表**——提议卡入库与
「采纳才升 ``canon_entry``」都是服务端的事（§10.5-④），本图若顺手写库，
「作者点采纳」这个动作就从流程里消失了。

上下文与生成链路共用同一个 L1 编译器（§10.3 约定 2）：见 :func:`build_chat_context`。
分阶段模型：回答用规划脑（``plan``），提议抽取用判定脑（``judge``）——后者判的是
「这句讨论到底定论了没有」，与出题那颗脑同源时最容易把自说自话认成结论。
角色槽仍是现成的两个（§10.3 约定 4），没有为本面板新增词汇。

运行位置与 novel 子图一致：由宿主以 ``agent="novel-chat"`` 直连（工作台右栏固定这么发），
或经 supervisor 以子图节点挂载；checkpointer 由父图统一供给，本图 ``compile()`` 不挂 saver。
"""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from po_agent_core import AgentCoreSettings, VerticalAgent, create_chat_model
from po_agent_core.config import ModelRole
from po_agent_core.errors import AgentCoreError
from po_agent_core.events import EventType
from po_agent_core.supervisor.state import CoreState
from po_agent_novel.agent import _resolve_stores
from po_agent_novel.config import NovelStoreSettings
from po_agent_novel.context import compile_context
from po_agent_novel.gates import evidence_verbatim
from po_agent_novel.graph import _emit
from po_agent_novel.offline import OfflineNovelChatModel
from po_agent_novel.prompts import novel_chat_prompt, proposal_extract_prompt
from po_agent_novel.schemas import BookIdea, ProposalCandidate, ProposalList
from po_agent_novel.store import BookSnapshot, CanonStore, NovelStore

logger = logging.getLogger(__name__)

# 插槽名 = artifacts 命名空间键 = 前端在 WSInFrame.agent 里填的值。
NOVEL_CHAT_AGENT_NAME = "novel-chat"
NOVEL_CHAT_KEY = "novel-chat"

PREPARE_NODE = "prepare"
ANSWER_NODE = "answer"
PROPOSE_NODE = "propose"

# 本图用到的角色槽（装配期逐个建模型；任一角色不可用即整体降级）。
CHAT_ROLES: tuple[str, ...] = (ModelRole.PLAN, ModelRole.JUDGE)

# 回灌模型的历史条数上限。与 talk（12）同量级，但**不是**照抄它的「按条数截断」：
# 这里的窗口只负责对话连贯性，设定事实一律走 L1 注入块（§10.3 约定 4 明确要求
# novel-chat 是第一个接 L1 编译器的对话 agent）。
HISTORY_LIMIT = 12

# 「动词 + 近距离宾语」与「强动词 + 宾语任意位置」两种形态：后者专门收
# 「把下一章生成出来」这种宾语前置的说法，而它只认强动词——「写作」「重写」
# 这类词在日常讨论里太常见，配上一个「正文」就会误判。
_PROSE_VERBS = r"写|续写|生成|产出|输出|来"
_PROSE_STRONG_VERBS = r"续写|生成|产出|输出"
_PROSE_OBJECTS = r"正文|一章|这一章|下一章|第\s*\d+\s*章|一段|几千字|稿子|成稿"
_PROSE_ASK = re.compile(f"(?:{_PROSE_VERBS})[^\\n]{{0,10}}?(?:{_PROSE_OBJECTS})")
_PROSE_OBJECT = re.compile(f"(?:{_PROSE_OBJECTS})")
_PROSE_STRONG = re.compile(f"(?:{_PROSE_STRONG_VERBS})")
# 讨论标记：命中任意一个就认定这句是在谈而非要稿子，守门让位给模型。
_DISCUSSION = re.compile(
    r"(怎么|怎样|如何|为什么|为何|是否|能不能|可不可以|行不|什么|说法|思路|"
    r"建议|意见|讨论|聊聊|评价|梗概|大纲|摘要|分析|问题|对不对|好不好)"
)

PROSE_REFUSAL = (
    "正文由生成链路产出，请在中栏查看；这里只讨论。"
    "要的话我可以先给这一章的节拍、因果关系与可参照的已定稿句子。"
)

# 上行 context 里本领域认得的键（其余键一概不读，见 :func:`_context_of`）。
_CONTEXT_KEYS = ("bookId", "chapterId")


def _ns(state: CoreState) -> dict[str, Any]:
    """读取本插槽的领域命名空间（副本，理由同 ``graph._ns``）。"""
    namespace = (state.get("artifacts") or {}).get(NOVEL_CHAT_KEY)
    return dict(namespace) if isinstance(namespace, dict) else {}


def _update(ns: dict[str, Any]) -> dict[str, Any]:
    """节点返回值：整体替换本插槽的命名空间。"""
    return {"artifacts": {NOVEL_CHAT_KEY: ns}}


def _context_of(config: RunnableConfig | None) -> dict[str, str]:
    """从 ``configurable.context`` 取本轮定位键（bookId / chapterId）。

    走 configurable 而不是提示词前缀是必要的：宿主把非保留键拼进了用户消息文本
    （见 ``chat/app/agent.py`` 的 ``RESERVED_CONTEXT_KEYS``），而「读哪本书」这个决定
    不能交给一段模型看得见、也照得抄的文本——打字进去的假 id 不该决定任何库读。
    白名单同理：context 是客户端原样送上行的字典，只认这两个键，其余不解释。
    """
    raw = (config or {}).get("configurable") or {}
    context = raw.get("context")
    if not isinstance(context, dict):
        return {}
    picked: dict[str, str] = {}
    for key in _CONTEXT_KEYS:
        value = context.get(key)
        if isinstance(value, str) and value.strip():
            picked[key] = value.strip()
        elif isinstance(value, int) and not isinstance(value, bool):
            picked[key] = str(value)
    return picked


def _thread_id(config: RunnableConfig | None) -> str:
    """会话标识：提议卡 payload 的 ``sessionId``（仅回溯用）。"""
    return str(((config or {}).get("configurable") or {}).get("thread_id") or "")


def _num_or_str(value: str | None) -> int | str:
    """Java 侧 bookId 是 Long：纯数字就发数字，否则原样发字符串。

    发字符串前端也能转，但 §10.3 约定 1 的「payload 即 ProposalRequest 字段、
    前端原样转发」要求这里给出的形态就是接口要的形态。
    """
    if value is None:
        return ""
    return int(value) if value.isdigit() else value


def _last_question(state: CoreState) -> str:
    """本轮用户输入（逆序第一条 HumanMessage），也是代写守门的判据。"""
    for message in reversed(state.get("messages") or []):
        if isinstance(message, HumanMessage):
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


def _last_answer(state: CoreState) -> str:
    """本轮的讨论答复（逆序第一条 AIMessage），提议抽取的唯一证据来源。

    从消息里取而不是让 answer 节点写进命名空间：那段文本已经在 ``messages`` 里了，
    再存一份就是同一轮答复在 checkpoint 里躺两遍。
    """
    for message in reversed(state.get("messages") or []):
        if isinstance(message, AIMessage):
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


def _window(messages: Sequence[AnyMessage], limit: int) -> list[AnyMessage]:
    """取最近 ``limit`` 条对话消息，窗口起点对齐到一条 HumanMessage。

    起点必须是人话：从 AI 回答中间切开，模型看到的是半句结论而无提问，
    多轮讨论最容易在这里跑偏。
    """
    pairs = [m for m in messages if isinstance(m, (HumanMessage, AIMessage))]
    if limit <= 0 or len(pairs) <= limit:
        return pairs
    for start in range(len(pairs) - limit, len(pairs)):
        if isinstance(pairs[start], HumanMessage):
            return list(pairs[start:])
    return pairs


def _wants_prose(question: str) -> bool:
    """确定性代写守门：只在「明显是要求产正文」时命中。

    三层收窄（代写形态命中 + 无讨论标记 + 不是问句）是刻意的：误判的代价是把作者
    正当的讨论挡在门外（「把第 3 章那段改冷一点的说法」正是必须放行的那句），
    而漏判的代价小得多——提示词里已经要求模型自己回那句引导。
    """
    if not question.strip():
        return False
    if _DISCUSSION.search(question):
        return False
    if "？" in question or "?" in question:
        return False
    if _PROSE_ASK.search(question):
        return True
    # 宾语前置的形态：动词与宾语分处两句，只有强动词才算（「写」太常见）
    return bool(_PROSE_STRONG.search(question) and _PROSE_OBJECT.search(question))


@dataclass(frozen=True, slots=True)
class ChatScope:
    """一轮对话的装配结果（``build_chat_context`` 的返回，也是 §10.3-② 的验证面）。

    ``error`` 非空即「本轮没有可用正典」，且原因已经写在里面；调用方必须把它发成
    可见事件——静默降级成「不带注入地回答」正是 §12.2 断链可见性要禁的东西。
    """

    book: BookSnapshot | None = None
    as_of: int | None = None
    block: str | None = None
    tokens: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    error: str | None = None


async def build_chat_context(
    novel_store: NovelStore,
    canon_store: CanonStore,
    *,
    book_id: str | None,
    chapter_id: str | None = None,
) -> ChatScope:
    """按「当前参照章」装配注入块：与生成链路同一个编译器、同一套编号（§10.3-②）。

    与写侧 :func:`po_agent_novel.context.compile_context` 的关系是「同一个函数、
    不同的一次调用」，因此对话与生成拿到的是同一份预算、同一套 ``[canon#N]``：
    不允许聊天窗知道得比生成链路多，否则作者在工作台对不上答案，等于人肉制造 C6。

    两处与生成侧刻意不同：
    - ``entities=None``（全量 as-of 快照）：讨论没有场景卡，挑实体就是猜实体，
      而猜出来的键会让 Tier-1 命中一堆无关断言（§6-1）；
    - ``task_chapter`` 由参照章给出：任务区不再出大纲，近因尾段取**这一章**的末尾。
      生成链路永不传这个参数。

    每轮都重读一次、不缓存注入块也是必要的：作者可能在两轮之间采纳一张卡或改了正文，
    缓存会让下一轮讨论建立在一份已经过期的正典上，而这种过期永远不会报错。
    """
    if not book_id:
        return ChatScope(error="no_book")
    try:
        book = await novel_store.load_book(book_id, chapter_id=chapter_id)
    except Exception as exc:
        # 读不回书目就当本轮没有书：提示词据此改口为「没有可依据的正典」。
        return ChatScope(error=f"load_book_failed：{exc}")
    # as-of 的唯一支点仍是章号：有参照章就用它，没有就退回「已归档章数」
    # （即「全书目前定稿到哪」）。参照章的正文可能晚于任何未定稿内容，
    # 但 load_book 只回已入库的章，所以这里不需要再判一次上界——编译器会兜。
    as_of = book.chapter.index if book.chapter is not None else book.chapter_count
    try:
        compiled = await compile_context(
            canon_store,
            book_id=book.book_id,
            idea=_idea(book),
            outline=(),
            index=as_of,
            chapters=(),
            task_chapter=book.chapter,
        )
    except Exception as exc:
        # 书目读到了、正典没读到：仍然回答（作者看得见书名），但必须说明没有事实可引。
        return ChatScope(book=book, as_of=as_of, error=f"compile_failed：{exc}")
    return ChatScope(
        book=book,
        as_of=as_of,
        block=compiled.block,
        tokens=compiled.tokens,
        counts=dict(compiled.counts),
    )


def _idea(book: BookSnapshot) -> BookIdea:
    """书目元数据 → 提示词要的「世界观与主线」背景。

    ``BookIdea`` 三个字段都有 ``min_length`` 下限，空串过不了校验；用「未登记」
    而不是补一个像样的说法，是因为 Tier-0 那一行会原样进提示词——编译器不许替
    作者把空白填成设定。
    """
    return BookIdea(
        title=book.title or "（书名未登记）",
        genre=book.genre or "（题材未登记）",
        summary=book.summary or "（梗概未登记）",
    )


def _book_of_ns(ns: dict[str, Any]) -> BookSnapshot | None:
    """从命名空间重建提示词用的书目（没带 bookId 时为 ``None``）。

    命名空间里只放原始类型：checkpoint 的 msgpack 对未注册类型会告警且未来版本将直接
    拒绝，把 dataclass 塞进 ``artifacts`` 等于押在一个第三方库的白名单策略上。
    参照章的正文也不进命名空间——它只以近因尾段的形态活在注入块里，再存一份就是
    把 300 字搬进 checkpoint，而提示词只需要书名/题材/梗概/归档数这四个字段。
    """
    book_id = ns.get("book_id")
    if not book_id:
        return None
    return BookSnapshot(
        book_id=str(book_id),
        title=str(ns.get("title") or ""),
        genre=str(ns.get("genre") or ""),
        summary=str(ns.get("summary") or ""),
        chapter_count=int(ns.get("chapter_count") or 0),
        chapter=None,
    )


def build_novel_chat_graph(
    stage_models: dict[str, BaseChatModel],
    novel_store: NovelStore,
    *,
    canon_store: CanonStore,
    history_limit: int = HISTORY_LIMIT,
) -> CompiledStateGraph:
    """编译对话面板子图（prepare → answer →（propose）→ END）。

    :param stage_models: 角色槽 → 模型（键见 :data:`CHAT_ROLES`）；
        ``plan`` 出讨论回答，``judge`` 判哪些结论该进正典
    :param novel_store: 成稿数据层，本图只用它的 ``load_book`` 读口
    :param canon_store: 正典数据层，本图只用它的 ``load_*`` 读口（经 L1 编译器）
    :param history_limit: 回灌的对话消息条数上限（只管连贯性，不管事实）
    """
    responder = stage_models[ModelRole.PLAN]
    # 抽取走结构化绑定（与生成侧的裁判/抽取节点同法）：直接 ainvoke 拿到的是
    # AIMessage，那张「提议卡」会在下一次重构里静默变成 result.proposals  AttributeError。
    # method 同样必须显式写：缺省的 json_schema response_format 会被 DeepSeek 拒 400，
    # 表现为工作台永远提不出设定卡。
    proposer = stage_models[ModelRole.JUDGE].with_structured_output(
        ProposalList, method="function_calling"
    )

    async def prepare_node(state: CoreState, config: RunnableConfig) -> dict[str, Any]:
        """装配节点：定位键 → 书目 + 注入块，并把结果摊平成原始类型存进命名空间。"""
        keys = _context_of(config)
        scope = await build_chat_context(
            novel_store,
            canon_store,
            book_id=keys.get("bookId"),
            chapter_id=keys.get("chapterId"),
        )
        ns = _ns(state)
        ns["book_id"] = keys.get("bookId")
        ns["as_of"] = scope.as_of
        ns["block"] = scope.block
        ns["prose_refused"] = False
        if scope.book is not None:
            ns["title"] = scope.book.title
            ns["genre"] = scope.book.genre
            ns["summary"] = scope.book.summary
            ns["chapter_count"] = scope.book.chapter_count
        if scope.error:
            # 降级必须可见：作者看到的是一句「这一轮没有正典可引」，而不是一个
            # 看起来正常、其实全靠模型记忆的答复。
            _emit(
                EventType.THINKING,
                f"对话上下文装配失败（{scope.error}），本轮答复不引用任何已登记设定",
                {"stage": "chat_context_failed", "path": "chat", "book_id": keys.get("bookId")},
            )
        else:
            counts = scope.counts
            _emit(
                EventType.THINKING,
                f"对话上下文已装配：截至第 {scope.as_of} 章，注入 {scope.tokens} token"
                f"（设定 {counts.get('tier1', 0)} 条 / 近因 {counts.get('tier2', 0)} 条）",
                {
                    "stage": "chat_context_compiled",
                    "path": "chat",
                    "as_of": scope.as_of,
                    "tokens": scope.tokens,
                    **counts,
                },
            )
        return _update(ns)

    async def answer_node(state: CoreState) -> dict[str, Any]:
        """讨论节点：注入块作系统提示词，历史窗口只作连贯性底。"""
        ns = _ns(state)
        question = _last_question(state)
        if _wants_prose(question):
            ns["prose_refused"] = True
            _emit(
                EventType.THINKING,
                "识别为「要正文」的请求：按约定只回引导，不调模型",
                {"stage": "chat_prose_refused"},
            )
            return {"messages": [AIMessage(content=PROSE_REFUSAL)], **_update(ns)}
        prompt = novel_chat_prompt(_book_of_ns(ns), ns.get("block"), ns.get("as_of"))
        # 注入块每轮重拼、不进消息历史：把整块塞回 messages 会让下一轮的历史里
        # 躺着两份旧正典，而旧快照与本轮快照的 [canon#N] 编号并不同源。
        response = await responder.ainvoke(
            [SystemMessage(content=prompt), *_window(state.get("messages") or [], history_limit)]
        )
        content = response.content if isinstance(response.content, str) else str(response.content)
        return {"messages": [AIMessage(content=content)], **_update(ns)}

    async def propose_node(state: CoreState, config: RunnableConfig) -> dict[str, Any]:
        """提议抽取节点：把本轮结论结构化，逐张卡做依据逐字校验后上浮事件。"""
        ns = _ns(state)
        answer = _last_answer(state)
        book_id = ns.get("book_id")
        if not answer:
            return _update(ns)
        try:
            result: ProposalList = await proposer.ainvoke(
                proposal_extract_prompt(_book_of_ns(ns), answer)
            )
        except Exception as exc:
            # 抽不出卡不影响答复已经送到作者手里；但要说一句，
            # 否则「这次讨论本来该有条设定」会永远无人知晓。
            logger.error("提议抽取失败（book=%s）：%s", book_id, exc)
            _emit(
                EventType.THINKING,
                "设定结论抽取失败，本轮没有可采纳的提议卡",
                {"stage": "chat_proposal_failed", "path": "chat", "book_id": book_id},
            )
            return _update(ns)
        kept: list[ProposalCandidate] = []
        dropped = 0
        for candidate in result.proposals:
            # 依据校验（机制② 的对话侧版本）：一张依据不在这轮讨论里的卡，作者采纳时
            # 无法复核它说的是什么，§10.5-④ 的冲突预览也救不了这种凭空结论。
            if evidence_verbatim(candidate.basisQuote, answer):
                kept.append(candidate)
            else:
                dropped += 1
        as_of = ns.get("as_of")
        session_id = _thread_id(config)
        for candidate in kept:
            _emit(
                EventType.PROPOSAL,
                f"{candidate.subjectKey} · {candidate.predicate} · {candidate.objectText}",
                {
                    "bookId": _num_or_str(str(book_id)),
                    "sessionId": session_id,
                    "asOfChapter": as_of,
                    "kind": candidate.kind,
                    "subjectKey": candidate.subjectKey,
                    "predicate": candidate.predicate,
                    "objectText": candidate.objectText,
                    # 生效起点由出卡时的参照章决定，不让模型自报章号（§10.3 约定 1）
                    "validFromChapter": as_of,
                    "basisQuote": candidate.basisQuote,
                },
            )
        _emit(
            EventType.THINKING,
            f"本轮产生 {len(kept)} 张待采纳提议卡"
            + (f"（{dropped} 条依据无法逐字对上讨论原文，已丢弃）" if dropped else ""),
            {
                "stage": "chat_proposals",
                "path": "chat",
                "proposals": len(kept),
                "dropped": dropped,
            },
        )
        return _update(ns)

    def after_answer(state: CoreState) -> str:
        """代写请求与「没选书」都不进提议抽取：前者没结论，后者无处挂卡。

        没有 bookId 就出卡会产出一张 ``POST /novel/proposals`` 拒收（或更糟：挂到
        错书）的卡，所以宁可不抽。
        """
        ns = _ns(state)
        if ns.get("prose_refused") or not ns.get("book_id"):
            return END
        return PROPOSE_NODE

    builder: StateGraph = StateGraph(CoreState)
    builder.add_node(PREPARE_NODE, prepare_node)
    builder.add_node(ANSWER_NODE, answer_node)
    builder.add_node(PROPOSE_NODE, propose_node)
    builder.add_edge(START, PREPARE_NODE)
    builder.add_edge(PREPARE_NODE, ANSWER_NODE)
    builder.add_conditional_edges(ANSWER_NODE, after_answer, [PROPOSE_NODE, END])
    builder.add_edge(PROPOSE_NODE, END)
    return builder.compile()


def _build_chat_models(settings: AgentCoreSettings) -> dict[str, BaseChatModel]:
    """按角色装配对话侧模型；任一角色不可用即整体降级（与 novel 侧同规则）。

    部分降级会得到「真模型讨论 + 占位模型出卡」的混合链路，而占位模型恒不出卡，
    于是作者看到的是一轮看起来正常、永远没有提议卡的讨论——比统一离线更难排查。
    """
    models: dict[str, BaseChatModel] = {}
    for role in CHAT_ROLES:
        try:
            models[role] = create_chat_model(settings, role=role)
        except AgentCoreError as exc:
            logger.warning("角色 %s 的模型不可用，对话面板降级为离线模式：%s", role, exc)
            return dict.fromkeys(CHAT_ROLES, OfflineNovelChatModel())
    logger.info(
        "对话面板阶段模型：%s",
        "，".join(f"{role}={getattr(m, 'model_name', type(m).__name__)}" for role, m in models.items()),
    )
    return models


def build_novel_chat_agent(
    settings: AgentCoreSettings | None = None,
    *,
    chat_model: BaseChatModel | None = None,
    store: NovelStore | None = None,
    canon_store: CanonStore | None = None,
    novel_settings: NovelStoreSettings | None = None,
    history_limit: int = HISTORY_LIMIT,
) -> VerticalAgent:
    """装配对话面板插槽（宿主第三个内置插槽，§10.3 约定 4）。

    依赖注入与 novel 插槽同构，且**共用 :func:`po_agent_novel.agent._resolve_stores`**：
    成稿与正典要么都打 Java、要么都留在进程内。两个插槽各持一份 store 实例是允许的
    （都是无状态客户端），但配置解析只有一份——否则「书在库里、正典在某个进程内存里」
    这种分裂会在两次装配里各解一半。

    :param chat_model: 显式注入模型（测试桩）：传入即两个角色共用同一实例，
        既不触发离线降级也不读 ``llm_roles``
    :param store: 成稿数据层（只用读口）
    :param canon_store: 正典数据层（只用读口）
    :param novel_settings: ``NOVEL_*`` 配置；``persist_enabled`` 为真时两个 store 都指向 Java
    :param history_limit: 回灌历史条数上限
    :return: ``utterances`` 为空的插槽——不参与 Layer1 意图路由，只接受直连
    """
    settings = settings or AgentCoreSettings()
    if chat_model is not None:
        stage_models: dict[str, BaseChatModel] = dict.fromkeys(CHAT_ROLES, chat_model)
    else:
        stage_models = _build_chat_models(settings)
    novel_store, resolved_canon = _resolve_stores(store, canon_store, novel_settings)
    graph = build_novel_chat_graph(
        stage_models,
        novel_store,
        canon_store=resolved_canon,
        history_limit=history_limit,
    )
    # 不配语料是刻意的：本面板的讨论用语与 novel 插槽的生成用语高度重叠（都在谈同一本书），
    # 而误命中的代价是「作者想生成却被当成讨论」——少一次生成比多一次误判贵。
    # 正确入口是工作台的显式直连（WSInFrame.agent="novel-chat"），通用聊天窗够不到它。
    return VerticalAgent(
        name=NOVEL_CHAT_AGENT_NAME,
        description="小说讨论：读正典与已定稿章节回答设定问题，产出待采纳的提议卡（不写正文、不写正典）",
        graph=graph,
        utterances=(),
        metadata={"roles": ",".join(CHAT_ROLES)},
    )


__all__ = [
    "ANSWER_NODE",
    "CHAT_ROLES",
    "HISTORY_LIMIT",
    "NOVEL_CHAT_AGENT_NAME",
    "NOVEL_CHAT_KEY",
    "PREPARE_NODE",
    "PROPOSE_NODE",
    "PROSE_REFUSAL",
    "ChatScope",
    "build_novel_chat_agent",
    "build_novel_chat_graph",
    "build_chat_context",
]
