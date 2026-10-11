---
name: goodzheng-python-dev
description: 为 po monorepo 的 Python 服务任务选择本地 FastAPI 约定和按需上游参考。用于 services/chat 宿主与 services/agent-* 四个库包的 FastAPI 路由、WebSocket 流式聊天、垂直 Agent 插槽、Pydantic 校验、依赖注入、Python API，或 Flask 迁移遗留与 LangGraph 规划。
---

# Po Python 路由

## 先识别框架边界

Python 侧现在是「1 个宿主 + 4 个库包」：

| 目录 | 包名 | 角色 |
| --- | --- | --- |
| `services/chat/` | `po-chat` | FastAPI + Uvicorn 宿主（端口 5090；`pyproject.toml` 声明 `fastapi>=0.115`、`requires-python>=3.11`），REST 挂 `/api`，WebSocket 走 `/ws/chat` |
| `services/agent-core/` | `po-agent-core` | 编排核心：settings、checkpointer、意图路由、supervisor 图、事件协议 |
| `services/agent-cooking/` | `po-agent-cooking` | 烹饪垂直 Agent（`build_cooking_agent`） |
| `services/agent-talk/` | `po-agent-talk` | 言外垂直 Agent（`build_talk_agent`） |
| `services/agent-novel/` | `po-agent-novel` | 长篇反幻觉 Agent，两个插槽：`build_novel_agent`（会写库的生成链路）与 `build_novel_chat_agent`（工作台右栏只读对话）；数据层走 Java 内网通道 |

四个库包都是 `src/` 布局的纯库，**没有独立 venv、没有 HTTP 端口**，测试复用 chat 的 `.venv`；每个包都有自己的 `README.md`，改哪个先读哪个。

当前 `services/chat/` 处理 Python 任务先读 `app/main.py`、`app/agent.py`（插槽装配）、`app/routers/`（health/items/ws）、`app/schemas.py`、`app/store.py`、`app/config.py` 与 `pyproject.toml`，以现有结构为唯一实现基线。旧 Flask + LangGraph 实现已删除；LangGraph 已在库包内使用，新增图节点前先看 `agent-core` 的 supervisor 装配。

## 二级披露路由

| 用户任务或代码信号 | 读取内容 |
| --- | --- |
| 既有 FastAPI 路由、WebSocket 端点、CRUD、配置调整 | 以 `services/chat/` 的既有结构为唯一实现基线，不读取上游 skill |
| Pydantic 建模、依赖注入（Depends/yield）、SSE、新端点设计模式 | `../../skill-sources/fastapi/fastapi/.agents/skills/fastapi/SKILL.md`，再只读命中的 `references/*.md`；镜像缺失时改以本仓库 `app/schemas.py`、`app/routers/*.py` 的既有写法为准（恢复方式见 `../project-router/SKILL.md`） |
| 新增/调整垂直 Agent | 读命中的库包 README + `app/agent.py::_builtin_agents` 的登记模式，不读取上游 skill |
| Flask→FastAPI 迁移遗留、Java/前端契约同步 | 读取 `project-router` 与受影响领域 skill，再按需读取 FastAPI 参考 |

上游 FastAPI 参考按主题按需读取，不要全量展开一份几百行的 SKILL.md。

## 本地硬约束

- `app/main.py` 的启动钩子用类式 `AppLifespan`（`__aenter__/__aexit__`），不要改回 `@asynccontextmanager`（已因弃用问题重构过一次）。
- Agent 配置全部走 `services/chat/.env` 的 `AGENT_CORE_*`（LLM=DeepSeek、embedding=百炼 MaaS `qwen3.7-text-embedding`、`AGENT_CORE_ROUTER_THRESHOLD=0.55`——默认 1.0 会把意图路由全部打到兜底档）；密钥只在该文件，不进代码/日志/skill。意图路由 embedding 走 `semantic_router.OpenAIEncoder`，不要换 langchain `OpenAIEmbeddings`（会预分词导致阿里端点报 input 类型错）。
- agent-novel 的数据层配置是另一套前缀 `NOVEL_`（`NOVEL_API_BASE_URL`、`NOVEL_INTERNAL_TOKEN`、`NOVEL_AUTHOR_ID`、`NOVEL_REQUEST_TIMEOUT_SECONDS`、`NOVEL_PERSIST_ENABLED`）。注意读取点：`NovelStoreSettings` 的 `env_file=".env"` 按**当前工作目录**解析，而 agent-novel 自己目录下没有 `.env`——进程内跑在 chat 里时值取自 `services/chat/.env`，`pnpm agentnovel:test`（cwd=包目录）取不到任何文件、只用默认值，这正是它的用例能零网络、零库的原因。`NOVEL_INTERNAL_TOKEN` 必须与 Java 侧 `APP_INTERNAL_TOKEN` 同值，两边都没配时表现是「链路全部跑完、最后归档 401」，不是启动报错。
- 垂直 Agent 的唯一登记点是 `services/chat/app/agent.py::_builtin_agents`，模式固定为「函数内延迟导入 + ImportError 只 info、装配异常只 warning、本插槽跳过」：未安装该包的部署环境必须仍能起 chitchat。新插槽在这里加，不要在别处 import。`agents=None` 装内置插槽、`agents=[]` 显式不装配（测试用）。
- 四个库包没有独立 venv，`pnpm chat:install` 按 agent-core → agent-cooking → agent-talk → agent-novel 的顺序，在 `services/chat` 下 `pip install -e '../agent-<pkg>[dev]'` 装进 chat 的 `.venv`（后三者依赖 agent-core 的协议）；包测试用 `pnpm agentcore:test` / `agentcooking:test` / `agenttalk:test` / `agentnovel:test`，同样复用那个 `.venv`。
- checkpointer 用 Redis 时环境必须是 redis-stack（需要 JSON+Search 模块），纯 redis 会静默降级为 memory；起来后先核对日志 `checkpointer 就绪：redis`。
- WebSocket 路由用 `@router.websocket(path)` 定义在 `app/routers/ws.py` 并由 `main.py` 挂载（不带 `/api` 前缀）；保持现有 `token`/`done`/`pong`/`error` JSON 帧协议，变更前先检查消费方：管理端 `apps/admin-web/src/pages/chatbot/service.ts`（dev 下经前端 `/ws` 代理，WS 同源）与言外小程序 `apps/echo-talk/src/lib/ai/talk-chat.ts`。**做菜小程序 `apps/cooking-mini` 已经不连这条 WS**——它改成本地意图解析 + 只读菜谱接口应答（`src/lib/ai/chat.ts`），动 WS 协议时不要再去改它，也别以为它是消费方。
- 数据校验统一 Pydantic V2 `BaseModel` + `response_model`；遵循上游规范：不用 ellipsis `...`、不用 RootModel、依赖注入用 `Annotated` 与函数式 `yield`。
- 依赖管理走 `pyproject.toml`（`pip install -e ".[dev]"`），仓库无 `requirements.txt`；新增依赖须与现有 FastAPI 版本兼容。
- LLM 或网络依赖必须保留离线或失败降级路径；不得把密钥、令牌或 `.env` 内容写入代码、日志或 skill。
- 启动与测试从仓库根目录执行 `pnpm chat:start`、`pnpm chat:test`；前者使用 `services/chat/.venv` 并开启热重载。
- 端口占用报 `WinError 10013` 时先 `Get-NetTCPConnection -LocalPort 5090 -State Listen` 查 PID 再 `Stop-Process`；starlette 1.6+ TestClient 的 WS 断连用例不得在 close 后再 receive（死锁）。
