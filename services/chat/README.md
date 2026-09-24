# po-chat

基于 FastAPI 的聊天宿主服务：REST CRUD 示例接口 + WebSocket 流式对话端点，
编排层由 `../agent-core`（po-agent-core）提供，垂直 Agent 经插槽机制接入
（内置烹饪助手 `../agent-cooking`，登记点见 `app/agent.py` 的 `_builtin_agents`）。

## 快速开始

```powershell
python -m venv .venv
pnpm chat:install   # 依次安装 ../agent-core → ../agent-cooking → 本服务
pnpm chat:start
```

或手动安装：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e "../agent-core[dev]"
pip install -e "../agent-cooking[dev]"
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 5090 --reload-dir . --reload-dir ../agent-core/src --reload-dir ../agent-cooking/src
```

`--reload-dir` 三个目录都要列：agent-core / agent-cooking 是 editable 安装的
本地库包，默认的 `--reload` 只盯当前目录，不显式加目录时改它们的 `src`
必须手动重启才生效（`pnpm chat:start` 已带上同样参数）。

启动后访问：

- 接口文档：http://localhost:5090/docs
- 健康检查：http://localhost:5090/api/health

## 编排装配（Orchestrator）

`app/agent.py` 在启动 lifespan 中组装 po-agent-core 组件，降级链保证启动永不因配置失败中断：

- LLM：`AGENT_CORE_LLM_API_KEY` 缺失 → 回显模式（EchoChatModel）；
- 多模型（可选）：闲聊走 `chat` 角色，其余阶段角色（`plan`/`write`/`judge` 等）
  由垂直 Agent 自行声明，按 `AGENT_CORE_LLM_ROLES__<角色>__*` 分角色配模型，
  不配即单模型（见 `../agent-core/README.md` 与根目录 `.env.example`）；
- checkpointer：redis/sqlite 连接失败 → memory；
- 意图路由：embedding 缺失或装配失败 → 本地关键词路由（垂直 Agent 仍可达），
  无命中再由 supervisor 兜底 chitchat；
- 垂直 Agent：`agents=None` 时装配内置插槽——当前登记 `cooking`
  （`po_agent_cooking.build_cooking_agent`，包缺失或装配异常只跳过本插槽）；
  新 Agent 同样在 `_builtin_agents` 登记；`agents=[]` 可显式关闭（测试用）。

会话标识：`conversation_id` 映射 LangGraph `thread_id`，实现多轮记忆与 interrupt 恢复。

## REST API

资源 `Item` 字段：`name`(必填)、`description`、`price`(>0)、`in_stock`，存储于内存（进程重启后数据丢失）。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/health` | 健康检查 |
| GET | `/api/items` | 列表，支持 `skip`/`limit`/`q` 查询参数 |
| POST | `/api/items` | 新建（201） |
| GET | `/api/items/{id}` | 详情（404 不存在） |
| PUT | `/api/items/{id}` | 全量替换（404 不存在） |
| PATCH | `/api/items/{id}` | 局部更新（404 不存在） |
| DELETE | `/api/items/{id}` | 删除（204） |

## WebSocket

端点：`/ws/chat`

入站帧：

```json
{"type": "message", "content": "你好", "conversation_id": "可选，续接既有会话"}
{"type": "ping", "content": "可选"}
{"type": "resume", "content": "确认值", "conversation_id": "必填，interrupt 挂起的会话"}
```

出站帧：

| 帧类型 | 说明 |
| --- | --- |
| `run_started` | 运行开始，`payload.thread_id` 为本次会话标识 |
| `token` | 流式文本分片 |
| `step` | 编排节点进入（`payload.node`） |
| `thinking` / `plan` | 垂直 Agent 领域进度（各 Agent 自定义阶段语义，`payload.stage`） |
| `tool_call_start` / `tool_call_args` / `tool_call_end` / `tool_call_result` | 工具调用过程 |
| `interrupt` | 等待用户确认（需 `resume` 帧继续） |
| `done` | 运行结束 |
| `error` | 运行失败 |
| `pong` | 心跳应答 |

## 测试

```powershell
pnpm chat:test
```

## 配置

环境变量（服务自身前缀 `PY_SERVER_`，编排层前缀 `AGENT_CORE_` 见 `../agent-core/README.md`，
烹饪插槽前缀 `COOKING_` 见 `../agent-cooking/README.md`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PY_SERVER_HOST` | `0.0.0.0` | 监听地址 |
| `PY_SERVER_PORT` | `5090` | 监听端口 |
| `PY_SERVER_CORS_ORIGINS` | 见 `.env.example` | 逗号分隔的跨域来源 |
| `COOKING_API_BASE_URL` | `http://localhost:8080/api` | 烹饪插槽读取的菜谱接口地址；容器内用 `http://api:8080/api` |
