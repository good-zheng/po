#!/usr/bin/env bash
# 介绍站（apps/brand，Astro 静态站）镜像构建 + 推送到微信云托管内置镜像仓库
#
# 用法:
#   pnpm brand:deploy                                  # 推荐入口（根 package.json 包装本脚本）
#   bash scripts/deploy-brand.sh                       # 直接执行
#   pnpm brand:deploy:official                         # 等价 USE_OFFICIAL_IMAGES=1
#   TAG=v2 bash scripts/deploy-brand.sh                # 覆盖 tag（需 bash，cmd/PowerShell 不认这种写法）
#   SITE_URL=https://真实域名 bash scripts/deploy-brand.sh   # 把域名烘进 sitemap/RSS/OG
#   USE_OFFICIAL_IMAGES=1 bash scripts/deploy-brand.sh       # 云端/梯子环境：用官方 Docker Hub 基础镜像
#
# 前置: 先手动登录镜像仓库（密码是 TCR「访问凭证」固定密码，非登录密码）:
#   docker login ccr.ccs.tencentyun.com --username=100053273154
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# ---- 可按需覆盖的配置（环境变量优先）----
REGISTRY="${REGISTRY:-ccr.ccs.tencentyun.com}"
NAMESPACE="${NAMESPACE:-tcb-100053273154-byrm}"   # 云托管环境内置镜像仓库命名空间
REPO="${REPO:-brand}"                              # 控制台里的镜像仓库名
TAG="${TAG:-prod}"
PLATFORM="${PLATFORM:-linux/amd64}"                # 云托管只跑 amd64

# 站点绝对域名：留空则沿用 apps/brand/src/config.yaml 里的值（当前是占位 example.com）
SITE_URL="${SITE_URL:-}"
# 境内拉 npm 包慢时传 https://registry.npmmirror.com
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

if [[ -z "$SITE_URL" ]]; then
  echo "!! 未传 SITE_URL，镜像里的 sitemap.xml / rss.xml / Open Graph / canonical 会沿用" >&2
  echo "!! src/config.yaml 的域名（当前为占位 https://example.com）。换域名必须重新构建。" >&2
fi

echo ">> 构建镜像: $IMAGE"
echo "   BUILD_IMAGE=$BUILD_IMAGE"
echo "   RUNTIME_IMAGE=$RUNTIME_IMAGE"
echo "   SITE_URL=${SITE_URL:-（沿用 config.yaml）}"
# 上下文是仓库根（Dockerfile 里 --frozen-lockfile 需要全部 workspace importer）
cd "$ROOT_DIR"
docker build \
  --platform="$PLATFORM" \
  --build-arg BUILD_IMAGE="$BUILD_IMAGE" \
  --build-arg RUNTIME_IMAGE="$RUNTIME_IMAGE" \
  --build-arg SITE_URL="$SITE_URL" \
  --build-arg NPM_REGISTRY="$NPM_REGISTRY" \
  -f apps/brand/Dockerfile \
  -t "$IMAGE" \
  .

echo ">> 推送镜像: $IMAGE"
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
echo "   无需环境变量、无需数据库与 Redis；公网访问按服务配置开启。"
echo "   服务开通后拿到的域名要和本脚本传入的 SITE_URL 一致，否则绝对链接指向别处。"
