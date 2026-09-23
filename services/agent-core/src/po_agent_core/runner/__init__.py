"""运行器：LangGraph 流 → AgentEvent 统一事件流。

``AgentRunner.astream`` 是编排层对外的唯一执行入口；传输层
（WebSocket / A2A / MCP）只消费它产出的事件，不直接接触 LangGraph。
"""

from po_agent_core.runner.runner import AgentRunner

__all__ = ["AgentRunner"]
