"""工具注册表：全局 + 垂直 Agent 命名空间两级。

MCP 外部工具（P3）经此注册表注入编排层；垂直 Agent 在构建子图时
按命名空间取用。注册发生在宿主装配期（启动阶段），运行期只读——
因此不做并发控制，换取零锁开销。
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

from po_agent_core.errors import AgentCoreError


class ToolRegistrationError(AgentCoreError):
    """工具注册冲突或删除不存在的工具。"""


class ToolRegistry:
    """两级工具注册表（global: name → tool；per-agent: agent → name → tool）。"""

    def __init__(self) -> None:
        self._global: dict[str, BaseTool] = {}
        self._by_agent: dict[str, dict[str, BaseTool]] = {}

    def register(
        self,
        tool: BaseTool,
        *,
        agent: str | None = None,
        replace: bool = False,
    ) -> None:
        """注册工具；``agent=None`` 注册到全局，否则绑定到指定垂直 Agent。"""
        if not tool.name:
            raise ToolRegistrationError("工具名不能为空")
        bucket = self._global if agent is None else self._by_agent.setdefault(agent, {})
        if tool.name in bucket and not replace:
            raise ToolRegistrationError(
                f"工具 {tool.name!r} 已注册"
                + (f"（agent={agent!r}）" if agent else "（全局）")
                + "，如需覆盖请传 replace=True"
            )
        bucket[tool.name] = tool

    def unregister(self, name: str, *, agent: str | None = None) -> None:
        bucket = self._global if agent is None else self._by_agent.get(agent)
        if bucket is None or name not in bucket:
            raise ToolRegistrationError(
                f"工具 {name!r} 未注册" + (f"（agent={agent!r}）" if agent else "（全局）")
            )
        del bucket[name]

    def get(self, name: str, *, agent: str | None = None) -> BaseTool:
        """取工具：优先 agent 命名空间，其次全局。"""
        if agent is not None:
            tool = self._by_agent.get(agent, {}).get(name)
            if tool is not None:
                return tool
        tool = self._global.get(name)
        if tool is None:
            raise ToolRegistrationError(f"工具 {name!r} 不存在")
        return tool

    def tools_for(self, agent: str | None = None) -> list[BaseTool]:
        """全局 + 指定 Agent 命名空间的全部工具（Agent 优先，同名覆盖全局）。"""
        if agent is None:
            return list(self._global.values())
        merged: dict[str, BaseTool] = dict(self._global)
        merged.update(self._by_agent.get(agent, {}))
        return list(merged.values())

    def list_names(self, agent: str | None = None) -> list[str]:
        return [tool.name for tool in self.tools_for(agent)]

    def __len__(self) -> int:
        return len(self._global) + sum(len(b) for b in self._by_agent.values())
