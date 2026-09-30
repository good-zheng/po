# chat / Redis 云托管部署

`services/chat`（FastAPI + LangGraph，端口 5090）与 Redis（会话 checkpointer）部署到微信云托管的流程。
后端主体部署见 `../api/DEPLOY_CLOUDRUN.md`，本文只覆盖 chat 与 Redis，以及两者的内网互访。

## 0. 密钥从哪来

生产环境变量集中在 **`services/chat/deploy-prod.json`**。该文件已被 `.gitignore` 与根 `.dockerignore` 排除——
**不入库、不进镜像**（chat 的构建上下文是仓库根，所以排除规则写在根清单里，不是 chat 目录下），
只作为往云托管控制台填环境变量的对照表。真实密钥不写进本文档。

> `deploy-prod.json` 里 `<>` 包裹的几项是占位，创建完 Redis / chat 服务后回填控制台给出的内网域名。
> 上线后请逐项轮换已经明文出现过的密钥（LLM Key、数据库、COS、讯飞）。

## 1. 一键脚本

前置：Docker Desktop 在运行；登录镜像仓库（密码是 TCR「访问凭证」固定密码，非登录密码）。

```bash
docker login ccr.ccs.tencentyun.com --username=100053273154

pnpm redis:deploy        # 拉 Redis Stack 镜像（国内加速）→ 转推到云托管内置镜像仓库
pnpm chat:deploy         # 构建 chat 镜像 + 推送

pnpm redis:deploy:official   # 有代理时改回官方 Docker Hub 基础镜像
pnpm chat:deploy:official
```

换 tag / 换镜像仓库名需要在 bash 里覆盖环境变量（cmd、PowerShell 不认这种写法）：

```bash
TAG=chat-v2 bash scripts/deploy-chat.sh
```

产物镜像地址（**云托管一服务一独立仓库，仓库名 = 环境ID_服务名，必须以控制台给出的为准**）：

| 服务 | 镜像地址 |
| --- | --- |
| api | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po:prod` |
| redis | `…/tcb-100053273154-byrm/ca-eyxzseoz_redis:prod` |
| chat | `…/tcb-100053273154-byrm/ca-eyxzseoz_po-chat:prod` |

> **仓库名以控制台为准，别按命名规律推。** 我一开始照着 api 的 `ca-eyxzseoz_po` 推了一条
> `ca-eyxzseoz_po-redis` —— `docker push` 真的会自动建仓库、也照样打印 digest，但控制台给 redis 服务
> provision 的是 `ca-eyxzseoz_redis`，于是服务一直 `Failed to pull image`。
> （chat 那条 `ca-eyxzseoz_po-chat` 恰好和服务名撞对了，纯属运气。）
> 先建服务、在「服务设置 → 部署设置」里读到控制台显示的仓库名，再 `REPO=<仓库名> bash scripts/deploy-xxx.sh` 推。

Docker Hub 上的公共镜像无法被云托管直接拉取，所以 Redis 需要「本地拉取 → 转推」这一步，这是它和 api/chat 唯一的流程差异。

### 手动等价命令

```bash
# chat：上下文必须是仓库根（agent-core / agent-cooking 是本地包，不在 PyPI）
docker build --platform=linux/amd64 \
  --build-arg RUNTIME_IMAGE=docker.m.daocloud.io/library/python:3.11-slim \
  -f services/chat/Dockerfile \
  -t ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po-chat:prod .
docker push ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po-chat:prod

# redis（必须是 Redis Stack，见第 3 节）
# 注意：不要用 pull → tag → push 的朴素转推，见下一节的多架构坑
mkdir -p /tmp/relay-empty          # 空目录当上下文，别用 /tmp 本身（会把整个 /tmp 打进构建上下文）
printf 'ARG BASE\nFROM ${BASE}\n' > /tmp/relay.Dockerfile
docker build --platform=linux/amd64 --build-arg BASE=docker.m.daocloud.io/redis/redis-stack-server:latest \
  -f /tmp/relay.Dockerfile -t ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_redis:prod /tmp/relay-empty
docker push ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_redis:prod

# 推完务必自证 tag 真的落库（push 返回 0 不代表成功）
docker manifest inspect ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_redis:prod >/dev/null && echo ok
```

### 多架构镜像的静默失败坑（redis 第一次推不上去的原因）

`redis-stack-server:latest` 是多架构 manifest list（含 arm64）。本机只拉到 amd64 那一份内容，
`docker tag` + `docker push` 推出去的是**引用了缺失平台的残缺 index**：
docker 只打印一行 `Not all multiplatform-content is present and only the available single-platform image was pushed` 的 warning 就返回 0，
但 registry 根本没接受这个 tag —— 事后 `docker manifest inspect` 报 `no such manifest`，云托管表现为拉不到镜像、控制台也看不到。

判别方法：看 push 最后一行的 `size:`。残缺 index 是 `size: 3034`（还带着缺失平台的引用），
单架构薄封装重导出后是 `size: 856`（和 api 那条正常镜像同一形态，`index → amd64 + attestation`）。

`deploy-redis.sh` 已经改成「空壳 Dockerfile `FROM` 一次单架构 build」的转推方式，并在 push 后自动 `manifest inspect` 自证，解析不到就非零退出。

### 推之前先在本地把容器跑起来

只看构建成功不够（曾经构建成功、镜像却起不来）。推之前在本地起一次并打健康检查：

```bash
# 端口用 5091，别用 5090：那会和你本地 pnpm chat:start 抢监听，
# 让小程序/Expo 连到这个没配 LLM key 的自测容器，看到假的「离线模式」
docker run -d -p 5091:5090 --name po-chat-boottest \
  ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_po-chat:prod
curl -s http://127.0.0.1:5091/api/health          # 期望 {"status":"ok","agent_core_version":"0.1.0"}
docker logs po-chat-boottest | tail -8            # 无容器外的环境变量时会有几条降级 WARNING，属正常
docker rm -f po-chat-boottest                     # 务必删掉，别留后台容器占端口
```

## 2. Dockerfile 里的三处网络适配

`services/chat/Dockerfile` 与 api 那份同样依赖国内加速，改动任何一条都会让构建在本机直接失败：

1. **基础镜像走 build-arg，默认 daocloud 加速**：`ARG RUNTIME_IMAGE=docker.m.daocloud.io/library/python:3.11-slim`；
   云端构建用 `--build-arg RUNTIME_IMAGE=python:3.11-slim` 覆盖回官方。
2. **绝对不要加 `# syntax=docker/dockerfile:1`**：这行会让 BuildKit 先去 Docker Hub 拉 `docker/dockerfile:1` 前端镜像，
   在拉任何业务层之前就失败。`ARG`-before-`FROM` 由内嵌解析器支持，不需要它。
3. **pip 固定清华源**：`ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`，默认 PyPI 在本机网络不可达。

另有一条与网络无关但同样致命的约束：

- **agent-core 必须带 `[redis]` extra 安装**（`pip install '/packages/agent-core[redis]' …`）。
  `langgraph-checkpoint-redis` 是 `po-agent-core` 的可选依赖，漏装时 `build_orchestrator` 会捕获导入失败、
  把 checkpointer 静默降级为 `memory`——服务照样启动、健康检查照样绿，但会话记忆只存在进程内，
  多副本互相看不见、重启即丢，Redis 部署等于白做。路径里的 `[redis]` 要加引号，避免被 shell 当通配。

## 2b. 宿主 `app/` 为什么不走 pip 打包

2026-09-28 第一次构建时 `pip install /packages/chat` 产出的 wheel 只有 1111 字节——dist-info 齐全、
一个 `.py` 都没打进（`site-packages` 里没有 `app`），镜像照样能推成功，但容器一启动
`uvicorn app.main:app` 就 `ModuleNotFoundError`，白烧一个云托管版本。

现在 Dockerfile 改成：`agent-core` / `agent-cooking` 走 pip 安装（含宿主自身的 fastapi/uvicorn/pydantic-settings 依赖），
宿主源码 `COPY services/chat/app /app/app` 直接落在 `WORKDIR /app`，按 CWD 导入——和本地 `pnpm chat:start` 的运行方式一致；
并加了一条构建期断言：

```dockerfile
RUN python -c "import app.main; import langgraph.checkpoint.redis; print('chat image smoke ok')"
```

导入不了就 `docker build` 直接失败，这类打包问题从此拦在推镜像之前。

## 3. 先建 Redis 服务

云托管里 Redis 是一个普通服务，只是不对公网暴露。

**镜像必须是 Redis Stack（`redis/redis-stack-server`），不能是 `redis:7-alpine`。**
`langgraph-checkpoint-redis` 用 `JSON.SET`/`JSON.GET` 写 checkpoint、用 redisvl 的 `SearchIndex` 建 `FT.SEARCH` 索引，
这些命令来自 RedisJSON 与 RediSearch 模块；普通 Redis 上没有，`CheckpointerManager.get_saver()` 里的
`await saver.setup()` 会直接报 unknown command，然后 `build_orchestrator` 捕获异常降级成 memory——
服务照样起、健康检查照样绿，但会话记忆只在本进程，等于 Redis 白部署。
`AsyncShallowRedisSaver` 同样依赖这两个模块，换 saver 也绕不开。

| 配置项 | 值 |
| --- | --- |
| 镜像 | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_redis:prod` |
| 服务端口 | `6379`（内网调用只放通部署时填写的这个端口，其余端口不可用） |
| 启动命令 | 留空，用镜像默认（`redis-stack-server` 自带 RedisJSON/RediSearch 模块） |
| 环境变量 | `REDIS_ARGS=--requirepass <REDIS_PASSWORD> --appendonly yes`（官方文档指定用 `REDIS_ARGS` 传附加参数，别去覆盖 entrypoint） |
| 公网访问 | 关闭，仅供环境内 chat/api 调用 |
| 最小副本数 | `1`（Redis 有状态，多副本会各自一份数据，checkpointer 不能这么分） |
| 规格 | 请求内存 **512MB 实测够用**（本机 `--memory=512m` 硬限下加载完 RedisJSON/RediSearch/RedisGears 仍 `PONG`）。控制台没有 384MB 档，256MB 会被拒 |
| 健康检查 | **必须把 HTTP 路径检查关掉 / 改成 TCP 探测 6379。** 这个镜像 `Config.Healthcheck` 是 `null`（不自带探活），而云托管默认拿 HTTP `GET /` 去打卡 6379，Redis 只会讲 RESP，永远探不通，报成 `Failed to schedule … container "<image>" probe terminated with exit code 0`。别把它当内存问题去加规格 |

`REDIS_ARGS` 里的密码必须与 chat 的 `AGENT_CORE_REDIS_URL`、api 的 `SPRING_DATA_REDIS_PASSWORD` 完全一致；
`--appendonly yes` 打开 AOF，但 AOF 写在容器 `/data` 里，版本重建仍会丢——持久性要求高请改用腾讯云 Redis 实例 + 私有网络，
注意腾讯云社区版 Redis 同样不带 JSON/Search 模块，换过去前要先确认实例支持这两个模块。

建完服务后，在 **服务列表 → 该服务 → 服务设置** 里确认「内网调用」已开启，并记下控制台给出的**内网域名**，
下一步要填进环境变量。

## 4. 再建 chat 服务

| 配置项 | 值 |
| --- | --- |
| 镜像 | `…/ca-eyxzseoz_po-chat:prod` |
| 服务端口 | `5090` |
| 健康检查路径 | `/api/health`（进程活着即返回 ok，不依赖 LLM/Redis 是否就绪） |
| 首次探测延迟 | ≥ 30s（LangGraph + semantic-router 导入较慢，别学 api 那样卡在探针上） |
| 最小副本数 | ≥ 1（WS 长连接会被缩容打断） |
| 公网出站 | 开启（要访问 DeepSeek / DashScope） |
| 环境变量 | 照 `deploy-prod.json` 逐条填 |

两个必须由控制台决定的变量：

- `AGENT_CORE_REDIS_URL=redis://:<REDIS_PASSWORD>@ca-eyxzseoz.redis.pm1sjzj4.g66pwcq9.com:6379/0`
- `COOKING_API_BASE_URL=http://ca-eyxzseoz-po.pm1sjzj4.g66pwcq9.com:8080/api` —— 烹饪插槽要通过内网调 api 查菜谱；
  沿用默认 `localhost` 会连不上，且这是「菜谱查得到却总是兜底回答」的常见原因。端口必须显式写 `:8080`。

**内网调用地址的真实形态是 `ca-eyxzseoz.<服务名>.pm1sjzj4.g66pwcq9.com`（点号分隔，不是连字符，也不是 `internal.run.tcloudbase.com`）**：

| 被调方 | 内网地址 | 端口 |
| --- | --- | --- |
| redis | `ca-eyxzseoz.redis.pm1sjzj4.g66pwcq9.com` | 6379 |
| api | `ca-eyxzseoz.po.pm1sjzj4.g66pwcq9.com` | 8080 |
| chat | `ca-eyxzseoz.chat.pm1sjzj4.g66pwcq9.com`（目前无人内网调它，小程序走免域名 wss） | 5090 |

中间那段是**服务名**，所以 `ca-eyxzseoz-redis-2265322945.internal.run.tcloudbase.com` 那种形式不要用在这里。
端口必须显式写（`:8080` / `:6379`），内网调用只放通服务部署时填的那个端口。
这些地址只在环境内解析，本地 curl 一定不通；值一律从 **服务列表 → 该服务 → 服务设置 → 内网调用** 逐字复制。

填错的表现很隐蔽：chat 会照常启动、`/api/health` 照常返回 ok，只在日志里留一行
`checkpointer redis 初始化失败，降级为 memory`。所以部署完第一件事是看 `po_agent_core.memory.checkpointer`
那行是 `checkpointer 就绪：redis` 还是 `：memory`，别看 `Orchestrator 就绪：checkpointer=redis`（那打印的是配置值，降级后也不变）。

WS 路径是 `/ws/chat`，**不带** `/api` 前缀（与 `app/main.py` 的挂载约定一致，改动即破坏前端契约）。

## 5. 小程序与 api 侧的连带改动

1. 小程序 `apps/cooking-mini/.env.production` 填 chat 的免域名：
   ```
   TARO_APP_CHAT_WS_URL=wss://<chat 免域名>/ws/chat
   ```
   然后 `pnpm mini:build` 重新出包。
2. 小程序后台「开发设置 → 服务器域名」把该 `wss://…run.tcloudbase.com` 加进 **socket 合法域名**
   （云托管免域名的 HTTP 校验不覆盖 WebSocket）。
3. api 服务补 `SPRING_DATA_REDIS_HOST/PORT/PASSWORD`（见 `../api/application-prod.json`）。
   api 的 classpath 上有 `spring-boot-starter-data-redis`，不配地址时 actuator 的 redis 探针会去连
   `localhost:6379` 并把 `/api/actuator/health` 整体判为 DOWN（HTTP 503），云托管健康检查用的正是这个路径。
   接上 Redis 即恢复正常；若确实不想让 api 依赖 Redis，用 `MANAGEMENT_HEALTH_REDIS_ENABLED=false` 关掉该探针。

## 6. 常见坑

- **chat 起来了但没有记忆**：日志里出现 `checkpointer redis 初始化失败，降级为 memory` →
  Redis 地址/密码不对，或镜像缺模块（见第 3 节）。
  **看日志别看错行**：`app.agent` 那句 `Orchestrator 就绪：checkpointer=redis` 打的是**配置值**，
  降级之后它照样印 `redis`；真正表示结果的是 `po_agent_core.memory.checkpointer` 那句
  `checkpointer 就绪：redis`（成功）或 `checkpointer 就绪：memory`（已降级）。
- **内网调用连不通**：确认两个服务在**同一环境**、目标服务的「内网调用」已开启、
  且访问的端口就是目标服务部署时填写的端口；地址别写成 `localhost` 或容器 IP（IP 每次发版都变）。
- **Redis 连上却 `unknown command`**：日志出现 `checkpointer redis 初始化失败，降级为 memory` 且 Redis 服务本身可达，
  基本是镜像用成了普通 `redis`（缺 RedisJSON/RediSearch）。换 `redis/redis-stack-server` 重建 Redis 服务；
  临时应急可把 `AGENT_CORE_CHECKPOINTER` 设为 `sqlite`（单机、需持久化目录），**不要**默默换成别的中间件，先定方向再改。
- **一问就冷启动**：最小副本数设 0 时每次 WS 连接都要等新版本拉起，保持 ≥1。
- **CORS**：小程序请求不受浏览器 CORS 约束，`PY_SERVER_CORS_ORIGINS` 只服务于 admin-web；
  管理端上线时把生产域名加进去即可。
- **密钥**：任何 `deploy-prod.json` / `application-prod.json` / `application-*.yaml` 都不得入库或进镜像，一律控制台环境变量注入。
