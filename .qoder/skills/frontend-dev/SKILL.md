---
name: goodzheng-frontend-dev
description: 为 goodzheng-pro 的 React 前端任务选择本地约定和按需开源参考。用于 po-admin 的 Ant Design Pro、shadcn-admin 的 TanStack Router、组件重构、页面、表格、路由、状态、国际化与 API 对接。
---

# Goodzheng 前端路由

## 先定位应用

| 目标目录 | 技术栈 | 默认策略 |
| --- | --- | --- |
| `web_client/po-admin/` | Umi Max、React 19、Ant Design 6、Ant Design Pro | Ant Design 任务按需读取 antd skill |
| `web_client/shadcn-admin/` | Vite、React 19、TanStack Router/Table、shadcn/ui、Tailwind | 以项目现有模式为准，不默认加载 Ant Design skill |

不得将 Ant Design 组件或 Umi 约定引入 `shadcn-admin`，也不得将 shadcn/Tailwind 组件模式迁入 `po-admin`。

## 二级披露路由

| 用户任务或代码信号 | 读取内容 |
| --- | --- |
| `po-admin` 中新增、调试、迁移 Ant Design 组件；`antd` import；组件 props、token、语义样式 | `../../skill-sources/ant-design-cli/skills/antd/SKILL.md` |
| React 组件出现布尔 props 膨胀、compound components、render props、Context Provider 或可复用组件 API 设计 | `../../skill-sources/vercel-agent-skills/skills/composition-patterns/SKILL.md`，再只读命中的 `rules/*.md`（跳过 `_template.md` 与 `_sections.md`） |
| `shadcn-admin` 的页面、TanStack Router/Table、React Query、Zustand、i18n 或 API 对接 | 不读取上游 skill；先从同功能模块与共享组件提炼现有模式 |

单一任务最多读取一个上游 skill。只有 Ant Design 组件重构同时涉及组件 API 设计时，才可同时读取两个。

## 本地硬约束

- 在 `po-admin` 中优先使用本地 CLI：进入该目录后执行 `pnpm exec antd ... --format json`；不要为本项目全局安装 CLI。
- `shadcn-admin` 的服务端筛选中，`DataTableToolbar` 的 `searchKey` 是 TanStack Table 列 id；URL 参数名由 `useTableUrlState` 的映射配置负责。
- TanStack Router 路由参数必须在 `validateSearch` 中声明；React Query mutation 成功后失效对应 query。
- 同时修改中英文界面文案时，同步更新 `src/locales/zh.json` 与 `src/locales/en.json`，避免 JSON 重复 key。
- 修改前读取目标应用的 `package.json` 和同类功能文件，使用该应用已有的包管理、格式化与测试脚本。
