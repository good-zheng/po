# po

三件作品共用的全栈 Monorepo：叮叮厨（菜谱 + AI 做菜助手）、言外 EchoTalk（实时转写 + 语义洞察）、
言外书斋（长文本一致性链路）。pnpm workspace 管理前端与共享类型，Maven reactor 管理 Spring Boot 后端，
Python FastAPI 提供流式聊天与 Agent 编排，Docker Compose + Nginx 网关统一编排本地环境，
线上按应用分别走微信云托管。

每个应用都有自己的 README，本文只讲跨应用的拓扑与命令；改动某应用前先读它目录下的那份。
`apps/admin-web/cloudflare-worker` 是 Ant Design Pro 模板自带的 demo，本项目不使用、不要往里加业务。

| 层 | 技术栈 | 位置 |
| --- | --- | --- |
| 管理前端 | Umi Max 4 + React 19 + Ant Design 6 + React Query 5 + Vitest 4 + Biome | `apps/admin-web` |
| 移动端 | Expo SDK 57 + React Native + expo-router + NativeWind + React Query + Jest | `apps/cooking-app` |
| 微信小程序（叮叮厨） | Taro 4.2.1 + React 18 + webpack5 + SCSS/rpx（无第三方状态库与请求库） | `apps/cooking-mini` |
| 言外小程序 | Taro 4.2.1 + React 18（录音 → 实时 ASR → 洞察建议） | `apps/echo-talk` |
| 小说阅读端 | Umi Max 4 + React 19 + Ant Design 6（移动优先，无 ProLayout / locale / Vitest） | `apps/novel-web` |
| 个人品牌站 | Astro + AstroWind + Tailwind（静态介绍站与开发手记） | `apps/brand` |
| 开发者知识库 | 上游 vendored PowerWiki（该目录被 gitignore，内容经 `pnpm wiki:sync` 发布） | `apps/power-wiki` |
| 共享类型 | TypeScript 包 `@po/types` | `packages/types` |
| 业务 API | Java 17 + Spring Boot 4 + MyBatis-Plus + MySQL + Redis + JWT | `services/api` |
| 聊天服务 | Python 3.11 + FastAPI + WebSocket + LangGraph | `services/chat` |
| Agent 编排 | 纯库 `po-agent-core`（supervisor / 事件流 / semantic-router 意图路由 / 记忆，垂直 Agent 经插槽接入） | `services/agent-core` |
| 烹饪助手 Agent | 纯库 `po-agent-cooking`（菜谱检索 / 详情 / 分类三个工具 + ReAct 子图，注册进 chat 宿主） | `services/agent-cooking` |
| 言外 Agent | 纯库 `po-agent-talk`（对话理解与表达建议子图，建议经 `/talk/internal/**` 回写落库），注册进 chat 宿主 | `services/agent-talk` |
| 小说 Agent | 纯库 `po-agent-novel`（构思 → 大纲 → 逐章生成与审稿 → 正典抽取 → 归档确认），成稿与正典经 `/novel/internal/**` 落库 | `services/agent-novel` |
| 网关与编排 | Nginx 1.27 + Docker Compose | `infra/nginx`、`docker-compose.yml` |

## 架构总览

```
apps/admin-web        管理前端（Docker 多阶段构建 → 云托管容器托管静态产物）
apps/cooking-app      Expo 移动端（expo-router + NativeWind，直连 API 与 /ws/chat）
apps/cooking-mini     微信小程序·叮叮厨（Taro；个人主体无 AI 类目，大模型链路已在源码里摘除，
                      「菜谱问答」tab 只走本地意图规则 + 菜谱接口）
apps/echo-talk        微信小程序·言外（Taro；录音 → Spring /ws/asr 实时转写 → chat /ws/chat 出洞察）
apps/novel-web        言外书斋阅读端（Umi，移动优先，游客可浏览）
apps/brand            个人品牌站与开发手记（Astro 静态站）
apps/power-wiki       开发者知识库（上游 vendored，目录被 gitignore，内容走 pnpm wiki:sync）
packages/types        前后端共享 TS 类型（@po/types，只有类型、无运行时代码）
services/api          Maven 多模块单体
  ├─ shared           公共 DTO / Result / 异常
  ├─ identity         用户、认证、JWT
  ├─ recipe           菜谱与分类（种子数据账目见 recipe/README.md）
  ├─ talk             言外对话与表达建议 + ASR 网关 /ws/asr（含 /talk/internal/** 回写）
  ├─ novel            书架/章节/角色 + L0 正典层 + 创作工作台（含 /novel/internal/** 写入通道）
  └─ api-bootstrap    启动模块（application.yaml，context-path=/api）
services/agent-core    编排核心纯库（supervisor / 事件流翻译 / 意图路由 / 会话记忆，
                      垂直 Agent 经插槽接入，不含业务领域知识）
services/agent-cooking 烹饪助手垂直 Agent（菜谱检索 / 详情 / 分类三个工具 + ReAct 子图，
                      按 cooking 角色取模型，模型或菜谱后端不可用时逐级降级）
services/agent-talk    言外垂直 Agent（对话理解 + 表达建议子图，建议回写内网端点）
services/agent-novel   小说垂直 Agent（六节点子图：构思 → 大纲 → 生成 ⇄ 审稿 → 正典抽取 →
                      归档确认；逐字证据闸门 + 幂等入库，模型缺配置时整体离线降级）
services/chat          FastAPI 宿主（/api/health、/api/items、/ws/chat 流式编排，装配 agent-core 与
                      cooking / talk / novel / novel-chat 四个插槽，LLM 缺配置时离线降级）
infra/nginx/nginx.conf 网关分流规则
```

请求统一从网关进入，按前缀分流：

| 路径 | 上游 | 说明 |
| --- | --- | --- |
| `/ws/chat` | chat:5090 | WebSocket 流式聊天 |
| `/ws/asr` | api:8080 | 言外的实时转写；对外保持 `/ws/asr`，内部重写成 `/api/ws/asr` 再转（Spring 的 context-path 会作用在 WebSocket 端点上） |
| `/api/health`、`/api/items/**` | chat:5090 | FastAPI 接口 |
| `/api/**`（其余） | api:8080 | Spring Boot（含 auth/users/recipes/actuator，前缀由 `server.servlet.context-path=/api` 消费） |
| `/` | Nginx 静态 | Umi 产物，history 路由回退 `index.html`，带 hash 资源长缓存 30d |

## 生产环境

### 服务拓扑（docker-compose）

| 服务 | 镜像 / 构建 | 端口 | 持久化 |
| --- | --- | --- | --- |
| `mysql` | `mysql:8.4` | 仅内网 3306 | 命名卷 `mysql_data` |
| `redis` | `docker.m.daocloud.io/redis/redis-stack-server:latest`（JSON + Search 模块，`chat` 会话持久化依赖；换官方名要用带前缀的镜像源，Docker Hub 直连不通） | 仅内网 6379 | 命名卷 `redis_data` |
| `api` | `services/api/Dockerfile` | 仅内网 8080 | 命名卷 `uploads_data` → `/app/uploads` |
| `chat` | `services/chat/Dockerfile`（构建上下文为仓库根，随包本地 agent-core / agent-cooking / agent-talk / agent-novel） | 仅内网 5090 | 无 |
| `web` | `apps/admin-web/Dockerfile`（构建上下文为仓库根） | **对外 `${WEB_PORT:-8000}:80`** | 只读挂载 `infra/nginx/nginx.conf` |

只有 `web` 暴露宿主机端口，其余服务仅在 compose 网络内互通；`api` 与 `chat` 都带健康检查，`web` 延迟到二者 healthy 后再启动。

这套 compose 是**本地一体化栈**（含网关与静态托管）。线上不是这个形态：`api`、`chat`、`redis`、
`admin-web`、`novel-web`、`brand` 各自是一个微信云托管服务，用 `pnpm <app>:deploy` 推镜像，
域名与运行时变量在控制台填，各应用的 `DEPLOY_CLOUDRUN.md` 是那一侧的手册
（`services/api`、`services/chat`、`apps/admin-web`、`apps/novel-web`、`apps/brand` 各有一份）。
两个小程序不在任何镜像里，走微信开发者工具上传。

### 环境变量

compose 自动读取仓库根目录 `.env`（已被 `.gitignore` 排除，不入库）。从模板创建后按需修改：

```bash
cp .env.example .env
```

| 变量 | 必填 | 说明 |
| --- | --- | --- |
| `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` | 是 | 业务库与账号，默认库名 `po` |
| `MYSQL_ROOT_PASSWORD` | 是 | MySQL root 密码 |
| `JWT_SECRET` | 是 | Base64 编码，**解码后至少 32 字节**；生产必须替换占位值 |
| `JWT_EXPIRATION` | 否 | Token 有效期（毫秒），默认 24 小时 |
| `APP_SEED_DEFAULT_ADMIN` | 否 | 默认 `false`；置 `true` 且库中无超管时创建 `superadmin/123456`，登录后应立即改密 |
| `WEB_PORT` | 否 | 网关对外端口，默认 `8000` |
| `PY_SERVER_CORS_ORIGINS` | 否 | 聊天服务 CORS 白名单 |
| `PY_SERVER_API_BASE_URL` / `PY_SERVER_INTERNAL_TOKEN` | 否 | chat 宿主回调 Spring 的地址与内网令牌（默认 `http://localhost:8080/api`） |
| `AGENT_CORE_LLM_PROVIDER` / `AGENT_CORE_LLM_MODEL` / `AGENT_CORE_LLM_API_KEY` | 否 | 聊天与四个 Agent 插槽共用的默认模型（OpenAI 兼容协议）；不配或密钥无效时聊天服务降级为离线模式，接口仍可用 |
| `AGENT_CORE_LLM_ROLES__<ROLE>__*` | 否 | 按角色覆盖模型（插槽决定角色名：`chat` / `cooking` / `talk` / `write` / `judge`，例如给 `talk` 配更快更便宜的小模型）。`.env.example` 里是写法示例而非全量清单，每个角色可覆盖 `PROVIDER` / `MODEL` / `API_KEY` / `BASE_URL` / `TEMPERATURE`，未填的回落默认槽位；跨 provider 时 `API_KEY` **不回落**（缺了直接报错并指明该配哪个变量）。 |
| `AGENT_CORE_EMBEDDING_*` | 否 | 意图路由的 embedding；不配则降级为本地关键词路由，垂直 Agent 仍可被命中 |
| `AGENT_CORE_CHECKPOINTER` / `AGENT_CORE_REDIS_URL` | 否 | 会话持久化后端，默认 `redis`。Redis 必须是 redis-stack（要 JSON+Search 模块），纯 redis 或没装 `agent-core[redis]` 会**静默**降级成 memory；`REDIS_PASSWORD` 由 compose 拼进这个 URL（`.env.example` 未列该键，默认 `123456`，改它要同步 Spring 侧的 Redis 口令） |
| `APP_INTERNAL_TOKEN` | 是（跑 Agent 落库时） | Python 回调 `/talk/internal/**`、`/novel/internal/**` 的内网令牌，compose 把它一分三映射成 `TALK_INTERNAL_TOKEN` / `NOVEL_INTERNAL_TOKEN` / `PY_SERVER_INTERNAL_TOKEN`，两端必须完全一致；Java 侧未配置时对内部端点一律拒绝 |
| `COOKING_API_BASE_URL` / `NOVEL_API_BASE_URL` / `NOVEL_INTERNAL_TOKEN` / `NOVEL_AUTHOR_ID` / `NOVEL_PERSIST_ENABLED` | 否 | 两个垂直 Agent 回写用的地址与身份（`NOVEL_AUTHOR_ID` 是内部建书时落名下的兜底归属） |
| `IFLYTEK_APP_ID` / `IFLYTEK_API_KEY` / `IFLYTEK_API_SECRET` / `IFLYTEK_TTS_VCN` / `IFLYTEK_ASR_*` | 否 | 讯飞 TTS 与实时听写（由 Java 侧直连，小程序与网页不接触这几个值） |
| `COS_SECRET_ID` / `COS_SECRET_KEY` / `COS_REGION` / `COS_BUCKET` / `COS_KEY_PREFIX` / `COS_BASE_URL` | 否 | 腾讯云对象存储：头像、上传、封面、TTS 音频的实际落点，接口返回公网 URL |
| `WEB_PORT` | 否 | 本地网关对外端口，默认 `8000` |

前端应用的地址**不写在根 `.env`**：Umi 与 Taro 只读各自目录下的 env 文件，根 `.env` 只属于 docker compose。
管理端与阅读端是 `apps/<app>/.env`（生产档，入库）+ `.env.local`（本机覆盖，不入库），
小程序是 `apps/<app>/.env.development` / `.env.production`。

生成强 JWT 密钥：

```bash
openssl rand -base64 48          # 或：printf 'your-random-secret-at-least-32-bytes!!' | base64 -w0
```

> 不要提交 `.env` 与 `services/api/api-bootstrap/src/main/resources/application-local.yaml`（含本地数据库、Redis、JWT 凭据，均已被忽略）。容器内不含 `application-local.yaml`，配置全部通过上表环境变量注入（12 因子）。

## 部署启动

### 首次部署 / 一键启动

```bash
cd /d/dev/po                     # PowerShell 用 D:\dev\po
cp .env.example .env             # 首次；随后编辑 MYSQL_* 与 JWT_SECRET
docker compose up -d --build     # 构建镜像并后台启动 5 个服务
docker compose ps                # 等待全部 healthy
```

入口：`http://localhost:${WEB_PORT}`（默认 `http://localhost:8000`）。

冒烟验证：

```bash
curl -fsS http://localhost:8000/api/actuator/health    # Spring Boot: {"status":"UP",...}
curl -fsS http://localhost:8000/api/health             # FastAPI: {"status":"ok"}
curl -X POST 'http://localhost:8000/api/auth/register?username=demo&password=Passw0rd123&email=demo@example.com'
```

数据库表结构由 `services/api/api-bootstrap/src/main/resources/schema.sql` 在 `api` 启动时幂等建表（`CREATE TABLE IF NOT EXISTS`），持久层为 MyBatis-Plus：各业务模块的 `repository` 包存放 `@Mapper` 接口（`BaseMapper<T>`），分页转换用 `shared` 模块的 `MyBatisPages`。默认不创建任何账号，可通过 `APP_SEED_DEFAULT_ADMIN=true` 或在页面上注册。

### 日常运维

```bash
docker compose ps                       # 服务状态
docker compose logs -f api              # 跟踪某个服务日志（api / chat / web / mysql / redis）
docker compose restart api              # 重启单服务
docker compose up -d --build            # 代码变更后重建并滚动更新
docker compose down                     # 停止并删除容器（保留数据卷）
docker compose down -v                  # 连同 mysql_data / uploads_data 一起删除（数据全部清空）
```

数据库与上传文件均在命名卷中，`down` 不丢数据；`nginx.conf` 为只读挂载，改完执行 `docker compose exec web nginx -t && docker compose exec web nginx -s reload` 即时生效。

## 本地开发启动

前置依赖：Node ≥ 22、pnpm 10、JDK 17、Python 3.11，以及本地 MySQL 8.4 与 Redis（本地连接信息写在 `services/api/api-bootstrap/src/main/resources/application-local.yaml`，默认 profile 即 `local`）。

Windows 注意事项：

- 命令给出 **PowerShell** 与 **Git Bash** 两种写法；`export` 只在 Git Bash 有效，PowerShell 要用 `$env:`（cmd 则用 `set JAVA_HOME=...` 并执行 `mvnw.cmd`）。
- `pnpm api:*` 由 `scripts/run-service.mjs` 启动，无需在终端配置 `JAVA_HOME`：先取当前 `JAVA_HOME`，未设置或无效时自动在 `~/.jdks/` 里按 `17` 优先挑选可用 JDK，再传给 `mvnw`。只有绕过脚本直接执行 `./mvnw` 时才需要终端自备 `JAVA_HOME`，否则报 `The JAVA_HOME environment variable is not defined correctly`。
- 本机 JDK 装在 `~/.jdks/`，目录名用 `ls ~/.jdks`（Git Bash）或 `dir "$env:USERPROFILE\.jdks"`（PowerShell）查看。想给直连 `./mvnw` 的终端配 JDK 时：PowerShell 用 `$env:JAVA_HOME = "$env:USERPROFILE\.jdks\ms-17.0.20.1"`、Git Bash 用 `export JAVA_HOME="$HOME/.jdks/ms-17.0.20.1"`；Git Bash 的 POSIX 路径只能配 `./mvnw`（shell 脚本），在 Git Bash 里调 `mvnw.cmd` 会因路径无法解析报错，须用 Windows 风格路径（推荐一次性写入用户级环境变量，无需管理员，**设置后必须重开终端**才生效）：

  ```powershell
  [Environment]::SetEnvironmentVariable("JAVA_HOME", "$env:USERPROFILE\.jdks\ms-17.0.20.1", "User")
  ```
- 前端 dev server 与 docker 网关都用 8000 端口：compose 栈在跑时 `netstat -ano | findstr :8000` 会看到占用（Umi 会自动退到 8001/8002 等端口）。想用 8000 就先 `docker compose stop web`（或 `docker compose down`），或在 `apps/admin-web/.env` 里设 `PORT=8001`。

### 1. Spring Boot API → http://127.0.0.1:8080/api

所有命令均在仓库根目录执行。`services/api` 是 Maven 多模块 reactor，父 POM 没有 main 类；`api:start` 在 `services/api` 目录内执行 `./mvnw -pl api-bootstrap -am spring-boot:run`，会在同一次 reactor 构建中编译 `shared`、`identity`、`recipe` 并只对 `api-bootstrap` 启动应用（父 POM 与其余模块通过 `spring-boot.run.skip` 跳过 boot goal），因此改完全部 Java 模块后直接 `api:start` 即可，无需先 `api:install`。

在仓库根目录执行即可，无需预先配置 JDK 环境变量（启动器会自动定位 JDK 17）：

```bash
pnpm api:start
```

启动后可用 `curl http://127.0.0.1:8080/api/actuator/health` 冒烟验证；MySQL 或 Redis 未就绪时 Redis 组件会报 `DOWN`。`SERVER_PORT=8085 pnpm api:start` 可临时换端口（Spring Boot 会读取该环境变量），适合 8080 已被 IDE 里的实例占用时。

若绕过脚本，在 `services/api` 目录里直接执行 `./mvnw -pl api-bootstrap -am spring-boot:run`（与 `pnpm api:start` 等价），则需要终端自带 `JAVA_HOME`，配置方式见上文 Windows 注意事项。

### 2. FastAPI 聊天服务 → http://127.0.0.1:5090

先在 `services/chat` 创建 `.venv`（`python -m venv .venv`），再从仓库根目录安装本地包并启动：

```bash
pnpm chat:install    # 按依赖序安装 agent-core → agent-cooking → agent-talk → agent-novel → chat（可编辑模式）
pnpm chat:start
```

该命令以 `services/chat/.venv` 的 Python 运行 Uvicorn，并开启热重载。

### 3. 管理端 Umi → http://127.0.0.1:8000（代理 `/api` → 8080、`/ws` → 5090）

```bash
pnpm install
pnpm admin:dev
```

### 4. Expo 做菜 App

先按上文启动 Spring Boot API 与聊天服务（`pnpm chat:start`），然后创建移动端本地配置：

```bash
cp apps/cooking-app/.env.example apps/cooking-app/.env
pnpm mobile:start
```

浏览器版固定走同源 `/api`，由 Expo dev server 代理到 `EXPO_PUBLIC_API_URL` 的主机（默认 8080），不会跨域；iOS 模拟器可保留 `EXPO_PUBLIC_API_URL=http://localhost:8080/api`。Android 模拟器应改为 `http://10.0.2.2:8080/api`，或执行 `adb reverse tcp:8080 tcp:8080` 后继续使用 `localhost`。真机 Expo Go 则改为开发机在同一局域网中可访问的地址，再扫描 Expo 输出的二维码。

「AI 指导」标签页连 `services/chat` 的 `/ws/chat` 流式问答：地址默认按 `EXPO_PUBLIC_API_URL` 的主机换到 5090 端口推导（Metro 只代理 HTTP，不代理 WebSocket 升级），网关 / 隧道场景可用 `EXPO_PUBLIC_CHAT_URL` 显式覆盖；聊天服务连不上时自动回退本地菜谱规则，界面不会报错。

移动端是 pnpm workspace 包，统一从根目录执行命令：

```bash
pnpm mobile:android   # Android 模拟器或已连接设备
pnpm mobile:ios       # iOS 模拟器（仅 macOS）
pnpm mobile:web       # 浏览器
```

本地 debug APK、EAS 内测 APK、正式 AAB 与生产 API 配置见 [移动端 README](apps/cooking-app/README.md)。

只需要 APK 而不启动模拟器时，在 `apps/cooking-app/android` 下执行 `./gradlew.bat assembleDebug`，产物为 `app/build/outputs/apk/debug/app-debug.apk`；本地编译需要 JDK 17 与 Android SDK（含 CMake、NDK），另需一个支持 Windows 长路径的 ninja（`pip install ninja`，≥ 1.11），详见移动端 README。

### 5. 微信小程序（叮叮厨 / 言外）

两端都要先起 Spring Boot（`pnpm api:start`，言外还要 `pnpm chat:start`），再在仓库根：

```bash
pnpm mini:dev        # 叮叮厨：watch 编译到 apps/cooking-mini/dist/
pnpm echo:dev        # 言外：同上，产物在 apps/echo-talk/dist/
```

微信开发者工具导入 **应用目录本身**（不是 `dist/`）。`.env.development` 里三个地址都填开发机局域网 IP
而不是 `127.0.0.1`（真机预览时 127.0.0.1 指向手机自己），并勾「不校验合法域名」。
`pnpm chat:start` 已带 `--host 0.0.0.0`；手动起 uvicorn 不带这个参数，局域网 IP 会被拒。
各自的约定与平台限制见 `apps/cooking-mini/README.md`、`apps/echo-talk/README.md`。

### 6. 言外书斋阅读端 → http://127.0.0.1:8001

```bash
pnpm novel:dev       # 读真库，与管理端 /novel 同源（先 pnpm api:start）
pnpm novel:mock      # 前端独立开发：mock/novel.ts 顶掉 /api/books*，不需要后端
```

`.env` 是生产档、`.env.local` 是本机覆盖（Umi 只有这两档且后者覆盖前者），新克隆必须先
`cp .env.example .env.local`，否则 dev 代理会打到线上域名。细节见 `apps/novel-web/README.md`。

### 7. 个人品牌站 → http://localhost:4321

```bash
pnpm brand:dev
pnpm brand:check     # astro check + eslint + prettier
pnpm brand:assets    # 把插画 SVG 栅格化成 webp（改过 src/assets/illustrations/ 必跑）
```

文案与占位约定见 `apps/brand/README.md`；`src/config.yaml` 里的站点域名在本地仍是占位符，
部署时用 `SITE_URL=... pnpm brand:deploy` 在容器内改写，不改仓库文件。

### 8. 开发者知识库

`apps/power-wiki/` 是 gitignore 的上游副本，只在本地起服务：`pnpm wiki:site`（装依赖 `wiki:site:install`）。
内容发布走 `pnpm wiki:sync`，归属规则见 `scripts/WIKI_SYNC.md`。
**它自带的 `README.md` / `README_ZH.md` 与本地状态有偏差**（`test:env` 不存在、端口实为 80、
`config.json` 已是真配置不要按 README 覆盖），动手前读 `scripts/WIKI_SYNC.md` 的「上游 README 里不要照做的几处」。

### 常用脚本（仓库根执行）

| 命令 | 作用 |
| --- | --- |
| `pnpm types:build` | 构建共享类型包 `@po/types` |
| `pnpm admin:dev` | 构建共享类型后启动管理端开发服务器 |
| `pnpm admin:build` | 构建共享类型与管理端生产产物 |
| `pnpm admin:lint` / `admin:test` / `admin:typecheck` | 管理端 Biome、Vitest 与 TypeScript 检查 |
| `pnpm api:install` | 安装 API 依赖模块到本地 Maven 仓库（一般无需执行，`api:start` 会在 reactor 内构建） |
| `pnpm api:start` | 在 reactor 内构建依赖模块并启动 `api-bootstrap`（等价于 `services/api` 下 `./mvnw -pl api-bootstrap -am spring-boot:run`） |
| `pnpm api:verify` | Java 全模块 `mvn verify` |
| `pnpm chat:install` | 按依赖序安装 agent-core → agent-cooking → agent-talk → agent-novel → chat 到 `services/chat/.venv` |
| `pnpm chat:start` / `chat:test` | 启动 FastAPI 聊天服务或运行 pytest |
| `pnpm agentcore:test` | 运行编排核心库的 pytest（复用 chat 的 `.venv`） |
| `pnpm agentcooking:test` | 运行烹饪垂直 Agent 的 pytest（复用 chat 的 `.venv`） |
| `pnpm agenttalk:test` | 运行言外垂直 Agent 的 pytest（复用 chat 的 `.venv`） |
| `pnpm agentnovel:test` | 运行小说垂直 Agent 的 pytest（复用 chat 的 `.venv`，离线零网络） |
| `pnpm mobile:start` | 启动 Expo 做菜 App 开发服务器 |
| `pnpm mobile:android` / `mobile:ios` / `mobile:web` | 启动 Android、iOS 或 Web 开发目标 |
| `pnpm mobile:apk` | 本地编译 Android debug APK（可加 `x86_64` 等架构参数只编单一 ABI） |
| `pnpm mobile:prebuild:android` | 生成本地 Android 原生项目，供 Gradle 编译 debug APK |
| `pnpm mobile:lint` / `mobile:typecheck` / `mobile:test` | 移动端 Biome、TypeScript 与 jest-expo 检查 |
| `pnpm mobile:eas:preview` | 提交 EAS 内测 APK 构建 |
| `pnpm mobile:eas:production` | 提交 EAS 正式 AAB 构建 |
| `pnpm mini:dev` / `mini:build` | 叮叮厨微信小程序 watch 编译 / 生产构建（Taro weapp） |
| `pnpm mini:dev:h5` / `mini:build:h5` | 同一套代码的 H5 档，只作版式调试 |
| `pnpm echo:dev` / `echo:build` | 言外小程序（各自先 `types:build`） |
| `pnpm novel:dev` / `novel:mock` | 阅读端：读真库 / 用 `mock/novel.ts` 脱开后端 |
| `pnpm novel:build` / `novel:preview` / `novel:lint` / `novel:typecheck` | 阅读端构建、预览与静态检查 |
| `pnpm brand:dev` / `brand:build` / `brand:preview` | 品牌站开发、构建与本地预览（端口 4321） |
| `pnpm brand:check` | `astro check` + `eslint` + `prettier --check`（CI 的 brand job 跑 `astro check` 与 `astro build`） |
| `pnpm brand:assets` | 把 `src/assets/illustrations/` 的 SVG 栅格化成 webp；改过任何插画都要跑并把产物一起提交 |
| `pnpm wiki:site` / `wiki:site:dev` / `wiki:site:install` | 本地起知识库站（nodemon 档、装依赖档） |
| `pnpm wiki:sync` / `wiki:sync:dry` / `wiki:sync:bootstrap` | 把 `.qoder/repowiki` 内容发布进知识库站（镜像用的计划任务 `goodzheng-wiki-sync` 当前是 Disabled，不会自动上站；改归属规则前读 `scripts/WIKI_SYNC.md`） |

### 上线命令（写远端，跑之前确认自己在做什么）

| 应用 | 命令 | 落点 |
| --- | --- | --- |
| Spring Boot | `pnpm api:deploy` | 构建 `services/api` 镜像并推云托管内置仓库 |
| FastAPI 宿主 | `pnpm chat:deploy` | 同上，上下文是仓库根（要随包装四个本地 agent 库） |
| Redis | `pnpm redis:deploy` | redis-stack 镜像 |
| 管理端 | `pnpm admin:deploy` | 静态产物镜像（前端 API 域名是**构建期**常量，换域名要重打） |
| 阅读端 | `pnpm novel:deploy` | 同上；容器反代的后端是运行时变量 `NOVEL_API_UPSTREAM` |
| 品牌站 | `pnpm brand:deploy` | 同上；`SITE_URL=https://真实域名 pnpm brand:deploy` 在容器内改写 `src/config.yaml` |

每条都有 `:deploy:official` 变体（`USE_OFFICIAL_IMAGES=1`，走官方基础镜像名而非国内加速前缀）。
这些是**共享远端写入**，不能从命令行回滚：不要把部署接在验证命令后面，也不要在没读过对应
`DEPLOY_CLOUDRUN.md` 的情况下执行。

## 持续集成

`.github/workflows/ci.yml` 在 push `main` / PR / 手动触发时运行六个 job：

- **frontend**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → 构建 `@po/types` → lint → vitest → 构建产物（覆盖 `apps/admin-web`）
- **mobile**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → 构建 `@po/types` → Expo App 的 Biome、TypeScript 与 jest-expo 检查
- **mini**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → 构建 `@po/types` → `pnpm mini:build`（只编 cooking-mini，主包限额在此把关）
- **brand**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → `astro check` → `astro build`
- **api**：Temurin 17 + Maven 缓存，以 MySQL 8.4 / Redis Stack 服务容器 + 环境变量注入（等价 `application-local.yaml`）→ `mvn verify`
- **chat**：Python 3.11 → 按依赖序安装本地包 `agent-core → agent-cooking → agent-talk → agent-novel → chat` → 依次运行 agent-core、agent-cooking、agent-talk、agent-novel、chat 五套 pytest（四套 Agent 套件全部离线，不需要 Key 与后端），另有两条独立门禁：小说一致性黄金集（`agent-novel/tests/test_golden.py`，PRD §12.1）与长测指标（`test_longrun_metrics.py`）

`@po/types` 的 `exports` 只指向 `dist/`，因此凡是依赖它的 job（frontend / mobile / mini）都必须先跑 `types:build`。

**门禁缺口**（截至本次核对的现状，不是遗漏一次而是覆盖矩阵）：`apps/novel-web`（依赖 `@po/types`）、
`apps/echo-talk` 与 `apps/power-wiki` **没有任何 job**——它们坏了 CI 不会红。Java 侧的 novel/talk 模块由
`api` job 的 `mvn verify` 覆盖，Python 侧四个库由 `chat` job 覆盖。

## 提交规范

Husky + commitlint（`.commitlintrc.cjs` 只 extends `@commitlint/config-conventional`，未自定义规则）。
提交前 lint-staged（`.lintstagedrc`）按目录执行：

| 命中路径 | 执行 |
| --- | --- |
| `apps/admin-web/**/*.{js,jsx,tsx,ts,css,less}` | `biome check --write` |
| `apps/cooking-app/**/*.{js,jsx,tsx,ts,css}` | `biome check --write` |
| `apps/novel-web/**/*.{js,jsx,tsx,ts,css,less}` | `biome check --write` |
| `packages/types/**/*.{js,jsx,tsx,ts}` | `pnpm --dir packages/types run typecheck` |

两个小程序（`apps/cooking-mini`、`apps/echo-talk`）与 `apps/brand`、`services/*` **不在钩子里**——
改了它们要靠各自 README 的命令自查。`packages/types` 那条用了 `bash -c`，Windows 上若命中 WSL 存根
会静默失败，钩子红/不生效时先确认走的是 Git Bash。

标题用中文时不要以大写字母开头的拉丁词起头（`Taro …`、`App …` 会被 `subject-case` 判 fail），
改成汉字开头。不要使用 `--no-verify` 跳过钩子。
