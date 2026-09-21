# po

菜谱 / 用户 / 小说业务的全栈 Monorepo：pnpm workspace 管理前端与共享类型，Maven reactor 管理 Spring Boot 后端，Python FastAPI 提供流式聊天，Docker Compose + Nginx 网关统一部署。

| 层 | 技术栈 | 位置 |
| --- | --- | --- |
| 管理前端 | Umi Max 4 + React 19 + Ant Design 6 + React Query 5 + Vitest 4 + Biome | `apps/admin-web` |
| 共享类型 | TypeScript 包 `@po/types` | `packages/types` |
| 业务 API | Java 17 + Spring Boot 4 + MyBatis-Plus / JPA + MySQL + Redis + JWT | `services/api` |
| 聊天服务 | Python 3.11 + FastAPI + WebSocket + LangGraph | `services/chat` |
| 网关与编排 | Nginx 1.27 + Docker Compose | `infra/nginx`、`docker-compose.yml` |

## 架构总览

```
apps/admin-web        前端（Docker 多阶段构建 → Nginx 托管静态产物）
packages/types        前后端共享 TS 类型（@po/types）
services/api          Maven 多模块单体
  ├─ shared           公共 DTO / Result / 异常
  ├─ identity         用户、认证、JWT
  ├─ recipe           菜谱与分类
  ├─ novel            小说
  └─ api-bootstrap    启动模块（application.yaml，context-path=/api）
services/chat         FastAPI（/api/health、/api/items、/ws/chat）
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

数据库表结构由 JPA `ddl-auto: update` 在 `api` 首次启动时自动建表；默认不创建任何账号，可通过 `APP_SEED_DEFAULT_ADMIN=true` 或在页面上注册。

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

```bash
# 1. Spring Boot API → http://127.0.0.1:8080/api
export JAVA_HOME="$HOME/.jdks/ms-17.0.20.1"
cd services/api && ./mvnw -pl api-bootstrap -am spring-boot:run

# 2. FastAPI 聊天服务 → http://127.0.0.1:5090（工作目录须在 services/chat）
cd services/chat && .venv/Scripts/python.exe -m uvicorn app.main:app --port 5090 --reload

# 3. 前端 Umi dev → http://127.0.0.1:8000（代理 /api → 8080、/ws → 5090）
cd <仓库根> && pnpm install && pnpm dev
```

### 常用脚本（仓库根执行）

| 命令 | 作用 |
| --- | --- |
| `pnpm dev` | 构建 `@po/types` 后启动前端 dev server |
| `pnpm build` | 构建共享类型与前端生产产物 |
| `pnpm test` | 前端 Vitest 测试 |
| `pnpm lint` | Biome + tsc 检查 |
| `pnpm typecheck` | 类型包构建 + 前端构建 + tsc |
| `pnpm api:verify` | Java 全模块 `mvn verify` |
| `pnpm chat:test` | Python `pytest` |

## 持续集成

`.github/workflows/ci.yml` 在 push `main` / PR / 手动触发时运行三个 job：

- **frontend**：pnpm 10.28.1 + Node 22 → 冻结锁文件安装 → 构建 `@po/types` → lint → vitest → 构建产物
- **api**：Temurin 17 + Maven 缓存，以 MySQL 8.4 / Redis 7 服务容器 + 环境变量注入（等价 `application-local.yaml`）→ `mvn verify`
- **chat**：Python 3.11 + `pip install -e '.[dev]'` → `pytest`

## 提交规范

Husky + commitlint（conventional commits），提交前 lint-staged 对 `apps/admin-web` 下改动文件执行 `biome check --write`；不要使用 `--no-verify` 跳过钩子。
