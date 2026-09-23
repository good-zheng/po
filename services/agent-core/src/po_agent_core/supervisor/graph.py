"""Supervisor graph 工厂。

``START → route_node → (垂直 Agent 子图 | chitchat) → END``

- ``route_node``：取最后一条 HumanMessage，经 Layer1 意图路由
  （semantic-router 同步调用，``asyncio.to_thread`` 包裹避免阻塞事件循环）；
- 条件边：intent 命中某垂直 Agent 名即委托该子图，否则落 ``chitchat``；
- ``chitchat``：直接用 chat model 应答（降级路由/闲聊的统一兜底）；
- 单轮委托语义：Agent 执行完即 END。多轮工具循环在垂直 Agent 子图
  内部完成（generate→reflect 等骨架均属领域内部结构）。

checkpointer / store 由调用方创建后传入 compile，管理器生命周期
归宿主（见 ``memory`` 模块）。
"""

from __future__ import annotations

import asyncio
import logging
from typing import Iterable, Protocol

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.store.base import BaseStore

from po_agent_core.agents.slots import VerticalAgent, VerticalAgentError
from po_agent_core.supervisor.state import CoreState

logger = logging.getLogger(__name__)

CHITCHAT_NODE = "chitchat"
ROUTE_NODE = "route"


class RouterLike(Protocol):
    """Layer1 意图路由协议（见 routing.router.IntentRouter）。"""

    def route(self, text: str) -> object: ...


def _last_user_text(state: CoreState) -> str:
    """取最后一条用户消息：路由只看本轮输入，历史轮次不参与判定。

    倒序扫描而非取 ``messages[-1]``，因为末条通常是 AI 回复。
    """
    for message in reversed(state.get("messages") or []):
        if isinstance(message, HumanMessage):
            content = message.content
            return content if isinstance(content, str) else str(content)
    return ""


def _build_supervisor_graph(
    agents: Iterable[VerticalAgent],
    router: RouterLike,
    chat_model: BaseChatModel,
) -> StateGraph:
    builder: StateGraph = StateGraph(CoreState)
    agent_list = list(agents)
    agent_names = {agent.name for agent in agent_list}

    async def route_node(state: CoreState) -> dict[str, str | float]:
        text = _last_user_text(state)
        decision = await asyncio.to_thread(router.route, text)
        # RouterLike.route 的具体返回类型由 routing.RouteDecision 定义；
        # 此处以属性访问解耦（duck typing），便于宿主替换实现。
        intent = getattr(decision, "intent", None) or ""
        score = float(getattr(decision, "score", 0.0) or 0.0)
        logger.debug("路由决策：text=%r intent=%r score=%.3f", text[:50], intent, score)
        return {
            "intent": intent,
            "route_score": score,
            "agent_name": intent if intent in agent_names else CHITCHAT_NODE,
        }

    async def chitchat_node(state: CoreState) -> dict[str, list]:
        """兜底节点：直接用聊天模型应答，不发委托。

        所有未命中垂直 Agent 的消息（闲聊、以及降级路由下的全部消息）
        都收口到这里，保证图在任何配置下都有可用出口。
        """
        response = await chat_model.ainvoke(state.get("messages") or [])
        if not isinstance(response, AIMessage):
            response = AIMessage(content=str(response.content))
        return {"messages": [response]}

    def route_from_intent(state: CoreState) -> str:
        """条件边选路：命中已注册的 Agent 名才委托，否则去 chitchat。"""
        intent = state.get("intent", "")
        if intent and intent in agent_names:
            return intent
        return CHITCHAT_NODE

    builder.add_node(ROUTE_NODE, route_node)
    builder.add_node(CHITCHAT_NODE, chitchat_node)
    for agent in agent_list:
        # 子图直接以 Agent 名为节点挂载：LangGraph 自行对接父子状态，
        # 子图内的 interrupt 也会穿透到父图执行面
        builder.add_node(agent.name, agent.graph)

    builder.add_edge(START, ROUTE_NODE)
    builder.add_conditional_edges(
        ROUTE_NODE,
        route_from_intent,
        [*(agent.name for agent in agent_list), CHITCHAT_NODE],
    )
    for agent in agent_list:
        builder.add_edge(agent.name, END)
    builder.add_edge(CHITCHAT_NODE, END)
    return builder


def build_supervisor_graph(
    agents: Iterable[VerticalAgent],
    router: RouterLike,
    chat_model: BaseChatModel,
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    store: BaseStore | None = None,
) -> CompiledStateGraph:
    """编译 supervisor graph。

    :param agents: 垂直 Agent 插槽（name 与路由 Route.name 对齐）
    :param router: Layer1 意图路由器（routing.IntentRouter 或等价物）
    :param chat_model: chitchat 兜底用聊天模型
    :param checkpointer: 短期记忆（线程恢复/interrupt 状态）
    :param store: 长期记忆（user namespace 隔离）
    """
    agent_list = list(agents)
    names = [agent.name for agent in agent_list]
    if len(names) != len(set(names)):
        raise VerticalAgentError(f"垂直 Agent 名称重复：{names}")
    if CHITCHAT_NODE in names or ROUTE_NODE in names:
        raise VerticalAgentError(
            f"垂直 Agent 名称不得占用保留节点名：{ROUTE_NODE!r}/{CHITCHAT_NODE!r}"
        )
    builder = _build_supervisor_graph(agent_list, router, chat_model)
    return builder.compile(checkpointer=checkpointer, store=store)
