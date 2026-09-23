# po-chat

基于 FastAPI 的聊天宿主服务：REST CRUD 示例接口 + WebSocket 流式对话端点，
编排层由 `../agent-core`（po-agent-core）提供，默认装配 `../agent-novel`
（po-agent-novel）小说创作垂直 Agent。

## 快速开始

```powershell
python -m venv .venv
pnpm chat:install   # 依次安装 ../agent-core → ../agent-novel → 本服务
pnpm chat:start
```

或手动安装：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e "../agent-core[dev]"
pip install -e "../agent-novel[dev]"
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 5090
```

启动后访问：

- 接口文档：http://localhost:5090/docs
- 健康检查：http://localhost:5090/api/health

## 编排装配（Orchestrator）

`app/agent.py` 在启动 lifespan 中组装 po-agent-core 组件，降级链保证启动永不因配置失败中断：

- LLM：`AGENT_CORE_LLM_API_KEY` 缺失 → 回显模式（EchoChatModel）；novel Agent
  同步降级为离线占位模式（`../agent-novel/README.md`）；
- 多模型（可选）：闲聊走 `chat` 角色、小说各阶段走 `plan`/`write`/`judge` 角色，
  按 `AGENT_CORE_LLM_ROLES__<角色>__*` 分阶段配模型，不配即单模型
  （见 `../agent-core/README.md` 与根目录 `.env.example`）；
- checkpointer：redis/sqlite 连接失败 → memory；
- 意图路由：embedding 缺失或装配失败 → 本地关键词路由（垂直 Agent 仍可达），
  无命中再由 supervisor 兜底 chitchat；
- 垂直 Agent：默认装配内置插槽（novel），包缺失逐个跳过；`agents=[]` 可显式
  关闭（测试用）。

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
| `thinking` / `plan` | 垂直 Agent 领域进度（如 novel 的构思/大纲/逐章状态，`payload.stage`） |
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

环境变量（服务自身前缀 `PY_SERVER_`，编排层前缀 `AGENT_CORE_` 见 `../agent-core/README.md`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PY_SERVER_HOST` | `0.0.0.0` | 监听地址 |
| `PY_SERVER_PORT` | `5090` | 监听端口 |
| `PY_SERVER_CORS_ORIGINS` | 见 `.env.example` | 逗号分隔的跨域来源 |
