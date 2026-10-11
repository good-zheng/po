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

### 一轮运行的预算（按插槽给，恢复轮同账）

`AgentRunner` 给每一轮加一个总超时，超了就发 `RUN_ERROR`（内容「运行超时」，映射成 `error`
帧）。这个数不能是全局一个值：`AGENT_CORE_RUN_TIMEOUT_SECONDS` 默认 300 秒，够一问一答的
插槽把卡死的模型调用兜住，但**一次写 3 章实测 322 秒**——长批次会在写作中途被掐掉。

所以预算是**每轮**的（`runner.astream(..., timeout_seconds=…)` 覆盖构造值），由宿主按插槽决定：

| 插槽 | 预算 | 依据 |
| --- | --- | --- |
| `novel` | 3600 秒 | 领域侧一轮最多 20 章（`_CONTINUE_MAX_CHAPTERS`），按每章约 2 分钟留出的余量 |
| 其余（`chitchat`/`cooking`/`talk`/`novel-chat`） | 构造值 300 秒 | 一问一答的插槽不需要更久；抬全局默认等于卡死时让客户端空等一小时才见错误帧 |

`resume` 帧不带 `agent`，预算从 checkpoint 的 `forced_agent` 读回来（`Orchestrator._forced_agent`）。
这一步不是可省的：作者按「先问问我」发起时计划闸门会截断发起轮，**剩下几章全写在恢复轮里**，
读不回插槽名就等于「只在不用闸门的那条路上修好了超时」。读不到（没挂 checkpointer、存储抖动）
按默认预算照常恢复——这一层失败不能变成「作者的确认发不出去」。

单测用的是 `InMemorySaver`，线上是 `AsyncRedisSaver`，而装配函数在连不上 Redis 时会**静默降级成
memory**——「读回插槽名」这件事到底成不成立，只有拿真 Redis 才算数。
`scripts/verify_resume_budget_redis.py` 用全离线模型（零额度、不落库）跑一遍发起→interrupt→恢复，
先把 saver 类型钉成 Redis，再断言恢复轮拿到 3600 秒、且陌生线程读回 `None`（反向对照，否则这条
断言是恒真的）。它不进 pytest，因为 CI 没有 Redis。

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

### 连接出问题时怎么定位（分层探针）

管理端创作面板的连接错误分三种情形，各自指向不同进程，浏览器侧看不出区别：

| 界面那句话 | 断在哪 | 先查 |
| --- | --- | --- |
| 连不上生成服务（且没取到握手票据） | chat 进程 / 反代 | chat 是否在跑（本机 5090）、管理端容器 `location ^~ /ws/chat` 与 `ADMIN_CHAT_UPSTREAM`、云托管实例是否缩容 |
| 握手被服务端拒绝（连接没建起来） | 验票通道 | chat 的 `PY_SERVER_INTERNAL_TOKEN` 是否等于 Java 的 `app.internal-token`、Java 是否可达（票据 60 秒过期也会走这条） |
| 生成连接已断开 | 跑起来之后 | 这一轮停在中断处，属运行期而非连接期，按下面的四态判读表查落盘日志 |

`scripts/probe_novel_channel.py` 一次把这四层跑完并只打结论（内部令牌只报长度，票据值与正文不外泄；
默认不发任何会消耗模型额度的帧）：

```powershell
# cwd 必须是 services/chat；--book-id 用于验内网读口与续写闸门
.venv\Scripts\python.exe scripts\probe_novel_channel.py --book-id 14
# 云上那条反代：换 --ws；真实票据只能现场从浏览器 DevTools 复制（60 秒过期）
.venv\Scripts\python.exe scripts\probe_novel_channel.py --book-id 14 --ws wss://<管理端域名>/ws/chat --ticket <票据>
```

退出码 0 表示链路完整；有 FAIL 时先修最前面那一层——后面各层的失败多半是它的连带。

**长跑被掐在 60 秒**是另一类故障，与上面三行都不同（连接建起来了、图也在跑，只是被服务端
自己撕掉）。`scripts/probe_ws_keepalive_backpressure.py` 在真实 uvicorn/ws 栈上用桩编排器复现它，
全程离线、不烧额度：

```powershell
# cwd 必须是 services/chat；默认「静默 75 秒 + 客户端每 30 秒一帧 JSON 心跳」，复刻管理端形状
.venv\Scripts\python.exe -X utf8 scripts\probe_ws_keepalive_backpressure.py
# 对照一：长跑期间客户端一帧都不发（连接能活，说明卡的不是空闲超时而是入站帧）
.venv\Scripts\python.exe -X utf8 scripts\probe_ws_keepalive_backpressure.py --no-heartbeat
# 对照二：把服务端保活窗口抬到心跳之上——它能活，但读通道仍停着，是止血带不是修复
.venv\Scripts\python.exe -X utf8 scripts\probe_ws_keepalive_backpressure.py --server-ping-timeout 300
```

退出码 0 = 收到 `done`。判据与机制写在脚本开头：uvicorn 0.54 的 websockets-sansio 实现是
「投一条消息就 `pause_reading()`，直到应用再次 `receive()` 且队列空了才 `resume_reading()`」，
而 `_loop` 在发帧期间没有人 `receive()`——心跳帧躺在队列里，服务端自己的保活 ping 等不到 PONG，
20 秒后 `keepalive ping timeout` 以 1011 撕掉这条还在正常生成的连接（关闭码非 1000，前端因此
只看到「生成连接已断开」而没有任何 `error` 帧）。修复是常驻的入站泵任务 `_pump_inbound`；
回归用例见 `tests/test_ws_inbound_pump.py`。

要证明修的是真问题、而不是桩编排器碰巧没崩，用 `scripts/probe_ws_long_run.py`：它起真 uvicorn +
真 `/ws/chat` + 真模型跑一整批（`NOVEL_PERSIST_ENABLED=false` 只在进程内，不写库），按浏览器形状
每 30 秒发一帧 JSON 心跳，打每帧时刻与最长静默间隔。**它消耗真实模型额度，只在作者要求时跑。**
2026-10-12 那次实测：3 章 / 361.8 秒 / 57,300 帧 / 最长静默 1.1 秒，以 `done` 收尾（同一批在修复前
既活不过 60 秒，也会在 300 秒处被「运行超时」掐掉），PRD §15.24 记的是这一条。

### 日志落盘与「静默断连」四态判读

日志同时写 stderr 与文件（`PY_SERVER_LOG_FILE`，默认 `.tmp/logs/chat.log`，相对进程 cwd；
5MB × 5 份滚动）。落盘是刻意要的：uvicorn 只给 `uvicorn*` 配 handler，`app.*` 的日志
原本靠 logging 的 lastResort 打到终端，进程一没就零记录——2026-10-12 那次 novel 长跑
「连接 open 后无终态帧就断」，事后完全无法判定是谁结束了进程。

看到「生成连接已断开」时，按落盘日志区分四态（`scripts/verify_log_sink.py` 可在不监听
端口的前提下把启动/装配/关闭三行验一遍）：

| 日志里最后出现的 | 结论 | 下一步 |
| --- | --- | --- |
| `RUN_ERROR` / 「运行超时」（会映射成 `error` 帧） | 编排层失败，终态帧已发出 | 前端显示的应是「生成连接出错」；按堆栈查节点 |
| `WS 连接结束：… code=<码>` 而本轮没有 `done` | 客户端或反代先断，服务端是被打断的一方 | 查前端心跳、nginx `proxy_read_timeout`、票据续期 |
| 同上，且时刻恰好是 open 之后 60 秒、码 1006 | 服务端自己撕的：长跑期间没人 `receive()`，入站心跳把读通道顶死，保活 ping 超时（1011） | 跑 `scripts/probe_ws_keepalive_backpressure.py`；已修，见上面那条 |
| `chat 关闭（pid=…）` 且没有本轮的任何结束行 | 进程优雅退出（Ctrl+C、reload、容器收到信号） | 核对是谁重启的；见下面 reload 那条坑 |
| 既没有连接结束行也没有关闭行，日志戛然而止 | 进程被硬杀或崩溃 | 查系统事件/容器 OOM；用同一 pid 定位断点时刻 |

一个会自己制造第四态的坑：`scripts/run-service.mjs chat start` 用 `--reload` 且
`--reload-dir .` 覆盖整个 `services/chat`，所以长跑期间在这个目录里保存任何 `.py`
（包括临时探针脚本）都会重启子进程、掐断正在跑的那一轮。

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

`services/chat/tests/` 有 7 个用例文件（55 个用例）：`test_api`（REST）、`test_config`（宿主设置解析）、
`test_cooking_wiring` / `test_novel_wiring`（插槽装配）、`test_logging_sink`（落盘）、
`test_ws` 与 `test_ws_handshake`（帧协议与握手闸门）。全部离线跑，不依赖模型密钥与 MySQL。

CI 的 Chat job 在 `services/chat` 目录下依次跑：`agent-core` → `agent-cooking` → `agent-talk`
→ `agent-novel` 四套 pytest，再加 novel 的两道门禁（`test_golden.py` 一致性黄金集、
`test_longrun_metrics.py` 长跑指标，均为零模型消耗的离线断言），最后跑本目录 `tests`。
安装顺序同样是 agent-* 先装、chat 后装（见「快速开始」）。

## 镜像与部署

完整流程在本目录 [`DEPLOY_CLOUDRUN.md`](./DEPLOY_CLOUDRUN.md)；一键脚本是仓库根的
`pnpm chat:deploy`（有代理时用 `pnpm chat:deploy:official`）。构建侧的几条硬约束，出错时先按这里对照：

- **构建上下文必须是仓库根**：`docker build -f services/chat/Dockerfile .`。
  四个本地库包不在 PyPI，只按 `services/chat/` 建上下文会拿不到。
- **`agent-core` 必须带 `[redis]` extra**：`langgraph-checkpoint-redis` 是可选依赖，
  不装则 `AGENT_CORE_CHECKPOINTER=redis` 会**静默降级成 memory**——Redis 部署等于白做
  （本地也要求 `redis-stack-server`，普通 redis 缺 JSON/Search 模块时同样静默降级，见根 README）。
- **宿主 `app/` 用 COPY 落盘，不走 pip 打包**：曾经按 wheel 装，构建出一堆只有 `dist-info`
  的空包，镜像看着推成功、容器一起手就 `ModuleNotFoundError`。
- **不要加 `# syntax=docker/dockerfile:1`**：那会让 BuildKit 去 Docker Hub 拉前端镜像，
  本地网络直连不通（基础镜像与 PyPI 也都固定走国内加速源，Dockerfile 顶部有注释）。
- 构建期有一条导入冒烟（`import app.main` + `import langgraph.checkpoint.redis`），失败就让 build 红。
- 容器 `EXPOSE 5090`，`CMD` 里 host/port 写死为 `0.0.0.0:5090`；要改监听走 `PY_SERVER_*`。

密钥与环境变量：生产值集中在 **`services/chat/deploy-prod.json`**（已入库排除，`.gitignore` +
`.dockerignore` 都挡着），部署时按它逐条填进云托管控制台，任何 `deploy-prod.json` /
`application-prod.json` 都不得入库或进镜像。

## 已知缺口

登记在这里，动它之前先确认目的；值以控制台为准，别按命名规律推。

- **`deploy-prod.json` 里没有 `PY_SERVER_INTERNAL_TOKEN`**。若云上控制台就是照这份文件逐条填的，
  那么线上就缺验票令牌，`app/ws_auth.py` 会走「未配置 → 返回 None → 当作匿名」分支，
  novel-chat（工作台右栏对话）**一律拒连**，而本机开发因为 `.env` 里有值所以看不出来。
  实际是否中招要在云托管控制台核对环境变量列表——不要凭这份文件断定线上状态。
  这条与 `services/api/README.md` 登记的「`application-prod.json` 缺 `APP_INTERNAL_TOKEN`」是
  同一条链路的两端，补哪一端都要同时核对另一端是否同名等值。
- 匿名连接上 `cooking` / `talk` 的 `conversation_id` 可被猜测，风险作为遗留项登记在 PRD §15.16；
  不带 `agent` 的 `resume` 帧不在帧级闸门覆盖范围内，同一编号。
- REST `/api/items` 是模板期的示例 CRUD，数据在内存、进程重启即丢，没有线上消费者。

## 配置

环境变量（服务自身前缀 `PY_SERVER_`，编排层前缀 `AGENT_CORE_` 见 `../agent-core/README.md`，
插槽各自有前缀：烹饪 `COOKING_`、言外 `TALK_`、小说 `NOVEL_`）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PY_SERVER_HOST` | `0.0.0.0` | 监听地址 |
| `PY_SERVER_PORT` | `5090` | 监听端口 |
| `PY_SERVER_CORS_ORIGINS` | `http://localhost:8000,http://localhost:5173` | 逗号分隔的跨域来源（`.env.example` 里就是这一行，可带空格/尾逗号） |
| `PY_SERVER_API_BASE_URL` | `http://localhost:8080/api` | 验票通道指向的 Spring Boot 地址（含 `/api` 前缀），容器内用 `http://api:8080/api` |
| `PY_SERVER_INTERNAL_TOKEN` | 空 | 调 `POST /api/novel/internal/chat-ticket/verify` 时带的 `X-Internal-Token`；须等于 Spring 侧 `app.internal-token`。**留空 = 没有验票通道**，novel-chat 一律拒连（其余插槽不受影响） |
| `PY_SERVER_TICKET_TIMEOUT_SECONDS` | `5.0` | 验票那次内网 HTTP 调用的超时；超时必须拒连而不是放行 |
| `PY_SERVER_LOG_FILE` | `.tmp/logs/chat.log` | 日志落盘路径（相对 cwd）；留空 = 只输出 stderr。判读方式见上文「四态判读」 |
| `PY_SERVER_LOG_LEVEL` | `INFO` | 落盘与终端的最低级别（启动/装配/WS 生命周期行都是 INFO） |
| `COOKING_API_BASE_URL` | `http://localhost:8080/api` | 烹饪插槽读取的菜谱接口地址；容器内用 `http://api:8080/api` |
| `TALK_INTERNAL_TOKEN` | 空 | 言外建议回写 `/talk/internal/**` 的令牌；须等于 Spring 侧 `app.internal-token`，否则该插槽不落库 |
| `NOVEL_API_BASE_URL` | `http://localhost:8080/api` | 小说成稿与正典写入的内网地址（含 `/api` 前缀） |
| `NOVEL_INTERNAL_TOKEN` | 空 | 同上令牌；不一致时 `/novel/internal/**` 回 `code=403` |
| `NOVEL_PERSIST_ENABLED` | `true` | `false` 时成稿与正典都只留进程内（本地无后端 / 跑离线回归） |

插槽令牌的前缀各不相同（各包自己的 `Settings`）：`docker-compose.yml` 里统一由根 `.env`
的 `APP_INTERNAL_TOKEN` 映射到 `TALK_INTERNAL_TOKEN` / `NOVEL_INTERNAL_TOKEN`，
两个 Python 包都不直接读 `APP_*`。
