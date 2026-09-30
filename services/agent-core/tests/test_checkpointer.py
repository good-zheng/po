"""CheckpointerManager 测试：memory/sqlite 全覆盖，redis 连接按环境变量门控。

CI 无 Redis service：redis 相关断言仅验证“延迟初始化不产生连接”，
真实连接测试需设置 ``AGENT_CORE_TEST_REDIS=1`` 且本机 Redis 可达。
"""

import os

import pytest
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from po_agent_core.config import AgentCoreSettings
from po_agent_core.memory.checkpointer import CheckpointerManager


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_echo_graph(checkpointer) -> object:
    builder = StateGraph(ChatState)

    async def echo(state: ChatState) -> dict:
        return {"messages": [HumanMessage(content=f"echo:{state['messages'][-1].content}")]}

    builder.add_node("echo", echo)
    builder.add_edge(START, "echo")
    builder.add_edge("echo", END)
    return builder.compile(checkpointer=checkpointer)


def memory_manager() -> CheckpointerManager:
    return CheckpointerManager(
        AgentCoreSettings(_env_file=None, checkpointer="memory")
    )


def sqlite_manager(tmp_path) -> CheckpointerManager:
    return CheckpointerManager(
        AgentCoreSettings(
            _env_file=None,
            checkpointer="sqlite",
            sqlite_path=str(tmp_path / "cp.sqlite"),
        )
    )


async def test_memory_strategy_lifecycle() -> None:
    manager = memory_manager()
    assert manager.strategy == "memory"
    assert manager.saver is None  # 延迟初始化：构造零副作用

    saver = await manager.get_saver()
    assert isinstance(saver, InMemorySaver)
    assert await manager.get_saver() is saver  # 幂等

    await manager.aclose()
    await manager.aclose()  # 幂等关闭


async def test_memory_saver_supports_thread_resume() -> None:
    manager = memory_manager()
    saver = await manager.get_saver()
    graph = build_echo_graph(saver)
    config = {"configurable": {"thread_id": "t-1"}}
    await graph.ainvoke({"messages": [HumanMessage(content="hi")]}, config)
    state = await graph.aget_state(config)
    assert state.values["messages"][-1].content == "echo:hi"
    await manager.aclose()


async def test_sqlite_strategy_lifecycle(tmp_path) -> None:
    # sqlite checkpointer 是可选依赖（langgraph-checkpoint-sqlite），未安装时跳过而非报错
    pytest.importorskip("langgraph.checkpoint.sqlite.aio", reason="未安装可选依赖 langgraph-checkpoint-sqlite")
    manager = sqlite_manager(tmp_path)
    assert manager.strategy == "sqlite"

    saver = await manager.get_saver()
    assert await manager.get_saver() is saver

    graph = build_echo_graph(saver)
    config = {"configurable": {"thread_id": "t-1"}}
    await graph.ainvoke({"messages": [HumanMessage(content="a")]}, config)
    await manager.aclose()

    # 关闭后新建管理器，同一路径恢复同一 thread 的检查点（持久化验证）
    manager2 = sqlite_manager(tmp_path)
    saver2 = await manager2.get_saver()
    graph2 = build_echo_graph(saver2)
    state = await graph2.aget_state(config)
    assert state.values["messages"][-1].content == "echo:a"
    await manager2.aclose()


async def test_manager_not_reusable_after_close() -> None:
    manager = memory_manager()
    await manager.get_saver()
    await manager.aclose()
    with pytest.raises(RuntimeError):
        await manager.get_saver()


async def test_redis_strategy_is_lazy_without_connection() -> None:
    """构造与关闭均不应触碰网络（CI 无 Redis 也能通过）。"""
    manager = CheckpointerManager(
        AgentCoreSettings(_env_file=None, checkpointer="redis")
    )
    assert manager.strategy == "redis"
    assert manager.saver is None
    await manager.aclose()  # 未初始化即关闭：安全 no-op


@pytest.mark.skipif(
    not os.environ.get("AGENT_CORE_TEST_REDIS"),
    reason="需要本机 Redis；设置 AGENT_CORE_TEST_REDIS=1 启用",
)
async def test_redis_strategy_real_connection() -> None:
    manager = CheckpointerManager(
        AgentCoreSettings(
            _env_file=None, checkpointer="redis", redis_url="redis://localhost:6379"
        )
    )
    saver = await manager.get_saver()
    graph = build_echo_graph(saver)
    config = {"configurable": {"thread_id": "redis-t-1"}}
    await graph.ainvoke({"messages": [HumanMessage(content="hello")]}, config)
    state = await graph.aget_state(config)
    assert state.values["messages"][-1].content == "echo:hello"
    await manager.aclose()
