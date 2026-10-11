# PO 做菜

基于 Expo、React Native、expo-router 和 NativeWind 构建的菜谱移动端应用，复用仓库中的 Spring Boot API 与 `@po/types` 共享类型。
Expo SDK ~57.0.24 / React Native 0.86.3 / React 19.2.3，应用名 `PO 做菜`（slug `po-cooking`，scheme `pocooking`）。

## 当前功能

- 强制登录：未登录只能看到登录/注册页，登录后才进入标签页
- 用户名 + 密码登录与注册，token 持久化（原生走 SecureStore，Web 走 localStorage），重启保留登录态
- 会话失效（后端 `Result.code === 401`）时统一清除会话并跳回登录页
- 四个标签页：首页（菜谱分页列表、下拉刷新、上拉加载、搜索历史）、分类、AI 指导、我的
- 「我的」下的子页：个人资料编辑（昵称/邮箱/手机号 + `expo-image-picker` 选图上传头像）、收藏、浏览历史、我的菜谱
- 菜谱详情 `recipe/[id]`、分类详情 `category/[id]`；「我的菜谱」可以新建也可以改（同一个 `recipe/form` 页，靠查询参数区分）
- 做菜模式 `cook/[id]`：按步骤计时，计时结束循环播放上菜铃提示音并震动；进入该页即 `useKeepAwake()` 保持屏幕常亮，切步骤用 `expo-speech` 播报「第 N 步，…」
- 「AI 指导」标签页：向聊天服务发起流式问答，回复中的菜谱以卡片呈现、可点进详情页；服务不可用时静默回退本地规则
- 浅色与深色模式（`useColorScheme`，标签页与卡片都跟着切）
- Axios API 客户端、统一 `Result` 响应解包与 401 处理、`resolveAssetUrl` 把后端返回的相对图片路径补成可访问地址
- TanStack Query 缓存与请求状态管理

## 页面与路由

`src/app/_layout.tsx:50-68` 用 `Stack.Protected` 按登录态切两组路由，未登录直接访问受保护路由不会渲染。

| 路由文件 | 路径 | 归属 |
| --- | --- | --- |
| `(tabs)/index` | 首页 | 登录后 |
| `(tabs)/categories` | 分类列表 | 登录后 |
| `(tabs)/ai` | AI 指导（`headerShown: false`） | 登录后 |
| `(tabs)/profile` | 我的 | 登录后 |
| `recipe/[id]` | 菜谱详情 | 登录后 |
| `recipe/form` | 新建 / 编辑菜谱（编辑时带查询参数） | 登录后 |
| `category/[id]` | 分类下的菜谱列表 | 登录后 |
| `profile/edit`、`profile/favorites`、`profile/history`、`profile/recipes` | 个人资料 / 收藏 / 历史 / 我的菜谱 | 登录后 |
| `cook/[id]` | 做菜模式（`slide_from_bottom`） | 登录后 |
| `login`、`register` | 登录 / 注册 | 仅未登录 |

## 开发环境

### 前置条件

- Node.js 22+、pnpm 10+
- 使用 Expo Go、Web 或 iOS 模拟器开发时，无需原生 Android 工具链
- 生成本地 Android APK 时，额外准备 JDK 17 与 Android SDK（Platform Tools、Platform、CMake、NDK 与一台模拟器）；命令行安装即可，不必装 Android Studio
- 再装一个支持 Windows 长路径的 ninja（`pip install ninja`，需 ≥ 1.11）。pnpm 的 `.pnpm` 目录名很长，react-native-* 原生模块的 CMake 中间文件路径会超过 260 字符，Android SDK 自带的 ninja 1.10.x 读写不了这类路径，会报 `manifest 'build.ninja' still dirty after 100 tries` 或 `mkdir(...): No such file or directory`；`pnpm mobile:android` 会在启动前自动把 SDK 里的旧版 ninja 换成 PATH 上的新版（原文件备份为 `ninja.exe.orig`）

所有命令均从仓库根目录执行。首次安装依赖并创建本地配置：

```bash
pnpm install
cp apps/cooking-app/.env.example apps/cooking-app/.env
```

`.env` 默认指向本机 Spring Boot API：

```env
EXPO_PUBLIC_API_URL=http://localhost:8080/api
# 可选：显式指定 AI 聊天的 WebSocket 地址；
# 不设置时按上面的主机换到 5090 端口推导（见下文「AI 指导」）
# EXPO_PUBLIC_CHAT_URL=ws://localhost:5090/ws/chat
```

先按根目录 README 启动 Spring Boot API 与聊天服务（`pnpm chat:start`，AI 指导标签页需要），再启动 Expo：

```bash
pnpm mobile:start
```

Web 版固定请求同源 `/api`，由 Metro 开发服务器代理；iOS 模拟器可保留 `localhost`。Android 模拟器需将 `.env` 改为 `http://10.0.2.2:8080/api`，或执行 `adb reverse tcp:8080 tcp:8080` 后继续使用 `localhost`。真机使用 Expo Go 时，改为同一局域网内开发机可访问的地址，例如 `http://<开发机局域网 IPv4>:8080/api`，随后扫描 Expo 输出的二维码。

浏览器里调试时，接口一律以同源的 `/api` 发出，由 Metro dev server 代理到后端（目标取自 `EXPO_PUBLIC_API_URL` 的主机，未设置时用 `http://localhost:8080`），因此不会跨域，后端也无需配置 CORS。后端若走 Docker 网关，把 `EXPO_PUBLIC_API_URL` 设为 `http://localhost:8000/api`，代理目标会跟着变。

### AI 指导（聊天服务）

「AI 指导」标签页对应 `services/chat` 的 `/ws/chat`：一轮对话一条 WebSocket，回复文本流式渲染，Agent 检索到的菜谱以卡片呈现、点按进入详情页，服务端按会话 id 保留多轮上下文，点「新对话」清空。

- 地址推导：优先取 `EXPO_PUBLIC_CHAT_URL`；未设置时按 `EXPO_PUBLIC_API_URL` 的主机换到 5090 端口（开发期 Metro 只代理 HTTP `/api`，不代理 WebSocket 升级，所以直连 chat 服务）；生产 Web 与网关同源，自动用 `wss://<站点域名>/ws/chat`
- 依赖链：chat 服务取菜谱要走 Spring Boot API、生成回复要走 LLM，所以先把 `pnpm api:start` 与 `pnpm chat:start` 都启动起来；后端或模型未就绪时回复里会给出可读提示，而不是白屏
- 降级：chat 服务连不上、超时或本轮无回复时，界面自动改用本地菜谱规则问答（`src/lib/ai/chat.ts`），断网也能查菜、给推荐，只是回答不来自模型
- 无密钥也能跑：模型密钥缺失时 chat 服务以离线模式启动（回复带「离线模式」标记），适合只调界面时使用

### 开发运行目标

| 命令 | 说明 |
| --- | --- |
| `pnpm mobile:start` | 启动 Expo 开发服务器，并在终端选择运行目标 |
| `pnpm mobile:android` | 启动 Android 模拟器或已连接设备 |
| `pnpm mobile:ios` | 启动 iOS 模拟器（仅 macOS） |
| `pnpm mobile:web` | 在浏览器中启动 |
| `pnpm mobile:lint` | 运行 Biome 检查 |
| `pnpm mobile:typecheck` | 运行 TypeScript 类型检查 |
| `pnpm mobile:test` | 运行 Jest 单元与组件测试 |

## 本地 Android APK

本地构建适用于开发和内测。生成的是可安装的 debug APK，不适用于应用商店发布。

### 命令行准备工具链

不需要安装 Android Studio，用命令行工具装齐 JDK 17 与 Android SDK 组件即可。先装 JDK 17（如 `~/.jdks/ms-17.0.20.1`）与 cmdline-tools，然后一次装完所有组件：

```bash
sdkmanager "platform-tools" \
  "platforms;android-36" \
  "build-tools;36.0.0" \
  "cmake;3.22.1" \
  "ndk;27.1.12297006" \
  "emulator" \
  "system-images;android-36;google_apis;x86_64"
```

再建一台模拟器（只需一次）：

```bash
avdmanager create avd -n po_pixel7 -k "system-images;android-36;google_apis;x86_64" --device pixel_7
avdmanager list avd          # 确认已创建
```

`sdkmanager`/`avdmanager` 默认取 `ANDROID_HOME`（Windows 下为 `%LOCALAPPDATA%\Android\Sdk`）定位 SDK；若装在别处，先导出该变量。`scripts/jdk.mjs` 会自动从 `~/.jdks` 里挑 JDK 17，`scripts/run-mobile.mjs` 会自动定位 SDK 并把 `platform-tools`、`emulator` 加进 PATH，所以日常只需保证组件已安装。

> **上面这串组件版本号会漂移。** 它们是某一次 prebuild 产物里的取值，`android/` 与 `ios/` 都不入库，
> 所以权威来源是本地跑一次 `pnpm mobile:prebuild:android` 之后生成的 `android/build.gradle`
> （以及 `node_modules/react-native/ReactAndroid` 声明的 `ndkVersion` / `compileSdkVersion`）。
> Expo 或 React Native 升级后按报错里的版本号补装即可，装错的表现通常是 Gradle 配置期
> `Failed to find NDK version` 或 `Failed to find Compile SDK version`。

### 一键构建、安装并启动

模拟器已启动（或真机已连接）后，在仓库根目录执行：

```bash
pnpm mobile:android
```

它会先做 Expo 预构建、再编译并安装 debug 包、最后启动 Metro。

只打包 APK（不装、不启动 Metro）：

```bash
pnpm mobile:apk              # 四种 ABI，可装真机
pnpm mobile:apk x86_64       # 只编模拟器架构，快很多
```

APK 位于：

```text
apps/cooking-app/android/app/build/outputs/apk/debug/app-debug.apk
```

也可以直接进原生目录用 Gradle 编译，效果等价（需自行保证 `JAVA_HOME`、`ANDROID_HOME` 已设置）：

```bash
cd apps/cooking-app/android
./gradlew.bat assembleDebug -PreactNativeArchitectures=x86_64
```

不带 `-PreactNativeArchitectures` 时按 `android/gradle.properties` 的 `reactNativeArchitectures` 取值，默认四种 ABI（`armeabi-v7a`、`arm64-v8a`、`x86`、`x86_64`）。装到已连接设备：

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

模拟器里若想让应用访问本机后端，除了把 `.env` 改成 `http://10.0.2.2:8080/api`，也可以转发端口后继续用 `localhost`：

```bash
adb reverse tcp:8080 tcp:8080
```

`android/` 与 `ios/` 是 Expo 预构建产物，默认已忽略，不提交到仓库；`pnpm mobile:android` 会在需要时重新生成，也可单独执行 `pnpm mobile:prebuild:android`。改动 `app.json` 里影响原生的配置（应用名、图标、权限、插件）后需要重新预构建。

## 生产部署

移动端不随 Docker Compose 部署。后端与网关先按根目录 README 的生产部署流程上线；移动端通过 EAS Build 单独签名和分发。

1. 为生产后端准备 HTTPS API 地址，并在 EAS 的 `production` 环境中配置 `EXPO_PUBLIC_API_URL`。该变量会写入客户端包，**不得**放入密码、令牌或其他机密。
2. 运行发布前检查：

   ```bash
   pnpm mobile:lint
   pnpm mobile:typecheck
   pnpm mobile:test
   ```

3. 登录 EAS。当前项目已链接到 EAS 项目；若在新机器上操作，执行：

   ```bash
   pnpm dlx eas-cli@latest login
   ```

4. 内测构建会生成可直接安装的 APK：

   ```bash
   pnpm mobile:eas:preview
   ```

   构建完成后，EAS 会提供下载页；将 APK 分发给测试人员安装。

5. 正式构建会生成 Google Play 要求的 AAB：

   ```bash
   pnpm mobile:eas:production
   ```

   EAS 使用 `eas.json` 中的 `production` profile 自动递增 Android 版本号，并托管签名凭据。将生成的 AAB 上传至 Google Play Console，先经内部测试、封闭测试，再发布到正式轨道。

生产 API 必须使用 HTTPS；不要提交 `.env`、签名文件或 EAS 访问令牌。

## 目录结构

```text
src/
├─ app/            Expo Router 页面：(tabs){index,categories,ai,profile} + recipe/[id]、recipe/form、
│                  category/[id]、cook/[id]、profile/{edit,favorites,history,recipes}、login、register
├─ components/     recipe-list / recipe-card / recipe-meta / recipe-filter-bar / recipe-status-badge、
│                  recipe-chat-card、form（TextField/FormError/SubmitButton）、screen-header、state-views
├─ lib/api/        Axios 客户端（含 resolveAssetUrl）+ auth / users / recipes 接口
├─ lib/ai/         agent-chat.ts（/ws/chat WebSocket 客户端）、chat.ts、assistant.ts（本地规则问答，
│                  服务不可用时的降级路径）
├─ lib/auth/       session.ts（SecureStore / localStorage）、auth-context.tsx（Provider 与守卫）
├─ lib/cooking/    cooking-context.tsx（做菜会话状态）、use-cook-alert.ts（循环响铃 + 震动）
├─ lib/            query-keys.ts、recipe-utils.ts（时长换算等）、use-search-history.ts、
│                  nativewind.ts、utils.ts（cn）
└─ __tests__/      Jest 单元与组件测试（14 个文件：screen / context / client / utils / alert）
```

顶层还有 `assets/`（图标与 `assets/sounds/step-done.wav`）、`jest/css-mock.js`（样式导入的测试替身）、
`scripts/reset-project.js`（Expo 模板自带，会把项目重置回空模板，本仓库不要用）、
`eas.json`（preview / production profile）、`app.json`、`metro.config.js`、`babel.config.js`、
`biome.json`、`jest.config.js`、`jest.setup.ts`。

路由使用 `src/app/` 下的文件式约定，`_layout.tsx` 通过 `Stack.Protected` 按登录状态切换可访问的路由组。样式通过 NativeWind 类名编写，跨端数据类型从 `@po/types` 导入。

## 做菜提示

做菜模式的等待计时归零时（自然归零，或用户点「跳过等待」——代码里把「跳过」也算作归零，
见 `src/app/cook/[id].tsx:155`）会响 `assets/sounds/step-done.wav`，非 Web 端同时震动 400ms。

- 声音内容：三声厨房上菜铃（C6 基音加高次不谐和分音），最后一击之后接一段油爆锅气，总长 2.0s
- 提醒逻辑在 `src/lib/cooking/use-cook-alert.ts`，走 `expo-audio`：
  - **循环响铃**（`player.loop = true`），不是一遍就停；单遍铃只有 2 秒，没人处理就一直响
  - `RING_DURATION_MS = 30_000`：默认响满 30 秒自动安静，期间点「停止响铃」、上/下一步、退出做菜页、
    「收起计时」都会立刻收尾（`stopAlert()` 在这几处都有调用）
  - 每次 `play()` 先 `seekTo(0)` 再 `play()`——上一次停在末尾的话，直接 `play()` 不出声
  - `setAudioModeAsync({ interruptionMode: 'duckOthers', playsInSilentMode: true })`：灶台边手机常静音或放着音乐，静音键下也要响，响的时候把背景音压下去
  - `stop()` 里先关 `loop` 再 `pause()`，并把播放器回到 0 秒，避免下次响铃没声音
- 屏幕常亮与语音播报在同一个页面：进入 `cook/[id]` 就 `useKeepAwake()`（`expo-keep-awake`），
  洗手沾油不用反复点亮屏幕；切步骤时 `expo-speech` 播报「第 N 步，…」（`language: 'zh-CN'`），
  离开页面（含完成、取消）在卸载回调里 `Speech.stop()`
- 音频文件由 `tools/cook-alert-sound.py` 用 Python 标准库合成，不依赖第三方素材；调整音色就是改脚本里的敲击时刻、分音与锅气参数，然后在仓库根目录重新生成：

  ```bash
  python tools/cook-alert-sound.py
  ```

  脚本自带分音能量与包络自检，可直接看出修改后的三声铃是否还清晰。换掉音频文件后需重启 Expo 才能生效。

## 已知遗留

登记在这里，动它之前先确认目的；清理与否是单独的决策。

- `@expo/ui` (~57.0.19) 与 `expo-glass-effect` (~57.0.3) 在 `package.json` 里，但 `src/` 没有任何引用，
  也不是 expo-router 的运行依赖——像是准备做玻璃质感界面时加的，界面没落地。
- `scripts/reset-project.js` 会把项目重置回空模板，本仓库不要用；`.claude/`、`AGENTS.md`、`CLAUDE.md`、
  `LICENSE`、`assets/images/*-logo.png` 等是 Expo 模板自带文件。
- 其余 `expo-device`、`expo-web-browser`、`expo-symbols`、`expo-system-ui`、`expo-font`、`expo-linking`、
  `expo-constants` 在 `src/` 里也没有直接 import，但它们是 Expo 模板与 expo-router 的运行依赖，
  **不要按「未使用」删掉**。
- CI 的 Mobile job 只跑 `mobile:lint`、`mobile:typecheck` 和 `jest --runInBand`，不覆盖 EAS 构建。
