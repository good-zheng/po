# 言外书斋（apps/novel-web，Umi Max SPA）镜像：Node 构建产物 + Nginx 静态宿主与 /api 反代。
#
# 构建上下文必须是仓库根（novel-web 在 pnpm workspace 里，依赖 @po/types）：
#   docker build -f apps/novel-web/Dockerfile .
# 日常走 pnpm novel:deploy（scripts/deploy-novel.sh）。
#
# 不要加 `# syntax=docker/dockerfile:1`：BuildKit 会去 Docker Hub 拉前端镜像，本地网络下必然失败
# （ARG-before-FROM 内嵌解析器已支持，services/api 与 chat 镜像同一条教训）。

# ==================== 构建阶段：pnpm workspace + Umi Max ====================
# 基础镜像默认走国内加速（Docker Hub 本地直连不通）；云端/有代理时 --build-arg 覆盖回官方镜像。
ARG BUILD_IMAGE=docker.m.daocloud.io/library/node:22-alpine
ARG RUNTIME_IMAGE=docker.m.daocloud.io/library/nginx:stable-alpine
# npm 源覆盖（默认官方源；境内拉包慢/超时可传 https://registry.npmmirror.com）
ARG NPM_REGISTRY=

FROM ${BUILD_IMAGE} AS build

# `--build-arg` 传进来的全局 ARG 只对 FROM 行可见，stage 内要用必须在这里重新声明；
# 漏了这一行，下面 `${NPM_REGISTRY}` 就是空串，换源开关会静默失效（照抄 apps/brand/Dockerfile
# 的写法时尤其注意，它那份就漏了，所以它的 NPM_REGISTRY 一直是空转的）。
ARG NPM_REGISTRY=

WORKDIR /repo

# husky 的 git hooks 与 CI 标记：镜像里不需要装 hooks
ENV HUSKY=0 \
    CI=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

# 仓库根 package.json 的 packageManager 字段决定 pnpm 版本
RUN corepack enable

# 先只拷清单装依赖，利用层缓存；pnpm-workspace.yaml 的 apps/* 通配匹配不到缺失目录是允许的，
# --frozen-lockfile 只校验被选中的这批 importer（与 apps/admin-web/Dockerfile 同一套路）。
# 换源只需 pnpm config set registry：lockfile v9 里不存 tarball 主机，包体地址按当前 registry 拼。
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json .npmrc ./
COPY packages/types/package.json packages/types/
COPY apps/novel-web/package.json apps/novel-web/
RUN if [ -n "${NPM_REGISTRY}" ]; then pnpm config set registry "${NPM_REGISTRY}"; fi \
    && pnpm install --frozen-lockfile --filter @po/novel-web...

COPY packages/types packages/types
COPY apps/novel-web apps/novel-web

# 先清掉上下文里可能带进来的本机 dist/：Umi 只删自己 manifest 认识的文件，
# 手工放进 public/ 的东西（或上一次构建遗留）会跨进新 dist，把旧版本资源一起推上去。
# 生产构建：src/app.tsx 的生产分支取 process.env.UMI_APP_API_BASE_URL（来自 apps/novel-web/.env
# 这份生产档；.env.local 既被 gitignore 也被 .dockerignore 拦在上下文外），值是烘进 JS 产物的常量，
# 改域名必须重新构建镜像。留空则退化成同源 /api，由下一阶段的 Nginx 反代兜住。
RUN rm -rf apps/novel-web/dist \
    && pnpm --filter @po/types build \
    && pnpm --filter @po/novel-web build

# 构建期自证：产物残缺的镜像推上去也是白屏，别让它出门。
# 文件名带 contenthash，只能 glob 校验；标题来自 config.ts 的 title，能顺带证明编码与配置生效。
# baseURL 那一条管的是拼接口径：src/services/*.ts 的路径本身已带 /api 前缀，所以 .env 的值
# 必须以域名结尾——带 /api 结尾的写法会打出 https://.../api/api/books，全站列表与登录一起 404。
RUN test -f apps/novel-web/dist/index.html \
    && test -f apps/novel-web/dist/favicon.svg \
    && grep -q '<title>言外书斋</title>' apps/novel-web/dist/index.html \
    && baked="$(grep -ho 'baseURL:"[^"]*"' apps/novel-web/dist/umi.*.js | grep -c '/api"$' || true)" \
    && if [ "${baked:-0}" != "0" ]; then \
         echo "!! 产物里的 baseURL 以 /api 结尾，而 src/services 的路径已带 /api 前缀，请求会打成 /api/api/**；把 .env 改成域名结尾" >&2; \
         exit 1; \
       fi \
    && ls apps/novel-web/dist/umi.*.js >/dev/null \
    && ls apps/novel-web/dist/umi.*.css >/dev/null \
    && ls apps/novel-web/dist/p__bookshelf__index.*.async.js >/dev/null \
    && ls apps/novel-web/dist/p__book__index.*.async.js >/dev/null \
    && ls apps/novel-web/dist/p__read__index.*.async.js >/dev/null \
    && ls apps/novel-web/dist/p__user__login__index.*.async.js >/dev/null \
    && echo "novel-web dist smoke ok"

# ==================== 运行阶段：Nginx 静态 + /api 反代 ====================
FROM ${RUNTIME_IMAGE} AS deploy

# 模板而不是硬编码 conf：官方镜像的 docker-entrypoint.sh 会用 envsubst 把
# /etc/nginx/templates/*.template 渲染到 /etc/nginx/conf.d/，所以后端域名可以在控制台
# 改环境变量后直接重启，不用重新构建镜像。
# 上游主机名不能写死在 proxy_pass 里（nginx 启动即解析，解析不到就退出），所以多挂一个
# .envsh：它排在 20-envsubst 之前，把归一化后的上游与容器自己的 DNS 导出成环境变量。
# .envsh 必须带执行位，否则 entrypoint 只打一句「Ignoring ... not executable」就跳过，
# 模板里的 $NOVEL_API_UPSTREAM 会渲染成空串——那种形态下 nginx 依旧起得来，但 /api 全空。
COPY apps/novel-web/nginx/novel.conf.template /etc/nginx/templates/novel.conf.template
COPY apps/novel-web/nginx/16-novel-api.envsh /docker-entrypoint.d/16-novel-api.envsh
RUN chmod 755 /docker-entrypoint.d/16-novel-api.envsh \
    && rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /repo/apps/novel-web/dist /usr/share/nginx/html

# 默认留空＝不启用同源 /api 反代（16-novel-api.envsh 会填一个永不解析的名字并打一条 WARN）。
# 生产产物里 api 域名是烘进 JS 的（apps/novel-web/.env），浏览器并不走这条反代；
# 只有把那个值置空、要求走同源时，才需要在控制台/compose 里填 api 服务的内网访问域名 host:port。
ENV NOVEL_API_UPSTREAM=

EXPOSE 8080
