# 介绍站（Astro 静态站）镜像。
#
# 构建上下文必须是仓库根：brand 已经并入 pnpm workspace，`--frozen-lockfile` 要看到
# 所有 importer 的 package.json，只拷 apps/brand 会直接报 lockfile 不匹配。
#   docker build -f apps/brand/Dockerfile --build-arg SITE_URL=https://真实域名 .
# 日常走 pnpm brand:deploy（scripts/deploy-brand.sh）。
#
# 不要加 `# syntax=docker/dockerfile:1`：BuildKit 会去 Docker Hub 拉前端镜像，本地网络下必然失败。
ARG BUILD_IMAGE=docker.m.daocloud.io/library/node:22-alpine
ARG RUNTIME_IMAGE=docker.m.daocloud.io/library/nginx:stable-alpine
# 站点绝对域名。Astro 是构建期产物，sitemap.xml / RSS / Open Graph / canonical 里的绝对链接
# 在这里烘死，换域名必须重新构建镜像。留空则沿用 apps/brand/src/config.yaml 里的值。
ARG SITE_URL=
# npm 源覆盖（默认官方源；境内拉包慢时可传 https://registry.npmmirror.com）
ARG NPM_REGISTRY=

FROM ${BUILD_IMAGE} AS build

WORKDIR /repo

# husky 的 git hooks 与 CI 标记：镜像里不需要装 hooks
ENV HUSKY=0 \
    CI=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

COPY . .

RUN corepack enable \
    && if [ -n "${NPM_REGISTRY}" ]; then pnpm config set registry "${NPM_REGISTRY}"; fi \
    && pnpm install --frozen-lockfile --filter @po/brand

# 把 SITE_URL 写进 src/config.yaml 的 site.site（只改缩进两格的 site: 键）
RUN if [ -n "${SITE_URL}" ]; then \
      sed -i "s|^  site: .*|  site: '${SITE_URL}'|" apps/brand/src/config.yaml; \
      grep -q "site: '${SITE_URL}'" apps/brand/src/config.yaml; \
    fi

RUN pnpm --filter @po/brand build

# 构建期自证：产物残缺的镜像推上去也是 404，别让它出门
RUN test -f apps/brand/dist/index.html \
    && test -f apps/brand/dist/404.html \
    && test -f apps/brand/dist/sitemap-index.xml \
    && test -f apps/brand/dist/rss.xml \
    && grep -q '<html' apps/brand/dist/index.html \
    && echo "brand dist smoke ok"

FROM ${RUNTIME_IMAGE} AS deploy

COPY apps/brand/nginx/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /repo/apps/brand/dist /usr/share/nginx/html

EXPOSE 8080
