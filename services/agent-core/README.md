# po-agent-core

po monorepo 的智能体编排核心库（框架无关）。为 `services/chat`（FastAPI 宿主）、未来的 agentgateway 与独立垂直 Agent 服务提供统一的编排能力。

## 架构铁律

- **本包是纯库**：任何模块不得 import `fastapi` / `flask` / `uvicorn` / `starlette` / `sqlalchemy` 等 Web 框架或宿主应用（`tests/test_architecture.py` 强制校验）。
- **禁止 import 副作用**：所有重资源（Redis 连接、模型客户端、graph 编译）必须在显式的工厂/初始化函数中延迟创建，模块顶层只允许定义。
- **依赖注入**：核心 API 接收显式的 settings / 组件参数，不读取全局单例。
- 领域逻辑（垂直 Agent）通过插槽注册进来，本包不含任何业务领域知识。

## 模块

| 模块 | 职责 | 状态 |
| --- | --- | --- |
| `config` | `AgentCoreSettings`（环境变量前缀 `AGENT_CORE_`） | 已实现（P0） |
| `llm.factory` | LLM / Embedding 工厂（OpenAI 兼容协议，qwen/deepseek/openai 预设） | 已实现（P0） |
| `events` | 统一事件流契约（对齐 `services/chat/agent_run_satus.json` 草案） | 已实现（P0） |
| `memory` | checkpointer（redis/sqlite/memory 三策略）+ 长期记忆 store（用户级命名空间） | 已实现（P1） |
| `routing` | Layer1 意图路由：semantic-router HybridRouter（稠密+BM25 混合）→ embedding 不可用时降级本地关键词路由（bigram 覆盖率）→ 兜底 | 已实现（P1/P5） |
| `supervisor` | supervisor graph 工厂（chitchat 兜底 + 垂直 agent 分发 + 条件边 Layer2） | 已实现（P1） |
| `runner` | AgentRunner：astream 驱动，LangGraph 流 → `AgentEvent` 统一翻译（含超时/异常/interrupt） | 已实现（P1） |
| `tools` | 两级工具注册表（全局 + Agent 命名空间） | registry 已实现（P1）；MCP 远端注入待 P3 |
| `agents` | 垂直 Agent 插槽协议（`VerticalAgent` 契约校验） | 已实现；暂无内置垂直 Agent，宿主侧登记点见 chat 的 `_builtin_agents` |
| `protocols.mcp` / `protocols.a2a` | MCP、A2A 协议双向适配 | 规划（P3/P4） |

## 安装（作为 chat 宿主的依赖）

```powershell
# 在 services/chat 下
pip install -e "../agent-core"        # 先装本包
pip install -e ".[dev]"               # 再装宿主
```

或直接用仓库根命令：`pnpm chat:install`。

## 测试

```powershell
pnpm agentcore:test
# 或在 services/agent-core 下（复用 chat 的 .venv）
..\chat\.venv\Scripts\python.exe -m pytest
```

测试不依赖外部服务：checkpointer 用 memory 策略，LLM 只做离线构造断言。
真实 Redis 连接测试由环境变量 `AGENT_CORE_TEST_REDIS=1` 门控（默认跳过，CI 无 Redis 也能全绿）。

## 配置

环境变量前缀 `AGENT_CORE_`（宿主 `.env` 与 `services/chat/.env` 同文件即可）：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `AGENT_CORE_LLM_PROVIDER` | `qwen` | `qwen` / `deepseek` / `openai` / `custom` |
| `AGENT_CORE_LLM_MODEL` | provider 预设 | 模型名（qwen 预设 `qwen-plus`，deepseek 预设 `deepseek-chat`） |
| `AGENT_CORE_LLM_API_KEY` | 空 | **必填**（调用 LLM 时校验） |
| `AGENT_CORE_LLM_BASE_URL` | provider 预设 | OpenAI 兼容 base_url，覆盖预设 |
| `AGENT_CORE_LLM_ROLES__<角色>__<字段>` | 空 | 分阶段模型覆盖槽位（`<角色>` 如 `CHAT`/`PLAN`/`WRITE`/`JUDGE`，`<字段>` 如 `MODEL`/`PROVIDER`/`API_KEY`/`TEMPERATURE`）。不配即单模型，见下节 |
| `AGENT_CORE_EMBEDDING_MODEL` | provider 预设 | 语义路由 embedding（qwen 预设 `text-embedding-v4`） |
| `AGENT_CORE_EMBEDDING_API_KEY` / `AGENT_CORE_EMBEDDING_BASE_URL` | 回退 LLM 同名项 | embedding 与 LLM 不同 provider 时配置 |
| `AGENT_CORE_CHECKPOINTER` | `redis` | `redis` / `sqlite` / `memory` |
| `AGENT_CORE_REDIS_URL` | `redis://localhost:6379` | checkpointer Redis 连接 |
| `AGENT_CORE_SQLITE_PATH` | `.agent-core/checkpoints.sqlite` | sqlite 策略文件路径 |
| `AGENT_CORE_ROUTER_THRESHOLD` | `1.0` | 意图路由命中阈值：HybridRouter 总分 = 稠密余弦（≈0~1）+ BM25 稀疏分（关键词命中可达 3+），低于阈值视为未命中走兜底 |
| `AGENT_CORE_RUN_TIMEOUT_SECONDS` | `300` | 单次编排运行超时 |

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
- 角色名大小写不敏感，取值是开放词汇（`ModelRole` 列的是推荐值）：垂直 Agent
  自行声明用哪些角色，core 不校验全集。
- **跨 provider 不复用密钥**：槽位指定了与默认槽位不同的 provider 时，默认槽位的
  model / base_url / api_key 一概不继承，缺密钥直接报错并指明该配哪个变量
  （把 A 家密钥发往 B 家是错误而非便利）。
- 模型在**装配期**取定（`build_*` 时按角色创建实例），改动后重启生效，运行中不热切换。
- API Key 只从环境变量读取，不进代码、日志与事件流。

## 参考来源

编排骨架模式参考自 `D:\dev\novel_server`（LangGraph 六阶段流水线）的重构分析：保留"结构化抽取路由、反思循环、interrupt 人工确认、流式进度事件"五骨架，修复其循环依赖、import 副作用、State 上帝对象、同步阻塞等问题。
