"""长期记忆 store 测试（memory 策略；redis 真实连接按环境变量门控）。"""

import os

import pytest
from langgraph.store.memory import InMemoryStore

from po_agent_core.config import AgentCoreSettings
from po_agent_core.memory.store import StoreManager, user_namespace


def test_user_namespace_shape() -> None:
    assert user_namespace("u-42") == ("users", "u-42")


def test_user_namespace_rejects_empty_user_id() -> None:
    with pytest.raises(ValueError):
        user_namespace("")


async def test_memory_store_roundtrip_and_isolation() -> None:
    manager = StoreManager(AgentCoreSettings(_env_file=None, checkpointer="memory"))
    assert manager.store is None  # 延迟初始化

    store = await manager.get_store()
    assert isinstance(store, InMemoryStore)
    assert await manager.get_store() is store

    await store.aput(user_namespace("alice"), "prefs", {"style": "武侠"})
    await store.aput(user_namespace("bob"), "prefs", {"style": "悬疑"})

    alice = await store.aget(user_namespace("alice"), "prefs")
    bob = await store.aget(user_namespace("bob"), "prefs")
    assert alice.value["style"] == "武侠"
    assert bob.value["style"] == "悬疑"

    await manager.aclose()
    await manager.aclose()  # 幂等


async def test_store_not_reusable_after_close() -> None:
    manager = StoreManager(AgentCoreSettings(_env_file=None, checkpointer="memory"))
    await manager.get_store()
    await manager.aclose()
    with pytest.raises(RuntimeError):
        await manager.get_store()


@pytest.mark.skipif(
    not os.environ.get("AGENT_CORE_TEST_REDIS"),
    reason="需要本机 Redis；设置 AGENT_CORE_TEST_REDIS=1 启用",
)
async def test_redis_store_real_connection() -> None:
    manager = StoreManager(
        AgentCoreSettings(
            _env_file=None, checkpointer="redis", redis_url="redis://localhost:6379"
        )
    )
    store = await manager.get_store()
    ns = user_namespace("itest-user")
    await store.aput(ns, "note", {"text": "跨重启"})
    item = await store.aget(ns, "note")
    assert item.value["text"] == "跨重启"
    await manager.aclose()
