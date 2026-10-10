"""Supervisor 共享状态（CoreState）。

参考实现（novel_server）的教训：20+ 字段的 State 上帝对象导致任何节点
都能读写一切。这里 CoreState 只保留编排必需的五类字段：

- ``messages``：对话消息（LangGraph ``add_messages`` 归并）；
- ``intent`` / ``route_score``：Layer1 路由决策结果；
- ``agent_name``：本次委托的垂直 Agent 名（观测用）；
- ``forced_agent``：调用方点名的插槽名（直连提示，见下）；
- ``artifacts``：各垂直 Agent 的私有数据，按 agent 名分命名空间，
  supervisor 不解释内容——领域状态进 ``artifacts[agent_name]``，
  禁止向 CoreState 添加领域字段。
"""

from __future__ import annotations

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


def merge_artifacts(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """artifacts 归并：浅合并，同名命名空间整体替换（后写胜出）。"""
    return {**left, **right}


class CoreState(TypedDict, total=False):
    """supervisor 图的状态：字段刻意维持在「编排必需」的最小集合。

    ``total=False`` 允许节点只返回自己改动的那几个键，
    LangGraph 按字段上的 reducer 归并（messages 追加、artifacts 浅合并）。
    """

    messages: Annotated[list[AnyMessage], add_messages]
    intent: str  # 路由命中意图（未命中为空串）
    route_score: float  # 路由分数，排查「差一点命中」用
    agent_name: str  # 实际被委托的节点名（观测用，兜底时为 chitchat）
    # 入站提示而非节点产物：客户端已点名插槽时由调用方随初始状态传入，
    # route 节点据此跳过语义路由。空串/缺省即「按路由选」，与旧行为一致。
    forced_agent: str
    artifacts: Annotated[dict[str, Any], merge_artifacts]
