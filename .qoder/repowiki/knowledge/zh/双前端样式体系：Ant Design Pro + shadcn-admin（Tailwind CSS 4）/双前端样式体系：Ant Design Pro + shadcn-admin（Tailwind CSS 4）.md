---
kind: frontend_style
name: 双前端样式体系：Ant Design Pro + shadcn-admin（Tailwind CSS 4）
category: frontend_style
scope:
    - '**'
source_files:
    - web_client/po-admin/package.json
    - web_client/po-admin/config/defaultSettings.ts
    - web_client/po-admin/src/global.less
    - web_client/po-admin/tailwind.css
    - web_client/po-admin/tailwind.config.js
    - web_client/shadcn-admin/package.json
    - web_client/shadcn-admin/components.json
    - web_client/shadcn-admin/src/styles/theme.css
    - web_client/shadcn-admin/src/styles/index.css
    - web_client/shadcn-admin/vite.config.ts
    - web_client/shadcn-admin/src/components/ui/button.tsx
---

## 1. 整体方案

本项目包含两个独立的前端应用，分别采用不同的 UI 与样式体系：

- **po-admin**（管理后台）：基于 `@umijs/max` 脚手架的 Ant Design Pro 6.x，使用 Ant Design 组件库 + antd-style，辅以 Tailwind CSS 4 作为补充。
- **shadcn-admin**（新版管理后台/客户端）：基于 Vite + React + TanStack Router，使用 shadcn/ui（Radix primitives）+ Tailwind CSS 4，通过 CSS 变量实现主题切换。

后端 Java Spring Boot 在 `resources/static`、`resources/templates` 下留有静态资源目录但当前为空；Python FastAPI 服务不直接提供前端页面。因此本仓库的“前端样式”完全集中在 `web_client/` 下的两个子项目中。

## 2. 关键文件与包

| 子系统 | 关键文件 | 作用 |
|---|---|---|
| po-admin | `package.json` | 依赖 `antd`、`@ant-design/pro-components`、`antd-style`、`tailwindcss`、`@umijs/max` |
| po-admin | `config/defaultSettings.ts` | 通过 ProLayout 的 `navTheme`、`colorPrimary`、`token` 等配置全局主题 |
| po-admin | `src/global.less` | 全局字体（AlibabaSans）、基础 reset、移动端表格适配 |
| po-admin | `tailwind.css` / `tailwind.config.js` | 引入 Tailwind 4 并扫描 `./src/**/*.tsx` |
| shadcn-admin | `components.json` | shadcn 配置：style=`new-york`、baseColor=`slate`、CSS Variables 开启、iconLibrary=`lucide` |
| shadcn-admin | `src/styles/theme.css` | 定义 light/dark 两套 OKLCH 色板及 `--radius`、sidebar 等设计令牌 |
| shadcn-admin | `src/styles/index.css` | 导入 Tailwind 4、tw-animate-css、theme.css，定义 base/utility 层 |
| shadcn-admin | `vite.config.ts` | 启用 `@tailwindcss/vite` 插件，别名 `@` → `src` |
| shadcn-admin | `src/components/ui/*.tsx` | Radix 原子组件封装，使用 `class-variance-authority` + `clsx` + `cn` 组合 className |

## 3. 架构与设计约定

### 3.1 po-admin（Ant Design Pro）
- **框架**：UmiJS Max 4 + React 19，构建产物由 `max build` 生成。
- **主题系统**：通过 `config/defaultSettings.ts` 中的 `ProLayoutProps` 设置 `navTheme: 'light'`、`colorPrimary: '#1677ff'`、`layout: 'mix'`、`contentWidth: 'Fluid'` 等；支持通过 `token` 字段覆盖 antd design token。
- **全局样式**：`src/global.less` 中声明 AlibabaSans 字重 300–700 的 `@font-face`，并通过 `.colorWeak` 类提供色弱模式；针对 `<768px` 的媒体查询为 `ant-table` 添加横向滚动与换行。
- **Tailwind 角色**：仅作为辅助，`tailwind.config.js` 的 `content` 指向 `./src/**/*.tsx`，`tailwind.css` 引入 Tailwind 4 入口。
- **组件样式**：业务组件位于 `src/pages/**`，通用 UI 组件位于 `src/components/**`，部分组件自带 `*.style.ts`（如 `ArticleListContent/index.style.ts`），遵循 Ant Design Pro 模板约定。

### 3.2 shadcn-admin（Radix + Tailwind 4）
- **框架**：Vite + React 19 + TanStack Router + TanStack Query + Zustand。
- **组件来源**：shadcn/ui 生成的 `src/components/ui/*` 全部基于 Radix primitives，通过 `class-variance-authority` 定义 `variants`（如 `buttonVariants` 的 `variant`/`size`），用 `clsx` + `cn` 合并 className。
- **设计令牌**：`src/styles/theme.css` 以 `:root` 和 `.dark` 两套 CSS 自定义属性（OKLCH 色彩空间）定义 background、foreground、primary、secondary、muted、accent、destructive、border、input、ring、chart-1~5、sidebar-* 等语义化变量；通过 `@theme inline { --color-* }` 映射到 Tailwind 4 的 `color.*` 命名空间。
- **样式分层**：`src/styles/index.css` 使用 Tailwind 4 的 `@layer base` 定义全局重置（边框、滚动条、body 背景/文字、移动端输入字号 16px 防缩放），`@utility` 定义 `container`、`no-scrollbar`、`faded-bottom` 等复用工具类。
- **暗色模式**：通过 `@custom-variant dark (&:is(.dark *));` 将 `.dark` 类作为 Tailwind 4 的 dark variant 触发器，配合 `theme-provider`（`src/context/theme-provider.tsx`）动态切换。
- **动画**：引入 `tw-animate-css` 提供过渡动画；同时定义 Collapsible 的 `slideDown`/`slideUp` keyframes。

## 4. 约定与约束

- **po-admin** 的主题变更统一走 `config/defaultSettings.ts` 的 `ProLayoutProps`，禁止在业务组件内硬编码主色调；全局字体与响应式表格规则集中在 `src/global.less`。
- **shadcn-admin** 的所有颜色必须使用 theme CSS 中定义的 `--*` 变量对应的 Tailwind 语义类（如 `bg-primary`、`text-foreground`），不得直接使用十六进制色值；新增组件需遵循 `cva` + `variants` + `defaultVariants` 的模式（参考 `button.tsx`）。
- 两个项目均使用 Tailwind CSS 4（`tailwindcss` ^4.x），通过各自的入口 CSS 引入，不再依赖传统 `tailwind.config.js` 的完整配置（po-admin 仅保留 `content` 路径，shadcn-admin 的 config 为空字符串）。
- 图标统一：po-admin 使用 `@ant-design/icons`，shadcn-admin 使用 `lucide-react`（见 `components.json` 的 `iconLibrary`）。
- 国际化文案与样式分离：po-admin 通过 `src/locales/*/` 多语言文件组织文案；shadcn-admin 通过 `src/locales/*.json` + `react-i18next` 管理，样式不受语言影响。
- 移动端适配策略：po-admin 使用 Less `@media (max-width: 768px)` 针对 antd 组件做局部覆盖；shadcn-admin 在 `index.css` 的 base 层对 `<767px` 的 input/select/textarea 强制 `font-size: 16px` 防止 iOS 缩放。

## 5. 不适用说明

本仓库的后端（Java Spring Boot、Python FastAPI）不包含任何前端样式代码，所有 UI 样式均位于 `web_client/po-admin` 与 `web_client/shadcn-admin` 两个独立前端工程中，因此本知识卡仅覆盖这两个前端项目的样式体系。
