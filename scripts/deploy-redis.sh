#!/usr/bin/env bash
# 把 Redis Stack 镜像转推到微信云托管内置镜像仓库（云托管不能直接拉 Docker Hub）
#
# 为什么是 redis-stack-server 而不是 redis:7-alpine：
# langgraph-checkpoint-redis 的 saver（含 AsyncRedisSaver / AsyncShallowRedisSaver）
# 用 JSON.SET / JSON.GET 存 checkpoint、用 redisvl 的 SearchIndex 建 FT.SEARCH 索引，
# 这两个命令来自 RedisJSON 与 RediSearch 模块，普通 Redis 镜像里没有，
# setup() 会直接报 unknown command，chat 随即静默降级为 memory checkpointer。
#
# 用法:
#   pnpm redis:deploy                                  # 默认 redis-stack-server:latest
#   REDIS_VERSION=7.4.0-v3 bash scripts/deploy-redis.sh # 拉成功后按控制台显示的具体版本固定 tag
#
# 推完在云托管「新建服务」里选这个镜像，端口填 6379，启动命令留空，
# 用环境变量 REDIS_ARGS=--requirepass <密码> --appendonly yes 传参（官方文档指定方式）。
# 密码要与 chat 的 AGENT_CORE_REDIS_URL、api 的 SPRING_DATA_REDIS_PASSWORD 一致。
set -euo pipefail

REGISTRY="${REGISTRY:-ccr.ccs.tencentyun.com}"
NAMESPACE="${NAMESPACE:-tcb-100053273154-byrm}"
# 云托管「一服务一独立镜像仓库」，仓库名 = 环境ID_服务名；
# 名字必须在控制台建服务后取（不要自己编，push 能自动建仓库但控制台不认，服务就拉不到镜像）
REPO="${REPO:-ca-eyxzseoz_redis}"
TAG="${TAG:-prod}"
REDIS_VERSION="${REDIS_VERSION:-latest}"
PLATFORM="${PLATFORM:-linux/amd64}"   # 云托管只跑 amd64

if [[ "${USE_OFFICIAL_IMAGES:-0}" == "1" ]]; then
  UPSTREAM_IMAGE="${UPSTREAM_IMAGE:-redis/redis-stack-server:${REDIS_VERSION}}"
else
  UPSTREAM_IMAGE="${UPSTREAM_IMAGE:-docker.m.daocloud.io/redis/redis-stack-server:${REDIS_VERSION}}"
fi

IMAGE="$REGISTRY/$NAMESPACE/$REPO:$TAG"

# 这里不能用 pull + tag + push：上游是「多架构 manifest list」，本机只拉到 amd64 那一份内容，
# push 写出的是引用了缺失平台的残缺 index —— docker 只打印一句
# "Not all multiplatform-content is present" 的 warning 就返回 0，
# 但 registry 根本没落这个 tag，云托管表现为拉不到镜像、控制台也看不到。
# 用一层空壳 build 把 base 重导出成单架构 manifest，push 出去的 index 才完整。
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
printf 'ARG BASE\nFROM ${BASE}\n' > "$WORK/Dockerfile"

echo ">> 单架构转换: $UPSTREAM_IMAGE ($PLATFORM) -> $IMAGE"
docker build --platform="$PLATFORM" --build-arg BASE="$UPSTREAM_IMAGE" -t "$IMAGE" "$WORK"

echo ">> 推送镜像: $IMAGE"
docker push "$IMAGE"

# 推完自己验证一次，别让人去控制台猜镜像到底在不在
if ! docker manifest inspect "$IMAGE" >/dev/null 2>&1; then
  echo "!! registry 里仍解析不到 $IMAGE（多半是 docker login 过期，用 TCR 固定密码重登）" >&2
  exit 1
fi
echo ">> 已验证 tag 可解析: $IMAGE"

echo ">> 完成。云托管新建服务填写:"
echo "   镜像地址: $IMAGE"
echo "   监听端口: 6379（内网调用只会放通这个端口）"
echo "   公网访问: 关闭（只给环境内的 chat/api 用）"
