# 言外书斋（apps/novel-web）

小说的 Web 阅读端，移动优先。需求与决策见仓库根目录 `NOVEL_WEB_PRD.md`。

## 跑起来

```bash
pnpm novel:dev        # http://localhost:8001，关 mock，走 config/proxy.ts 打到 127.0.0.1:8080
pnpm novel:mock       # 前端独立开发用：mock/novel.ts 顶掉 /api/books*，不需要后端
pnpm novel:typecheck
pnpm novel:lint       # biome check
pnpm novel:build
```

`novel:dev` 是默认档，读的是真库，与管理端 `/novel` 同源（先起着 `pnpm api:start`）。
`novel:mock` 返回的是 `mock/novel.ts` 里写死的《檐下三年》那 4 本书——**它们不在库里**，
所以那一档只能用来验排版、滚动位置与首屏，不能用来判断数据对不对。
（mock 的由来是 Java novel 模块没恢复时要把阅读三页跑通，那个前提已经过去了，故从默认档退到显式档。）

环境变量只有两档（Umi 4.7 在 `@umijs/core/dist/service/env.js` 里写死读 `.env` 与 `.env.local`，
**没有 `.env.production`**，且后读的 `.env.local` 无条件覆盖）：

- `.env` —— 生产值（`UMI_APP_API_BASE_URL=https://api.dingdingchu.site`，与两个小程序同一个 api 服务）。
  入库、进 docker 构建上下文，`max build` 把它内联进 JS 产物。
- `.env.local` —— 本机开发覆盖（`PORT=8001`、`http://127.0.0.1:8080`）。不入库、不进镜像，
  `cp .env.example .env.local` 得到。改完要重启 dev server，Umi 不监听 env 文件。

dev 一律同域打 `/api`（`src/app.tsx` 里 `baseURL` 只在 `NODE_ENV=production` 才取这个值），
所以 mock 与 `config/proxy.ts` 拦得住；生产才是绝对域名，跨域由后端 `SecurityConfig` 的
`AllowedOriginPatterns("*")` 兜着。域名的值与换域名要重新构建镜像等细节见 `DEPLOY_CLOUDRUN.md` §3。

**部署产物必须由镜像构建产出**：本机直接 `pnpm novel:build` 会读出 `.env.local` 的开发地址。

## 目录约定

- `config/config.ts`：部署形态（根路径 or `/novel/` 子路径）只改 `PUBLIC_PATH` 这一处；`layout` 插件刻意不启用，理由写在文件注释里。`metas` 覆掉了 Umi 默认的 `user-scalable=no` 并补上 `viewport-fit=cover`，安全区才有值。
- `config/routes.ts`：游客可读的三页不带 `access`；`/studio` 是 M3，届时再挂 `access: 'canAdmin'`。
- `src/layouts/index.tsx` + `src/components/Chrome.tsx`：全局外壳走 Umi 的约定式 layout。**不要**把壳放回 `app.tsx` 的 `rootContainer`——那里在 Router 与 initialState 的 Provider 外层，`useLocation` / `useModel` 会直接抛错，整站白屏。
- `src/app.tsx`：`getInitialState` 只做「有令牌才换用户」，换不到就降级为游客，绝不跳登录。
- `src/requestErrorConfig.ts`：与管理端同一套 `Result` 信封处理，唯一差别是 401 只在 `PROTECTED_PREFIXES`（`/studio`）内才回跳登录页。
- `src/services/book.ts`：只读接口。写接口在 `git show b23a633^:apps/admin-web/src/services/book.ts`，M3 恢复。
- `src/hooks/useReaderPrefs.ts` / `useReadingProgress.ts`：字号行距主题、逐书进度，全部只落 localStorage。进度冗余存了 `chapterIndex`，书架才不用为「读到第 N 章」再请求一次目录。
- `src/global.less`：设计令牌（纸墨色板 + 字体栈）全部在 `:root` 用 CSS 自定义属性声明，组件只引用 `var()`。断点与 PRD §4 对齐。

## 视觉系统

- 主色朱砂 `#a83e2b`，与 `config/config.ts` 里 antd 的 `colorPrimary` 同值——两套主色并排就是没做完的设计。
- **色板必须用 CSS 自定义属性，不能用 Less 变量**：阅读页三主题与系统深色都是运行时切换，
  Less 变量在编译期就定死了。
- 阅读页的 `--r-*` 一组变量**自带浅色值，不引用 chrome 的 `--accent`**：夜间模式下 chrome 把主色
  提到 `#d0795e`，白字压上去只剩 2.8:1；正文底色是用户显式选的，不该被系统偏好改掉。
  同理 `--on-accent`（主色作填充时的字色）在深色下要翻成墨色。
- 封面绝大多数为空。`components/BookCover.tsx` 按书名哈希出配色、把书名竖排（`writing-mode: vertical-rl`）
  生成排印封面——同一本书永远同一张，刷新不跳色；真封面到了直接走 `<img>`。
- 顶部读位线（`.reader-topline-fill`）由 scroll 回调直接改 `style.width`，不进取省状态：
  逐帧 `setState` 会让整篇正文重渲染（小程序那边踩过的同一类坑）。

## 已知的临时处理

`GET /api/books/:bookId/chapters` 目前把每章正文一起返回，移动端目录会因此超重。
前端先用 `toChapterBriefs()` 把正文从渲染路径上剥掉，真正的修法是后端加 `ChapterBrief`
投影（PRD §7-①，属 M1）。后端就绪后这段可以删掉，删时记得同步 `book/index.tsx`、
`read/index.tsx` 两处调用。

## 移动端实测口径

窄屏数据是用 375/320 宽的 iframe 量出来的（媒体查询按 iframe 视口生效），不是靠肉眼看：
320 与 375 均无横向溢出，书架两列、封面 3:4、标题两行封顶；筛选 input/搜索键 44px，
体裁标签横向单行滚动（375 下 472/375）；阅读页工具栏在 375 与 320 下都折成两行 = 113px，
所以 `.reader` 的 `padding-bottom` 留到 132px——实测「下一章」按钮与工具栏之间还剩 35px 空隙。
改这些数值时请连 `padding-bottom` 一起改。

量样式时的两个环境假象，别当成 bug 去修：隐藏文档（`visibilityState: hidden`）里
**CSS transition 不推进**，`getComputedStyle` 会读到换主题前的旧色值（重新加载即可验证）；
原生 `scroll` 事件也不触发，要手动 `window.dispatchEvent(new Event('scroll'))`。
