# apps/admin-web — 内容管理端

三件作品共用的管理后台：菜谱内容与分类、用户与小程序准入、个人资料，以及小说「创作工作台」。
站点标题 `GoodZheng Po`（`config/config.ts:117`）。线上形态是 Nginx 静态容器 + 同源反代，
部署见本目录 [`DEPLOY_CLOUDRUN.md`](./DEPLOY_CLOUDRUN.md)。

本应用从 Ant Design Pro v6 模板派生，但**业务页面已全部换成本仓库的模块**——模板的
Welcome / Dashboard / Form / List / Profile / Result / Account Center 都不在路由表里
（`config/routes.ts` 是唯一事实）。上游框架说明仍留在
[`docs/cheatsheet.zh-CN.md`](./docs/cheatsheet.zh-CN.md)，只在查 Pro 能力时参考，
不要按它找页面。

## 技术栈

| 项 | 版本 | 备注 |
| --- | --- | --- |
| 框架 | `@umijs/max` ^4.7.3 | 在 devDependencies，`max` CLI 也从这里解析 |
| 视图 | `react` ^19.2.7 | |
| 组件 | `antd` ^6.6.0、`@ant-design/pro-components` ^3.1.14-2、`@ant-design/icons` ^6.3.2 | |
| AI 对话组件 | `@ant-design/x` + `x-markdown` + `x-sdk` ^2.9.0 | 聊天页当前被注释掉（见「路由」） |
| 服务端状态 | `@tanstack/react-query` ^5.101.2 | Umi `reactQuery: {}` 插件已开 |
| 图表 | `@ant-design/plots` ^2.6.8、`d3`、`topojson-client` | |
| 样式 | `tailwindcss` ^4.3.2 + `antd-style` | `tailwind.config.js`、`tailwind.css` |
| 类型契约 | `@po/types`（workspace） | 前后端共用字段定义在 `packages/types/` |
| 检查/测试 | `@biomejs/biome` ^2.5.3、`vitest` 4.1.10、`typescript` ^7.0.2 | |
| 运行时 | Node `>=22.0.0`（`engines`） | |

`package.json` 里的 `overrides` 把 `@umijs/plugins` 自带的 pro-components 锁到本应用版本，
避免同时装两套 Pro 组件——升级 Pro 组件时要连这里一起看。

## 命令

一律从**仓库根**执行，`admin:*` 系列会先跑 `pnpm types:build`（`exports` 只指向 `dist/`，
类型包没构建就 import 不到）：

| 命令 | 作用 |
| --- | --- |
| `pnpm admin:dev` | dev server，默认 8000（`PORT` 可覆盖），脚本自带 `UMI_ENV=dev MOCK=none` |
| `pnpm admin:build` | 产出 `dist/` |
| `pnpm admin:typecheck` | `tsc --noEmit` |
| `pnpm admin:lint` | `biome lint` + `tsc` |
| `pnpm admin:test` | `vitest run` |
| `pnpm admin:deploy` | 构建镜像 + 启动自证 + 推送 TCR（**写远端**，跑之前确认自己在做什么） |
| `pnpm admin:deploy:official` | 有可用代理时改用官方 Docker Hub 基础镜像 |

`apps/admin-web/package.json` 另有一批**上游模板脚本，本仓库不用**：
`simple`（不可逆删页面目录）、`i18n-remove`、`deploy`（`gh-pages`，推的是上游演示仓）、
`record` / `openapi`（对着 `config/oneapi.json` 那份上游演示 schema 生成 service 和 mock）、
`analyze`、`preview`、`preview:build`、`doctor`、`start` / `start:no-mock` / `start:pre` / `start:test`。
要动 `simple` 或 `i18n-remove` 前先读 `scripts/` 里对应脚本删了什么。

## 环境与地址（最容易出事的一块）

Umi 4.7 **只加载 `.env` 与 `.env.local` 两档**，且后者无条件覆盖前者——没有 `.env.production` 这一档。
本仓库的约定把这两档当成了「线上 / 本机」：

| 文件 | 入库 | 含义 |
| --- | --- | --- |
| `.env` | 是 | **生产档**。docker build 读它，`UMI_APP_API_BASE_URL` 被烘进 JS 产物，改完必须重新构建镜像才生效 |
| `.env.local` | 否 | **本机开发档**。`pnpm admin:dev` 用它当 `/api`、`/ws` 的代理目标 |
| `.env.example` | 是 | 模板：`cp .env.example .env.local` |

> **新克隆必须先复制出 `.env.local`。** 没有它，`config/proxy.ts` 的 dev 目标会取到 `.env` 的
> 生产域名——本地点「保存」就是往线上写数据（`config/proxy.ts:16-18` 原话）。

`.env.example` 的本机默认值：`UMI_APP_API_BASE_URL=http://127.0.0.1:8080`（Spring Boot）、
`UMI_APP_WS_BASE_URL=http://127.0.0.1:5090`（FastAPI 聊天服务）。
**改了 `.env` 要重启 dev server**，Umi 不监听 `.env`。

`UMI_APP_API_BASE_URL` **末尾不要带 `/api`**：`src/app.tsx:244` 把它当 axios `baseURL`，
而请求路径本身已含 `/api`（`/api/books` 等），写成 `https://…/api` 会打出 `/api/api/books`。
留空 = 同源模式，产物不带跨域地址，由容器里的 nginx 反代兜住（见「构建与部署」）。

## 路由与权限

路由表在 `config/routes.ts`，`src/access.ts` 定义三级角色：
`canSuperAdmin`（`role === 'superadmin'`）、`canAdmin`（`superadmin` 或 `admin`）、`canUser`（已登录）。

| 路径 | 页面 | 权限 |
| --- | --- | --- |
| `/user/login`、`/user/register`、`/user/register-result` | 登录/注册（`layout: false`） | 公开 |
| `/recipes/**` → list / review / categories / create / edit/:id / detail/:id | 菜谱管理 | `canAdmin` |
| `/novel/**` → list / review / new / book/:bookId / book/:bookId/edit / **book/:bookId/studio** | 小说书架、裁定、工作台 | `canAdmin` |
| `/users/**` → list / approval | 用户与小程序准入 | `canAdmin` |
| `/account/settings` | 个人资料与头像 | `canAdmin` |
| `/` | 重定向到 `/recipes/list` | |

三条写在代码里的约定，改路由时别破：

- `/chatbot` **整段注释掉了**（`config/routes.ts:140-144`）。页面代码还在 `src/pages/chatbot/`，
  要恢复就是取消注释，但 `/ws/chat` 的握手现在要 JWT + 作者作用域。
- 小说的动态段一律带 `book/` 前缀（`/novel/book/:bookId`）——写成 `/novel/:bookId` 会和
  `list`、`new` 抢匹配。
- 工作台 `/novel/book/:bookId/studio` 带 `layout: false`，跳出 ProLayout 的 mix 菜单，
  否则左栏被菜单挤掉。

未登录访问任何页面会在 `onPageChange` 里跳 `/user/login?redirect=…`（`src/app.tsx:161-169`）。

## 请求约定

- `config.ts:163-165` 的 `request: { dataField: 'data' }` 对应后端 `shared` 模块的 `Result<T>` 包装：
  业务数据在 `data`，`code` / `message` 由 `src/requestErrorConfig.ts` 处理。
- 请求路径**自带 `/api` 前缀**（`/api/users/me`、`/api/books`…），所以 `baseURL` 只能是裸域名或空串。
- 鉴权用 `localStorage` 里的 token + `Authorization` 头，不依赖 cookie；后端 CORS 已放开
  `AllowedOriginPatterns=*`，跨域直连可用。
- 401 / 业务失败的跳登录逻辑在 `src/requestErrorConfig.ts`（`LOGIN_PATH` + `redirect` 参数）。
- 服务层按模块分文件：`src/services/`（`user.ts`、`recipe.ts`、`novel.ts`、`file.ts`）是本项目在用的，
  类型从 `@po/types` 导入。**`src/services/ant-design-pro/` 是模板遗留**，里面只有
  `login`（已改指向真实后端 `POST /api/auth/login`）和 `currentUser`（`/api/users/me`）在用，
  `outLogin`（`/api/login/outLogin`）、`getNotices`、`rule` 系列打的都是后端没有的路径——
  `AvatarDropdown.tsx:40` 里的 `outLogin()` 已注释掉。新增接口写到 `src/services/<模块>.ts`，别加进这里。

## 目录结构

```
config/           config.ts（Umi 配置）、routes.ts（路由真源）、proxy.ts（dev 代理）、
                  defaultSettings.ts（ProLayout 主题）、oneapi.json、md-raw-loader.cjs
src/
  app.tsx         initialState、ProLayout 运行时配置、request 基址
  access.ts       角色 -> 权限布尔
  requestErrorConfig.ts  错误处理与登录跳转
  pages/          user / recipes / novel / system(users) / account / chatbot / exception
  components/     ErrorBoundary、Footer、HeaderDropdown、OfflineBanner、RightContent
  services/       user / recipe / novel / file + ant-design-pro（遗留，见上）
  locales/        zh-CN.ts、en-US.ts 及各语言目录
  utils/          avatar.tsx（顶栏头像兜底）、chinaDivision 等
mock/             仅 user.ts、utils.ts；另有 src/pages/**/_mock.ts 两处
nginx/            admin.conf.template + 16-admin-upstreams.envsh（容器内反代）
tests/            setupTests.ts
cloudflare-worker/  上游 Pro 演示的 `pro-api`（hono + wrangler），本仓库未使用，
                  只在 config/proxy.ts 的 test 档里被引用
```

## 国际化

`config.ts:135-141`：默认 `zh-CN`，`baseNavigator: true`（浏览器语言会覆盖默认值）。
`src/locales/` 下有 8 个语言族，但**只有 `zh-CN` 和 `en-US` 跟着业务走**——
其余 6 个（bn-BD、fa-IR、id-ID、ja-JP、pt-BR、zh-TW）没有小说模块的菜单键，是模板遗留。

新增或改文案时同步 `src/locales/zh-CN.ts` 与 `src/locales/en-US.ts`（Umi locale 插件的 TS 模块，不是 JSON）。
菜单键按 `menu.<路由段>` 生成，例如 `/novel` 的标题在 `menu.novel`。

## 样式

Tailwind v4 + `antd-style`。`config.ts` 里 `tailwindcss: {}` 已启用；
antd 侧在 `configProvider` 统一了 `variant: 'filled'` 与 `fontFamily: AlibabaSans`（`config.ts:147-157`）。
主题/导航设置集中在 `config/defaultSettings.ts`。组件级查询、props、废弃用法走本地
`@ant-design/cli`：在 `apps/admin-web/` 内 `pnpm exec antd ... --format json`，不要全局装。

## 测试与静态检查

- `vitest.config.ts`：`happy-dom` 环境、`globals: true`、`setupFiles: ['./tests/setupTests.ts']`，
  覆盖 provider v8。**`src/pages/user/login/login.test.tsx` 被显式排除**（依赖 Umi 自带的 Jest 跑法，
  Vitest 跑不动，文件仍在）。
- 当前在跑的 15 个用例文件集中在：`access` / `app` / `requestErrorConfig` / `utils`（头像、行政区划）/
  `account/settings` / `novel`（工作台 `useNovelRun`、`RunPanel`、`lineDiff`、`chapterRange`、
  `conflictLedger`、`chapterPlaceholder`、`studioConflict`）。
- Biome 负责 lint+format（`biome.json`），并在 `includes` 里排除了 `src/services`、`mock`、`public`、
  `tailwind.css` 等生成或静态目录。仓库根 `lint-staged` 会对本目录跑 `biome check`。
- 没有 e2e；`pnpm admin:lint` 与 `pnpm admin:test` 是本地门禁，CI 的 frontend job 覆盖同一组命令。

## 构建与部署

`Dockerfile` 两段式：Node 构建镜像（`pnpm build`，构建时读 `.env` 生产档）+ 官方 nginx 运行镜像。
运行期由 `nginx/16-admin-upstreams.envsh` 归一化两个上游，`admin.conf.template` 反代：

| 路径 | 上游变量 |
| --- | --- |
| `/api` | `ADMIN_API_UPSTREAM`（未设置则 `/api` 回 502） |
| `/ws/chat` | `ADMIN_CHAT_UPSTREAM`（未设置则聊天页与创作工作台不可用） |

键名刻意带 `ADMIN_` 前缀，避免 envsubst 撞环境变量名。共享的坑（nginx 启动期解析上游、
`# syntax=` 指令、envsubst 撞名）记在
[`apps/novel-web/DEPLOY_CLOUDRUN.md` 第 7 节](../novel-web/DEPLOY_CLOUDRUN.md)，
管理端特有部分记在本目录 `DEPLOY_CLOUDRUN.md`。镜像仓库名以控制台为该服务 provision 的名字为准，
不要按其他服务的命名规律推。

## 已知遗留

登记在这里，动它之前先确认目的；清理与否是单独的决策。

- `config.ts:183-185` 的 `analytics: { ga_v2: 'G-59NF1VHHPF' }` 沿用上游模板的 GA4 站点 ID，
  本仓库没有自己的属性——等于把管理端用量打到别人的统计里。
- 6 个未维护的语言包（见「国际化」）。
- `src/services/ant-design-pro/` 的死接口、`config/oneapi.json` 演示 schema、
  `mock/` 与 `record`/`openapi` 链路。
- `cloudflare-worker/`（`pro-api` demo）仍在树里，只在 `config/proxy.ts` 的 `test` 档被引用；
  `test`/`pre` 两档还指向上游演示域名。
- `.claude/skills/`、`docs/cheatsheet.*`、`CODE_OF_CONDUCT.md`、`codecov.yml` 等模板附带文件。

## 改代码时的注意事项

- **前后端字段变更先改 `packages/types/`**，再改调用方；类型包只放 `export type`，没有代码生成步骤。
- 新页面优先复用 Pro 组件与同类既有页面模式（`src/pages/recipes/list` 与 `src/pages/novel/list`
  是最近的两个样板），不引入第二套组件库或路由体系。
- 顶栏头像走 `src/utils/avatar.tsx` 的 `headerAvatarProps()`：ProLayout 在没有可用图标/标题时
  会把整块渲染成 `null`（不是空圆圈），所以 `avatarProps` 必须留兜底（`src/app.tsx:151-156`）。
- 登录成功但不跳转，先查登录后 `/api/users/me` 是否失败或角色不是 admin——会被权限静默打回登录页。
