"""长期记忆 store：user namespace 隔离。

短期记忆 = checkpointer 内的 messages（随 thread 恢复）；
长期记忆 = store 内按 ``("users", user_id)`` 命名空间隔离的跨会话数据
（用户偏好、人设、领域事实等）。

策略与 checkpointer 对齐：redis → ``AsyncRedisStore``（跨重启持久），
其余 → ``InMemoryStore``（进程内，重启丢失；langgraph 未提供 sqlite store）。
生命周期与 ``CheckpointerManager`` 同构：延迟初始化 + 显式关闭。
"""

from __future__ import annotations

import logging
from typing import AsyncContextManager

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from po_agent_core.config import AgentCoreSettings

logger = logging.getLogger(__name__)


def user_namespace(user_id: str) -> tuple[str, str]:
    """长期记忆命名空间：``("users", user_id)``。

    所有宿主必须经由此函数构造命名空间，禁止散落硬编码，
    以保证 WS、A2A 等不同入口对同一用户的记忆视图一致。
    """
    if not user_id:
        raise ValueError("user_id 不能为空")
    return ("users", user_id)


class StoreManager:
    """延迟初始化 + 显式关闭的长期记忆管理器。"""

    def __init__(self, settings: AgentCoreSettings) -> None:
        self._settings = settings
        self._store: BaseStore | None = None
        self._cm: AsyncContextManager[BaseStore] | None = None
        self._closed = False

    @property
    def store(self) -> BaseStore | None:
        return self._store

    async def get_store(self) -> BaseStore:
        """获取长期记忆 store；首次调用建立连接。

        复用 checkpointer 的策略选择（与 redis_url 同一实例）：
        langgraph 没有 sqlite store，故只有 redis 会跨重启持久，
        其余策略一律落到进程内存储。
        """
        if self._closed:
            raise RuntimeError("StoreManager 已关闭，不可复用")
        if self._store is not None:
            return self._store

        if self._settings.checkpointer == "redis":
            # import 与连接都延迟到这里：未配置 redis 的部署不加载 redis 驱动
            from langgraph.store.redis import AsyncRedisStore

            cm = AsyncRedisStore.from_conn_string(self._settings.redis_url)
            store = await cm.__aenter__()
            self._cm = cm
        else:
            store = InMemoryStore()
        self._store = store
        logger.info(
            "长期记忆 store 就绪：%s",
            "redis" if self._settings.checkpointer == "redis" else "memory",
        )
        return store

    async def aclose(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._cm is not None:
            await self._cm.__aexit__(None, None, None)
            self._cm = None
        self._store = None
