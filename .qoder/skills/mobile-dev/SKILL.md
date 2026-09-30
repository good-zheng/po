---
name: mobile-dev
description: 为 po monorepo 的 apps/cooking-app（Expo）和 apps/cooking-mini（Taro 微信小程序）提供移动端开发约定。用于页面、路由、状态、接口、样式、配置、构建与微信小程序 CSS 规则。
---

# Po 做菜 App 开发

## 项目边界

目标应用是 `apps/cooking-app/`（`@po/cooking`）：Expo SDK 57、React Native、expo-router、NativeWind、TanStack Query、Axios、Jest Expo 与 Biome。路由位于 `src/app/`，业务组件位于 `src/components/`，接口位于 `src/lib/api/`，认证位于 `src/lib/auth/`。

- 使用 expo-router 文件路由与现有 `Stack.Protected` 鉴权结构；不要引入 React Navigation 或第二套路由体系。
- 样式使用 NativeWind className 与现有主题适配；不要引入 Web 专用组件库或管理端 Ant Design。
- 服务端状态使用 TanStack Query；请求继续复用 `src/lib/api/client.ts` 的 Axios 实例、`Result` 解包与 401 会话失效处理。
- 登录令牌通过既有会话存储保存：原生端为 SecureStore，Web 为 localStorage；不要在 `EXPO_PUBLIC_*` 或代码中写入机密。

## 接口与跨端链路

应用调用 Spring Boot API，并从 `@po/types` 复用请求和响应类型。

1. 字段或业务契约变更时，先更新 `packages/types/` 与 `services/api/` 的 API 契约，再更新移动端调用。
2. 将 Query Key 集中在 `src/lib/` 的既有约定中；mutation 成功后按实际资源失效相关查询。
3. 原生端直连 `EXPO_PUBLIC_API_URL`；Web 端固定请求同源 `/api`，由 `metro.config.js` 代理到该变量指定的主机。
4. iOS 模拟器可使用 `localhost`；Android 模拟器使用 `http://10.0.2.2:8080/api` 或 `adb reverse`；真机使用开发机局域网地址。

## 配置与命令

从仓库根目录执行命令。复制 `apps/cooking-app/.env.example` 为 `.env` 后配置 `EXPO_PUBLIC_API_URL`；改动该文件后重启 Expo。

| 目的 | 命令 |
| --- | --- |
| 启动 Expo | `pnpm mobile:start` |
| 启动 Android、iOS、Web | `pnpm mobile:android`、`pnpm mobile:ios`、`pnpm mobile:web` |
| 静态检查与测试 | `pnpm mobile:lint`、`pnpm mobile:typecheck`、`pnpm mobile:test` |
| 生成 Android 原生项目 | `pnpm mobile:prebuild:android` |
| 本地编译 debug APK | `pnpm mobile:apk`（加架构参数如 `pnpm mobile:apk x86_64` 只编模拟器架构，快很多；不传参则产出四种 ABI） |
| EAS 内测 APK / 正式 AAB | `pnpm mobile:eas:preview`、`pnpm mobile:eas:production` |

本地 debug APK 需要 JDK 17 与 Android SDK（Platform Tools、Platform、CMake、NDK），命令行安装即可，不必装 Android Studio；`scripts/run-mobile.mjs` 会自动定位 JDK 与 SDK，`mobile:apk` 在 `android/` 缺失时自动预构建。Windows 上还必须有一个支持长路径的 ninja（`pip install ninja`，≥ 1.11）：pnpm 的 `.pnpm` 目录名很长，react-native-* 原生模块的 CMake 中间文件路径会超过 260 字符，而 AGP 只认 Android SDK 自带的 ninja（`cmake/<版本>/bin/ninja.exe`，不受 PATH 影响），SDK 捆绑的 1.10.x 处理不了这类路径，报 `manifest 'build.ninja' still dirty after 100 tries` 或 `mkdir(...): No such file or directory`。`pnpm mobile:android` 与 `mobile:apk` 启动前会自动用 PATH 上的新版覆盖 SDK 里的旧版（先备份为 `*.orig`）；直接跑 Gradle 时需自行保证 SDK 内 ninja ≥ 1.11。预构建产生的 `android/`、`ios/` 目录和 `.env` 不提交；完整开发、构建与发布说明以 `apps/cooking-app/README.md` 为准。

## 微信小程序（cooking-mini）

`apps/cooking-mini/`（`@po/cooking-mini`）：Taro 4.2.1、React 18、webpack5（`compiler: 'webpack5'`、`framework: 'react'`）。页面位于 `src/pages/`，接口位于 `src/lib/api/`，认证位于 `src/lib/auth/`，全局样式 `app.scss`，路由配置 `src/app.config.ts`。

### 组件与样式

- `View`、`Text`、`Image`、`ScrollView`、`Button` 等全部从 `@tarojs/components` 导入，不使用 React Native 组件或 HTML 标签。
- 样式用 SCSS + rpx（`designWidth: 750`），不用 NativeWind。
- `box-sizing: border-box` 在 `app.scss` 中通过具体元素选择器全局设置，**不能用 `*` 通配符**（WXSS 不支持）。
- `flex-wrap: wrap` 不可靠——用显式行容器 + 固定百分比代替。
- `calc()` 不可靠——用固定百分比或 rpx 代替。
- `gap` 在 flexbox 中不支持——用 `margin-right` / `margin-bottom` 代替。
- Emoji 字符不渲染——用 Unicode 转义（如 `'\u{1F37D}\uFE0F}'`）。
- `Text` 组件是行内的——需要块级布局时用 `View`。

### API 客户端

`src/lib/api/client.ts` 封装 `Taro.request`（不用 Axios）：

- 基础 URL 来自 `src/config/env.ts` 的 `TARO_APP_API_BASE_URL`（dev 为 `http://localhost:8080/api`，线上为云托管 https 域名），自动附加 `Authorization: Bearer <token>`。
- `request<T>()` 解包 `Result<T>` 信封，`success === false` 抛 `ApiError`，HTTP 401 触发 `handleUnauthorized()`。
- 导出 `apiClient` 对象提供 `.get<T>()`、`.post<T>()`、`.put<T>()`、`.delete<T>()`。
- `setUnauthorizedHandler(handler)` 由 AuthProvider 注册为 `signOut()`。
- `resolveAssetUrl()` 解析相对资源路径到 API 服务器；COS 上线后头像/封面/TTS 音频返回绝对公网 URL，`Image`/`audio` 不受合法域名限制。
- 领域 API 模块：`auth.ts`（`openIdLoginRequest`、`passwordLoginRequest`、`appRegisterRequest`、`fetchCurrentUser`）、`recipes.ts`（菜谱 CRUD、收藏、历史）。

## 认证模型（与后端 SecurityConfig 对齐）

`src/lib/auth/auth-context.tsx`：登录方式=微信 OpenID 一键登录 / 用户名密码 / 注册（需管理员审批，`approvalStatus` pending/rejected 在登录页提示）；仅 `role === 'user'` 的会话可用，管理员账号走管理端。恢复会话失败（网络异常）保留本地会话。

### 会话管理

`src/lib/auth/session.ts`：

- 存储键 `po.session`，用 `Taro.setStorageSync` / `getStorageSync` / `removeStorageSync`（不用 SecureStore / localStorage）。
- 内存镜像 `currentToken` 变量，`getSessionToken()` 快速读取避免每次访问存储。
- `restorePersistedSession()` 恢复时校验 token 为 string、user 含 id/username/role。

### WebSocket 流式聊天

`src/pages/ai/chat.tsx` 使用 `Taro.connectSocket`（每消息新建连接，非持久连接）：

- 连接超时 8s（`CONNECT_TIMEOUT`），运行超时 90s（`RUN_TIMEOUT`），心跳 30s（`PING_INTERVAL`，发送 `{ type: 'ping', content: 'ping' }`）。
- 发送 `{ type: 'message', content, conversation_id? }`。
- 帧类型：`run_started`（捕获 `thread_id` 为 `conversationId`）、`token`（追加流式文本）、`tool_call_result`（解析菜谱卡片）、`error`、`done`。
- 模块级 `conversationId` 跨消息持久化；`resetConversation()` 清除。

### AuthGuard 路由守卫与登录策略

`src/lib/auth/auth-guard.tsx`：包裹受保护页面内容。`loading`/`unauthenticated` 时渲染空，未登录时先 `saveReturnTo(当前页面URL)`（`src/lib/auth/return-path.ts`，存储键 `po.auth.returnTo`）再 `Taro.navigateTo('/pages/login/index')`；登录页成功后 `consumeReturnTo()` 回跳（tab 路径用 `switchTab`，其余 `redirectTo`）。

登录 gating 约定（用户明确要求，不得回退成强制跳转）：

- 游客可浏览：首页、分类、分类详情、菜谱详情（后端 `GET /recipes*` 已 permitAll）、AI 聊天页**整个界面**（欢迎语气泡、建议 chip、输入框均可看可输入）。
- 登录只在「动作」时刻要：开始做菜（详情页按钮检查 `status`，未登录 saveReturnTo 后去登录页；`pages/cook/index` 外层再包 `AuthGuard` 兜底）；AI 聊天在**点发送**时才跳登录（`pages/ai/chat.tsx` 的 `send()` 内判 `status !== 'authenticated'` → saveReturnTo + navigateTo，且不清空输入框）；「我的」页及其子页仍需登录。
- AI 聊天页游客态在输入栏上方渲染 `.guest-hint` 提示条（「登录后即可发送消息，点我去登录」），避免发送无反馈。
- 「我的」tab 页未登录时**不自动跳转**，渲染 `src/lib/auth/guest-placeholder.tsx` 缺省页 + 「去登录」按钮；直接 `redirectTo` 曾在返回时造成白屏，已被否决。任何 tab 页的登录跳转都只能由用户动作触发。

### 路径别名与构建

- `@/` 别名必须同时配置在 `config/index.ts`（webpack alias: `'@': path.resolve(__dirname, '..', 'src')`）和 `tsconfig.json`（`paths: { "@/*": ["./src/*"] }`），缺一会构建失败。
- `webpack` 版本锁定 `~5.95.0`——更高版本与 `@tarojs/webpack5-runner` 4.2.1 不兼容，会导致构建失败。
- SCSS 引用主题令牌必须用 `@use '…/styles/theme.scss' as *;`，不得用 `@import`（Dart Sass 弃用警告会导致上传检查报红）。
- `src/app.config.ts` 必须保留 `lazyCodeLoading: 'requiredComponents'`（代码包「组件按需注入」上传检查项）。
- `project.config.json`：`appid` 填真实 AppID（非 `touristappid`），`miniprogramRoot: "dist/"`，`setting` 中 es6/postcss/bundle 为 `false`（由 Taro 处理），`minified/minifyWXSS/minifyWXML` 为 `true`（上传压缩检查）。根目录与 `dist/` 两份配置需保持一致。
- 后端地址走 `.env.development` / `.env.production`（`TARO_APP_API_BASE_URL`、`TARO_APP_CHAT_WS_URL`，由 `src/config/env.ts` 读取）；`dev:weapp` 载入 development、`build:weapp` 载入 production。WS 地址必须是 `ws://`/`wss://` 前缀，写成 `http://` 时 `Taro.connectSocket` 静默失败。真机/体验版只允许 https 与 wss，且域名必须加入小程序后台合法域名（云托管默认 `*.sh.run.tcloudbase.com` 可直接配置）。
- `getPhoneNumber` 需要认证小程序（营业执照 + 300 元/年审核费）；后端 `application-local.yaml` 同步配置 `wechat.mini.app-id` 和 `wechat.mini.app-secret`。

### 命令

| 目的 | 命令 |
| --- | --- |
| 开发编译（根目录） | `pnpm mini:dev` |
| 生产构建（根目录） | `pnpm mini:build` |
| H5 模式调试（根目录） | `pnpm mini:dev:h5`、`pnpm mini:build:h5` |

构建产物输出到 `dist/`，在微信开发者工具中导入项目根目录即可预览（开发者工具自动读取 `project.config.json`）。

## 验证

修改前读取目标模块的 `package.json`、相邻页面和测试。Expo 端完成后运行 Biome、TypeScript 与 Jest 检查，UI 改动在受影响目标验证正常路径与错误/空状态。小程序端完成后运行 `pnpm mini:build` 确认编译通过，UI 改动在微信开发者工具中验证。
