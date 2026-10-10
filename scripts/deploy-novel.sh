#!/usr/bin/env bash
# 言外书斋（apps/novel-web，Umi Max SPA + Nginx）镜像构建 + 推送到微信云托管内置镜像仓库
#
# 用法:
#   pnpm novel:deploy                                  # 推荐入口（根 package.json 包装本脚本）
#   bash scripts/deploy-novel.sh                       # 直接执行
#   pnpm novel:deploy:official                         # 等价 USE_OFFICIAL_IMAGES=1
#   TAG=v2 bash scripts/deploy-novel.sh                # 覆盖 tag（需 bash，cmd/PowerShell 不认这种写法）
#   USE_OFFICIAL_IMAGES=1 bash scripts/deploy-novel.sh      # 云端/梯子环境：用官方 Docker Hub 基础镜像
#   NPM_REGISTRY=https://registry.npmmirror.com bash scripts/deploy-novel.sh   # 境内拉 npm 慢时
#
# 后端域名不在构建期决定：nginx 配置是容器启动时由 envsubst 渲染的，改后端只需在控制台
# 改 NOVEL_API_UPSTREAM 再重启，不必重新构建镜像（与 brand 的 SITE_URL 必须烘进去不同）。
# 推之前有两道本地自证（SKIP_BOOT_CHECK=1 可跳）：容器在「没配上游」和「上游解析不到」
# 两种形态下都必须存活且 /healthz 通——云托管上那次「创建版本失败」正是缺了这一条。
#
# 前置: 先手动登录镜像仓库（密码是 TCR「访问凭证」固定密码，非登录密码）:
#   docker login ccr.ccs.tencentyun.com --username=100053273154
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- 可按需覆盖的配置（环境变量优先）----
REGISTRY="${REGISTRY:-ccr.ccs.tencentyun.com}"
NAMESPACE="${NAMESPACE:-tcb-100053273154-byrm}"   # 云托管环境内置镜像仓库命名空间
# 一服务一独立镜像仓库，名字必须用控制台给该服务 provision 的那条（别按 api 的命名规律推）
REPO="${REPO:-ca-eyxzseoz_novel}"
TAG="${TAG:-prod}"
PLATFORM="${PLATFORM:-linux/amd64}"                # 云托管只跑 amd64

NPM_REGISTRY="${NPM_REGISTRY:-}"

# ---- 基础镜像：默认国内加速镜像（Docker Hub 本地直连不通）----
if [[ "${USE_OFFICIAL_IMAGES:-0}" == "1" ]]; then
  BUILD_IMAGE="${BUILD_IMAGE:-node:22-alpine}"
  RUNTIME_IMAGE="${RUNTIME_IMAGE:-nginx:stable-alpine}"
else
  BUILD_IMAGE="${BUILD_IMAGE:-docker.m.daocloud.io/library/node:22-alpine}"
  RUNTIME_IMAGE="${RUNTIME_IMAGE:-docker.m.daocloud.io/library/nginx:stable-alpine}"
fi

IMAGE="$REGISTRY/$NAMESPACE/$REPO:$TAG"

echo ">> 构建镜像: $IMAGE"
echo "   BUILD_IMAGE=$BUILD_IMAGE"
echo "   RUNTIME_IMAGE=$RUNTIME_IMAGE"
echo "   NPM_REGISTRY=${NPM_REGISTRY:-（官方源）}"
# 上下文是仓库根（Dockerfile 里 --frozen-lockfile 要看 workspace 清单）
cd "$ROOT_DIR"
docker build \
  --platform="$PLATFORM" \
  --build-arg BUILD_IMAGE="$BUILD_IMAGE" \
  --build-arg RUNTIME_IMAGE="$RUNTIME_IMAGE" \
  --build-arg NPM_REGISTRY="$NPM_REGISTRY" \
  -f apps/novel-web/Dockerfile \
  -t "$IMAGE" \
  .

echo ">> 推送镜像: $IMAGE"

# ---- 启动自证：build 退出 0 不代表容器起得来 ----
# 这次云托管「创建版本失败」的根因是 nginx 启动时解析不到 /api 上游就直接退出，而它在
# 平台上伪装成 initenv.sh 的 137 报错；本地一条 curl 就能抓到，所以拦在 push 之前。
# 两个场景都必须「活着且 /healthz 通」：默认（没配上游）与一个解析不到的域名。
NOVEL_BOOT_HOST="${NOVEL_BOOT_HOST:-127.0.0.1}"

boot_check() {
  local label="$1" port="$2"
  shift 2
  local name="novel-bootcheck-${label}"
  local i state body

  docker rm -f "$name" >/dev/null 2>&1
  if ! docker run -d --name "$name" -p "${port}:8080" "$@" "$IMAGE" >/dev/null; then
    echo "!! 启动自证[$label]：docker run 就失败了" >&2
    return 1
  fi

  # 最多等 20s：nginx 起不来会立刻退出，等不到就是有问题
  for i in $(seq 1 20); do
    state=$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null || echo gone)
    [ "$state" != "running" ] && break
    body=$(curl -s --max-time 3 "http://${NOVEL_BOOT_HOST}:${port}/healthz" 2>/dev/null || true)
    [ "$body" = "ok" ] && break
    sleep 1
  done

  if [ "$state" != "running" ]; then
    echo "!! 启动自证[$label]：容器已退出（state=$state），日志：" >&2
    docker logs "$name" 2>&1 | tail -15 >&2
    docker rm -f "$name" >/dev/null 2>&1
    return 1
  fi
  if [ "$body" != "ok" ]; then
    echo "!! 启动自证[$label]：/healthz 没答上（得到「${body:-空}」），日志：" >&2
    docker logs "$name" 2>&1 | tail -15 >&2
    docker rm -f "$name" >/dev/null 2>&1
    return 1
  fi
  if docker logs "$name" 2>&1 | grep -q '\[emerg\]'; then
    echo "!! 启动自证[$label]：日志里有 [emerg]，配置没通过" >&2
    docker logs "$name" 2>&1 | grep '\[emerg\]' >&2
    docker rm -f "$name" >/dev/null 2>&1
    return 1
  fi

  echo "   启动自证[$label]：/healthz=ok，容器存活"
  docker rm -f "$name" >/dev/null 2>&1
}

if [ "${SKIP_BOOT_CHECK:-0}" = "1" ]; then
  echo ">> 跳过启动自证（SKIP_BOOT_CHECK=1）"
else
  echo ">> 启动自证"
  # 不配上游：阅读站产物里烘的是 api 绝对域名，这条反代本就可省，缺了也必须起得来
  boot_check unset 18089 -e NOVEL_API_UPSTREAM= || exit 1
  # 配了个解析不到的域名：这正是云托管上那次崩掉容器的形态
  boot_check bogus 18090 -e NOVEL_API_UPSTREAM=novel-bootcheck-should-not-resolve.invalid:8080 || exit 1
fi

docker push "$IMAGE"

# push 返回 0 不代表 tag 真的落库，推完自证一次
if ! docker manifest inspect "$IMAGE" >/dev/null 2>&1; then
  echo "!! registry 里仍解析不到 $IMAGE（多半是 docker login 过期，用 TCR 固定密码重登）" >&2
  exit 1
fi
echo ">> 已验证 tag 可解析: $IMAGE"

echo ">> 完成。微信云托管『从镜像部署』填写:"
echo "   镜像地址: $IMAGE"
echo "   监听端口: 8080   健康检查: /healthz"
echo "   环境变量: NOVEL_API_UPSTREAM 可不填——产物里的 api 域名是烘进 JS 的（apps/novel-web/.env），"
echo "            浏览器不走这条同源反代。只有把那个值置空、要求走同源时，才需要填"
echo "            api 服务『服务信息 → 内网访问域名』的 host:port，从控制台原样复制，别凭规律拼。"
echo "            填错或留空都不再影响容器启动（/api 回 502，error.log 里点名那个解析不到的 host）。"
echo "   启动命令: 留空。渲染 nginx 配置靠镜像自带 entrypoint，填了执行命令会把它跳过。"
echo "   详见 apps/novel-web/DEPLOY_CLOUDRUN.md"
