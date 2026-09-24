"""cooking 垂直 Agent 的 ReAct 子图。

结构::

    START → agent → (有工具调用?) → tools → agent → … → END
                     └─ 无 ────────→ END

状态直接复用 :class:`CoreState`：supervisor 把子图挂成节点时会做状态对接，
子图只认 ``messages``，领域数据一律不进 ``artifacts``（菜谱通过工具结果
文本回传，前端从 TOOL_CALL_RESULT 帧取，不需要第二条通路）。

与常见的 ``create_react_agent`` 相比，这里手写节点是为了控制两件事：

- **注入系统提示但不落库**：SystemMessage 每轮拼在窗口最前面，不进 state。
  若写进 state，checkpointer 会把它当普通消息层层累积，同一段提示词
  在长会话里会被重复塞进上下文几十次。
- **窗口裁剪到 HumanMessage 边界**：只按条数截断会产生「孤儿 ToolMessage」
  （工具结果还在、对应的 AIMessage 工具调用被截掉），多数 LLM 会直接报
  「tool_call_id 未找到」而让整轮对话失败。
"""

from __future__ import annotations

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from po_agent_core import CoreState
from po_agent_cooking.prompts import HISTORY_LIMIT, SYSTEM_PROMPT

AGENT_NODE = "agent"
TOOLS_NODE = "tools"


def _window(messages: list[Any], limit: int) -> list[Any]:
    """取最近 ``limit`` 条消息，并把窗口起点对齐到一条 HumanMessage。

    对齐的两个作用：一是保证发给模型的上下文以用户提问开头；
    二是让窗口内的 ToolMessage 一定能找到它的 AIMessage 工具调用。
    """
    if limit <= 0 or len(messages) <= limit:
        return list(messages)
    for index in range(len(messages) - limit, len(messages)):
        if isinstance(messages[index], HumanMessage):
            return list(messages[index:])
    # 窗口内一条 HumanMessage 都没有（异常情况）：退回不裁剪，
    # 宁可多花些上下文也不要发出残缺的工具调用序列
    return list(messages)


def build_cooking_graph(
    chat_model: BaseChatModel,
    tools: list[BaseTool],
    *,
    history_limit: int = HISTORY_LIMIT,
) -> CompiledStateGraph:
    """编译 cooking 子图。

    :param chat_model: 已按 ``cooking`` 角色解析好的聊天模型（或离线模型）
    :param tools: 经 ``build_recipe_tools`` 装配的菜谱工具
    :param history_limit: 每次调模型时回灌的历史条数上限
    """
    model_with_tools = chat_model.bind_tools(tools)

    async def agent_node(state: CoreState) -> dict[str, Any]:
        messages = _window(list(state.get("messages") or []), history_limit)
        response = await model_with_tools.ainvoke(
            [SystemMessage(content=SYSTEM_PROMPT), *messages]
        )
        return {"messages": [response]}

    builder: StateGraph = StateGraph(CoreState)
    builder.add_node(AGENT_NODE, agent_node)
    # ToolNode 默认读 state["messages"]，靠最后一条 AIMessage 的 tool_calls 执行；
    # 内部已捕获工具异常（返回错误 ToolMessage），与工具自身的 try/except 形成双层兜底
    builder.add_node(TOOLS_NODE, ToolNode(tools))

    builder.add_edge(START, AGENT_NODE)
    # tools_condition：末条 AIMessage 带 tool_calls → "tools"，否则结束（"__end__"）
    builder.add_conditional_edges(
        AGENT_NODE,
        tools_condition,
        {TOOLS_NODE: TOOLS_NODE, END: END},
    )
    builder.add_edge(TOOLS_NODE, AGENT_NODE)
    return builder.compile()
