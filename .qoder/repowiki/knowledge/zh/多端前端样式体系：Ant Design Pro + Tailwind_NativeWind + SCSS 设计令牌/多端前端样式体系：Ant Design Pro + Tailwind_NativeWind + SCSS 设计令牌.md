---
kind: frontend_style
name: 多端前端样式体系：Ant Design Pro + Tailwind/NativeWind + SCSS 设计令牌
category: frontend_style
scope:
    - '**'
source_files:
    - apps/admin-web/tailwind.config.js
    - apps/admin-web/tailwind.css
    - apps/admin-web/src/global.less
    - apps/admin-web/src/global.style.ts
    - apps/admin-web/config/defaultSettings.ts
    - apps/cooking-app/tailwind.config.js
    - apps/cooking-app/src/global.css
    - apps/cooking-app/src/lib/nativewind.ts
    - apps/cooking-mini/src/styles/theme.scss
    - apps/cooking-mini/src/app.scss
    - apps/cooking-mini/src/components/recipe-card.scss
---

## 1. 整体方案

仓库包含三个前端应用，各自采用不同的样式技术栈，但共享同一套品牌色（`#f97316` 系）。

| 应用 | UI 框架 | 样式方案 | 主题/令牌 |
|---|---|---|---|
| `apps/admin-web` | Ant Design / @ant-design/pro-components (UmiJS) | Less + CSS Modules (`antd-style`) + Tailwind v4 (`tailwind.css` 仅导入 base/components/utilities) | ProLayout token + `defaultSettings.ts` |
| `apps/cooking-app` | React Native (Expo) + NativeWind | Tailwind CSS v3 + NativeWind (`nativewind/preset`)，组件内直接写 `className` | `tailwind.config.js` 中扩展 `brand.*` 颜色族 |
| `apps/cooking-mini` | 微信小程序原生 | SCSS，集中式变量 + mixin | `src/styles/theme.scss` 定义 `$brand-*`、`$text-*`、`$card-bg` 等令牌 |

## 2. 关键文件

- `apps/admin-web/tailwind.config.js` — Tailwind v4 极简配置，仅声明 `content: ['./src/**/*.tsx']`
- `apps/admin-web/tailwind.css` — 通过 `@import "tailwindcss/index.css"` 和 `@source "./src"` 启用 v4 引擎
- `apps/admin-web/src/global.less` — 全局字体（AlibabaSans woff2）、Ant Design Pro 布局覆盖、移动端表格适配
- `apps/admin-web/src/global.style.ts` — 使用 `antd-style` 的 `createStyles` 编写 CSS-in-JS 样式（与 `global.less` 内容基本一致）
- `apps/admin-web/config/defaultSettings.ts` — ProLayout 主题配置，`colorPrimary: '#1677ff'`，`layout: 'mix'`，预留 `token` 字段
- `apps/cooking-app/tailwind.config.js` — 引入 `nativewind/preset`，在 `theme.extend.colors.brand` 下定义 `50/100/500/600/700` 五级色阶
- `apps/cooking-app/src/global.css` — 通过 `@tailwind base/components/utilities` 注入 Tailwind，并在 `:root` 中声明 CSS 变量 `--font-display/--font-mono/--font-rounded/--font-serif`
- `apps/cooking-app/src/lib/nativewind.ts` — 用 `cssInterop(ExpoImage, { className: 'style' })` 让 `expo-image` 支持 `className` prop
- `apps/cooking-mini/src/styles/theme.scss` — 设计令牌中心：`$brand-*`、`$page-bg/$card-bg/$text-*`、`$danger/$success/$warning/$info`、`$wechat-green`，以及 `@mixin card`、`@mixin ellipsis($lines)`
- `apps/cooking-mini/src/app.scss` — 小程序全局 reset，设置 `box-sizing: border-box`、背景色 `#fafafa`、系统字体栈

## 3. 架构与约定

### 3.1 品牌色统一
三个子应用的 brand 色值完全一致：`#fff7ed` / `#ffedd5` / `#f97316` / `#ea580c` / `#c2410c`（分别对应 50/100/500/600/700），由 `cooking-app/tailwind.config.js` 首次定义，随后被 `cooking-mini/src/styles/theme.scss` 以 SCSS 变量形式复制，admin-web 则通过 Ant Design Pro 的 `colorPrimary` 及 Tailwind 默认 orange 色系间接使用。

### 3.2 桌面端（admin-web）
- 主样式入口为 `src/global.less`，同时存在一份语义相同的 `src/global.style.ts`（`antd-style` 版本），两者并存，未做去重。
- 组件级样式使用 `*.style.ts`（CSS-in-JS，基于 `antd-style` 的 `createStyles`），例如 `components/ArticleListContent/index.style.ts`、`pages/chatbot/style.ts` 等。
- 全局布局通过 Ant Design Pro 的 `ProLayoutProps` 配置（`config/defaultSettings.ts`），而非手写 CSS。
- Tailwind v4 已安装但未作为主要样式语言，仅在 `tailwind.css` 中导入基础层，实际业务类名未见广泛使用。

### 3.3 移动 Web/App（cooking-app）
- 纯 Tailwind + NativeWind 方案，所有样式写在 JSX 的 `className` 中（如 `flex-row items-center gap-3 border-b border-stone-100 px-4 pb-3`）。
- 深色模式通过 Tailwind 的 `dark:` 前缀实现（如 `bg-stone-50 dark:bg-stone-950`、`text-stone-900 dark:text-stone-50`）。
- 自定义字体通过 CSS 变量暴露给 Tailwind，未在 `tailwind.config.js` 中注册。
- 品牌色通过 `tailwind.config.js` 的 `theme.extend.colors.brand` 扩展，组件中使用 `bg-brand-50`、`text-brand-700` 等。

### 3.4 微信小程序（cooking-mini）
- 不使用 Tailwind，全部手写 SCSS，按页面/组件分文件（`pages/*/index.scss`、`components/*.scss`）。
- 所有颜色、字号、间距均通过 `@import '../styles/theme.scss'` 引用，禁止硬编码魔法色值（见 `theme.scss` 顶部注释：「设计令牌：集中主题色，供各页面 SCSS 通过 @import 引用，避免魔法色值散落」）。
- 复用样式通过 `@mixin card`、`@mixin ellipsis($lines)` 提供。
- 针对微信不支持 `flex-wrap` 的情况，代码中有明确注释说明改用 flex 行切分（`// 网格布局（微信不支持 flex-wrap：按行切分）`）。

## 4. 约定与约束

- **品牌色必须从设计令牌引用**：`cooking-mini` 的 `theme.scss` 是单一事实来源；`cooking-app` 的 `tailwind.config.js` 中的 `brand.*` 是单一事实来源。SCSS 组件中不得出现裸色值（除临时调试外）。
- **admin-web 的 antd 主题通过 ProLayout token 配置**：`config/defaultSettings.ts` 中 `colorPrimary: '#1677ff'`，新增主题变量应优先走 `token` 字段而非覆盖 CSS。
- **Tailwind v4 vs v3 混用**：admin-web 使用 v4（`tailwind.css` 中 `@import "tailwindcss/index.css"` + `@source`），cooking-app 使用 v3（`nativewind/preset`）。两个版本的 `tailwind.config.js` 语法不同，不可互换。
- **cooking-app 的 Image 组件需通过 `lib/nativewind.ts` 导出**：只有经过 `cssInterop` 包装的 `Image` 才接受 `className`，直接使用 `expo-image` 的 `Image` 不会生效。
- **cooking-mini 的全局 reset 必须在 `app.scss` 中声明**：所有小程序原生标签（`page/view/text/image` 等）统一设置 `box-sizing: border-box`，新页面不应重复声明。
- **响应式策略**：admin-web 使用 Less 的 `@media(max-width: 768px)` 处理 Ant Design 表格横向滚动；cooking-app 依赖 Tailwind 断点（如 `sm:`/`md:`）；cooking-mini 无响应式框架，靠固定像素尺寸（如 `.grid-cover { height: 240px }`）适配。
- **字体策略**：admin-web 通过 `global.less` 的 `@font-face` 加载 AlibabaSans（woff2，CDN 托管）；cooking-app 通过 CSS 变量声明字体栈；cooking-mini 使用系统字体栈 `-apple-system, BlinkMacSystemFont, ...`。