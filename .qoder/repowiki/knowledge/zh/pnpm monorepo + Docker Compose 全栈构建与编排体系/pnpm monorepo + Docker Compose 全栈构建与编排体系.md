---
kind: build_system
name: pnpm monorepo + Docker Compose 全栈构建与编排体系
category: build_system
scope:
    - '**'
source_files:
    - package.json
    - pnpm-workspace.yaml
    - docker-compose.yml
    - .github/workflows/ci.yml
    - scripts/run-service.mjs
    - scripts/deploy-api.sh
    - scripts/deploy-chat.sh
    - scripts/deploy-redis.sh
    - infra/nginx/nginx.conf
    - services/api/Dockerfile
    - services/chat/Dockerfile
    - apps/admin-web/Dockerfile
---

## 1. 整体方案

仓库采用 **pnpm workspace** 聚合前端（Umi Max admin、Expo cooking-app、Taro cooking-mini）、后端（Spring Boot API）与聊天服务（FastAPI），并通过 `docker-compose.yml` 统一编排 MySQL 8.4、Redis Stack、API、Chat、Nginx 网关，实现“本地一键起全栈”。

- Node 工具链：Node ≥22 + pnpm 10.28.1（由根 `package.json` 的 `engines` 与 `packageManager` 字段锁定）。
- Java 后端：Maven Reactor（`services/api/pom.xml`），JDK 17（Temurin），通过 `scripts/run-service.mjs` 自动解析本机 JDK 并调用 `mvnw`。
- Python 聊天/Agent：Python 3.11，使用 `.venv`（位于 `services/chat/.venv`），依赖 `agent-core`、`agent-cooking` 两个本地包以 editable 模式安装。
- 容器化：每个服务独立 `Dockerfile`，镜像基础镜像默认走国内加速前缀 `docker.m.daocloud.io/library/*`，可通过 `USE_OFFICIAL_IMAGES=1` 切换回官方 Docker Hub。
- CI：GitHub Actions（`.github/workflows/ci.yml`），按 job 并行跑 Frontend / Mobile / API / Chat & Agents。
- 部署：Shell 脚本 `scripts/deploy-{api,chat,redis}.sh` 构建镜像并推送到微信云托管 TCR（`ccr.ccs.tencentyun.com`）。

## 2. 关键文件

| 角色 | 路径 |
|---|---|
| 根工作区入口 | `package.json`、`pnpm-workspace.yaml`、`pnpm-lock.yaml` |
| 本地编排 | `docker-compose.yml`、`.env.example` |
| Nginx 网关 | `infra/nginx/nginx.conf` |
| CI 流水线 | `.github/workflows/ci.yml` |
| 服务启动包装器 | `scripts/run-service.mjs`、`scripts/run-sh.mjs`、`scripts/jdk.mjs` |
| 部署脚本 | `scripts/deploy-api.sh`、`scripts/deploy-chat.sh`、`scripts/deploy-redis.sh`、`scripts/run-mobile.mjs` |
| Spring Boot 镜像 | `services/api/Dockerfile`、`services/api/maven-settings.xml` |
| FastAPI 镜像 | `services/chat/Dockerfile` |
| 前端镜像 | `apps/admin-web/Dockerfile` |
| 共享类型包 | `packages/types/package.json`、`packages/types/src/index.ts` |
| Husky 钩子 | `.husky/pre-commit`、`.husky/commit-msg` |

## 3. 架构与约定

### 3.1 pnpm workspace 依赖图
根 `package.json` 暴露统一脚本，所有跨包命令都通过 `pnpm --filter <pkg>` 或 `pnpm --dir <pkg>` 转发：
- `types:build` → `@po/types` 先构建（admin 的 tsc 依赖其产物）。
- `admin:*` → 先 build types，再对 `@po/admin` 执行 lint/test/build。
- `mobile:*` → 直接转发到 `apps/cooking-app`（Expo）。
- `mini:*` → 转发到 `apps/cooking-mini`（Taro）。
- `api:*` / `chat:*` / `agentcore:test` / `agentcooking:test` → 经 `scripts/run-service.mjs` 分发到对应语言工具链。

`pnpm-workspace.yaml` 声明了 workspace 成员；`pnpm-lock.yaml` 在 CI 中以 `--frozen-lockfile` 校验，禁止锁文件漂移。

### 3.2 服务生命周期包装器
`scripts/run-service.mjs` 是 Node 编写的多语言调度器：
- `api install/start/verify` → 设置 `JAVA_HOME`（由 `jdk.mjs` 解析本机 JDK）后执行 `./mvnw`（Windows 下走 `mvnw.cmd`）。
- `chat install/start/test` → 定位 `services/chat/.venv/bin/python`，按依赖序 `pip install -e ../agent-core[dev]` → `../agent-cooking[dev]` → `.[dev]`。
- `agentcore test` / `agentcooking test` → 复用 chat 的 venv 运行 pytest。
- Windows 上通过 shell 模式拼接参数以避免 DEP0190 警告。

### 3.3 Docker 镜像分层策略
- **Spring Boot** (`services/api/Dockerfile`)：两阶段构建。Build 阶段用 Maven 镜像拉取依赖（`dependency:go-offline` 预缓存），Runtime 阶段仅拷贝 JRE + jar，并以非 root `appuser` 运行，暴露 8080。
- **FastAPI** (`services/chat/Dockerfile`)：单阶段，从 `python:3.11-slim` 安装本地 agent-core/agent-cooking 与 fastapi/uvicorn，COPY `services/chat/app` 到 `/app`，并在构建期执行 `import app.main; import langgraph.checkpoint.redis` 做 smoke 测试，失败即阻断镜像产出。
- **Admin Web** (`apps/admin-web/Dockerfile`)：两阶段。Build 阶段 node:22-alpine + corepack 启用 pnpm，只 COPY `pnpm-workspace.yaml`、`pnpm-lock.yaml`、`package.json`、`.npmrc`、`packages/types/package.json`、`apps/admin-web/package.json` 以利用层缓存；Runtime 阶段 nginx:1.27-alpine 托管 `dist`。

所有 Dockerfile 的基础镜像默认带 `docker.m.daocloud.io/library/` 前缀，避免本地直连 Docker Hub 失败；云端构建通过 `--build-arg BUILD_IMAGE=... RUNTIME_IMAGE=...` 覆盖回官方镜像。

### 3.4 docker-compose 编排
`docker-compose.yml` 定义 5 个服务，严格的健康检查与依赖顺序：
```
mysql(health) ← redis(health) ← api(health) ← chat(health) ← web(80)
```
- MySQL 8.4，健康检查 `mysqladmin ping`。
- Redis 必须用 `redis-stack-server`（注释说明普通 redis 缺少 JSON/FT 模块会导致 checkpointer 静默降级为 memory）。
- API 注入 JDBC URL、JWT_SECRET、COS/TTS 密钥等环境变量，依赖 mysql/redis healthy。
- Chat 注入 LLM provider/model/api_key、checkpointer=redis 的 Redis URL，依赖 redis 与 api healthy。
- Web 挂载 `infra/nginx/nginx.conf` 作为只读配置，端口映射 `${WEB_PORT:-8000}:80`。

### 3.5 Nginx 网关路由
`infra/nginx/nginx.conf` 将单一入口按前缀分流：
- `/` → Umi 静态 SPA（history fallback 到 index.html）。
- `/ws/chat` → FastAPI WebSocket（长连接超时 3600s）。
- `/api/health`、`/api/items*` → FastAPI。
- `/api/**` 其余 → Spring Boot（`server.servlet.context-path=/api` 已含前缀）。
- 静态资源（js/css/图片/woff2）开启 30d immutable 缓存。

### 3.6 CI 流水线
`.github/workflows/ci.yml` 四个并行 job：
- **Frontend**：Node 22 + pnpm 10.28.1，`pnpm install --frozen-lockfile` → `pnpm types:build` → `pnpm admin:lint` → `pnpm admin:test` → `pnpm admin:build`。
- **Mobile**：同上环境，`pnpm mobile:lint` → `pnpm mobile:typecheck` → `pnpm --filter @po/cooking exec jest --runInBand`。
- **API**：Java 17 (Temurin)，启动 MySQL 8.4 与 Redis 7-alpine service，通过环境变量注入 `application-local.yaml` 等价配置，执行 `mvn verify`。
- **Chat & Agents**：Python 3.11，按依赖序 `pip install -e '../agent-core[dev]'` → `../agent-cooking[dev]'` → `'.[dev]'`，分别对三个包运行 pytest。

CI 中 Redis 使用普通 `redis:7-alpine`（无 Redis Stack），因为 CI 不依赖 LangGraph checkpoint 功能；而本地 compose 强制使用 `redis-stack-server`。

### 3.7 版本与发布
- 镜像 tag 默认 `prod`，可通过 `TAG=vX.Y.Z bash scripts/deploy-api.sh` 覆盖。
- 推送目标固定为 `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po:<TAG>`。
- 推送后自证 `docker manifest inspect`，失败则提示重新 `docker login`。
- 前端构建产物由 Nginx 托管，无独立 npm publish 流程。

## 4. 约定与约束

- **Node 版本锁定**：根 `package.json` 的 `engines.node >=22.0.0` 与 `packageManager pnpm@10.28.1` 强制运行时版本，CI 也显式 setup-node 22 + pnpm/action-setup 10.28.1。
- **依赖锁文件不可变**：CI 与 Dockerfile 均使用 `pnpm install --frozen-lockfile`，任何未提交变更的 lock 都会导致构建失败。
- **Husky 钩子在 CI 被跳过**：所有 CI 步骤设置 `HUSKY=0`，避免安装 hooks。
- **本地 Python venv 位置固定**：`scripts/run-service.mjs` 硬编码 `services/chat/.venv`，不存在时抛出明确错误并要求先创建。
- **Agent 包安装顺序即依赖顺序**：`run-service.mjs` 与 CI 都要求先 `agent-core` 再 `agent-cooking` 再 `chat`，顺序写死在代码中。
- **Redis 必须是 Redis Stack**：compose 注释明确说明普通 redis 会触发 unknown command，chat 静默降级成 memory checkpointer；因此本地开发不允许替换为普通 redis 镜像。
- **基础镜像国内加速**：所有 Dockerfile 与 deploy 脚本默认使用 `docker.m.daocloud.io/library/*`，仅在 `USE_OFFICIAL_IMAGES=1` 时切回官方源。
- **Spring Boot 健康端点**：compose 与 CI 都通过 `curl http://localhost:8080/api/actuator/health` 判定就绪，要求 `server.servlet.context-path=/api`。
- **Chat 健康端点**：compose 通过 `python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5090/api/health')"` 探测。
- **上传目录持久化**：compose 将 `uploads_data:/app/uploads` 挂载给 API 服务，保证重启后上传文件不丢失。
- **Nginx 配置只读挂载**：compose 中 `./infra/nginx/nginx.conf:/etc/nginx/nginx.conf:ro`，防止容器内修改生效。
- **Maven 依赖离线缓存**：Dockerfile 先 `COPY pom.xml` 再 `RUN mvn dependency:go-offline`，再 COPY src，最大化层缓存命中率。
- **Chat 镜像构建期冒烟**：`RUN python -c "import app.main; import langgraph.checkpoint.redis; ..."` 确保产出的镜像可导入，避免 wheel 缺失导致的 ModuleNotFoundError。
- **WebSocket 长连接超时**：Nginx 对 `/ws/chat` 设置 `proxy_read_timeout 3600s` 与 `proxy_send_timeout 3600s`，配合 `Connection` 头映射支持流式回复。
- **Git 提交规范**：通过 `@commitlint/config-conventional` + Husky `commit-msg` 钩子强制执行 conventional commits 格式（见 `.commitlintrc.cjs`）。