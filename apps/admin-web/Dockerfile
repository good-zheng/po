# 管理后台（apps/admin-web，Umi Max + Ant Design Pro SPA）镜像：Node 构建产物 + Nginx 静态宿主与
# /api、/ws/chat 反代。
#
# 构建上下文必须是仓库根（admin-web 在 pnpm workspace 里，依赖 @po/types）：
#   docker build -f apps/admin-web/Dockerfile .
# 日常走 pnpm admin:deploy（scripts/deploy-admin.sh）。
#
# 不要加 `# syntax=docker/dockerfile:1`：BuildKit 会去 Docker Hub 拉前端镜像，本地网络下必然失败
# （services/api、chat、novel 镜像同一条教训）。以前这份 Dockerfile 的第一行就是它。
#
# 也不再依赖 docker-compose 挂载 infra/nginx/nginx.conf：容器自带 nginx 配置模板，
# 可以独立部署到云托管，compose 网关那条路不受影响。

# ==================== 构建阶段：pnpm workspace + Umi Max ====================
# 基础镜像默认走国内加速（Docker Hub 本地直连不通）；云端/有代理时 --build-arg 覆盖回官方镜像。
ARG BUILD_IMAGE=docker.m.daocloud.io/library/node:22-alpine
ARG RUNTIME_IMAGE=docker.m.daocloud.io/library/nginx:stable-alpine
# npm 源覆盖（默认官方源；境内拉包慢/超时可传 https://registry.npmmirror.com）
ARG NPM_REGISTRY=

FROM ${BUILD_IMAGE} AS build

# `--build-arg` 传进来的全局 ARG 只对 FROM 行可见，stage 内要用必须在这里重新声明；
# 漏了这一行，下面 `${NPM_REGISTRY}` 就是空串，换源开关会静默失效（apps/brand/Dockerfile 就漏了）。
ARG NPM_REGISTRY=

WORKDIR /repo

# husky 的 git hooks 与 CI 标记：镜像里不需要装 hooks
ENV HUSKY=0 \
    CI=1 \
    COREPACK_ENABLE_DOWNLOAD_PROMPT=0

# 仓库根 package.json 的 packageManager 字段决定 pnpm 版本
RUN corepack enable

# 先只拷清单装依赖，利用层缓存；pnpm-workspace.yaml 的 apps/* 通配匹配不到缺失目录是允许的，
# --frozen-lockfile 只校验被选中的这批 importer。
# 换源只需 pnpm config set registry：lockfile v9 里不存 tarball 主机，包体地址按当前 registry 拼。
COPY pnpm-workspace.yaml pnpm-lock.yaml package.json .npmrc ./
COPY packages/types/package.json packages/types/
COPY apps/admin-web/package.json apps/admin-web/
RUN if [ -n "${NPM_REGISTRY}" ]; then pnpm config set registry "${NPM_REGISTRY}"; fi \
    && pnpm install --frozen-lockfile --filter @po/admin...

COPY packages/types packages/types
COPY apps/admin-web apps/admin-web

# 先清掉上下文里可能带进来的本机 dist/：Umi 只删自己 manifest 认识的文件，上一次构建或半途中断
# 留下的残件（本仓库就出现过没有 index.html 的 dist/）会跨进新 dist，把残缺产物推上线。
#
# 接口域名在构建期决定：src/app.tsx 生产分支取 process.env.UMI_APP_API_BASE_URL（来自 apps/admin-web/.env
# 这份生产档，.env.local 既被 gitignore 也被 .dockerignore 拦在上下文外），值是烘进 JS 产物的常量，
# 改域名必须重新构建镜像。留空则产物走同源，由下一阶段的 Nginx 反代兜住。
RUN rm -rf apps/admin-web/dist \
    && pnpm --filter @po/types build \
    && pnpm --filter @po/admin build

# 构建期自证：产物残缺的镜像推上去也是白屏，别让它出门。
# 标题来自 config.ts 的 title；不校验 chunk 文件名是因为 utoopack 的命名带模块路径哈希，比 webpack 脆。
RUN test -f apps/admin-web/dist/index.html \
    && grep -q 'GoodZheng Po' apps/admin-web/dist/index.html \
    && ls apps/admin-web/dist/umi*.js >/dev/null \
    && echo "admin-web dist smoke ok"

# 域名自证：产物里必须烘进 .env 的生产值，且不存在任何指向本机的 baseURL。
# 漏了这一条，「线上前端指向开发机」这种事故会在 push 成功、页面正常打开的情况下静默发生
# （本机 pnpm admin:build 一定带 .env.local 的开发地址，残件混进上下文就是这个形状）。
# .env 里留空（同源模式）时正向断言自动跳过，只保留负向断言。
# 第三条断言管拼接口径：src/services/*.ts 的路径本身已含 /api，域名值再带 /api 结尾就是
# /api/api/books —— 本仓库 admin 与 novel 两家的 .env 都写过这种值，全站列表与登录一起 404。
# 五条实测教训，改动这段前先读完：
#   ① 别在 RUN 的双引号串里写 \" 拼内层引号 —— Dockerfile 解析层吃掉反斜杠，grep 拿到的是不含
#      引号的模式，`baseURL:"..."` 这种字面形态永远匹配不上，断言假失败。所以正向只匹配域名本身。
#   ② alpine 里的 grep 是 BusyBox 的，不认 --include（unrecognized option，退出码 2）。
#   ③ 用 dist/*.js 的 glob 而不是 -r，且天然跳过 *.js.map（`*.js` 不匹配 `.js.map` 结尾）。
#      glob 只覆盖顶层：utoopack 的资产都落在 dist 根下，将来若改成嵌套输出要跟着调整，
#      否则会退化成「正向断言查不到文件而失败」，不会静默放过。
#   ④ 读 .env 一定要 tr -d '\r'：本仓库 core.autocrlf=true，Windows 上 checkout 出来的 .env 是
#      CRLF，sed 取到的值末尾带 CR，拿去 grep 永远不命中 —— 实测这样误报过「产物里没有生产域名」。
#   ⑤ 断言连续失败时先怀疑取到的值，不要先怀疑产物：`printf '%s' "$api" | od -An -c` 一行命令
#      就能看见不可见字符，比对着 dist 反复 grep 快得多。
RUN api="$(sed -n 's/^UMI_APP_API_BASE_URL=//p' apps/admin-web/.env | tr -d '\r' | tail -1)" \
    && if [ -n "${api}" ]; then \
         grep -qF -- "${api}" apps/admin-web/dist/*.js \
           || { echo "!! 产物里找不到 .env 的生产域名 ${api}，检查 .env 是否进了构建上下文" >&2; exit 1; }; \
       fi \
    && doubled="$(grep -ho 'baseURL:"[^"]*"' apps/admin-web/dist/*.js | grep -c '/api"$' || true)" \
    && if [ "${doubled:-0}" != "0" ]; then \
         echo "!! 产物里的 baseURL 以 /api 结尾，而 src/services 的路径已带 /api 前缀，请求会打成 /api/api/**；把 .env 改成域名结尾" >&2; \
         exit 1; \
       fi \
    && leak="$(grep -lE 'baseURL:"https?://(127\.0\.0\.1|localhost)' apps/admin-web/dist/*.js || true)" \
    && if [ -n "${leak}" ]; then \
         echo "!! 产物里烘进了本机 baseURL: ${leak}，检查 .env.local 是否漏进构建上下文" >&2; \
         exit 1; \
       fi \
    && echo "admin-web baseURL smoke ok (${api:-同源模式})"

# ==================== 运行阶段：Nginx 静态 + /api、/ws/chat 反代 ====================
FROM ${RUNTIME_IMAGE} AS deploy

# 模板而不是硬编码 conf：官方镜像的 docker-entrypoint.sh 会用 envsubst 把
# /etc/nginx/templates/*.template 渲染到 /etc/nginx/conf.d/，所以后端域名可以在控制台
# 改环境变量后直接重启，不用重新构建镜像。
# 上游主机名不能写死在 proxy_pass 里（nginx 启动即解析，解析不到就退出），所以多挂一个
# .envsh：它排在 20-envsubst 之前，把归一化后的两个上游与容器自己的 DNS 导出成环境变量。
# .envsh 必须带执行位，否则 entrypoint 只打一句「Ignoring ... not executable」就跳过。
COPY apps/admin-web/nginx/admin.conf.template /etc/nginx/templates/admin.conf.template
COPY apps/admin-web/nginx/16-admin-upstreams.envsh /docker-entrypoint.d/16-admin-upstreams.envsh
RUN chmod 755 /docker-entrypoint.d/16-admin-upstreams.envsh \
    && rm -f /etc/nginx/conf.d/default.conf

COPY --from=build /repo/apps/admin-web/dist /usr/share/nginx/html

# utoopack 生产构建照样产出 .js.map，本仓库实测占 dist 的 43%（198MB → 112MB）。
# 管理端源码没有对外发布的需要，浏览器 DevTools 少一个 sourceMappingURL 跳转不影响使用。
RUN find /usr/share/nginx/html -name '*.map' -delete

# 默认留空＝两条反代都不指向任何后端（16-admin-upstreams.envsh 会各填一个永不解析的名字并打 WARN），
# 容器仍然起得来、静态页与 /healthz 正常，症状从「创建版本失败」降级成一眼可辨的 502。
# 管理端必须填这两个变量才有可用的 /api 与 /ws/chat：值取自控制台各服务的「内网访问域名」host:port，
# compose 里则填服务名（api:8080 / chat:5090）。
ENV ADMIN_API_UPSTREAM= \
    ADMIN_CHAT_UPSTREAM=

EXPOSE 8080
