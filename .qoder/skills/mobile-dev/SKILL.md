---
name: mobile-dev
description: 为 po monorepo 的 apps/cooking-app（Expo）、apps/cooking-mini 与 apps/echo-talk（Taro 微信小程序）提供移动端开发约定。用于页面、路由、状态、接口、样式、配置、构建、录音/WS 实时链路与微信小程序 CSS 规则。
---

# Po 移动端开发

## 项目边界

三个目标，别把它们当同一个技术栈：

| 目录 | 栈 | 备注 |
| --- | --- | --- |
| `apps/cooking-app/` | Expo SDK 57、React Native、expo-router、NativeWind、TanStack Query、Axios、Jest Expo、Biome（`@po/cooking`） | 路由 `src/app/`、组件 `src/components/`、接口 `src/lib/api/`、认证 `src/lib/auth/` |
| `apps/cooking-mini/` | Taro 4.2.1 + React 18 + webpack5（`@po/cooking-mini`） | 叮叮厨微信小程序，AI 页已是本地意图解析，**不连 `/ws/chat`** |
| `apps/echo-talk/` | 同一套 Taro 4.2.1 结构（`@po/echo-talk`） | 言外微信小程序，两条 WS（ASR + 聊天）都在这里；无 lint/test 脚本 |

下面四条只针对 Expo 端（小程序另见「微信小程序」一节，两套约定不要混用）：

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

## 微信小程序（cooking-mini 与 echo-talk）

两个小程序共用下面这套 Taro 约定（组件、WXSS、rpx、别名、构建配置、登录 gating）。`apps/cooking-mini/`：页面位于 `src/pages/`，接口位于 `src/lib/api/`，认证位于 `src/lib/auth/`，全局样式 `app.scss`，路由配置 `src/app.config.ts`；`apps/echo-talk/` 目录形状相同，另多一个 `src/lib/asr/`。

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

### AI 能力：两个小程序走的是两条完全不同的路

**cooking-mini 不连任何模型**。`src/pages/ai/chat.tsx` 调 `askAssistant()`（`src/lib/ai/chat.ts`），它只做本地意图识别（`src/lib/ai/assistant.ts` 的 `parseIntent`：greeting / help / recommend / search …）再按需读 `/recipe-categories`、`/recipes`、`/recipes/{id}`。原因不是性能而是**平台资质**：个人主体小程序不能上 AI 类目，大模型 WS 在编译期就被摘掉了，代码里已经没有 `Taro.connectSocket`。改这块时不要"顺手把聊天接回 `/ws/chat`"，那需要企业主体 + 类目审批；也别按 WS 消费方去搜它。

**echo-talk 才有两条 WS**，都是 `Taro.connectSocket`，注意 Taro 4 的破坏性变更：它返回 `Promise<SocketTask>`，必须先 `await`/`.then` 拿到 task 再注册回调，直接对返回值 `onMessage` 会 undefined。

| | ASR（`src/lib/asr/asr-client.ts`） | 聊天（`src/lib/ai/talk-chat.ts`） |
| --- | --- | --- |
| 地址 | `TARO_APP_ASR_WS_URL` → Spring Boot `/api/ws/asr` | `TARO_APP_CHAT_WS_URL` → FastAPI `/ws/chat` |
| 鉴权 | 票据拼在 **query**（`?ticket=`），小程序 WS 不能带自定义请求头，后端在握手拦截器验票 | 同一套 JWT；连接期失效即静默失败 |
| 上行帧 | `{type:'start'}` / `{type:'frame',audio:<base64>}` / `{type:'stop'}` | `{type:'message',content,conversation_id,agent:'talk',context:{utteranceId,scene,speaker}}` |
| 下行帧 | `ready` / `partial` / `final` / `segment_end` / `error`，都带 `segment` | `token`（累加成整段再回调）/ `done` / `error` |

- `agent: 'talk'` 是**显式钉插槽**，绕开意图路由；`context` 里除 `utteranceId` 外都会拼进提示词，`utteranceId`/`bookId` 这类定位键在 `services/chat/app/agent.py` 的 `RESERVED_CONTEXT_KEYS` 里被保留，不要指望模型从文本里读到它们。
- 松手即发、`segment_end` 收迟到定稿：先发出的 partial 用后到的 final 纠正，网关侧收到 `stop` 会等讯飞收尾再回 `segment_end`（实测 final 距松手约 100ms）。前端那个"松手后保留连接"的超时只是 `segment_end` 死活不来时的兜底，不是"等定稿"。
- 三条地址在 `.env.development` 里都填**开发机局域网 IP**，写 `127.0.0.1` 时真机握手必失败（手机上它指向手机自己）；线上必须 `wss` 且路径自带 context-path（直连 api 实例，不经 nginx）。详见 `apps/echo-talk/README.md`。

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
- 后端地址走 `.env.development` / `.env.production`，由各自 `src/config/env.ts` 读取：cooking-mini 只剩 `TARO_APP_API_BASE_URL`（摘掉大模型 WS 后 `TARO_APP_CHAT_WS_URL` 已删），echo-talk 是三个（`TARO_APP_API_BASE_URL`、`TARO_APP_CHAT_WS_URL`、`TARO_APP_ASR_WS_URL`）；`dev:weapp` 载入 development、`build:weapp` 载入 production。WS 地址必须是 `ws://`/`wss://` 前缀，写成 `http://` 时 `Taro.connectSocket` 静默失败。真机/体验版只允许 https 与 wss，且域名必须加入小程序后台合法域名（云托管默认 `*.sh.run.tcloudbase.com` 可直接配置）。
- `getPhoneNumber` 需要认证小程序（营业执照 + 300 元/年审核费）；后端 `application-local.yaml` 同步配置 `wechat.mini.app-id` 和 `wechat.mini.app-secret`。

### 命令

| 目的 | 命令 |
| --- | --- |
| 做菜小程序开发编译（根目录） | `pnpm mini:dev` |
| 做菜小程序生产构建（根目录） | `pnpm mini:build` |
| 言外小程序开发编译 / 生产构建（根目录） | `pnpm echo:dev`、`pnpm echo:build`（两者都带 `types:build` 前置） |
| H5 模式调试（根目录） | `pnpm mini:dev:h5`、`pnpm mini:build:h5`；言外的 H5 档 `pnpm --filter @po/echo-talk dev:h5`（未收进根脚本） |

构建产物输出到 `dist/`，在微信开发者工具中导入项目目录本身即可预览（工具自动读取 `project.config.json`）。

**`dist/` 是 dev 与 prod 共用的同一个目录**（两个 app 的 `config/index.ts` 都写死 `outputRoot: 'dist'`）。这意味着 `pnpm mini:build` 会把 `.env.production` 的云托管域名烤进 dist，开发者工具下次打开就连线上——所以**验证编译不要用 `mini:build`**，跑一次性 dev 编译再杀进程：

```bash
cd apps/cooking-mini && npx taro build --type weapp --watch   # 等 compiled successfully 后 Ctrl-C
```

后台跑时别接 `| tail`：管道会缓冲到进程退出，而 watch 永不退出，日志永远是空的；直接重定向或看 `dist/**` 的 mtime。要在产物里断言中文/常量，写个 `.mjs` 用 `node` 跑——terser 的 `ascii_only` 会把中文写成 `\uXXXX`，Git Bash 传中文 argv 会假阴性。另外 Taro 只在**整包**构建时把 `project.config.json` 拷进 dist，增量 watch 不刷新：改 `packOptions.ignore` 之类必须重启 watcher 才能在产物里看到效果，只 grep 源文件会误判成「已生效」。

## 微信小程序的性能三条（只真机能复现，务必先读）

- **`Taro.getRecorderManager()` 是全局单例，`onFrameRecorded`/`onStop`/`onError`/`onInterruptionBegin` 是「追加」监听而不是覆盖。** 每次 `new` 一个录音器都注册一遍，第 N 次按住时原生会把同一帧派发给 N 个闭包，停一次触发 N 个错误回调，而每个僵尸闭包都把它那次 `start()` 捕获的 `AsrClient`/SocketTask 钉在内存里——表现是「录音越久越卡」且永不回收。正确形状见 `apps/echo-talk/src/lib/asr/recorder.ts`：模块级拿 manager + `listenersBound` 只绑一次 + 回调转发给模块级可变 `active`。动任何「一次性的原生单例」（RecorderManager / InnerAudioContext / SocketTask）前先问：这个监听是覆盖还是追加。
- **setData 经济学**：Taro 每次 `setState` 重渲染整棵页面树并把变化文本作为 setData 载荷上行。① 流式回复逐 token `setState` 会让第 k 个 token 携带全文，累加成 O(n²)——写流式渲染时先合并增量窗口再一次性落 state，且收尾必须"先 flush 再 teardown"，否则最后一个窗口的字丢；② 每秒一跳的 tick 放页面级等于整页每秒一次无谓 diff——把 `remaining` 关进叶子子组件。例外：这段期间页面本来就被更高频事件重渲染（录音中 ASR partial 每帧都在写输入框）时，下沉计时器零收益，别为了"统一风格"再搬回去。
- **体积最大头是封面图，不是 JS**：`services/api/api-bootstrap/src/main/resources/static/covers/` 是 117 张 JPEG / 约 26 MB（均值 224 KB），列表页一屏 10 张卡就是约 2.2 MB。`<Image lazyLoad>` 只推迟加载不缩体积，要真省得服务端出缩略图（COS 数据万象 `imageMogr2` 或后端缩略图路由）。这条属于封面双轨链路，见 `tools/README-covers.md`。

## 验证

修改前读取目标模块的 `package.json`、相邻页面和测试。Expo 端完成后运行 Biome、TypeScript 与 Jest 检查，UI 改动在受影响目标验证正常路径与错误/空状态。小程序端完成后用**一次性 dev 编译**确认编译通过（命令见上面「命令」一节，不要用 `mini:build`/`echo:build` 当验证——那会改写 dist 的环境地址；正式上载前再跑一次生产构建），UI 改动在微信开发者工具中验证。言外没有 lint/test 脚本、也没有 CI job，`pnpm echo:build` 只能手工跑。
