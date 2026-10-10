# novel-web（言外书斋）云托管部署

`apps/novel-web`（Umi Max SPA，Nginx 宿主，端口 8080）打成镜像推到微信云托管内置镜像仓库，再在控制台「从镜像部署」。
后端侧的小说 Agent（`services/agent-novel`）**不单独出镜像**——它是 chat 镜像里的一个 pip 包，见 `services/chat/DEPLOY_CLOUDRUN.md`；
`services/api/novel` 是 Java 模块，随 api 镜像走，见 `services/api/DEPLOY_CLOUDRUN.md`。本文只覆盖阅读站这个前端容器。

## 0. 前置

- Docker Desktop 在运行。
- 登录镜像仓库（密码是 TCR「访问凭证」里的固定密码，不是登录密码；过期后 push 会 401）：

```bash
docker login ccr.ccs.tencentyun.com --username=100053273154
```

## 1. 一键脚本

```bash
pnpm novel:deploy                    # 构建 + 启动自证 + 推送 + 自证 tag 可解析
pnpm novel:deploy:official           # 有代理时改用官方 Docker Hub 基础镜像
NPM_REGISTRY=https://registry.npmmirror.com pnpm novel:deploy    # 境内拉 npm 慢/超时时
```

Windows 下必须走 `pnpm novel:deploy`：`node scripts/run-sh.mjs` 会定位 Git Bash，直接 `bash scripts/deploy-novel.sh` 在 cmd/PowerShell 里可能命中 WSL 的 bash 桩。
需要在 bash 里覆盖变量时（cmd/PowerShell 不认这种写法）：

```bash
TAG=v2 bash scripts/deploy-novel.sh
```

可覆盖变量：`REGISTRY` `NAMESPACE` `REPO` `TAG` `PLATFORM` `NPM_REGISTRY` `BUILD_IMAGE` `RUNTIME_IMAGE`，以及启动自证相关的 `SKIP_BOOT_CHECK=1`（跳过，不建议）与 `NOVEL_BOOT_HOST`（本机不是 127.0.0.1 时）。

镜像地址（命名空间与仓库名以控制台为准，别按规律推——`services/chat/DEPLOY_CLOUDRUN.md` 里踩过）：

| 服务      | 镜像地址                                                             |
| --------- | -------------------------------------------------------------------- |
| novel-web | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_novel:prod` |

### 手动等价命令

```bash
# 上下文必须是仓库根：novel-web 在 pnpm workspace 里，要看到 pnpm-lock.yaml 与 packages/types
docker build --platform=linux/amd64 \
  --build-arg BUILD_IMAGE=docker.m.daocloud.io/library/node:22-alpine \
  --build-arg RUNTIME_IMAGE=docker.m.daocloud.io/library/nginx:stable-alpine \
  -f apps/novel-web/Dockerfile \
  -t ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_novel:prod .
docker push ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_novel:prod
```

Dockerfile 里有一道构建期自证：`dist/index.html`、`favicon.svg`、`umi.*.js/css` 与四个页面 chunk（书架/详情/阅读/登录）齐全，且 `<title>言外书斋</title>` 在——产物残缺的镜像出不来。

## 2. 控制台部署

云托管环境 → 新建服务 → **从镜像部署**：

| 填写项       | 值                                                                          |
| ------------ | --------------------------------------------------------------------------- |
| 镜像地址     | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_novel:prod`        |
| 监听端口     | `8080`                                                                       |
| 健康检查路径 | `/healthz`（返回 `ok`，不查上游）                                            |
| 环境变量     | `NOVEL_API_UPSTREAM` 可留空                                                 |
| 启动命令     | **留空**。渲染 nginx 配置靠镜像自带 entrypoint，填了执行命令就跳过 envsubst  |
| 公网访问     | 按需开启                                                                     |

`NOVEL_API_UPSTREAM` **可留空**：生产产物里 api 域名是烘进 JS 的（第 3 节），浏览器并不走这条同源
反代。只有把 `UMI_APP_API_BASE_URL` 置空、要求走同源时才需要填它，值从 api 服务的「服务信息 →
内网访问域名」原样复制（去掉 `http://` 前缀，端口非 80 时要带上），**不要凭规律拼**。
留空与填错都只让 `/api` 回 502——容器照起，`16-novel-api.envsh` 在启动日志里打一条 WARN 并点名
那个解析不到的 host。（2026-10-10 之前这里写的是「没设置时走镜像默认值 `api:8080`，云托管上会 502」，
那句是错的：实际是 nginx 启动即解析失败、`[emerg] host not found in upstream` 直接退出，
云托管表现为「创建版本失败」，见第 7 节。）

### 这条环境变量为什么不需要重新构建

阅读站的 nginx 配置是 `apps/novel-web/nginx/novel.conf.template`，容器启动时由官方镜像的 entrypoint 用 envsubst 渲染成 `conf.d/novel.conf`，替换发生在 nginx 读配置之前。所以换后端域名 = 改环境变量 + 重启，不用重新 build/push。
（对比 `apps/brand`：Astro 的 `SITE_URL` 是构建期产物，必须重新构建。本站的**前端 API 域名**同样也是构建期的，见下一节——别把两者混为一谈。）

## 3. 两档 env 与前端 API 域名

Umi 4.7 只加载 `.env` 和 `.env.local` 两档（`@umijs/core/dist/service/env.js` 写死，**没有 `.env.production`**），后读的 `.env.local` 无条件覆盖。本 app 的约定：

| 文件         | 用途 | 入库 | 进 docker 上下文 |
| ------------ | ---- | ---- | ---------------- |
| `.env`       | 生产值 `UMI_APP_API_BASE_URL=https://api.dingdingchu.site`（与两个小程序同一个 api 服务） | 是 | 是 |
| `.env.local` | 本机开发覆盖（`PORT=8001`、`http://127.0.0.1:8080`） | 否 | 否 |
| `.env.example` | 开发档模板，`cp` 成 `.env.local` 用 | 是 | 无所谓 |

- `src/app.tsx` 的 `baseURL` 只在 `NODE_ENV=production` 时取这个值；dev 一律同域 `/api`，这样 `config/proxy.ts` 和 `mock/novel.ts` 才拦得住。
- 域名是**构建期内联进 JS 产物**的，运行时改环境变量对它没有任何作用：换线上 api 域名要改 `.env` 后重新 `pnpm novel:deploy`。
- 值的写法：不带 `/api` 结尾。`src/services/*.ts` 的路径本身已是 `/api/books`，补两次会变成 `/api/api/books`；小程序侧的 `TARO_APP_API_BASE_URL` 反而要带 `/api`，因为那边请求路径不含前缀。
- 浏览器直连 `api.dingdingchu.site` 属跨域，靠 `SecurityConfig` 的 `AllowedOriginPatterns("*") + AllowedHeaders("*")` 兜着，凭据走 `Authorization: Bearer`（localStorage），不用 cookie，所以不需要 allowCredentials。
- 本机直接 `pnpm novel:build` 会读出 `.env.local` 的开发地址（上面两档表的覆盖方向）。**部署产物必须由镜像构建产出**，或先把 `.env.local` 挪走再 build。
- 想改回「同源反代」形态（不烘域名、只靠容器里 nginx 转 `/api`）：把 `.env` 的值置空即可，此时第 2 节的 `NOVEL_API_UPSTREAM` 就是唯一通路。

根 `.gitignore`/`.dockerignore` 默认屏蔽 `.env*`，这里为 `apps/novel-web/.env` 单独开了 `!` 放行口子——域名的公开程度等同于一行反代配置，密钥仍一律不入库。注意两家的匹配语义不同：gitignore 的 `.env.*` 按 basename 匹配任意层级，dockerignore 的模式不带 `/` 只匹配上下文根，所以 `.dockerignore` 里对 `apps/novel-web/.env.local` 写了显式路径。

## 4. 本地先验一遍再推

```bash
docker build --platform=linux/amd64 -f apps/novel-web/Dockerfile -t novel-diag:local .
docker run --rm -p 18080:8080 -e NOVEL_API_UPSTREAM=host.docker.internal:8080 novel-diag:local
curl -s http://localhost:18080/healthiz           # 拼错路径应回落 SPA，返回 index.html 而不是 404
curl -s http://localhost:18080/healthz            # ok
curl -s http://localhost:18080/read/1/2 | head -3 # history 路由回落 index.html
curl -s http://localhost:18080/api/books          # 走 nginx 反代（本机 8080 的 Spring 在跑才有数据）
docker run --rm novel-diag:local sh -c 'grep -o "baseURL:\"[^\"]*\"" /usr/share/nginx/html/umi.*.js'
```

最后一条是域名自证：镜像产物里应该是 `https://api.dingdingchu.site`，出现 `127.0.0.1` 说明本机的 `.env.local` 漏进了构建上下文。

再加两个「崩容器」形态——`pnpm novel:deploy` 推之前会自动跑同样的两条，手动验一次也行：

```bash
for e in "NOVEL_API_UPSTREAM=" "NOVEL_API_UPSTREAM=should-not-resolve.invalid:8080"; do
  docker rm -f novel-bootcheck >/dev/null 2>&1
  docker run -d --name novel-bootcheck -p 18081:8080 -e "$e" novel-diag:local >/dev/null
  sleep 2
  echo "$e → state=$(docker inspect -f '{{.State.Status}}' novel-bootcheck) healthz=$(curl -s --max-time 3 localhost:18081/healthz)"
  docker logs novel-bootcheck 2>&1 | grep -c '\[emerg\]'
  docker rm -f novel-bootcheck >/dev/null 2>&1
done
```

两行都必须是 `state=running healthz=ok` 且 `[emerg]` 计数为 `0`。上游留空或写错都只该让 `/api` 变 502，静态页与登录前的阅读照常。一旦看到 `state=exited`，说明配置又回到「启动即解析」的老写法了，见第 7 节第一条。

## 5. 验证清单

- `docker manifest inspect ccr.ccs.tencentyun.com/tcb-100053273154-byrm/ca-eyxzseoz_novel:prod` 能解析出 `linux/amd64`。
- 服务 Running，日志里 nginx 只有 access log，没有 `[error] ... "novel.conf" test failed`，也没有任何 `[emerg]`。
- 浏览器打开首页：书架有数据、控制台无 CORS 报错；`view-source` 里 `umi.*.js` 的 URL 指向 `api.dingdingchu.site`。
- 控制台 Network 里书名请求是 `https://api.dingdingchu.site/api/books`，**不是** `/api/api/books`（多一层就是 `.env` 的值带了 `/api` 结尾，见第 3 节）。
- 登录后刷新不掉会话（token 在 localStorage，与 `apps/admin-web` 同一个 key）。
- 未知路径（如 `/nope`）返回站内 404 页而不是 nginx 默认 404。
- `umi.*.js` 响应头带 `Cache-Control: public, immutable`，`/index.html` 带 `no-cache`。

## 6. 回滚

`TAG=prod` 是覆盖式推送，回滚要靠历史版本。要能回滚就别复用 `prod`：

```bash
TAG=v2 pnpm novel:deploy
```

然后在控制台「版本管理」里把流量切回上一个镜像版本。

## 7. 坑位记录

- **上游主机名最终落在 `proxy_pass` 的字面量里 = 平台上的「创建版本失败」**（2026-10-10 实录）。老模板写的是 `proxy_pass http://$NOVEL_API_UPSTREAM;`，看着像变量，其实 envsubst 在 nginx 读配置之前就把 `$NOVEL_API_UPSTREAM`（镜像默认值 `api:8080`）替换成了字面量 `http://api:8080`，于是解析发生在加载那一刻，云托管的 pod 网络里没有 `api` 这个名字，直接 `nginx: [emerg] host not found in upstream "api" in /etc/nginx/conf.d/novel.conf:33`，进程退出。平台把这件事伪装成生命周期钩子的报错打给你看：
  ```
  Exec lifecycle hook ([/bin/sh /app/cert/initenv.sh]) ... exited with 137
  cannot exec in a stopped container / Back-off restarting failed container
  ```
  `initenv.sh` 是装平台 CA 证书的那步，137 是容器已停后被强杀，全是次生噪声——真因只在「启动日志」最后两行。修法就是第 2 节那套「变量 + `resolver`」：目标由 `16-novel-api.envsh` 注入，解析推迟到每个请求，上游没配或写错只让 `/api` 变 502。这条教训适用于所有 nginx 静态站镜像，`apps/admin-web` 当时带着同一个隐患（它的 `/ws/chat` 是真需要反代的），一并改了。
- **老镜像可以先只在控制台热修，但那是止血。** 把 `NOVEL_API_UPSTREAM` 填成 api 服务「内网访问域名」的 `host:port`，envsubst 渲染出的字面量在环境内解析得到，容器就起来了（实测同一个镜像：填可解析的名字 → `state=running`、`/healthz=ok`；填解析不到的 → `state=exited` + 上面那句 `[emerg]`）。代价是这条 DNS 只在容器启动那一刻做一次，后端 pod 的 IP 一变就要重启本服务才不 502；新镜像改成逐请求解析（`valid=10s`），找机会推上去。
- **`.env` 里 `UMI_APP_API_BASE_URL` 不能带 `/api` 结尾**（同一次事故里差点第二个坑）。`src/services/*.ts` 的路径本身已经是 `/api/books`，值再带前缀就成了 `/api/api/books`，404 得很难看却和容器启动无关。Dockerfile 里现在有一条构建期断言会 grep 产物、`baseURL` 以 `/api` 结尾就直接让 build 失败；小程序侧的 `TARO_APP_API_BASE_URL` 相反，必须带 `/api`，别照抄。这次排查发现 `apps/admin-web/.env` 里也是同一个带 `/api` 的写法，两家一起改了。
- **仓库名以控制台为准。** 一服务一独立仓库，`docker push` 会顺手建仓、照样打印 digest，但服务拉的是控制台 provision 的那个名字，猜错就一直 `Failed to pull image`。
- **平台架构只能 amd64。** 云托管不跑 arm；脚本已默认 `PLATFORM=linux/amd64`。
- **不要给 Dockerfile 加 `# syntax=docker/dockerfile:1`**：BuildKit 会去 Docker Hub 拉前端镜像，本地网络直连不通（api/chat/brand 同一条教训）。`apps/admin-web/Dockerfile` 以前第一行就是它，现在只剩一段注释在劝退。
- **`fill in 启动命令` 会静默废掉反代**：nginx 配置靠镜像 entrypoint 渲染，控制台里填了执行命令就等于绕过它，`/api` 直接 404，而静态页一切正常，很难往这个方向查。
- **envsubst 的撞名风险**：它替换「当前已存在的环境变量名」，平台会注入 `PORT`/`HOSTNAME` 之类。模板里那个键刻意叫 `NOVEL_API_UPSTREAM`，改名时保持这个前缀。
- **`.dockerignore` 与 `.gitignore` 匹配语义不同**（见第 3 节末）。当年 `services/api/.dockerignore` 就是因为 compose 的上下文在子目录、根清单不生效才单独建的一份。
- **M3 创作端上传封面时**要提 nginx 的 `client_max_body_size`（默认 1m，后端 Spring 是 100m），否则表现为上传 413 而后端日志一片干净。现在阅读侧只读，故意没加。
- 本站目前不连 chat 的 WebSocket（`/ws/chat?agent=novel` 在 `services/agent-novel` 那侧，随 chat 镜像部署）。真要在阅读页里接流式对话，得在 `novel.conf.template` 里补一条带 `Upgrade`/`Connection` 头的 `location ^~ /ws/`，参照 `infra/nginx/nginx.conf`。
