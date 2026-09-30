# po 项目知识手册

> 叮叮厨：菜谱内容平台 + AI 做菜助手。本文汇总架构、链路、部署与平台坑，供开发与运维查阅；密钥一律只存于各自 `.env`，本文不记录任何密钥值。

## 1. 工程结构与工作区

pnpm workspace monorepo（Node ≥ 22，pnpm ≥ 10）：

| 目录 | 内容 | 技术栈 |
| --- | --- | --- |
| `apps/admin-web/` | 管理后台 | Umi Max 4、React 19、Ant Design 6、React Query 5、Biome/Vitest |
| `apps/cooking-app/` | 移动端 App | Expo SDK 57、React Native、expo-router、NativeWind、TanStack Query |
| `apps/cooking-mini/` | 微信小程序 | Taro 4.2.1、React 18、webpack5（webpack 锁 ~5.95.0） |
| `apps/brand/` | 项目/个人介绍站 | Astro 7 + Tailwind CSS 4，模板 AstroWind（MIT）；静态站点，不与其它端共享组件与路由 |
| `services/api/` | 主后端 | Java 17、Spring Boot 4.1.1、MyBatis-Plus、MySQL、Redis(Jedis)、jjwt；Maven reactor 多模块：shared/identity/recipe/api-bootstrap |
| `services/chat/` | AI 聊天服务 | FastAPI + Uvicorn（5090）、LangChain/LangGraph、pyproject 管理依赖 |
| `packages/types/` | 跨端契约 `@po/types` | 前后端字段变更先改这里 |
| `scripts/` | 启动/部署包装器 | run-service.mjs、run-sh.mjs、run-mobile.mjs、deploy-*.sh |
| `infra/` | Nginx 网关配置 | docker-compose 部署形态 |

工作流入口：Qoder skills 位于 `.qoder/skills/`（project-router 分流 → frontend-dev / mobile-dev / java-dev / python-dev），上游开源参考是 `.qoder/skill-sources/` 只读镜像。

## 2. 认证与登录体系

- 账号来源：微信 OpenID 一键登录（`Taro.login` 换 code）、用户名密码、App 注册；注册与 OpenID 新用户进入**审批流**（`approval_status` pending/approved/rejected，管理后台 `system/users/approval` 审批）。
- 小程序只认 `role === 'user'` 会话；管理员走管理端。
- 登录 gating（前后端一致）：
  - 游客可浏览：首页、分类、菜谱详情（后端 `GET /recipes*`、`/recipe-categories*` 等 permitAll）、AI 聊天页整个界面。
  - 必须登录：开始做菜、AI 聊天的**发送消息**动作（点发送才跳登录，输入前界面完全可见）、个人中心及子页、收藏/点赞/上传/UGC。
  - 「我的」tab 页未登录显示缺省页 + 「去登录」按钮，聊天页游客态在输入栏上方显示登录提示条；**禁止自动强制跳转**（曾导致返回白屏）；跳登录前用 `po.auth.returnTo` 记录回跳地址。
- JWT：jjwt，`Authorization: Bearer`；401 统一触发前端 signOut。
- 生产网络链路必须 https/wss + 小程序后台合法域名；见第 5 节。

## 3. AI 聊天与做菜 Agent 链路

- 入口：`services/chat` WebSocket `/ws/chat`（不带 `/api` 前缀），帧协议 `run_started / token / tool_call_result / error / done / pong`；`thread_id` 作为 conversation_id 贯穿会话。
- `po_agent_core`：Orchestrator + VerticalAgent（烹饪）+ CheckpointerManager + 意图路由（HybridRouter：dense embedding + BM25，alpha=0.3）。
- 模型：LLM=DeepSeek（OpenAI 兼容）；embedding=阿里云百炼 MaaS 工作空间 `qwen3.7-text-embedding`（dim 1024）。`AGENT_CORE_ROUTER_THRESHOLD=0.55`（默认 1.0 过严，实际相似度 ~0.69 会全部落兜底）。
- 四层降级（设计上"坏掉也看起来正常"，排障要看日志不要只看行为）：EchoChatModel（LLM 不可用）、memory checkpointer（Redis 不可用）、关键词路由（embedding 不可用）、OfflineCookingModel（网络不可用）。
- 小程序 WS 客户端：每消息新建连接，8s 连接超时 / 90s 运行超时 / 30s ping；**失败静默回退本地规则回答**，验证真实连通要看开发者工具 Network 的 socket 面板；URL 必须是 `ws://`/`wss://` 前缀，写 `http://` 会静默失败。
- 生命周期：`app/main.py` 用类式 `AppLifespan`（`__aenter__/__aexit__`），不用 `@asynccontextmanager`。
- 陷阱：langchain `OpenAIEmbeddings` 会预分词，阿里端点拒收，路由侧必须用 `semantic_router.OpenAIEncoder`。

## 4. TTS 语音与对象存储

- 讯飞 TTS v2 WebSocket 合成，Java 侧（recipe 模块 `tts/`）实现；对外只返回**音频 URL**，不返回字节。
- 音频存腾讯云 COS，键规则 `tts/recipes/{id}/{vcn}/...`，桶公共读，返回绝对公网 URL。
- 缓存优先：`POST /tts/prefetch` 批量预热（命中缓存直接回 URL，未命中后台合成）；小程序进详情页/做菜页即预取全部步骤音频与完成播报。
- COS 也承载头像/封面/食材图上传（`/files/upload` 需登录；`/files/**` GET 公开）。
- 播放提示音 `step-done.wav` 由后端静态目录 `/api/sounds/` 提供，两端共用。

## 5. 部署（微信云托管 CloudRun）

- 服务：`po-api`（Spring）、`chat`（FastAPI）、redis；部署脚本 `pnpm api:deploy / chat:deploy / redis:deploy`，official 变体设 `USE_OFFICIAL_IMAGES=1`。Docker 构建走国内镜像（DaoCloud 基础镜像、腾讯 PyPI 镜像），详见 DEPLOY_CLOUDRUN.md 两份台账。
- Windows 注意：`bash foo.sh` 会命中 WSL 存根报 `execvpe(/bin/bash) failed`；所有 pnpm 脚本经 `scripts/run-sh.mjs` 显式定位 Git Bash，并支持 `--env KEY=VAL`。
- 镜像仓库 `ccr.ccs.tencentyun.com`，`docker push` 前需 `docker login`。
- 内网地址形态：`ca-<env>.<服务名>.<repo>.<域>.com:<端口>`（点号分隔、端口显式写），只在云托管环境内可达；chat 调 api 走 `COOKING_API_BASE_URL` 内网地址，api/chat 调 redis 同理。
- Redis 必须是 **redis-stack**（JSON+Search 模块），纯 redis 会让 LangGraph checkpointer 静默降级 memory。
- 小程序访问：
  - 内网/免域名只对 HTTP 云调用生效且需走 `wx.cloud.callContainer`（X-WX-SERVICE 头）；`wx.request` 直连内网地址在真机不可达。
  - WebSocket 不走云调用，必须公网 `wss://` + socket 合法域名。
  - 云托管默认公网域名 `*.sh.run.tcloudbase.com` 已备案，可直接填合法域名；自有域名需备案后在云托管「自定义域名」绑定。
  - api 需配 request+uploadFile 合法域名，chat 需配 socket 合法域名。
- 平台常量（域名、环境 ID、仓库名）一律从控制台逐字复制，禁止凭记忆填写。

## 6. 微信小程序平台坑（WXSS/构建/上传）

- WXSS 不支持：`flex-wrap`（用行容器+百分比）、`calc()`、flexbox `gap`（用 margin）、`*` 通配符（box-sizing 用元素选择器）；emoji 用 Unicode 转义（`'\u{1F37D}\uFE0F}'`）；`Text` 是行内元素。
- SCSS 引用主题令牌用 `@use '…/theme.scss' as *;`，`@import` 已被 Dart Sass 弃用（构建报警告）。
- `app.config.ts` 必须 `lazyCodeLoading: 'requiredComponents'`（组件按需注入是上传审核项）。
- `project.config.json`（根与 dist 两份保持一致）：真实 appid、`miniprogramRoot: "dist/"`、`setting.minified/minifyWXSS/minifyWXML: true`。
- 环境变量：Taro 只注入 `TARO_APP_*`；`dev:weapp` 载入 `.env.development`，`build:weapp` 载入 `.env.production`，改完必须重新构建。
- 产物 `dist/` 约 640K（压缩后），主包限额 2M 内无压力。

## 7. 后端持久层约定（services/api）

- MyBatis-Plus 统一持久层：`@Mapper` 继承 `BaseMapper`，实体 `@TableName`/`@TableId(AUTO)`，审计字段由 api-bootstrap 的 `AuditMetaObjectHandler` 填充（创建时间 `NEVER` 更新、更新时间 `INSERT_UPDATE`）。
- 表结构以 `api-bootstrap/src/main/resources/schema.sql` 为准（`spring.sql.init.mode: always` 幂等建表），新表先改 schema.sql 再改实体。
- 复杂 SQL 用 XML mapper（`src/main/resources/mapper/XxxMapper.xml`，namespace 为接口全限定名）；例：recipe `selectDetailWithChildren` 一次 LEFT JOIN 带出食材/步骤。
- 分页：Controller/Service 用 spring-data-commons 的 `Page`，shared 模块 `MyBatisPages` 转换；依赖 api-bootstrap 的 `PaginationInnerInterceptor`。
- 响应协议：shared `Result<T>` 包装 + 现有业务码，全端共享同一信封解包逻辑。
- 本地启动依赖 Docker：根目录 `.env` + `docker compose up -d mysql redis`；验证 `pnpm api:verify`。

## 8. 常用命令速查

| 目的 | 命令（仓库根） |
| --- | --- |
| 类型包构建 | `pnpm types:build` |
| 管理端 开发/构建/检查 | `pnpm admin:dev`、`pnpm admin:build`、`pnpm admin:typecheck` |
| 后端 启动/验证 | `pnpm api:start`、`pnpm api:verify`（脚本自动定位 JDK 17） |
| 聊天 启动/测试 | `pnpm chat:start`、`pnpm chat:test` |
| App | `pnpm mobile:start`、`pnpm mobile:apk`、`pnpm mobile:test` |
| 小程序 | `pnpm mini:dev`、`pnpm mini:build`（H5：`mini:dev:h5`） |
| 介绍站 | `pnpm brand:dev`、`pnpm brand:build`、`pnpm brand:preview`、`pnpm brand:check`、`pnpm brand:assets`（改完 `src/assets/illustrations/*.svg` 后重新生成 OG 与博客封面位图；Astro 端口 4321） |
| 介绍站 部署 | `pnpm brand:deploy`（镜像推云托管内置仓库 `tcb-100053273154-byrm/brand`，流程见 `apps/brand/DEPLOY_CLOUDRUN.md`） |
| 云托管部署 | `pnpm api:deploy`、`pnpm chat:deploy`、`pnpm redis:deploy`（+ `:official` 变体） |
