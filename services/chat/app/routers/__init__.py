"""API routers for po-chat.

存放 chat 宿主对外暴露的三组端点，每个子模块只声明自己的 ``APIRouter``，
前缀与中间件统一在 :func:`app.main.create_app` 里挂载（便于测试按需裁剪）：

- :mod:`app.routers.health`：``/api/health`` 探活，附带 agent-core 版本；
- :mod:`app.routers.items`：``/api/items`` 示例 CRUD，依赖内存存储；
- :mod:`app.routers.ws`：``/ws/chat`` 流式聊天，桥接编排事件流与前端帧协议。

本文件不 re-export 子模块，导入方显式写 ``from app.routers import health``。
"""
