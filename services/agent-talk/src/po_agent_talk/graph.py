"""言外 Agent 的子图：单节点（无工具）。

结构::

    START → agent → END

刻意不用 ReAct：本 Agent 的输入是「对方的一句话」，不需要外部工具检索，
一次模型调用即可产出完整 JSON。引入工具循环只会增加延迟，而段级触发的
体验目标（3.5s 内出卡片）容不下多余的一跳。

与 cooking 子图一致的两处处理：

- **系统提示不落库**：每轮拼在窗口最前面，不进 state，避免被 checkpointer
  层层累积；
- **窗口对齐到 HumanMessage 边界**：避免截断出「没有提问的半截上下文」。

领域结果不写 ``artifacts``：结构化输出就是 AIMessage 的文本（纯 JSON），
前端把 token 拼起来直接解析，不需要第二条回传通路。
"""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from po_agent_core import CoreState
from po_agent_talk.prompts import HISTORY_LIMIT, build_system_prompt

AGENT_NODE = "agent"


def _window(messages: list[Any], limit: int) -> list[Any]:
    """取最近 ``limit`` 条消息，并把窗口起点对齐到一条 HumanMessage。"""
    if limit <= 0 or len(messages) <= limit:
        return list(messages)
    for index in range(len(messages) - limit, len(messages)):
        if isinstance(messages[index], HumanMessage):
            return list(messages[index:])
    return list(messages)


def build_talk_graph(
    chat_model: BaseChatModel,
    *,
    history_limit: int = HISTORY_LIMIT,
) -> CompiledStateGraph:
    """编译言外子图。

    :param chat_model: 已按 ``talk`` 角色解析好的模型（或离线降级模型）
    :param history_limit: 每次调模型回灌的历史条数上限
    """
    system_prompt = build_system_prompt()

    async def agent_node(state: CoreState) -> dict[str, Any]:
        messages = _window(list(state.get("messages") or []), history_limit)
        response = await chat_model.ainvoke(
            [SystemMessage(content=system_prompt), *messages]
        )
        return {"messages": [response]}

    builder: StateGraph = StateGraph(CoreState)
    builder.add_node(AGENT_NODE, agent_node)
    builder.add_edge(START, AGENT_NODE)
    builder.add_edge(AGENT_NODE, END)
    return builder.compile()
