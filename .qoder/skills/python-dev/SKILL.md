---
name: goodzheng-python-dev
description: 为 goodzheng-pro 的 Python 服务任务选择本地 FastAPI 约定和按需上游参考。用于 py_server 的 FastAPI 路由、WebSocket 流式聊天、Pydantic 校验、依赖注入、Python API，或 Flask 迁移遗留与 LangGraph 规划。
---

# Goodzheng Python 路由

## 先识别框架边界

当前 `py_server/` 是 FastAPI 0.141 + Uvicorn 服务（端口 5090）：REST 挂 `/api` 前缀，WebSocket 走 `/ws/chat`。处理 Python 任务先读 `app/main.py`、`app/routers/`、`app/schemas.py`、`app/store.py`、`app/config.py` 与 `pyproject.toml`，以现有结构为唯一实现基线。旧 Flask + LangGraph 实现已删除；LangGraph 智能体尚未落地，引入前先走 OpenSpec 变更。

## 二级披露路由

| 用户任务或代码信号 | 读取内容 |
| --- | --- |
| 既有 FastAPI 路由、WebSocket 端点、CRUD、配置调整 | 以 `py_server/` 的既有结构为唯一实现基线，不读取上游 skill |
| Pydantic 建模、依赖注入（Depends/yield）、SSE、新端点设计模式 | `../../skill-sources/fastapi/fastapi/.agents/skills/fastapi/SKILL.md`，再只读命中的 `references/*.md` |
| Flask→FastAPI 迁移遗留、Java/前端契约同步 | 先走 `project-router` 的 OpenSpec 边界，再读取 FastAPI 参考与受影响领域 skill |

FastAPI 上游参考按主题按需读取；上游 SKILL.md 约 320 行，普通 Python 任务不得全量展开。

## 本地硬约束

- WebSocket 路由用 `@router.websocket(path)` 定义在 `app/routers/ws.py` 并由 `main.py` 挂载（不带 `/api` 前缀）；保持现有 `token`/`done`/`pong`/`error` JSON 帧协议，变更前先检查前端消费方。
- 数据校验统一 Pydantic V2 `BaseModel` + `response_model`；遵循上游规范：不用 ellipsis `...`、不用 RootModel、依赖注入用 `Annotated` 与函数式 `yield`。
- 依赖管理走 `pyproject.toml`（`pip install -e ".[dev]"`），仓库无 `requirements.txt`；新增依赖须与现有 FastAPI 版本兼容。
- LLM 或网络依赖必须保留离线或失败降级路径；不得把密钥、令牌或 `.env` 内容写入代码、日志或 skill。
- 启动：`.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 5090`（免激活 venv 写法）；测试：`.\.venv\Scripts\python.exe -m pytest`。
- 端口占用报 `WinError 10013` 时先 `Get-NetTCPConnection -LocalPort 5090 -State Listen` 查 PID 再 `Stop-Process`；starlette 1.6+ TestClient 的 WS 断连用例不得在 close 后再 receive（死锁）。
