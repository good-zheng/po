# po-agent-core

po monorepo 的智能体编排核心库（框架无关）。当前唯一的消费者是 `services/chat`（FastAPI 宿主）：
它在本包的 `supervisor` 父图上把四个垂直插槽挂上去——`cooking`（`../agent-cooking`）、
`talk`（`../agent-talk`）、`novel`（`../agent-novel`，成稿链路）与
`novel-chat`（同一包里的工作台对话面板，与 `novel` 各自独立注册），登记点见 chat 的
`app/agent.py` `_builtin_agents`。本包自己不认得任何业务领域。

## 架构铁律

- **本包是纯库**：任何模块不得 import Web 框架、ORM 或宿主应用。`tests/test_architecture.py`
  的 `FORBIDDEN_MODULES` 是判定集合：`fastapi`、`flask`、`uvicorn`、`starlette`、`socketio`、
  `django`、`sqlalchemy`、`po_chat`。
- **禁止 import 副作用**：所有重资源（Redis 连接、模型客户端、graph 编译）必须在显式的
  工厂/初始化函数中延迟创建，模块顶层只允许定义。同一测试文件用 `SUSPICIOUS_CALLS`
  在 AST 层面查顶层调用：`connect`、`from_conn_string`、`compile`、`setup`、`invoke`、`stream`。
- **依赖注入**：核心 API 接收显式的 settings / 组件参数，不读取全局单例。
- 领域逻辑（垂直 Agent）通过插槽注册进来，本包不含任何业务领域知识。

## 模块

| 模块 | 职责 | 状态 |
| --- | --- | --- |
| `config` | `AgentCoreSettings`（环境变量前缀 `AGENT_CORE_`） | 已实现（P0） |
| `llm.factory` | LLM / Embedding 工厂（OpenAI 兼容协议，qwen/deepseek/openai 预设） | 已实现（P0） |
| `events` | 统一事件流契约（lifecycle / thinking / tool / output / control 五组 + `STEP`） | 已实现（P0） |
| `errors` | `AgentCoreError` 与 `AgentCoreConfigError` 两级异常：宿主既可统一兜底，也靠配置类错误驱动降级链（回显模型 / 关键词路由），而不是让服务起不来 | 已实现 |
| `memory` | checkpointer（redis/sqlite/memory 三策略）+ 长期记忆 store（用户级命名空间） | 已实现（P1） |
| `routing` | Layer1 意图路由：semantic-router HybridRouter（稠密+BM25 混合）→ embedding 不可用时降级本地关键词路由（bigram 覆盖率）→ 兜底 | 已实现（P1/P5） |
| `supervisor` | supervisor graph 工厂（chitchat 兜底 + 垂直 agent 分发 + 条件边 Layer2） | 已实现（P1） |
| `runner` | AgentRunner：astream 驱动，LangGraph 流 → `AgentEvent` 统一翻译（含超时/异常/interrupt） | 已实现（P1） |
| `tools` | 两级工具注册表（全局 + Agent 命名空间） | registry 已实现（P1）；MCP 远端注入待 P3 |
| `agents` | 垂直 Agent 插槽协议（`VerticalAgent` 契约校验） | 已实现；本包不含内置垂直 Agent，四个插槽（`cooking` / `talk` / `novel` / `novel-chat`）都在宿主 chat 的 `_builtin_agents` 登记 |
| `protocols.mcp` / `protocols.a2a` | MCP、A2A 协议双向适配 | **仅有规划（P3/P4），`src/po_agent_core/protocols/` 目录还不存在** |

## 安装（作为 chat 宿主的依赖）

本包没有自己的 venv，靠 `services/chat/.venv` 跑。顺序不能反——四个库包都依赖 core，
core 必须先装，且 chat 的 `.env` 里同文件混着 `AGENT_CORE_*` 与 `PY_SERVER_*` 两段命名空间：

```powershell
# 在 services/chat 下，按序
pip install -e "../agent-core[dev]"
pip install -e "../agent-cooking[dev]"
pip install -e "../agent-talk[dev]"
pip install -e "../agent-novel[dev]"
pip install -e ".[dev]"
```

或直接用仓库根命令：`pnpm chat:install`（就是上面这五条，见 `scripts/run-service.mjs`）。

镜像里不一样：`services/chat/Dockerfile` 装的是 `/packages/agent-core[redis]`（不带 `dev`），
**`[redis]` extra 不能省**——`langgraph-checkpoint-redis` 是可选依赖，缺了它
`AGENT_CORE_CHECKPOINTER=redis` 会静默降级成 memory，Redis 部署等于白做。

## 测试

```powershell
pnpm agentcore:test
# 或在 services/agent-core 下（复用 chat 的 .venv）
..\chat\.venv\Scripts\python.exe -m pytest
```

当前收集到 96 个用例，不依赖外部服务：checkpointer 用 memory 策略，LLM 只做离线构造断言。
真实 Redis 连接测试由环境变量 `AGENT_CORE_TEST_REDIS=1` 门控（默认跳过，CI 无 Redis 也能全绿）。
`tests/test_architecture.py` 是上面「架构铁律」的执行器，改铁律要连它一起改。

## 配置

环境变量前缀 `AGENT_CORE_`（宿主 `.env` 与 `services/chat/.env` 同文件即可）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `AGENT_CORE_LLM_PROVIDER` | `qwen` | `qwen` / `deepseek` / `openai` / `custom` |
| `AGENT_CORE_LLM_MODEL` | provider 预设 | 模型名（qwen 预设 `qwen-plus`，deepseek 预设 `deepseek-chat`） |
| `AGENT_CORE_LLM_API_KEY` | 空 | **必填**（调用 LLM 时校验） |
| `AGENT_CORE_LLM_BASE_URL` | provider 预设 | OpenAI 兼容 base_url，覆盖预设 |
| `AGENT_CORE_LLM_TEMPERATURE` | `0.7` | 默认槽位温度；可按角色覆盖（`…__<角色>__TEMPERATURE`） |
| `AGENT_CORE_LLM_TIMEOUT_SECONDS` | `120.0` | 单次模型调用超时，属传输层参数，**对所有角色统一生效**，不分角色配 |
| `AGENT_CORE_LLM_MAX_RETRIES` | `2` | 同上，客户端重试次数 |
| `AGENT_CORE_LLM_ROLES__<角色>__<字段>` | 空 | 分阶段模型覆盖槽位（`<角色>` 如 `CHAT`/`PLAN`/`WRITE`/`JUDGE`，`<字段>` 为 `MODEL`/`PROVIDER`/`API_KEY`/`BASE_URL`/`TEMPERATURE`）。不配即单模型，见下节 |
| `AGENT_CORE_EMBEDDING_MODEL` | provider 预设 | 语义路由 embedding（qwen 预设 `text-embedding-v4`）；仍为空则路由层降级为关键词路由 |
| `AGENT_CORE_EMBEDDING_API_KEY` / `AGENT_CORE_EMBEDDING_BASE_URL` | 回退 LLM 同名项 | embedding 与 LLM 不同 provider 时配置。**没有 `EMBEDDING_PROVIDER` 这一项**，provider 跟随 `AGENT_CORE_LLM_PROVIDER` |
| `AGENT_CORE_EMBEDDING_DIMENSIONS` | `1024` | embedding 维度，须与实际模型输出维度一致，否则 semantic-router 的稠密比对失配 |
| `AGENT_CORE_CHECKPOINTER` | `redis` | `redis` / `sqlite` / `memory` |
| `AGENT_CORE_REDIS_URL` | `redis://localhost:6379` | checkpointer 连接串；本地要用 **redis-stack-server**（普通 redis 缺 JSON/Search 模块会静默降级成 memory） |
| `AGENT_CORE_SQLITE_PATH` | `.agent-core/checkpoints.sqlite` | sqlite 策略文件路径（相对进程 cwd） |
| `AGENT_CORE_ROUTER_THRESHOLD` | `1.0` | 意图路由命中阈值：HybridRouter 总分 = 稠密余弦（≈0~1）+ BM25 稀疏分（关键词命中可达 3+），低于阈值视为未命中走兜底 |
| `AGENT_CORE_RUN_TIMEOUT_SECONDS` | `300.0` | 单次编排运行总预算，超时由 runner 翻译成 `RUN_ERROR` 事件，避免前端一直等不到 `done` |

### Provider 预设与「embedding 和 LLM 不同源」

`llm/factory.py` 的 `PROVIDER_PRESETS` 决定不配时的默认值：

| provider | 默认 chat 模型 | 默认 embedding 模型 |
| --- | --- | --- |
| `qwen` | `qwen-plus` | `text-embedding-v4` |
| `deepseek` | `deepseek-chat` | **空**（DeepSeek 没有 embedding 接口） |
| `openai` | `gpt-4o-mini` | `text-embedding-3-small` |
| `custom` | 空，必须自己给 `LLM_MODEL` + `LLM_BASE_URL` | 空 |

本包**没有 `AGENT_CORE_EMBEDDING_PROVIDER` 这一项**：embedding 的预设永远按 `LLM_PROVIDER` 取。
所以「正文用 DeepSeek、向量走别家」这种组合，要把 `EMBEDDING_MODEL`、`EMBEDDING_API_KEY`、
`EMBEDDING_BASE_URL` **三项都显式配上**——少一项就回落到 `LLM_*`，等于把 A 家的地址和密钥
发给 B 家。三项都配齐时路由层用的就是第二家的 embedding 模型，与 LLM 互不干扰。

### 多模型（分阶段切换）

`AGENT_CORE_LLM_*` 是「默认槽位」；按用途声明覆盖槽位即可让不同阶段用不同模型：

```bash
AGENT_CORE_LLM_ROLES__CHAT__MODEL=qwen-turbo        # 闲聊兜底换便宜模型
AGENT_CORE_LLM_ROLES__WRITE__MODEL=qwen-max         # 正文用最强模型
AGENT_CORE_LLM_ROLES__WRITE__TEMPERATURE=0.8        # 温度也可按角色覆盖
AGENT_CORE_LLM_ROLES__JUDGE__PROVIDER=deepseek      # 跨 provider 必须连密钥一起给
AGENT_CORE_LLM_ROLES__JUDGE__MODEL=deepseek-chat
AGENT_CORE_LLM_ROLES__JUDGE__API_KEY=sk-xxx
```

- 解析优先级：显式参数 > 角色槽位 > `AGENT_CORE_LLM_*` > provider 预设；未声明的角色
  完全回落默认槽位（「不配就是单模型」）。
- 角色名大小写不敏感，取值是开放词汇。`config.ModelRole` 列出的四个推荐值是
  `chat`（闲聊兜底、轻量问答）、`plan`（构思/大纲/拆解）、`write`（长文本正文）、
  `judge`（评审、打分、结构化抽取）——垂直 Agent 可声明自己的角色，core 不校验全集。
- **跨 provider 不复用密钥**：槽位指定了与默认槽位不同的 provider 时，默认槽位的
  model / base_url / api_key 一概不继承，缺密钥直接报错并指明该配哪个变量
  （把 A 家密钥发往 B 家是错误而非便利）。
- 模型在**装配期**取定（`build_*` 时按角色创建实例），改动后重启生效，运行中不热切换。
- API Key 只从环境变量读取，不进代码、日志与事件流。

## 已知偏差

- `events.py:3` 与 `runner/runner.py:3` 的 docstring 都说事件名「对齐
  `services/chat/agent_run_satus.json` 草案」，**那份文件已不在仓库里**。事件契约的唯一真源是
  `src/po_agent_core/events.py` 的枚举，以及 chat 侧 `app/routers/ws.py` 的出站帧表
  （见 `services/chat/README.md`）。改协议以代码为准，别去找那份 JSON。
- `protocols.mcp` / `protocols.a2a` 只在模块表里作为 P3/P4 规划出现，目录尚未创建；
  「未来的 agentgateway」这类早期设想也不在本包范围内——当前宿主只有 `services/chat`。

## 参考来源

编排骨架模式参考自 `D:\dev\novel_server`（LangGraph 六阶段流水线）的重构分析：保留"结构化抽取路由、反思循环、interrupt 人工确认、流式进度事件"五骨架，修复其循环依赖、import 副作用、State 上帝对象、同步阻塞等问题。
