"""Checkpointer 生命周期管理：三策略（redis/sqlite/memory）。

参考实现（novel_server）的教训：三套 checkpointer 并存、import 即连 Redis、
连接管理无人负责。这里收敛为唯一入口 ``CheckpointerManager``：

- **延迟初始化**：构造零副作用，首次 ``get_saver()`` 才建立连接；
- **幂等**：重复 ``get_saver()`` 返回同一实例，重复 ``aclose()`` 安全；
- **显式关闭**：宿主在 shutdown 钩子中调用 ``aclose()``（Redis 连接、
  SQLite 文件句柄由此释放）；
- redis 是默认策略（生产），sqlite 适合单机演示，memory 用于测试与 CI。

langgraph 的三个异步 saver 工厂均返回 async context manager，
由本管理器负责手动进入/退出。
"""

from __future__ import annotations

import logging
from typing import AsyncContextManager

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver

from po_agent_core.config import AgentCoreSettings

logger = logging.getLogger(__name__)


# 两个工厂把「可选后端的 import」放在函数体内：redis / sqlite 的驱动属于
# 可选依赖，放进模块顶层会让未安装该后端的环境连 import 本包都失败。
# 返回的 async context manager 不在此处进入——进入与退出都由管理器统一负责，
# 避免连接在无人持有时被提前建立。
def _build_async_redis_saver(
    url: str,
) -> AsyncContextManager[BaseCheckpointSaver]:
    from langgraph.checkpoint.redis import AsyncRedisSaver

    return AsyncRedisSaver.from_conn_string(url)  # type: ignore[return-value]


def _build_async_sqlite_saver(
    path: str,
) -> AsyncContextManager[BaseCheckpointSaver]:
    from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

    return AsyncSqliteSaver.from_conn_string(path)  # type: ignore[return-value]


class CheckpointerManager:
    """延迟初始化 + 显式关闭的 checkpointer 管理器。"""

    def __init__(self, settings: AgentCoreSettings) -> None:
        self._settings = settings
        self._saver: BaseCheckpointSaver | None = None
        self._cm: AsyncContextManager[BaseCheckpointSaver] | None = None
        self._closed = False

    @property
    def strategy(self) -> str:
        return self._settings.checkpointer

    @property
    def saver(self) -> BaseCheckpointSaver | None:
        """已创建的 saver（未初始化时为 None；不触发连接）。"""
        return self._saver

    async def get_saver(self) -> BaseCheckpointSaver:
        """获取 saver；首次调用建立连接并执行 schema 初始化。

        连接失败（如 Redis 未启动）会向上抛异常，由宿主装配层降级到
        memory 策略——本管理器不做静默降级，以免掩盖真实故障。
        """
        if self._closed:
            raise RuntimeError("CheckpointerManager 已关闭，不可复用")
        if self._saver is not None:
            return self._saver

        strategy = self._settings.checkpointer
        if strategy == "memory":
            # 进程内存储：不需要连接，也不需要关闭，测试与降级场景用
            self._saver = InMemorySaver()
            logger.info("checkpointer 就绪：memory")
            return self._saver

        if strategy == "sqlite":
            cm = _build_async_sqlite_saver(self._settings.sqlite_path)
        elif strategy == "redis":
            cm = _build_async_redis_saver(self._settings.redis_url)
        else:  # pragma: no cover - Literal 已在 settings 层拦截
            raise ValueError(f"未知 checkpointer 策略: {strategy!r}")

        # 手动进入 context manager 并把 cm 存起来：连接要活到进程退出，
        # 不能像 with 语句那样出了作用域就释放
        saver = await cm.__aenter__()
        await _setup_saver(saver)
        self._cm = cm
        self._saver = saver
        logger.info("checkpointer 就绪：%s", strategy)
        return self._saver

    async def aclose(self) -> None:
        """释放连接；幂等。"""
        if self._closed:
            return
        self._closed = True
        if self._cm is not None:
            await self._cm.__aexit__(None, None, None)
            self._cm = None
        self._saver = None


async def _setup_saver(saver: BaseCheckpointSaver) -> None:
    setup = getattr(saver, "setup", None)
    if setup is not None:
        await setup()
