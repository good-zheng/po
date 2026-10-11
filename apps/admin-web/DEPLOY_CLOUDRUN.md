# admin-web（管理后台）云托管部署

`apps/admin-web`（Umi Max + Ant Design Pro SPA，Nginx 宿主，端口 8080）打成镜像推到微信云托管内置镜像仓库，
再在控制台「从镜像部署」。后端侧见 `services/api/DEPLOY_CLOUDRUN.md` 与 `services/chat/DEPLOY_CLOUDRUN.md`，
本文只覆盖管理端这个前端容器。

与 `apps/novel-web` 是同一条流水线形状（官方 nginx 镜像 + envsubst 模板 + `.envsh` 归一化上游），
**共享的坑（nginx 启动期解析上游、`# syntax=` 指令、envsubst 撞名）只记在
[`apps/novel-web/DEPLOY_CLOUDRUN.md` 第 7 节](../novel-web/DEPLOY_CLOUDRUN.md#7-坑位记录)**，本文只写管理端特有的部分。

## 0. 前置

- Docker Desktop 在运行。
- 登录镜像仓库（密码是 TCR「访问凭证」里的固定密码，不是登录密码）：

```bash
docker login ccr.ccs.tencentyun.com --username=100053273154
```

## 1. 一键脚本

```bash
pnpm admin:deploy                    # 构建 + 启动自证 + 推送 + 自证 tag 可解析
pnpm admin:deploy:official           # 有代理时改用官方 Docker Hub 基础镜像
NPM_REGISTRY=https://registry.npmmirror.com pnpm admin:deploy    # 境内拉 npm 慢/超时时
TAG=v2 bash scripts/deploy-admin.sh  # 覆盖 tag（需 bash，cmd/PowerShell 不认这种写法）
```

Windows 下必须走 `pnpm admin:deploy`：`node scripts/run-sh.mjs` 会定位 Git Bash。

可覆盖变量：`REGISTRY` `NAMESPACE` `REPO` `TAG` `PLATFORM` `NPM_REGISTRY` `BUILD_IMAGE` `RUNTIME_IMAGE`
`SKIP_BOOT_CHECK=1`（跳过启动自证，不建议）`ADMIN_BOOT_HOST`。

`REPO` 默认 `admin`——**这个名字必须以控制台为该服务 provision 的仓库为准**，别按 api 的命名规律推。

## 2. 控制台部署

| 填写项       | 值                                                                       |
| ------------ | ------------------------------------------------------------------------ |
| 镜像地址     | `ccr.ccs.tencentyun.com/<控制台给的命名空间>/<控制台给的仓库名>:prod`    |
| 监听端口     | `8080`                                                                    |
| 健康检查路径 | `/healthz`（返回 `ok`，不查上游）                                         |
| 环境变量     | `ADMIN_API_UPSTREAM`、`ADMIN_CHAT_UPSTREAM` **都要填**                    |
| 启动命令     | **留空**。渲染 nginx 配置靠镜像自带 entrypoint，填了执行命令就跳过 envsubst |
| 最小副本数   | `≥ 1`。不设就是 0，约半小时无请求实例被回收，下次打开管理端要等一次冷启动；`/ws/chat` 的长连接更会被缩容直接打断 |

两个值的来源：api / chat 各自「服务信息 → 内网访问域名」的 `host:port`，**原样复制，不要凭规律拼**
（去掉 `http://` 前缀；端口非 80 时要带上）。docker compose 里则填服务名 `api:8080` / `chat:5090`。

- 不填会怎样：容器照样起得来，`/api` 与 `/ws/chat` 各回 502，启动日志里 `16-admin-upstreams.envsh`
  打 WARN 并点名是哪个上游没配。（改之前是「镜像默认 `api:8080`」——云托管上解析不到就是
  `[emerg] host not found in upstream` + 创建版本失败。）
- **`ADMIN_CHAT_UPSTREAM` 没有构建期替代方案**：聊天页与创作工作台的 WS 地址是
  `src/pages/chatbot/service.ts` 用 `window.location.host` 拼的，永远同源，所以这条反代是管理端
  WebSocket 在生产环境唯一的通路。`/api` 可以靠烘进 JS 的域名绕过，`/ws/chat` 不行。

## 3. 两类后端地址，别混

| 类别 | 变量 | 何时决定 | 改动成本 |
| ---- | ---- | -------- | -------- |
| 浏览器直连的 API 域名 | `apps/admin-web/.env` 的 `UMI_APP_API_BASE_URL` | 构建期，烘进 JS 产物 | 重新 build + push |
| 容器反代的后端地址 | `ADMIN_API_UPSTREAM` / `ADMIN_CHAT_UPSTREAM` | 容器启动时 envsubst | 改环境变量 + 重启 |

- `.env` 的值**必须以域名结尾，不带 `/api`**：`src/services/*.ts` 的路径本身已是 `/api/books`，
  再带前缀就是 `/api/api/books`。这条现在有构建期断言拦（见 `Dockerfile` 的域名自证段）。
- 留空 = 同源模式，全部走第 2 节的两条反代。
- `.env` 与 `.env.local` 的覆盖关系、以及 `.dockerignore` 只放行 `.env` 拦住 `.env.local` 的写法，
  与 novel-web 完全一致，见 [`apps/novel-web/DEPLOY_CLOUDRUN.md` 第 3 节](../novel-web/DEPLOY_CLOUDRUN.md#3-两档-env-与前端-api-域名)。

## 4. 本地先验一遍再推

```bash
docker build --platform=linux/amd64 -f apps/admin-web/Dockerfile -t admin-diag:local .
for e in "ADMIN_API_UPSTREAM= -e ADMIN_CHAT_UPSTREAM=" \
         "ADMIN_API_UPSTREAM=nope.invalid:8080 -e ADMIN_CHAT_UPSTREAM=nope.invalid:5090"; do
  docker rm -f admin-bootcheck >/dev/null 2>&1
  docker run -d --name admin-bootcheck -p 18086:8080 -e $e admin-diag:local >/dev/null
  sleep 2
  echo "state=$(docker inspect -f '{{.State.Status}}' admin-bootcheck) healthz=$(curl -s --max-time 3 localhost:18086/healthz) emerg=$(docker logs admin-bootcheck 2>&1 | grep -c '\[emerg\]')"
  docker rm -f admin-bootcheck >/dev/null 2>&1
done
```

两行都必须是 `state=running healthz=ok emerg=0`。`pnpm admin:deploy` 推之前会自动跑同样的两条。

## 5. 验证清单

- 服务 Running，启动日志没有任何 `[emerg]`。
- 登录后菜谱、小说工作台都有数据；Network 里请求是 `https://api.dingdingchu.site/api/books`，**不是** `/api/api/books`。
- 聊天页与创作工作台连得上：WS 地址是同源的 `wss://<管理端域名>/ws/chat`，控制台里能看到帧；连不上先查 `ADMIN_CHAT_UPSTREAM`。
- 刷新不掉会话（token 在 localStorage，与 `apps/novel-web` 同一个 key）。
- 产物里已无 `.js.map`（`Dockerfile` 会删，实测占 dist 的 43%）。

## 6. 回滚

`TAG=prod` 是覆盖式推送，要能回滚就别复用 `prod`：`TAG=v2 pnpm admin:deploy`，
然后在控制台「版本管理」里把流量切回上一个镜像版本。

## 7. 管理端特有的坑

- **`REPO` 与镜像地址一律从控制台抄**，`docker push` 会顺手建仓并打印 digest，但服务拉的是控制台
  provision 的那个名字。
- **两个上游都必须填对才有可用的聊天与工作台**，与 novel-web「可以留空」相反；填错不再拖死容器，
  但表现为聊天页一直转圈，容易往模型侧去查。
- **`map $http_upgrade $connection_upgrade` 写在模板文件顶层**：本文件被 include 进 http 块，写在
  server 块里才会报错——挪动模板结构时注意。
