---
name: mobile-dev
description: 为 po monorepo 的 apps/cooking-app 提供 Expo、React Native、expo-router、NativeWind、TanStack Query、Axios、认证、跨端 API、测试与 Android 构建约定。用于移动端页面、路由、状态、接口、样式、Expo 配置或 APK/AAB 任务。
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

## 验证

修改前读取目标模块的 `package.json`、相邻页面和测试。完成后运行对应的 Biome、TypeScript 与 Jest 检查；UI 改动还要启动 Expo，在受影响的运行目标上验证正常路径与加载、错误或空状态。
