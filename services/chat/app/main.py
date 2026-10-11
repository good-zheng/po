"""应用工厂与生命周期：把 Orchestrator 与三组路由挂成一个 FastAPI 应用。

在链路中的位置：这是 chat 宿主的程序入口（``uvicorn app.main:app``）。启动时
由 lifespan 装配编排能力并写入 ``app.state``，供 WS 路由在每次连接时取用；
关闭时释放 checkpointer（redis/sqlite 连接）。

路由前缀约定（改动即破坏前端契约）：

- ``/api/health``、``/api/items/*``：REST，统一 ``prefix="/api"``；
- ``/ws/chat``：WebSocket，**不加** ``/api`` 前缀——前端 ``apps/admin-web``
  开发态用独立的 ``/ws`` 代理转发 WS，与 ``/api`` 代理分离。

消费方：``apps/admin-web/src/pages/chatbot/service.ts``（dev 下经前端代理）。
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent import Orchestrator, build_orchestrator
from app.config import get_settings
from app.logging_setup import configure_logging
from app.routers import health, items, ws

logger = logging.getLogger(__name__)


class AppLifespan:
    """应用生命周期：启动时装配 Orchestrator，关闭时释放其持有的外部连接。

    ``build_orchestrator`` 内部已含完整降级链（见 :mod:`app.agent`），因此这里
    不需要 try/except：即使 LLM Key 缺失或 checkpointer 不可达也会拿到一个
    可用的 Orchestrator，保证服务能正常监听端口。

    注意装配结果会覆盖 ``create_app`` 注入的测试实例——只有不进入 lifespan 的
    调用方式（如未用作上下文管理器的 ``TestClient``、直接走 ASGI 传输）才会
    使用注入实例。

    进出口各落一行带 pid 的日志，是为了让「连接无故断开」能事后归因：文件里有
    关闭行 = 进程优雅退出（Ctrl+C / reload / 容器信号）；日志停在半句、没有关闭行
    = 进程被硬杀或崩溃（见 :mod:`app.logging_setup`）。
    """

    def __init__(self, app: FastAPI) -> None:
        self.app = app
        self.orchestrator: Orchestrator | None = None

    async def __aenter__(self) -> None:
        logger.info("chat 启动（pid=%s）", os.getpid())
        self.app.state.orchestrator = await build_orchestrator()
        self.orchestrator = self.app.state.orchestrator

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        # 用 getattr 兜底：装配阶段若抛异常，这里不应再掩盖原始错误（关闭报错的
        # 堆栈会掩盖启动失败的真实原因）。
        orchestrator: Orchestrator | None = getattr(self.app.state, "orchestrator", None)
        if orchestrator is None:
            logger.warning("chat 关闭（pid=%s）：没有已装配的 Orchestrator，跳过释放", os.getpid())
            return
        logger.info("chat 关闭（pid=%s）：释放 checkpointer 与模型连接", os.getpid())
        await orchestrator.aclose()


def create_app(orchestrator: Orchestrator | None = None) -> FastAPI:
    """构建应用实例；``orchestrator`` 供测试注入替身，运行时留空由 lifespan 装配。"""
    settings = get_settings()
    # 先接线日志，再装配路由：装配阶段（build_orchestrator 的降级链）的 warning
    # 也必须落盘，否则最关键的「为什么降级」那段恰恰看不到。
    configure_logging(settings.log_file, settings.log_level)
    application = FastAPI(title="po-chat", lifespan=AppLifespan)
    # 挂给 WS 握手层用（app/routers/ws.py 的 _settings）：握手发生在 lifespan 之外，
    # 而测试要在不写环境变量、不污染进程级 lru_cache 的前提下注入验票配置。
    application.state.settings = settings
    if orchestrator is not None:
        # 注入的实例先落到 app.state：WS 路由只在连接建立时读取一次，
        # 因此测试可在不启动 lifespan 的前提下直接驱动编排。
        application.state.orchestrator = orchestrator
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(health.router, prefix="/api")
    application.include_router(items.router, prefix="/api")
    # WS 不带 /api：前端为 WS 单独配置了 /ws 代理，前缀与 REST 保持区分。
    application.include_router(ws.router)
    return application


# 模块级实例供 ``uvicorn app.main:app`` 直接引用（生产/容器启动路径）。
app = create_app()
