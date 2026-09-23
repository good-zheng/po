"""探活端点：确认宿主进程存活并暴露所依赖的 agent-core 版本。

上游是部署编排/负载均衡的健康检查；下游无依赖（不触碰 Orchestrator，
因此即使编排尚未就绪或外部依赖不可达，只要进程能响应就返回 ok）。
``agent_core_version`` 用于线上快速核对实际装入的包版本，排查
「配置改对了但跑的是旧包」这类问题。
"""

import po_agent_core
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """返回 ``{"status": "ok", "agent_core_version": ...}``。

    完整路径为 ``/api/health``（前缀在 :func:`app.main.create_app` 挂载）。
    """
    return {"status": "ok", "agent_core_version": po_agent_core.__version__}
