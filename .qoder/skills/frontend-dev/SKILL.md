---
name: goodzheng-frontend-dev
description: 为 po monorepo 的 React 前端任务选择本地约定和按需开源参考。用于 apps/admin-web 与 apps/novel-web 的 Ant Design Pro、Umi Max、组件重构、页面、表格、路由、状态、国际化与 API 对接。
---

# Po 前端路由

## 先定位应用

| 目标目录 | 技术栈 | 默认策略 |
| --- | --- | --- |
| `apps/admin-web/` | Umi Max 4、React 19、Ant Design 6、Ant Design Pro 组件、React Query 5、Tailwind 4、Vitest、Biome | Ant Design 任务按需读取 antd skill；镜像部署见 `apps/admin-web/DEPLOY_CLOUDRUN.md` |
| `apps/novel-web/` | Umi Max 4、React 19、Ant Design 6（无 ProLayout、无 locale、无 Vitest），阅读端 | 同上；约定与部署见 `apps/novel-web/README.md`、`DEPLOY_CLOUDRUN.md` |

本 skill 覆盖两个 Umi 应用；`apps/cooking-app/` 与 `apps/cooking-mini/`、`apps/echo-talk/`（Taro 微信小程序）由 `../mobile-dev/SKILL.md` 处理。管理端不得引入 shadcn/ui、TanStack Router 等第二套组件与路由体系；新页面优先复用 Pro 组件与现有页面模式。

## 二级披露路由

| 用户任务或代码信号 | 读取内容 |
| --- | --- |
| 新增、调试、迁移 Ant Design 组件；`antd` import；组件 props、token、语义样式 | `../../skill-sources/ant-design-cli/skills/antd/SKILL.md`，并用本地 CLI 交叉验证（见本地硬约束） |
| React 组件出现布尔 props 膨胀、compound components、render props、Context Provider 或可复用组件 API 设计 | `../../skill-sources/vercel-agent-skills/skills/composition-patterns/SKILL.md`，再只读命中的 `rules/*.md`（跳过 `_template.md` 与 `_sections.md`） |
| React Query 服务端状态、缓存失效、mutation | 以本仓库同类页面现有用法为准，不读取上游 skill |
| Umi 路由、布局、代理、插件配置 | 直接读 `config/`（config.ts、routes.ts、proxy.ts、defaultSettings.ts），不读取上游 skill |

单一任务最多读取一个上游 skill。只有 Ant Design 组件重构同时涉及组件 API 设计时，才可同时读取两个。

## 上游镜像读不到时

`../../skill-sources/...` 是 git 里的 gitlink（无 `.gitmodules`），目录被清空后 `git checkout` 取不回来，恢复方式见 `../project-router/SKILL.md` 的「上游镜像的当前状态」。镜像缺失**不阻塞任务**：改以「本仓库同类代码（`apps/admin-web/src/pages/**`、两个 app 的 `src/components/`）+ `pnpm exec antd --format json` + 各自 `README.md`」为准，并在交付说明里写明未读上游。

## 本地硬约束

- Ant Design CLI 本地执行：在 `apps/admin-web/` 内运行 `pnpm exec antd ... --format json`（`@ant-design/cli` 已在 devDependencies）；不要全局安装。
- 后端地址配置走 `apps/admin-web/.env` 两档（见下条），由 `src/app.tsx` 的 `baseURL`（仅 `NODE_ENV=production`）和 `config/proxy.ts`（dev）读取；Umi 只加载本目录 env 文件，不读 monorepo 根目录 `.env`（那份只属于 docker compose）。改 env 文件必须重启 dev server 才生效。
- Umi 4.7 只加载 `.env` 与 `.env.local` 两档（`@umijs/core/dist/service/env.js` 写死，**没有 `.env.production`/`.env.development`**），且后读的 `.env.local` 无条件覆盖。`apps/admin-web` 与 `apps/novel-web` 据此统一为：`.env` = 生产域名（入库、进 docker 上下文、`max build` 内联进 JS 产物），`.env.local` = 本机开发覆盖（不入库不进镜像，模板 `.env.example`）。别在这两个 app 里新建 `.env.production`，那是死配置。因此新克隆必须先 `cp .env.example .env.local`，否则 dev 代理的目标会取到 `.env` 的线上域名。`UMI_APP_API_BASE_URL` 的值不带 `/api` 结尾（请求路径本身已含前缀）。
- 线上镜像：两个 app 各有独立 Dockerfile + nginx 模板 + 部署脚本（`pnpm admin:deploy` / `pnpm novel:deploy`，仓库名 `admin` / `ca-eyxzseoz_novel`），约定见 `apps/admin-web/DEPLOY_CLOUDRUN.md`、`apps/novel-web/DEPLOY_CLOUDRUN.md`。两类后端地址分开：前端调用的 API 域名是构建期常量（改它要重打镜像），容器反代的后端是运行时变量（`ADMIN_API_UPSTREAM` / `ADMIN_CHAT_UPSTREAM` / `NOVEL_API_UPSTREAM`，改完重启即可）。管理端的 WS 永远同源（`src/pages/chatbot/service.ts` 用 `window.location.host`），没有对应的构建期域名变量。
- 开发与构建走 workspace 脚本：仓库根 `pnpm admin:dev` / `pnpm admin:build`（均先执行 `pnpm types:build`），静态检查 `pnpm admin:typecheck` / `pnpm admin:lint` / `pnpm admin:test`；类型契约在 `packages/types/`，前后端字段变更先改类型包。
- **CI 只跑管理端**：`.github/workflows/ci.yml` 的 `frontend` job 是 `admin:lint` + `admin:test` + `admin:build`，`mini` job 只编 cooking-mini，novel-web 与 echo-talk 都**没有对应 job**。改这两个 app 时绿钩子不代表没坏，收尾必须自己跑 `pnpm novel:lint`、`pnpm novel:typecheck`、`pnpm novel:build`（或 `pnpm echo:build`）。
- 同时修改中英文界面文案时，同步更新 `src/locales/zh-CN.ts` 与 `src/locales/en-US.ts`（Umi locale 插件的 TS 模块，不是 JSON 文件）。
- 修改前读取目标模块的 `package.json` 和同类功能文件，用既有 Biome / Vitest 脚本验证。
