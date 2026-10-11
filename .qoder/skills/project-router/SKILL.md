---
name: goodzheng-project-router
description: 为 po monorepo 的跨端或需求不明确任务选择管理端、阅读端、Expo/微信小程序端、Spring Boot 或 Python 工作流。用于全栈功能、跨服务联调与模块归属判定；不用于已明确的单一领域代码任务。
---

# Po 项目调度器

## 领域分流

1. 涉及 `apps/admin-web/`、`apps/novel-web/`、React、Umi、Ant Design、页面、路由、表格或状态管理时，读取 `../frontend-dev/SKILL.md`（两个 app 同为 Umi Max 4 + React 19 + antd 6；阅读端没有 ProLayout、没有 locale、没有 Vitest，别把管理端模式硬搬过去）。
2. 涉及 `apps/cooking-app/`、Expo、React Native、expo-router、NativeWind、移动端页面或 APK 构建时，读取 `../mobile-dev/SKILL.md`。
3. 涉及 `apps/cooking-mini/`、`apps/echo-talk/`、Taro、微信小程序、`pnpm mini:*`、`pnpm echo:*` 或微信开发者工具时，同样读取 `../mobile-dev/SKILL.md`（其「微信小程序」章节含 WXSS 限制、登录 gating、合法域名约定；两个小程序都是个人主体，AI 类目不能上）。
4. 涉及 `services/api/`、Java、Spring Boot、Controller、Service、数据库、JWT 或 Redis 时，读取 `../java-dev/SKILL.md`。
5. 涉及 `services/chat/`、`services/agent-core|agent-cooking|agent-talk|agent-novel/`、Python、FastAPI、WebSocket、流式聊天、垂直 Agent 插槽或 AI 对话（Flask/LangGraph 仅作迁移历史信号）时，读取 `../python-dev/SKILL.md`。chat 是宿主、四个 agent-* 是无端口库包，改协议时两边同看。
6. 涉及 `apps/brand/`、Astro、AstroWind、widget 文案、开发手记文章或 `pnpm brand:*` 时，不读取任何上游 skill，直接读 `apps/brand/README.md`（来源与占位约定）和 `apps/brand/AGENTS.md`（模板自带的验证清单）；镜像与上线任务再读 `apps/brand/DEPLOY_CLOUDRUN.md`。该应用是静态介绍站，与管理端/移动端不共享组件与路由体系，不得引入 React/Ant Design 或 shadcn/ui。
7. 跨端契约类型（请求/响应 DTO）统一维护在 `packages/types/`（`@po/types`）；字段变更先更新类型包与 API 契约，再更新管理端或移动端调用。
8. 跨端任务按「Java API 契约 → Python 服务契约（如涉及）→ 管理端或移动端调用」顺序读取对应领域 skill；只加载当前步骤需要的上游参考。

## 渐进式披露规则

- 此 skill 只负责领域判定，不加载任何开源框架 skill。
- 领域 skill 只加载一个最匹配的上游 skill；单一问题不要全量读取来源目录。
- 上游 skill 位于 `.qoder/skill-sources/`，为只读镜像（由 `.qoder/scripts/sync-skill-sources.ps1` 按 pinned commit 同步，勿手改）；项目适配规则始终以 `.qoder/skills/` 为准。
- 若用户已给出模块或文件路径，跳过本调度器，直接命中对应领域 skill。

## 上游镜像的当前状态

`.qoder/skill-sources/` 下四份只读镜像（antd、composition-patterns、spring-boot-4、fastapi）**已在本工作副本中就位**（2026-10-12 按 pinned commit 重建），四条领域 skill 里指向它们的相对路径都可读。

一个容易踩的存储形态：这四个目录在 git 里是 mode `160000` 的 gitlink（只存 commit，不存内容），而仓库根**没有 `.gitmodules`**。于是 `git checkout`、`git restore`、`git submodule update --init` 都拿不回文件内容——看着"HEAD 里有"其实只有 commit 指针。目录被删空时（新克隆、换机器、误清理）恢复方式是这两个普通文件仍在仓库里，取回后重跑同步脚本：

```bash
git checkout HEAD -- .qoder/scripts .qoder/skill-sources/manifest.json
powershell -ExecutionPolicy Bypass -File .qoder/scripts/sync-skill-sources.ps1
```

脚本按 manifest 里 pinned 的 commit 做 `--filter=blob:none` + `sparse-checkout` 重建四个目录，幂等，且只检出各自的 `skills/*` 子目录（三条另带 `LICENSE`）；需要能访问 GitHub。

镜像缺失时不阻塞任务：领域 skill 的「本地硬约束」和每个模块的 `README.md` 已经是完整可执行的口径，读不到上游就按本地走，并在交付说明里写明「未读上游」。反过来说，也不要因为某个规范「上游 skill 里好像提过」就去磁盘上翻找目录——先读本地同类代码。

## 本地拓扑速查

- 管理端：`pnpm admin:dev` 启动 Umi 8000（`/api`、`/ws` 代理到本地后端）；后端地址在 `apps/admin-web/.env` 配置。
- 移动端：`pnpm mobile:start` 启动 Expo；API 地址在 `apps/cooking-app/.env` 的 `EXPO_PUBLIC_API_URL` 配置。Android 模拟器使用 `10.0.2.2`，真机使用开发机局域网地址。
- 微信小程序：`pnpm mini:dev` / `pnpm mini:build`（Taro weapp）；接口地址走 `apps/cooking-mini/.env.development|.env.production`，产物在 `dist/`，用微信开发者工具导入 `apps/cooking-mini` 目录。言外是同一套 Taro 结构的第二个小程序：`pnpm echo:dev` / `echo:build`，除 HTTP 与聊天 WS 外还多一条 ASR WS（`TARO_APP_ASR_WS_URL`），三个地址都写开发机局域网 IP 而不是 `127.0.0.1`；它**没有 CI job**，改完必须手工 `pnpm echo:build`。两个小程序都是个人主体，不能带大模型类目：cooking-mini 的 AI 页已经是本地意图解析 + 只读菜谱接口，不连 `/ws/chat`。
- 阅读端：`pnpm novel:dev`（`MOCK=none` 读真库）/ `novel:mock` / `novel:build` / `novel:preview`（8001）；与管理端同为 Umi Max 但独立 app、独立 Dockerfile 与部署脚本（`pnpm novel:deploy`）。契约与页面对齐 `apps/novel-web/README.md`。
- API 与聊天：`pnpm api:start` 在 `services/api` reactor 内以 `-pl api-bootstrap -am spring-boot:run` 构建依赖模块并启动 Spring Boot 8080（脚本自动定位 JDK 17，无需终端配置 `JAVA_HOME`；模块改动后也无需先 `pnpm api:install`）；`pnpm chat:start` 启动 FastAPI 5090。部署走 `pnpm api:deploy` / `chat:deploy` / `redis:deploy`（Node 包装器 `scripts/run-sh.mjs` 定位 Git Bash，规避 Windows WSL bash 存根）。
- 介绍站：`pnpm brand:dev` / `brand:build` / `brand:preview` / `brand:check`（Astro 7 + AstroWind，端口 4321）；上线 `pnpm brand:deploy`（Docker 镜像推微信云托管内置仓库，见 `apps/brand/DEPLOY_CLOUDRUN.md`）。站点文案与文章全部在 `apps/brand/src/` 内，`src/config.yaml` 的 `site.site` 是待替换占位，不要填入猜测域名；需要临时指定域名时用 `SITE_URL=... pnpm brand:deploy`，不改仓库文件。
- 部署模式：`docker compose up -d` 由 Nginx 网关统一分流（`${WEB_PORT:-8000}` 对外，`/api` 大部分给 Spring Boot，`/api/health`、`/api/items`、`/ws/chat` 给 FastAPI），仅 `web` 暴露宿主机端口。
- 知识库：站点本体是 gitignore 的上游副本 `apps/power-wiki/`（无 `.git`，重解压即丢，**不要直接改它自带的 README**），起服务 `pnpm wiki:site`（nodemon `wiki:site:dev`，装依赖 `wiki:site:install`，端口 `PORT` > `config.json.port`（本机 80）> 3150）；内容发布走 `pnpm wiki:sync` 与 `/wiki-capture`，归属规则与「上游 README 里不要照做的几处」见 `scripts/WIKI_SYNC.md`。镜像 Skill 的计划任务 `goodzheng-wiki-sync` 当前 Disabled，不会自动上站。
