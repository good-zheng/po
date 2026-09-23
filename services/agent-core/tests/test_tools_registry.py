from langchain_core.tools import tool

import pytest

from po_agent_core.tools.registry import ToolRegistrationError, ToolRegistry


@tool
def echo(text: str) -> str:
    """回显文本。"""
    return text


@tool
def lookup(keyword: str) -> str:
    """查询资料。"""
    return f"资料:{keyword}"


@tool("lookup")
def fast_lookup(keyword: str) -> str:
    """快速查询资料（novel 命名空间覆盖版）。"""
    return f"快:{keyword}"


def test_global_register_and_get() -> None:
    registry = ToolRegistry()
    registry.register(echo)
    assert registry.get("echo") is echo
    assert registry.list_names() == ["echo"]
    assert len(registry) == 1


def test_agent_namespace_overrides_global_in_tools_for() -> None:
    registry = ToolRegistry()
    registry.register(lookup)
    registry.register(fast_lookup, agent="novel")  # novel 命名空间同名覆盖

    # 同名以 Agent 命名空间优先；全局视角不受影响
    assert registry.get("lookup", agent="novel") is fast_lookup
    assert registry.get("lookup") is lookup
    assert registry.list_names("novel") == ["lookup"]

    # 其他 Agent 只见全局
    assert registry.list_names("other") == ["lookup"]


def test_duplicate_registration_rejected_unless_replace() -> None:
    registry = ToolRegistry()
    registry.register(echo)
    with pytest.raises(ToolRegistrationError, match="已注册"):
        registry.register(echo)
    registry.register(echo, replace=True)  # 覆盖不报错


def test_unregistered_lookup_raises() -> None:
    registry = ToolRegistry()
    with pytest.raises(ToolRegistrationError, match="不存在"):
        registry.get("nope")
    with pytest.raises(ToolRegistrationError, match="未注册"):
        registry.unregister("nope")


def test_unregister_scoped_to_namespace() -> None:
    registry = ToolRegistry()
    registry.register(lookup)
    registry.register(fast_lookup, agent="novel")
    registry.unregister("lookup", agent="novel")

    # novel 命名空间已清空：get 回退全局，全局注册不受影响
    assert registry.get("lookup", agent="novel") is lookup
    assert registry.list_names("novel") == ["lookup"]
