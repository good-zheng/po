---
name: goodzheng-frontend-dev
description: 为 po monorepo 的 React 前端任务选择本地约定和按需开源参考。用于 apps/admin-web 的 Ant Design Pro、Umi Max、组件重构、页面、表格、路由、状态、国际化与 API 对接。
---

# Po 前端路由

## 先定位应用

| 目标目录 | 技术栈 | 默认策略 |
| --- | --- | --- |
| `apps/admin-web/` | Umi Max 4、React 19、Ant Design 6、Ant Design Pro 组件、React Query 5、Tailwind 4、Vitest、Biome | Ant Design 任务按需读取 antd skill |

本 skill 仅覆盖管理端；`apps/cooking-app/` 与 `apps/cooking-mini/`（Taro 微信小程序）由 `../mobile-dev/SKILL.md` 处理。管理端不得引入 shadcn/ui、TanStack Router 等第二套组件与路由体系；新页面优先复用 Pro 组件与现有页面模式。

## 二级披露路由

| 用户任务或代码信号 | 读取内容 |
| --- | --- |
| 新增、调试、迁移 Ant Design 组件；`antd` import；组件 props、token、语义样式 | `../../skill-sources/ant-design-cli/skills/antd/SKILL.md` |
| React 组件出现布尔 props 膨胀、compound components、render props、Context Provider 或可复用组件 API 设计 | `../../skill-sources/vercel-agent-skills/skills/composition-patterns/SKILL.md`，再只读命中的 `rules/*.md`（跳过 `_template.md` 与 `_sections.md`） |
| React Query 服务端状态、缓存失效、mutation | 以本仓库同类页面现有用法为准，不读取上游 skill |
| Umi 路由、布局、代理、插件配置 | 直接读 `config/`（config.ts、routes.ts、proxy.ts、defaultSettings.ts），不读取上游 skill |

单一任务最多读取一个上游 skill。只有 Ant Design 组件重构同时涉及组件 API 设计时，才可同时读取两个。

## 本地硬约束

- Ant Design CLI 本地执行：在 `apps/admin-web/` 内运行 `pnpm exec antd ... --format json`（`@ant-design/cli` 已在 devDependencies）；不要全局安装。
- 后端地址配置走 `apps/admin-web/.env`（`UMI_APP_API_BASE_URL` 指向 Spring Boot 8080、`UMI_APP_WS_BASE_URL` 指向 FastAPI 5090），由 `config/proxy.ts` 读取；Umi 只加载本目录 `.env`，不读 monorepo 根目录 `.env`（那份只属于 docker compose）。改 `.env` 必须重启 dev server 才生效。
- 开发与构建走 workspace 脚本：仓库根 `pnpm admin:dev` / `pnpm admin:build`（均先执行 `pnpm types:build`），静态检查 `pnpm admin:typecheck` / `pnpm admin:lint` / `pnpm admin:test`；类型契约在 `packages/types/`，前后端字段变更先改类型包。
- 同时修改中英文界面文案时，同步更新 `src/locales/zh-CN.ts` 与 `src/locales/en-US.ts`（Umi locale 插件的 TS 模块，不是 JSON 文件）。
- 修改前读取目标模块的 `package.json` 和同类功能文件，用既有 Biome / Vitest 脚本验证。
