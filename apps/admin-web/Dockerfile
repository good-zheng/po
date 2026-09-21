# syntax=docker/dockerfile:1
# ==================== 构建阶段：pnpm workspace + Umi Max ====================
# 构建上下文必须是仓库根目录：
#   docker build -f apps/admin-web/Dockerfile .
FROM node:22-alpine AS build

RUN corepack enable
# 仓库根 package.json 的 packageManager 字段决定 pnpm 版本
ENV HUSKY=0
WORKDIR /repo

# 先装依赖（仅 @po/admin 及其 workspace 依赖 @po/types），利用层缓存
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json .npmrc ./
COPY packages/types/package.json packages/types/
COPY apps/admin-web/package.json apps/admin-web/
RUN pnpm install --frozen-lockfile --filter @po/admin...

# 生产构建：baseURL 为空（同源），由 Nginx 网关统一分流
COPY packages/types packages/types
COPY apps/admin-web apps/admin-web
RUN pnpm --filter @po/types build && pnpm --filter @po/admin build

# ==================== 运行阶段：Nginx 网关 ====================
FROM nginx:1.27-alpine

# 静态前端；路由分流规则由 docker-compose 挂载 infra/nginx/nginx.conf 提供
COPY --from=build /repo/apps/admin-web/dist /usr/share/nginx/html
