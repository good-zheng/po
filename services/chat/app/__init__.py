"""po-chat FastAPI application package.

chat 宿主服务（默认端口 5090）的 Python 包根：自身不含编排逻辑，只负责把
``po-agent-core`` 装配出来的能力以 HTTP/WS 形式暴露给外部。

对外路由约定（见 :mod:`app.main`）：

- REST 统一挂在 ``/api`` 前缀下（health 探活 + items 示例 CRUD）；
- WebSocket 聊天端点为 ``/ws/chat``，**不带** ``/api`` 前缀——前端
  ``apps/admin-web`` 在开发态经独立的 ``/ws`` 代理转发，与 REST 的 ``/api``
  代理分离，因此两者的前缀必须各自保持稳定。

模块职责划分：

- :mod:`app.main`：应用工厂与 lifespan（启动装配 / 关闭释放）；
- :mod:`app.config`：宿主自身设置（监听地址、CORS），与 ``AgentCoreSettings``
  分离；
- :mod:`app.agent`：Orchestrator 装配层（全部降级策略集中于此）；
- :mod:`app.schemas`：REST 与 WS 共用的 Pydantic V2 校验模型；
- :mod:`app.store`：进程内 items 存储（示例用，重启即丢）；
- :mod:`app.routers`：health / items / ws 三组端点。

升级提示：P3 的 MCP（``/mcp``）与 P4 的 A2A（``/a2a``）会作为新的同级路由
挂入，不改变上述既有前缀。
"""
