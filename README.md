# po

菜谱 / 用户 / 小说业务的全栈 Monorepo：pnpm workspace 管理前端与共享类型，Maven reactor 管理 Spring Boot 后端，Python FastAPI 提供流式聊天，Docker Compose + Nginx 网关统一部署。

| 层 | 技术栈 | 位置 |
| --- | --- | --- |
| 管理前端 | Umi Max 4 + React 19 + Ant Design 6 + React Query 5 + Vitest 4 + Biome | `apps/admin-web` |
| 移动端 | Expo SDK 57 + React Native + expo-router + NativeWind + React Query + Jest | `apps/cooking-app` |
| 共享类型 | TypeScript 包 `@po/types` | `packages/types` |
| 业务 API | Java 17 + Spring Boot 4 + MyBatis-Plus + MySQL + Redis + JWT | `services/api` |
| 聊天服务 | Python 3.11 + FastAPI + WebSocket + LangGraph | `services/chat` |
| Agent 编排 | 纯库 `po-agent-core`（supervisor / 事件流 / semantic-router 意图路由 / 记忆）+ 垂直 Agent 插槽 `po-agent-novel` | `services/agent-core`、`services/agent-novel` |
| 网关与编排 | Nginx 1.27 + Docker Compose | `infra/nginx`、`docker-compose.yml` |

## 架构总览

```
apps/admin-web        管理前端（Docker 多阶段构建 → Nginx 托管静态产物）
apps/cooking-app      Expo 移动端（expo-router + NativeWind，直连 API）
packages/types        前后端共享 TS 类型（@po/types）
services/api          Maven 多模块单体
  ├─ shared           公共 DTO / Result / 异常
  ├─ identity         用户、认证、JWT
  ├─ recipe           菜谱与分类
  ├─ novel            小说
  └─ api-bootstrap    启动模块（application.yaml，context-path=/api）
services/agent-core    编排核心纯库（supervisor / 事件流翻译 / 意图路由 / 会话记忆，
                      垂直 Agent 经插槽接入，不含业务领域知识）
services/agent-novel   小说创作垂直 Agent（构思→大纲→逐章生成+反思循环→归档确认，
                      数据层走 NovelStore Protocol，当前为 mock 实现）
services/chat          FastAPI 宿主（/api/health、/api/items、/ws/chat 流式编排，
                      装配 agent-core + agent-novel，LLM 缺配置时离线降级）
infra/nginx/nginx.conf 网关分流规则
```

请求统一从网关进入，按前缀分流：

| 路径 | 上游 | 说明 |
| --- | --- | --- |
| `/ws/chat` | chat:5090 | WebSocket 流式聊天 |
| `/api/health`、`/api/items/**` | chat:5090 | FastAPI 接口 |
| `/api/**`（其余） | api:8080 | Spring Boot（含 auth/users/recipes/books/actuator，前缀由 `server.servlet.context-path=/api` 消费） |
| `/` | Nginx 静态 | Umi 产物，history 路由回退 `index.html`，带 hash 资源长缓存 30d |

## 生产环境

### 服务拓扑（docker-compose）

| 服务 | 镜像 / 构建 | 端口 | 持久化 |
| --- | --- | --- | --- |
| `mysql` | `mysql:8.4` | 仅内网 3306 | 命名卷 `mysql_data` |
| `redis` | `redis:7-alpine` | 仅内网 6379 | 无（缓存用途） |
| `api` | `services/api/Dockerfile` | 仅内网 8080 | 命名卷 `uploads_data` → `/app/uploads` |
| `chat` | `services/chat/Dockerfile` | 仅内网 5090 | 无 |
| `web` | `apps/admin-web/Dockerfile`（构建上下文为仓库根） | **对外 `${WEB_PORT:-8000}:80`** | 只读挂载 `infra/nginx/nginx.conf` |

只有 `web` 暴露宿主机端口，其余服务仅在 compose 网络内互通；`api` 与 `chat` 都带健康检查，`web` 延迟到二者 healthy 后再启动。

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
| `UMI_APP_API_BASE_URL` | 否 | 仅本地开发使用：前端 dev server 的 `/api` 代理目标 |

生成强 JWT 密钥：

```bash
openssl rand -base64 48          # 或：printf 'your-random-secret-at-least-32-bytes!!' | base64 -w0
```

> 不要提交 `.env` 与 `services/api/api-bootstrap/src/main/resources/application-local.yaml`（含本地数据库、Redis、JWT 凭据，均已被忽略）。容器内不含 `application-local.yaml`，配置全部通过上表环境变量注入（12 因子）。

## 部署启动

### 首次部署 / 一键启动

```bash
cd /d/pro/po                     # PowerShell 用 D:\pro\po
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

所有命令均在仓库根目录执行。`services/api` 是 Maven 多模块 reactor，父 POM 没有 main 类；`api:start` 在 `services/api` 目录内执行 `./mvnw -pl api-bootstrap -am spring-boot:run`，会在同一次 reactor 构建中编译 `shared`、`identity`、`recipe`、`novel` 并只对 `api-bootstrap` 启动应用（父 POM 与其余模块通过 `spring-boot.run.skip` 跳过 boot goal），因此改完全部 Java 模块后直接 `api:start` 即可，无需先 `api:install`。

在仓库根目录执行即可，无需预先配置 JDK 环境变量（启动器会自动定位 JDK 17）：

```bash
pnpm api:start
```

启动后可用 `curl http://127.0.0.1:8080/api/actuator/health` 冒烟验证；MySQL 或 Redis 未就绪时 Redis 组件会报 `DOWN`。`SERVER_PORT=8085 pnpm api:start` 可临时换端口（Spring Boot 会读取该环境变量），适合 8080 已被 IDE 里的实例占用时。

若绕过脚本，在 `services/api` 目录里直接执行 `./mvnw -pl api-bootstrap -am spring-boot:run`（与 `pnpm api:start` 等价），则需要终端自带 `JAVA_HOME`，配置方式见上文 Windows 注意事项。

### 2. FastAPI 聊天服务 → http://127.0.0.1:5090

先在 `services/chat` 创建 `.venv`（`python -m venv .venv`），再从仓库根目录安装本地包并启动：

```bash
pnpm chat:install    # 按依赖序安装 agent-core → agent-novel → chat（可编辑模式）
pnpm chat:start
```

该命令以 `services/chat/.venv` 的 Python 运行 Uvicorn，并开启热重载。

### 3. 管理端 Umi → http://127.0.0.1:8000（代理 `/api` → 8080、`/ws` → 5090）

```bash
pnpm install
pnpm admin:dev
```

### 4. Expo 做菜 App

先按上文启动 Spring Boot API，然后创建移动端本地配置：

```bash
cp apps/cooking-app/.env.example apps/cooking-app/.env
pnpm mobile:start
```

浏览器版固定走同源 `/api`，由 Expo dev server 代理到 `EXPO_PUBLIC_API_URL` 的主机（默认 8080），不会跨域；iOS 模拟器可保留 `EXPO_PUBLIC_API_URL=http://localhost:8080/api`。Android 模拟器应改为 `http://10.0.2.2:8080/api`，或执行 `adb reverse tcp:8080 tcp:8080` 后继续使用 `localhost`。真机 Expo Go 则改为开发机在同一局域网中可访问的地址，再扫描 Expo 输出的二维码。

移动端是 pnpm workspace 包，统一从根目录执行命令：

```bash
pnpm mobile:android   # Android 模拟器或已连接设备
pnpm mobile:ios       # iOS 模拟器（仅 macOS）
pnpm mobile:web       # 浏览器
```

本地 debug APK、EAS 内测 APK、正式 AAB 与生产 API 配置见 [移动端 README](apps/cooking-app/README.md)。

只需要 APK 而不启动模拟器时，在 `apps/cooking-app/android` 下执行 `./gradlew.bat assembleDebug`，产物为 `app/build/outputs/apk/debug/app-debug.apk`；本地编译需要 JDK 17 与 Android SDK（含 CMake、NDK），另需一个支持 Windows 长路径的 ninja（`pip install ninja`，≥ 1.11），详见移动端 README。

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
| `pnpm chat:install` | 按依赖序安装 agent-core → agent-novel → chat 到 `services/chat/.venv` |
| `pnpm chat:start` / `chat:test` | 启动 FastAPI 聊天服务或运行 pytest |
| `pnpm agentcore:test` / `agentnovel:test` | 运行编排核心库 / 小说垂直 Agent 的 pytest（复用 chat 的 `.venv`） |
| `pnpm mobile:start` | 启动 Expo 做菜 App 开发服务器 |
| `pnpm mobile:android` / `mobile:ios` / `mobile:web` | 启动 Android、iOS 或 Web 开发目标 |
| `pnpm mobile:apk` | 本地编译 Android debug APK（可加 `x86_64` 等架构参数只编单一 ABI） |
| `pnpm mobile:prebuild:android` | 生成本地 Android 原生项目，供 Gradle 编译 debug APK |
| `pnpm mobile:lint` / `mobile:typecheck` / `mobile:test` | 移动端 Biome、TypeScript 与 jest-expo 检查 |
| `pnpm mobile:eas:preview` | 提交 EAS 内测 APK 构建 |
| `pnpm mobile:eas:production` | 提交 EAS 正式 AAB 构建 |

## 持续集成

`.github/workflows/ci.yml` 在 push `main` / PR / 手动触发时运行四个 job：

- **frontend**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → 构建 `@po/types` → lint → vitest → 构建产物
- **mobile**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → Expo App 的 Biome、TypeScript 与 jest-expo 检查
- **api**：Temurin 17 + Maven 缓存，以 MySQL 8.4 / Redis 7 服务容器 + 环境变量注入（等价 `application-local.yaml`）→ `mvn verify`
- **chat**：Python 3.11 → 按依赖序安装本地包 `agent-core → agent-novel → chat` → 依次运行 agent-core、agent-novel、chat 三套 pytest

## 提交规范

Husky + commitlint（conventional commits），提交前 lint-staged 对 `apps/admin-web` 下改动文件执行 `biome check --write`；不要使用 `--no-verify` 跳过钩子。
