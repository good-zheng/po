#!/usr/bin/env bash
# po API (Spring Boot) 镜像构建 + 推送到微信云托管内置镜像仓库
#
# 用法:
#   pnpm api:deploy                        # 推荐入口（根 package.json 包装本脚本）
#   bash scripts/deploy-api.sh             # 直接执行
#   pnpm api:deploy:official               # 等价 USE_OFFICIAL_IMAGES=1
#   TAG=v2 bash scripts/deploy-api.sh      # 覆盖 tag（需 bash，cmd/PowerShell 不认这种写法）
#   USE_OFFICIAL_IMAGES=1 bash scripts/deploy-api.sh   # 云端/梯子环境：用官方 Docker Hub 基础镜像
#
# 前置: 先手动登录镜像仓库（密码是 TCR「访问凭证」固定密码，非登录密码）:
#   docker login ccr.ccs.tencentyun.com --username=100053273154
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVICE_DIR="$ROOT_DIR/services/api"

# ---- 可按需覆盖的配置（环境变量优先）----
REGISTRY="${REGISTRY:-ccr.ccs.tencentyun.com}"
NAMESPACE="${NAMESPACE:-tcb-100053273154-byrm}"   # 云托管环境内置镜像仓库命名空间
REPO="${REPO:-ca-eyxzseoz_po}"                     # 服务对应的镜像仓库名
TAG="${TAG:-prod}"
PLATFORM="${PLATFORM:-linux/amd64}"                # 云托管只跑 amd64

# ---- 基础镜像：默认国内加速镜像（Docker Hub 本地直连不通）----
# APT_MIRROR 同理：运行阶段要装 curl（compose 健康检查用），Ubuntu 自带源指向 archive.ubuntu.com
# 会在 universe 索引上反复断连；传空串则保留镜像自带源（云端/梯子构建）。
if [[ "${USE_OFFICIAL_IMAGES:-0}" == "1" ]]; then
  BUILD_IMAGE="${BUILD_IMAGE:-maven:3.9-eclipse-temurin-17}"
  RUNTIME_IMAGE="${RUNTIME_IMAGE:-eclipse-temurin:17-jre}"
  APT_MIRROR="${APT_MIRROR:-}"
else
  BUILD_IMAGE="${BUILD_IMAGE:-docker.m.daocloud.io/library/maven:3.9-eclipse-temurin-17}"
  RUNTIME_IMAGE="${RUNTIME_IMAGE:-docker.m.daocloud.io/library/eclipse-temurin:17-jre}"
  APT_MIRROR="${APT_MIRROR:-mirrors.tuna.tsinghua.edu.cn}"
fi

IMAGE="$REGISTRY/$NAMESPACE/$REPO:$TAG"

echo ">> 构建镜像: $IMAGE"
echo "   BUILD_IMAGE=$BUILD_IMAGE"
echo "   RUNTIME_IMAGE=$RUNTIME_IMAGE"
echo "   APT_MIRROR=${APT_MIRROR:-（镜像自带源）}"
docker build \
  --platform="$PLATFORM" \
  --build-arg BUILD_IMAGE="$BUILD_IMAGE" \
  --build-arg RUNTIME_IMAGE="$RUNTIME_IMAGE" \
  --build-arg APT_MIRROR="$APT_MIRROR" \
  -t "$IMAGE" \
  "$SERVICE_DIR"

echo ">> 推送镜像: $IMAGE"
docker push "$IMAGE"

# push 返回 0 不代表 tag 真的落库，推完自证一次
if ! docker manifest inspect "$IMAGE" >/dev/null 2>&1; then
  echo "!! registry 里仍解析不到 $IMAGE（多半是 docker login 过期，用 TCR 固定密码重登）" >&2
  exit 1
fi
echo ">> 已验证 tag 可解析: $IMAGE"

echo ">> 完成。云托管『从镜像部署』填写:"
echo "   镜像地址: $IMAGE"
echo "   监听端口: 8080   健康检查: /api/actuator/health"
echo "   环境变量: 见 services/api/application-prod.json（SPRING_PROFILES_ACTIVE=prod 必填）"
