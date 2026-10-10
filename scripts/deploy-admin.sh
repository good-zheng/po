#!/usr/bin/env bash
# 管理后台（apps/admin-web，Umi Max + Ant Design Pro SPA + Nginx）镜像构建 + 推送到微信云托管内置镜像仓库
#
# 用法:
#   pnpm admin:deploy                                  # 推荐入口（根 package.json 包装本脚本）
#   bash scripts/deploy-admin.sh                       # 直接执行
#   pnpm admin:deploy:official                         # 等价 USE_OFFICIAL_IMAGES=1
#   TAG=v2 bash scripts/deploy-admin.sh                # 覆盖 tag（需 bash，cmd/PowerShell 不认这种写法）
#   USE_OFFICIAL_IMAGES=1 bash scripts/deploy-admin.sh      # 云端/梯子环境：用官方 Docker Hub 基础镜像
#   NPM_REGISTRY=https://registry.npmmirror.com bash scripts/deploy-admin.sh   # 境内拉 npm 慢时
#
# 两类后端地址分开管，别混：
#   前端调用的 API 域名 —— 构建期常量，来自 apps/admin-web/.env（生产档），烘进 JS 产物，改它必须重打镜像；
#   容器反代的后端地址 —— 运行时变量 ADMIN_API_UPSTREAM / ADMIN_CHAT_UPSTREAM，由 nginx 的 envsubst
#   在启动时渲染，控制台改了直接重启即可（与 brand 的 SITE_URL 必须烘进去不同）。
#
# 推之前有两道启动自证（SKIP_BOOT_CHECK=1 可跳）：容器在「两个上游都没配」和「上游解析不到」
# 两种形态下都必须存活且 /healthz 通 —— 2026-10-10 novel 那次「创建版本失败」就是缺了这一条。
# 详见 apps/admin-web/DEPLOY_CLOUDRUN.md
#
# 前置: 先手动登录镜像仓库（密码是 TCR「访问凭证」固定密码，非登录密码）:
#   docker login ccr.ccs.tencentyun.com --username=100053273154
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- 可按需覆盖的配置（环境变量优先）----
REGISTRY="${REGISTRY:-ccr.ccs.tencentyun.com}"
NAMESPACE="${NAMESPACE:-tcb-100053273154-byrm}"   # 云托管环境内置镜像仓库命名空间
# 一服务一独立镜像仓库，名字以控制台为该服务 provision 的那条为准（这里按用户指定填 admin）
REPO="${REPO:-admin}"
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
  -f apps/admin-web/Dockerfile \
  -t "$IMAGE" \
  .

echo ">> 推送镜像: $IMAGE"

# ---- 启动自证：build 退出 0 不代表容器起得来（与 deploy-novel.sh 同一条教训）----
# 管理端的两个上游在云托管上必须填对才可用，但「填错/没填」绝不该演变成容器起不来：
# 2026-10-10 novel 那次就是 nginx 启动即解析上游失败 → 平台报「创建版本失败」，
# 还把 initenv.sh 的 137 一起打出来当噪声。推之前本地各验一种形态。
# SKIP_BOOT_CHECK=1 可跳过（不建议）；本机回环不是 127.0.0.1 时用 ADMIN_BOOT_HOST 覆盖。
ADMIN_BOOT_HOST="${ADMIN_BOOT_HOST:-127.0.0.1}"

boot_check() {
  local label="$1" port="$2"
  shift 2
  local name="admin-bootcheck-${label}"
  local i state body

  docker rm -f "$name" >/dev/null 2>&1
  if ! docker run -d --name "$name" -p "${port}:8080" "$@" "$IMAGE" >/dev/null; then
    echo "!! 启动自证[$label]：docker run 就失败了" >&2
    return 1
  fi

  for i in $(seq 1 20); do
    state=$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null || echo gone)
    [ "$state" != "running" ] && break
    body=$(curl -s --max-time 3 "http://${ADMIN_BOOT_HOST}:${port}/healthz" 2>/dev/null || true)
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
  # 两个上游都不填：容器仍须存活，只有 /api 与 /ws/chat 会 502
  boot_check noenv 18091 -e ADMIN_API_UPSTREAM= -e ADMIN_CHAT_UPSTREAM= || exit 1
  # 填了但解析不到：novel 那次崩掉容器的形态
  boot_check bogus 18092 \
    -e ADMIN_API_UPSTREAM=admin-bootcheck-api-should-not-resolve.invalid:8080 \
    -e ADMIN_CHAT_UPSTREAM=admin-bootcheck-chat-should-not-resolve.invalid:5090 || exit 1
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
echo "   环境变量: ADMIN_API_UPSTREAM=<api 服务的内网访问域名 host:port>"
echo "            ADMIN_CHAT_UPSTREAM=<chat 服务的内网访问域名 host:port>"
echo "            两条都从控制台对应服务『服务信息 → 内网访问域名』原样复制，不要凭规律拼。"
echo "            管理端的 /ws/chat 只有同源反代这一条通路，这两条不填聊天页与创作工作台就连不上；"
echo "            但填错或留空都不再拖死容器启动（各路径回 502，启动日志里点名未配置）。"
echo "   启动命令: 留空。渲染 nginx 配置靠镜像自带 entrypoint，填了执行命令会把它跳过。"
echo "   详见 apps/admin-web/DEPLOY_CLOUDRUN.md"
