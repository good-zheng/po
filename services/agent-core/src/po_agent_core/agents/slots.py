"""垂直 Agent 插槽定义。

垂直 Agent = supervisor 之下的一个领域子图。插槽契约：

- ``name`` 必须与 Layer1 路由的 ``Route.name`` 一致（命中即委托）；
- ``utterances`` 是 Layer1 意图路由的语料（典型用户说法），
  宿主经 ``routing.routes_from_agents`` 派生 Route 列表；为空表示
  该 Agent 不参与意图路由（仅供直连调用/测试）；
- ``graph`` 是已编译的 LangGraph 子图，状态 schema 与 ``CoreState``
  兼容（至少接受/返回 ``messages``，领域私有数据写入 ``artifacts[name]``）；
- 子图内部的 ``interrupt()`` 会沿父子关系穿透到 supervisor 的执行面
  （由 Runner 翻译为 INTERRUPT 事件）。

构建子图所需的 chat model、tools、store 等依赖由领域侧在编译前
自行注入——插槽不做装配，只做契约声明与校验。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from langgraph.graph.state import CompiledStateGraph

from po_agent_core.errors import AgentCoreError


class VerticalAgentError(AgentCoreError):
    """垂直 Agent 插槽注册契约违反。"""


@dataclass(frozen=True, slots=True)
class VerticalAgent:
    name: str
    description: str
    graph: CompiledStateGraph
    # Layer1 意图路由语料（典型用户说法）；空 = 不参与意图路由
    utterances: tuple[str, ...] = ()
    # 提示词等静态资源挂在 metadata，supervisor 不解释（预留扩展位）
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise VerticalAgentError("垂直 Agent name 不能为空")
        if self.name.startswith("__"):
            raise VerticalAgentError(
                f"垂直 Agent name {self.name!r} 不得以 __ 开头（LangGraph 保留前缀）"
            )
        if not self.description:
            raise VerticalAgentError(f"垂直 Agent {self.name!r} 缺少 description（路由语料与 AgentCard 均依赖它）")
        if not isinstance(self.graph, CompiledStateGraph):
            raise VerticalAgentError(
                f"垂直 Agent {self.name!r} 的 graph 必须是 CompiledStateGraph（先 StateGraph(...).compile()）"
            )
        for utterance in self.utterances:
            if not isinstance(utterance, str) or not utterance.strip():
                raise VerticalAgentError(
                    f"垂直 Agent {self.name!r} 的 utterances 含空语料：{self.utterances!r}"
                )
