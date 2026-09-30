---
name: goodzheng-python-dev
description: 为 po monorepo 的 Python 服务任务选择本地 FastAPI 约定和按需上游参考。用于 services/chat 的 FastAPI 路由、WebSocket 流式聊天、Pydantic 校验、依赖注入、Python API，或 Flask 迁移遗留与 LangGraph 规划。
---

# Po Python 路由

## 先识别框架边界

当前 `services/chat/` 是 FastAPI + Uvicorn 服务（端口 5090；`pyproject.toml` 声明 `fastapi>=0.115`、Python>=3.11）：REST 挂 `/api` 前缀，WebSocket 走 `/ws/chat`。处理 Python 任务先读 `app/main.py`、`app/routers/`（health/items/ws）、`app/schemas.py`、`app/store.py`、`app/config.py` 与 `pyproject.toml`，以现有结构为唯一实现基线。旧 Flask + LangGraph 实现已删除；引入 LangGraph 前先评估现有 FastAPI 架构、依赖与调用方。

## 二级披露路由

| 用户任务或代码信号 | 读取内容 |
| --- | --- |
| 既有 FastAPI 路由、WebSocket 端点、CRUD、配置调整 | 以 `services/chat/` 的既有结构为唯一实现基线，不读取上游 skill |
| Pydantic 建模、依赖注入（Depends/yield）、SSE、新端点设计模式 | `../../skill-sources/fastapi/fastapi/.agents/skills/fastapi/SKILL.md`，再只读命中的 `references/*.md` |
| Flask→FastAPI 迁移遗留、Java/前端契约同步 | 读取 `project-router` 与受影响领域 skill，再按需读取 FastAPI 参考 |

FastAPI 上游参考按主题按需读取；上游 SKILL.md 约 320 行，普通 Python 任务不得全量展开。

## 本地硬约束

- `app/main.py` 的启动钩子用类式 `AppLifespan`（`__aenter__/__aexit__`），不要改回 `@asynccontextmanager`（已因弃用问题重构过一次）。
- Agent 配置全部走 `services/chat/.env` 的 `AGENT_CORE_*`（LLM=DeepSeek、embedding=百炼 MaaS `qwen3.7-text-embedding`、`AGENT_CORE_ROUTER_THRESHOLD=0.55`——默认 1.0 会把意图路由全部打到兜底档）；密钥只在该文件，不进代码/日志/skill。意图路由 embedding 走 `semantic_router.OpenAIEncoder`，不要换 langchain `OpenAIEmbeddings`（会预分词导致阿里端点报 input 类型错）。
- checkpointer 用 Redis 时环境必须是 redis-stack（需要 JSON+Search 模块），纯 redis 会静默降级为 memory；起来后先核对日志 `checkpointer 就绪：redis`。
- WebSocket 路由用 `@router.websocket(path)` 定义在 `app/routers/ws.py` 并由 `main.py` 挂载（不带 `/api` 前缀）；保持现有 `token`/`done`/`pong`/`error` JSON 帧协议，变更前先检查前端消费方（`apps/admin-web/src/pages/chatbot/service.ts`，dev 下经前端 `/ws` 代理转发；小程序 `apps/cooking-mini/src/pages/ai/chat.tsx` WS 断了会静默回退本地规则回答，故障不可见，验证时看 Network 面板有没有真实连接）。
- 数据校验统一 Pydantic V2 `BaseModel` + `response_model`；遵循上游规范：不用 ellipsis `...`、不用 RootModel、依赖注入用 `Annotated` 与函数式 `yield`。
- 依赖管理走 `pyproject.toml`（`pip install -e ".[dev]"`），仓库无 `requirements.txt`；新增依赖须与现有 FastAPI 版本兼容。
- LLM 或网络依赖必须保留离线或失败降级路径；不得把密钥、令牌或 `.env` 内容写入代码、日志或 skill。
- 启动与测试从仓库根目录执行 `pnpm chat:start`、`pnpm chat:test`；前者使用 `services/chat/.venv` 并开启热重载。
- 端口占用报 `WinError 10013` 时先 `Get-NetTCPConnection -LocalPort 5090 -State Listen` 查 PID 再 `Stop-Process`；starlette 1.6+ TestClient 的 WS 断连用例不得在 close 后再 receive（死锁）。
