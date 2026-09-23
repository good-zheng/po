"""垂直 Agent 插槽：领域子图接入 supervisor 的契约层。

领域包实现 ``VerticalAgent``（name + utterances + 已编译子图）后交给
``build_supervisor_graph`` 挂载为图节点。本包只声明与校验契约，
不装配任何领域依赖——领域侧的 model / tools / store 由领域包自行注入。
"""

from po_agent_core.agents.slots import VerticalAgent, VerticalAgentError

__all__ = ["VerticalAgent", "VerticalAgentError"]
