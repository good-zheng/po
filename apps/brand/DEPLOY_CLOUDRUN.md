# brand 介绍站云托管部署

`apps/brand`（Astro 静态站，Nginx 宿主，端口 8080）打成镜像推到微信云托管内置镜像仓库，再在控制台「从镜像部署」。
api / chat 的部署见 `services/api/DEPLOY_CLOUDRUN.md`、`services/chat/DEPLOY_CLOUDRUN.md`；本文只覆盖介绍站。

## 0. 前置

- Docker Desktop 在运行。
- 登录镜像仓库（密码是 TCR「访问凭证」里的固定密码，不是登录密码；一次登录管一阵子，过期后 push 会 401）：

```bash
docker login ccr.ccs.tencentyun.com --username=100053273154
```

介绍站**不需要任何环境变量、数据库、Redis、外网调用**——它是纯静态产物，容器里只有一个 Nginx。

## 1. 一键脚本

```bash
pnpm brand:deploy                      # 构建 + 推送 + 自证 tag 可解析
pnpm brand:deploy:official             # 有代理时改用官方 Docker Hub 基础镜像
SITE_URL=https://真实域名 pnpm brand:deploy    # 把域名烘进绝对链接（见第 4 节）
```

Windows 下必须走 `pnpm brand:deploy`：`node scripts/run-sh.mjs` 会定位 Git Bash，直接 `bash scripts/deploy-brand.sh` 在 cmd/PowerShell 里可能命中 WSL 的 bash 桩。
需要在 bash 里覆盖变量时（cmd/PowerShell 不认这种写法）：

```bash
TAG=v2 bash scripts/deploy-brand.sh
```

可覆盖变量：`REGISTRY` `NAMESPACE` `REPO` `TAG` `PLATFORM` `SITE_URL` `NPM_REGISTRY` `BUILD_IMAGE` `RUNTIME_IMAGE`。

镜像地址（命名空间与仓库名以控制台为准，别按规律推——`services/chat/DEPLOY_CLOUDRUN.md` 里就踩过这个坑）：

| 服务  | 镜像地址                                                  | 体积     |
| ----- | --------------------------------------------------------- | -------- |
| brand | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/brand:prod` | 约 95 MB |

### 手动等价命令

```bash
# 上下文必须是仓库根：brand 在 pnpm workspace 里，--frozen-lockfile 要看到全部 importer 的清单
docker build --platform=linux/amd64 \
  --build-arg BUILD_IMAGE=docker.m.daocloud.io/library/node:22-alpine \
  --build-arg RUNTIME_IMAGE=docker.m.daocloud.io/library/nginx:stable-alpine \
  -f apps/brand/Dockerfile \
  -t ccr.ccs.tencentyun.com/tcb-100053273154-byrm/brand:prod .
docker push ccr.ccs.tencentyun.com/tcb-100053273154-byrm/brand:prod
```

Dockerfile 里有两道构建期自证，任一失败镜像就出不来：产物齐全（`index.html` / `404.html` / `sitemap-index.xml` / `rss.xml`），以及传入的 `SITE_URL` 确实写进了 `src/config.yaml`。

## 2. 控制台部署

云托管环境 → 新建服务（或改现有服务）→ **从镜像部署**：

| 填写项       | 值                                                                     |
| ------------ | ---------------------------------------------------------------------- |
| 镜像地址     | `ccr.ccs.tencentyun.com/tcb-100053273154-byrm/brand:prod`              |
| 监听端口     | `8080`                                                                 |
| 健康检查路径 | `/healthz`（返回 `ok`，`access_log off`，别用 `/`，那是 80 KB 的首页） |
| 环境变量     | 无                                                                     |
| 公网访问     | 按需开启（小程序/后台都不依赖它，只有人要用手机或浏览器打开时才需要）  |

实例规格给最小的即可：静态文件全在镜像里，没有冷启动依赖。

## 3. 本地先验一遍再推

```bash
docker run --rm -p 18080:8080 ccr.ccs.tencentyun.com/tcb-100053273154-byrm/brand:prod &
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18080/          # 200
curl -s http://localhost:18080/healthz                                    # ok
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:18080/nope      # 404，返回站内 404.html
```

## 4. 域名必须在构建期定死

Astro 是构建期产物。`sitemap-index.xml`、`rss.xml`、Open Graph、canonical、`robots.txt` 里的绝对链接全部来自
`src/config.yaml` 的 `site.site`，**运行时改环境变量没有任何作用**。站内相对链接不受影响，但搜索引擎和分享卡片会读到错的域名。

`--build-arg SITE_URL=` 会在镜像构建时改写 `src/config.yaml`，只影响镜像层，不动仓库文件（仓库里保持占位值）。

因此顺序是：

1. 先在控制台把服务建出来，拿到公网域名（或用已备案的自定义域名）。
2. `SITE_URL=https://那个域名 pnpm brand:deploy`。
3. 控制台重新部署，选新镜像。

绑自定义域名走云托管的域名管理，需要域名已完成 ICP 备案；未备案只能使用云托管给的默认域名。

## 5. 验证清单

- `docker manifest inspect ccr.ccs.tencentyun.com/tcb-100053273154-byrm/brand:prod` 能解析出 `linux/amd64`。
- 服务状态 Running，实例日志里没有 nginx `access log` 之外的报错。
- 打开首页后：`view-source` 里搜 `example.com` 应该搜不到（搜到就是忘了传 `SITE_URL`）。
- `/sitemap-index.xml`、`/rss.xml`、`/blog`、`/category/ai`、`/404`（任意未知路径）都正常。
- `/_astro/*` 响应头带 `Cache-Control: public, immutable`。

## 6. 回滚

`TAG=prod` 是覆盖式推送，回滚要靠历史版本号。要能回滚就别复用 `prod`：

```bash
TAG=v3 SITE_URL=https://真实域名 pnpm brand:deploy
```

然后在控制台「版本管理」里把流量切回上一个镜像版本。

## 7. 坑位记录

- **仓库名以控制台为准。** 一服务一独立仓库，`docker push` 会顺手建仓、照样打印 digest，但服务拉的是控制台 provision 的那个名字，猜错就一直是 `Failed to pull image`。
- **平台架构只能 amd64。** 云托管不跑 arm；Apple 芯片或 arm 机器上要显式 `PLATFORM=linux/amd64`（脚本已默认）。
- **npm 拉包慢/超时**：传 `NPM_REGISTRY=https://registry.npmmirror.com pnpm brand:deploy`，脚本会转成 `--build-arg NPM_REGISTRY=`，在镜像里 `pnpm config set registry`。
- **不要给 Dockerfile 加 `# syntax=docker/dockerfile:1`**：BuildKit 会去 Docker Hub 拉前端镜像，本地网络直连不通（和 chat 镜像同一条教训）。
- `pnpm brand:dev` 报 `Failed to load url /vendor/integration/index.ts` 与部署无关，是 Vite 缓存过期，见 `README.md`。
