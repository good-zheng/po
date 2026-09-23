"""Supervisor：意图路由 + 垂直 Agent 委托 + chitchat 兜底。

``build_supervisor_graph(agents, router, chat_model)`` 编译出宿主实际运行的
编排图：START → route → (垂直 Agent 子图 | chitchat) → END。
``CoreState`` 是父子图共享的状态契约，领域数据一律进 ``artifacts``。
"""

from po_agent_core.supervisor.graph import build_supervisor_graph
from po_agent_core.supervisor.state import CoreState, merge_artifacts

__all__ = ["CoreState", "build_supervisor_graph", "merge_artifacts"]
