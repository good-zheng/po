#!/usr/bin/env bash
# po chat (FastAPI + LangGraph) 镜像构建 + 推送到微信云托管内置镜像仓库
#
# 用法:
#   pnpm chat:deploy                    # 推荐入口
#   TAG=v2 bash scripts/deploy-chat.sh  # 覆盖 tag（需 bash，cmd/PowerShell 不认这种写法）
#   USE_OFFICIAL_IMAGES=1 bash scripts/deploy-chat.sh   # 云端/梯子环境：用官方 Docker Hub 基础镜像
#
# 与 api 的区别：chat 依赖 services/agent-core、services/agent-cooking 两个本地 Python 包
# （不在 PyPI），所以构建上下文必须是仓库根目录，用 -f 指定 Dockerfile。
#
# 前置: 先登录镜像仓库（密码是 TCR「访问凭证」固定密码，非登录密码）:
#   docker login ccr.ccs.tencentyun.com --username=100053273154
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

REGISTRY="${REGISTRY:-ccr.ccs.tencentyun.com}"
NAMESPACE="${NAMESPACE:-tcb-100053273154-byrm}"   # 云托管环境内置镜像仓库命名空间
# 云托管一服务一独立镜像仓库；名字必须用控制台给该服务 provision 的那条（别按 api 的命名规律推，
# 推错也能 push 成功、也会打印 digest，但控制台不认，服务就 Failed to pull image）
REPO="${REPO:-ca-eyxzseoz_po-chat}"
TAG="${TAG:-prod}"
PLATFORM="${PLATFORM:-linux/amd64}"               # 云托管只跑 amd64

if [[ "${USE_OFFICIAL_IMAGES:-0}" == "1" ]]; then
  RUNTIME_IMAGE="${RUNTIME_IMAGE:-python:3.11-slim}"
else
  RUNTIME_IMAGE="${RUNTIME_IMAGE:-docker.m.daocloud.io/library/python:3.11-slim}"
fi

IMAGE="$REGISTRY/$NAMESPACE/$REPO:$TAG"

echo ">> 构建镜像: $IMAGE"
echo "   RUNTIME_IMAGE=$RUNTIME_IMAGE"
echo "   构建上下文=$ROOT_DIR"
docker build \
  --platform="$PLATFORM" \
  --build-arg RUNTIME_IMAGE="$RUNTIME_IMAGE" \
  -f "$ROOT_DIR/services/chat/Dockerfile" \
  -t "$IMAGE" \
  "$ROOT_DIR"

echo ">> 推送镜像: $IMAGE"
docker push "$IMAGE"

# push 返回 0 不代表 tag 真的落库（多架构残缺 index 就是这么骗过人的），推完自证一次
if ! docker manifest inspect "$IMAGE" >/dev/null 2>&1; then
  echo "!! registry 里仍解析不到 $IMAGE（多半是 docker login 过期，用 TCR 固定密码重登）" >&2
  exit 1
fi
echo ">> 已验证 tag 可解析: $IMAGE"

echo ">> 完成。云托管『从镜像部署』填写:"
echo "   镜像地址: $IMAGE"
echo "   监听端口: 5090   健康检查: /api/health"
echo "   环境变量: 见 services/chat/deploy-prod.json"
echo "   详见 services/chat/DEPLOY_CLOUDRUN.md"
