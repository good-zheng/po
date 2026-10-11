# po-chat

基于 FastAPI 的聊天宿主服务：REST CRUD 示例接口 + WebSocket 流式对话端点，
编排层由 `../agent-core`（po-agent-core）提供，垂直 Agent 经插槽机制接入
（内置 `../agent-cooking` 烹饪、`../agent-talk` 言外、`../agent-novel` 小说，
登记点见 `app/agent.py` 的 `_builtin_agents`）。

## 快速开始

```powershell
python -m venv .venv
pnpm chat:install   # 依次安装 ../agent-core → ../agent-cooking → ../agent-talk → ../agent-novel → 本服务
pnpm chat:start
```

或手动安装：

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e "../agent-core[dev]"
pip install -e "../agent-cooking[dev]"
pip install -e "../agent-talk[dev]"
pip install -e "../agent-novel[dev]"
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 5090 --reload-dir . --reload-dir ../agent-core/src --reload-dir ../agent-cooking/src --reload-dir ../agent-talk/src --reload-dir ../agent-novel/src
```

`--reload-dir` 每个本地库包都要列：agent-core / agent-cooking / agent-talk / agent-novel
是 editable 安装的，默认的 `--reload` 只盯当前目录，不显式加目录时改它们的 `src`
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
- 垂直 Agent：`agents=None` 时装配内置插槽——当前登记 `cooking` → `talk` → `novel` → `novel-chat`
  （各自 `build_*_agent`，**逐个**延迟导入，包缺失或装配异常只跳过本插槽，其余照常；
  `novel-chat` 是工作台右栏的对话面板，与生成链路的 `novel` 各自独立注册）；
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
{"type": "message", "content": "…", "conversation_id": "…", "agent": "novel-chat", "context": {"bookId": 1, "chapterId": 12}}
{"type": "ping", "content": "可选"}
{"type": "resume", "content": "确认值", "conversation_id": "必填，interrupt 挂起的会话"}
```

`agent` 显式指定插槽（跳过意图路由，但仍在 supervisor 父图上执行——子图不挂 checkpointer，
run 走子图、resume 走父图时两边不是同一份 checkpoint，插槽内的 `interrupt` 就确认不了）；
`context` 走 `config.configurable`，对模型不可见，只给垂直插槽定位数据层。
两者都缺省时行为与历史上线一致。

### 握手身份（novel-chat 与续写帧）

`/ws/chat` 的握手 URL 可带一张短效票据：

```
ws://<host>:5090/ws/chat?ticket=<票据>
```

票据由 Spring Boot 侧 `GET /api/novel/chat-ticket` 签发（管理端登录态才能取），有效期 60 秒；
**同一张票在这 60 秒内可重复校验**（`ChatTicketService.consume()` 只解析签名与过期，不作废），
所以「重连时复用刚取到的票」是成立的，而过期后必然被拒。本服务**不加签 JWT、也不持 `jwt.secret`**：验票走内网
`POST /api/novel/internal/chat-ticket/verify`（带 `X-Internal-Token`），验出的 uid 绑进该连接的任务上下文，
`po-agent-novel` 的 HTTP 数据层据此给正典读口补一个 `X-Actor-Uid`，Java 侧再按 `book.author_id` 判归属。

为什么要票据而不是把会话 JWT 拼在 query 上：浏览器与微信小程序都不能给 WebSocket 握手带请求头，
而 query 会被网关访问日志原样留存——把 24 小时有效的令牌写进日志等于把长期凭据交给日志系统。

三态与对应客户端行为：

| 握手 | 结果 |
| --- | --- |
| 不带 `ticket` | 匿名连接：cooking / talk / chitchat 照旧，需要身份的帧（见下）回一帧 `error`（不关连接） |
| 带票且校验通过 | 连接绑定该作者，novel-chat 与续写可用 |
| 带票但校验失败 | **accept 之前**就 `close(code=4401)`，客户端拿 HTTP 403；收到 4401 表示该重新取票 |

`PY_SERVER_INTERNAL_TOKEN` 未配置即「没有验票通道」，novel-chat 一律拒连（其余插槽不受影响）。
刻意只强制 novel-chat：已发布小程序没有换票流程，一刀切等于当场断聊；
cooking / talk 的 `conversation_id` 猜测风险作为遗留项登记在 PRD §15.16。

哪些帧需要身份判在 `app/ws_auth.requires_actor(agent, context)`：`agent=novel-chat` 全要，
`agent=novel` 只在帧里带 `context.bookId` 时要。后者是续写带来的变化——新书那一轮读的是本轮
自己刚归档的书，而续写读的是作者从帧里带来的**既有书目**，读完还按章追加写回同一本书；
Java 的归属校验只在看见 `X-Actor-Uid` 时才跑，匿名连接等于整段跳过，
于是任何能连上 `/ws/chat` 的对等方都能拿别人的 `bookId` 塞一章进去。生成链路因此不再天然安全，
闸门从「插槽名单」改成了「插槽 + 定位键」。

帧级闸门判的是帧里的 `agent`（所以报了 `novel-chat` 的 `resume` 帧同样被拦），
不带 `agent` 的 `resume` 不在它覆盖范围内——收它需要宿主侧记 `thread_id → uid`，同一条遗留项。

出站帧：

| 帧类型 | 说明 |
| --- | --- |
| `run_started` | 运行开始，`payload.thread_id` 为本次会话标识 |
| `token` | 流式文本分片 |
| `step` | 编排节点进入（`payload.node`） |
| `thinking` / `plan` | 垂直 Agent 领域进度（各 Agent 自定义阶段语义，`payload.stage`） |
| `proposal` | 仅 novel-chat 插槽：一张提议卡，`payload` 即 Java `ProposalRequest` 的 9 个字段。前端只转发不拼装，采纳/驳回走 REST；不认识该帧的客户端必须忽略它 |
| `tool_call_start` / `tool_call_args` / `tool_call_end` / `tool_call_result` | 工具调用过程 |
| `interrupt` | 等待用户确认（需 `resume` 帧继续） |
| `done` | 运行结束 |
| `error` | 运行失败——编排层的 `RUN_ERROR` 就映射到这里（**没有 `run_error` 这种帧类型**，客户端别按它写分支），帧级闸门的拒绝也走同一类型 |
| `pong` | 心跳应答 |

## 测试

```powershell
pnpm chat:test
```

## 配置

环境变量（服务自身前缀 `PY_SERVER_`，编排层前缀 `AGENT_CORE_` 见 `../agent-core/README.md`，
插槽各自有前缀：烹饪 `COOKING_`、言外 `TALK_`、小说 `NOVEL_`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PY_SERVER_HOST` | `0.0.0.0` | 监听地址 |
| `PY_SERVER_PORT` | `5090` | 监听端口 |
| `PY_SERVER_CORS_ORIGINS` | 见 `.env.example` | 逗号分隔的跨域来源 |
| `COOKING_API_BASE_URL` | `http://localhost:8080/api` | 烹饪插槽读取的菜谱接口地址；容器内用 `http://api:8080/api` |
| `TALK_INTERNAL_TOKEN` | 空 | 言外建议回写 `/talk/internal/**` 的令牌；须等于 Spring 侧 `app.internal-token`，否则该插槽不落库 |
| `NOVEL_API_BASE_URL` | `http://localhost:8080/api` | 小说成稿与正典写入的内网地址（含 `/api` 前缀） |
| `NOVEL_INTERNAL_TOKEN` | 空 | 同上令牌；不一致时 `/novel/internal/**` 回 `code=403` |
| `NOVEL_PERSIST_ENABLED` | `true` | `false` 时成稿与正典都只留进程内（本地无后端 / 跑离线回归） |

插槽令牌的前缀各不相同（各包自己的 `Settings`）：`docker-compose.yml` 里统一由根 `.env`
的 `APP_INTERNAL_TOKEN` 映射到 `TALK_INTERNAL_TOKEN` / `NOVEL_INTERNAL_TOKEN`，
两个 Python 包都不直接读 `APP_*`。
