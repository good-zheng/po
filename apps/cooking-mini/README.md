# 叮叮厨微信小程序（`apps/cooking-mini`）

Taro 4.2.1 + React 18 的微信端，`@po/cooking-mini`。与 `apps/cooking-app`（Expo）打同一个 Spring Boot
后端，页面形态接近，但**能力集不同**：小程序端没有大模型对话（原因见下）。

## 命令

全部从仓库根执行（本包 `package.json` 只有 `dev:weapp` / `build:weapp` / `dev:h5` / `build:h5` 等
Taro 原生命令，没有 lint 与 test）：

```bash
pnpm mini:dev        # taro build --type weapp --watch，产物写 dist/
pnpm mini:build      # 生产构建（一次性，用于确认能编译过）
pnpm mini:dev:h5     # 浏览器里看版式（只作调试，微信端样式差异不会在这里暴露）
pnpm mini:build:h5
```

`pnpm types:build` 不在 `mini:*` 的前置里，改过 `packages/types` 后要先单独跑一次，否则 TS 报找不到导出。

产物导入方式：微信开发者工具打开 **`apps/cooking-mini` 目录本身**（不是 `dist/`），工具会读根目录的
`project.config.json`，其 `miniprogramRoot` 指向 `dist/`。`dist/` 里也有一份 `project.config.json`
（构建产物），两份的 `appid` 与 `setting` 必须一致，手改根目录那份后重跑一次构建再上传。

## 环境

只有两个变量档，且**只有一个变量**：

| 文件 | 载入时机 | 内容 |
| --- | --- | --- |
| `.env.development` | `dev:weapp`（--watch） | `TARO_APP_API_BASE_URL=http://127.0.0.1:8080/api` |
| `.env.production` | `build:weapp` | `TARO_APP_API_BASE_URL=https://api.dingdingchu.site/api`（旧云托管地址以注释形式保留在同一文件） |

`src/config/env.ts` 只读 `process.env.TARO_APP_API_BASE_URL`，缺省回退 `http://localhost:8080/api`。
Taro 只注入 `TARO_APP_` 前缀的变量，写成别的名字会静默用缺省值——本地 8080 没起时表现为「所有请求失败」，
而不是「地址没配」。`/api` 前缀包含在变量值里（Spring 的 `server.servlet.context-path`），别再在请求路径上拼一次。

开发者工具本地调试要勾「不校验合法域名」；真机预览只允许 https/wss，且域名必须先进小程序后台的
「request 合法域名」。

## 目录

```
src/app.config.ts        13 个页面 + 4 个 tab（首页 / 分类 / 菜谱问答 / 我的），lazyCodeLoading 已开
src/pages/               index、categories、category/detail、recipe/detail、recipe/form、cook、
                         ai/chat、profile/{index,favorites,history,recipes,edit}、login
src/components/          recipe-card.tsx（含 RecipeGrid）、recipe-status-badge.tsx
src/lib/api/             client.ts（Taro.request 封装）、recipes.ts、auth.ts、users.ts —— 没有独立 services 目录
src/lib/auth/            auth-context.tsx、auth-guard.tsx、guest-placeholder.tsx、session.ts、return-path.ts
src/lib/cooking/         cooking-context.tsx、use-cook-alert.ts
src/lib/ai/              chat.ts、assistant.ts —— 本地意图识别 + 菜谱数据应答
src/lib/tts.ts           分步音频与批量预热
src/config/env.ts        唯一的地址来源
src/styles/theme.scss    设计令牌；SCSS 里必须用 `@use '…/theme.scss' as *;`，用 `@import` 会被 Dart Sass 的弃用警告刷屏
src/assets/icons/        tabBar 图标（png）
```

状态管理没有引入第三方库：会话在 `auth-context.tsx`，做菜流程在 `cooking-context.tsx`，页面内用
`useState`。请求也不走 Axios，全部经 `apiClient`（`.get/.post/.put/.delete`），它解 `Result<T>` 信封、
`success === false` 抛 `ApiError`、HTTP 401 触发由 AuthProvider 注册的 `signOut()`。
`resolveAssetUrl()` 会把相对资源路径剥掉 `/api` 再拼根域；COS 上线后头像/封面/TTS 返回的是公网绝对
URL，`<Image>` 与音频不受合法域名限制。

## 登录与游客边界

- 登录方式：`Taro.login()` 拿 code → `POST /auth/openid-login`（只认请求体 `loginCode`）；
  用户名密码 `POST /auth/login`；注册 `POST /auth/app-register`，需管理员审批，
  `approvalStatus` 为 pending / rejected 时在登录页提示，只有 `role === 'user'` 的会话可用。
- 会话存 `Taro.setStorageSync` 的 `po.session`（键名与校验逻辑在 `session.ts`），
  恢复失败（网络异常）保留本地会话不清令牌。
- **游客可完整浏览**：首页、分类、分类详情、菜谱详情、AI 问答页的整个界面。
- 只在「动作」上要登录：点「开始做菜」、在 AI 页点发送。跳转前用 `saveReturnTo()` 记下当前页，
  登录成功后 `consumeReturnTo()` 回跳（tab 路径用 `switchTab`）。
- tab 页未登录**绝不自动跳转**，渲染 `guest-placeholder.tsx` 缺省页 + 「去登录」按钮；
  直接 `redirectTo` 曾在返回时白屏，已被明确否决。`AuthGuard` 只包非 tab 的受保护页
  （`cook`、`recipe/form`、`profile/*`）。

## 为什么没有大模型对话

个人主体小程序不允许申请「AI 大模型」类目，所以 `6e70944` 把大模型 WebSocket 链路从源码里摘掉了：
`src/config/env.ts` 不再有 WS 地址变量，`pages/ai/chat.tsx` 与 `lib/ai/chat.ts` 只走本地意图规则
（`assistant.ts` 的 `parseIntent` + `buildReply`）加菜谱接口。`lib/ai/chat.ts` 里那句注释就是当前事实——
「这条链路只读菜谱接口，不经过任何模型，也是小程序唯一的应答来源」。

要恢复必须等有 AI 类目资质（企业主体），恢复的是 `Taro.connectSocket` 打 `services/chat` 的 `/ws/chat`，
别把 `api.dingdingchu.site` 之外的地址写回来。

## TTS

`src/lib/tts.ts`：进详情页或做菜页时 `POST /tts/prefetch`（`PREFETCH_LIMIT = 50`，一次批量合成），
单条 `GET /tts`；**无 token 直接 return**，游客不消耗讯飞额度。返回的是 COS 公网地址，播放用
`Taro.createInnerAudioContext`。做菜提示音走静态资源 `resolveAssetUrl('/api/sounds/step-done.wav')`。

## 微信平台限制（代码里已按这些写法，改动时不要退回）

- `flex-wrap: wrap` 不可靠——`RecipeGrid` 显式按每行 2 张切分（`components/recipe-card.tsx:104` 有注释）。
- 逐秒 `setState` 会让整页每秒一次 `setData`——计时的 `remaining` 关在子组件自己的 state 里，
  页面只在「时间到」被叫醒一次（`pages/cook/index.tsx:30-36` 注释）。同理列表排序结果要固定，
  否则每次渲染都反复 diff。
- 组件必须从 `@tarojs/components` 导入（`View`/`Text`/`Image`/`ScrollView`/`Button`），不能用 HTML 标签；
  `Text` 是行内元素，需要块级布局时用 `View`。
- `box-sizing` 全局设置不能用 `*` 通配符（WXSS 不支持），`app.scss` 里按具体元素选择器写。
- 样式用 SCSS + rpx（`designWidth: 750`），不共享 Expo 端的 NativeWind。
- 表情符号在部分环境不渲染，界面里用图标或 Unicode 转义。
- `config/index.ts` 的 `alias['@']` 与 `tsconfig.json` 的 `paths` 必须同时存在，缺一构建失败；
  `webpack` 锁 `~5.95.0`，升高版本与 `@tarojs/webpack5-runner` 4.2.1 不兼容。
  同文件里 `cache.enable: false` 是刻意关掉的，改回 `true` 前要先确认增量构建产物是否新鲜。
- `project.config.json` 的 `appid` 是真实 AppID（不是 `touristappid`），`setting.es6/postcss/bundle` 为
  `false`（编译由 Taro 承担），`minified/minifyWXSS/minifyWXML` 为 `true` 以通过上传检查。

## 验证

改完先 `pnpm mini:build` 确认能编译过，UI 改动在微信开发者工具里看。
**不要用 `mini:build` 做日常热调试**——它是生产档，读 `.env.production`，会把本地联调打到线上域名；
日常用 `mini:dev`（`--watch`）。工具里看到的是 `dist/` 的内容，编译没跑或跑错档时界面仍是旧产物，
怀疑这一点就重跑一次编译再刷新，不要凭界面下结论。
