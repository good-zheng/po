# `po-agent-talk` — 言外 EchoTalk 垂直 Agent（纯库）

对话理解与表达建议的子图：把「对方刚说的那句话」解析成意图、潜台词、情绪、风险，加三条可照读的回复。

**它不是一个服务。**没有 `main.py`、没有端口、没有自己的容器——由宿主 `services/chat` 在启动时把它
注册成一个 Agent 插槽（`services/chat/app/agent.py` 的 `_builtin_agents`，talk 那一段），建议的落库回写
走宿主的钩子（`services/chat/app/talk.py` 里 `agent != TALK_AGENT` 就返回的那个 after-hook）。所以本目录
没有 Dockerfile，镜像由 `services/chat/Dockerfile` 把四个本地库包按依赖序 `pip install` 进去。

## 安装与测试

依赖序很重要：`po-agent-core` 与本包都不在 PyPI 上，必须先装 agent-core 再装本包。

```bash
pnpm chat:install      # 仓库根；按 agent-core → agent-cooking → agent-talk → agent-novel → chat 顺序装进 services/chat/.venv
pnpm agenttalk:test    # 仓库根；在 services/agent-talk 下用 chat 的 .venv 跑 python -m pytest tests
```

`agenttalk` 分支只支持 `test` 目标（`scripts/run-service.mjs:95-98`），本包没有 `install` / `start`
入口，别指望 `pnpm agenttalk:start`。测试共收集 12 例（`tests/test_agent.py` 2 例、
`tests/test_schema.py` 7 个函数其中 1 个 parametrize 4 例），**全程离线**，不需要模型 Key 与后端，
所以 CI 的 chat job 里也照跑（`.github/workflows/ci.yml:209,218,228-229`）。

## 目录

| 文件 | 职责 |
| --- | --- |
| `agent.py` | 插槽装配。插槽名 `talk`（`TALK_AGENT_NAME`，必须与 Layer1 路由的 `Route.name` 一致，前端也可用 `WSInFrame.agent` 直连）；模型角色同为 `talk`；按角色取模型失败即降级为 `OfflineTalkModel`（`:61-67`） |
| `graph.py` | 单节点子图 `START → agent → END`：无工具、非 ReAct。系统提示每轮拼在最前、不进 state；历史窗口按 `HISTORY_LIMIT` 对齐 `HumanMessage` |
| `prompts.py` | 场景表（`general` / `work` / `sales` / `romance`，由宿主把 `context.scene` 拼进用户消息前缀，模型自己对号入座）与系统提示；输出被硬性约束成单个 JSON 对象 |
| `schema.py` | `TalkAnalysis` / `SuggestionItem`；三条建议的风格固定为「稳妥 / 共情 / 推进」（前端卡片配色与朗读顺序依赖这三个值）；`parse_analysis` 宽容剥离代码围栏与寒暄，解析失败返回 `None` 而不是抛错 |
| `offline.py` | 关键词→情绪的 5 组规则与 `OfflineTalkModel`（`OFFLINE_TAG = "offline"`），模型缺配置或不可用时的兜底档 |
| `persist.py` | 落库：`POST {api_base_url}/talk/internal/suggestions` + `X-Internal-Token`；HTTP ≥ 400 记 warning 返 `False`，网络异常只记日志、**不阻断对话** |
| `config.py` | `TalkSettings`（pydantic-settings，`env_prefix="TALK_"`、读 `.env`、`extra="ignore"`） |

## 配置

只有四个字段，且**刻意不含任何 LLM 字段**——模型供应商配置统一在 agent-core，
按角色覆盖用 `AGENT_CORE_LLM_ROLES__TALK__MODEL`（可以给 `talk` 配一个更快更便宜的小模型）。

| 字段 | 默认 | 环境变量 |
| --- | --- | --- |
| `api_base_url` | `http://localhost:8080/api` | `TALK_API_BASE_URL`（容器内指向 `http://api:8080/api`，含 `/api` 前缀） |
| `internal_token` | 空 | `TALK_INTERNAL_TOKEN`；与 Spring 侧 `app.internal-token` 必须一致，不一致落库被 403 拒 |
| `request_timeout_seconds` | `5.0` | `TALK_REQUEST_TIMEOUT_SECONDS` |
| `persist_enabled` | `True` | `TALK_PERSIST_ENABLED`；关掉只在内存里跑分析、不回写，便于本地无后端自测 |
| `history_limit` | `12` | `TALK_HISTORY_LIMIT` |

密钥只写在 `services/chat/.env`（ compose 侧对应 `docker-compose.yml` 的 `TALK_INTERNAL_TOKEN`），
不进代码、日志与文档。

## 与其他服务的边界

- 小程序 `apps/echo-talk` **不直连本包**：它打的是 Spring Boot 的 `/talk/**`（会话与转写增删改查），
  洞察结果由 `services/chat` 经 `/ws/chat` 流式返回，并由本包回写到 `POST /talk/internal/suggestions`。
- 实时转写不在这里。ASR 网关在 Java 侧（`services/api` 的 `talk` 模块，`/ws/asr`），本包只做语义分析。
- `apps/echo-talk/PRD.md` 里把 ASR 网关画在 chat 侧，那是初稿口径，与现状不符，以代码为准。

## 已知的取舍

- 落库失败只记日志：建议没存进 `talk_suggestion` 表，用户侧仍能看到结果。历史里回看会缺这一条。
- 系统提示里的第 4 条硬性要求（不臆造背景）与第 5 条（医疗/法律/金融/人事必须提示咨询专业人士）
  是刻意写死的，改动会让 `tests/test_schema.py` 的形状断言失效。
- 插槽名同时被路由语料命中和前端 `agent` 字段依赖，改名要三处一起动（本包、`services/chat` 的
  `_builtin_agents`、前端帧）。
