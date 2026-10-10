# 小说 web 端（apps/novel-web）PRD — 待评审

版本：v0.1（评审稿）｜日期：2026-10-02｜状态：**未开始实施，等本稿拍板**

本稿的依据全部来自仓库现状与 git 历史，不含推测：

- 小说业务线在 `b23a633`（"feat: 删掉小说业务线，新增烹饪 Agent 并接入 App 聊天框"）被整体下线。删除前的 web 端是 `apps/admin-web/src/pages/books/**`，属桌面后台，无任何移动适配。
- 该提交同时新增 agent-cooking、cooking-app 移动端与 agent-core 修复，**不能 `git revert`**，只能按文件捞回并手工插回（冲突面见 §9）。
- `apps/novel-web/` 目前是一个空目录，git 历史里从未存在过，本 PRD 把它当作新 app 的落位。

---

## 1. 已确认的方向

| 决定 | 结论 | 由此产生的硬约束 |
| --- | --- | --- |
| 代码载体 | 新建 `apps/novel-web`（fork `apps/admin-web` 的 Umi Max 骨架） | 独立 workspace 包、独立构建、独立部署位；不牵动管理端布局 |
| 后端与数据 | Java `novel` 模块 + `schema.sql` 三表 + `packages/types/src/novel.ts` + `services/agent-novel` 创作链路，全部恢复 | 一期就要动 `services/api/pom.xml`、`api-bootstrap` 依赖、`SecurityConfig`、CI 与 chat 装配 |
| 移动端优先路径 | 阅读：书架列表 → 书详情/目录 → 连续正文阅读页 | 创作端（建书、录章节、人物管理）在手机上只做"能看能改"，不追求顺手 |
| 登录 | 按现有链路扩展，不新造鉴权 | 读者侧游客可读，创作侧沿用 `client:'admin'` + `canAdmin`（§5） |

## 2. 目标 / 非目标

**目标**

1. 手机浏览器上能读完一本书：打开快、字好读、翻页不丢进度、弱网不白屏。
2. 小说数据的唯一真源回到 `services/api/novel` + MySQL 三表，web 端、AI 创作链路、未来的小程序共用同一套契约（`packages/types`）。
3. `agent-novel` 的产出真正落库——这是历史上没做完的一段（§7）。

**非目标（一期明确不做）**

- 付费、书架收藏、评论、划线笔记、TXT/EPUB 导入导出。
- 多作者协作与按作者隔离数据（`book.authorId` 字段保留但不做权限细分）。
- iOS/Android 原生壳、离线下载、PWA Service Worker。
- 读者账号体系（不做注册、不做个性化推荐）。
- token 刷新与服务端登出——现状本来就没有，本 PRD 不补（风险见 §10）。

## 3. 用户与场景

- **作者（你本人）**：在**管理端 `apps/admin-web` 的 `/novel/**` 创作工作台**建书、维护正典设定、复核冲突；偶尔在手机上确认"昨天那本生成到第几章了"。角色 = `admin|superadmin`。创作端**不在本站**（原 `/studio` 方案已作废，见 `NOVEL_AGENT_PRD.md` §10）。
- **读者（手机上的访客）**：从分享链接或首页进入，**无需登录**即可浏览书架、看目录、读正文；换设备后不承诺进度同步（一期进度只存本机）。
- **审核者/未来的自己**：三个月后靠 `novel-web` 判断这条线还值不值得继续投入，因此页面上的每个数字都必须来自接口，不允许假数据兜底。

## 4. 信息架构与页面

`novel-web` 路由（`config/routes.ts` 新写，不继承 admin 的菜单树）：

| 路由 | 页面 | 登录 | 断点行为 |
| --- | --- | --- | --- |
| `/` | 书架：按 `updatedAt` 倒序的书卡（封面/书名/类型/状态/总字数） | 否 | <768px 两列卡；≥768px 四列 |
| `/book/:id` | 详情：简介 + 章节目录（倒序可切） + 人物卡列表 | 否 | 手机上目录做成吸底「目录」按钮唤起的全屏面板 |
| `/read/:bookId/:chapterId` | 阅读页：正文流 + 上下章切换 + 字号/行距/主题 | 否 | 核心页，见 §6 |
| `/search` | 按书名/类型筛选书架 | 否 | 与 `/` 共用组件，手机端是顶部搜索条 |
| `/user/login` | 账密登录（从 admin 复制后删掉验证码 Tab） | 是 | 手机端表单宽度 100%、不居中成卡片 |
| ~~`/studio` `/studio/book/:id`~~ | ~~创作端~~ | — | **已作废，移到 admin-web `/novel/**`**（`NOVEL_AGENT_PRD.md` §10） |

一期交付 `/`、`/book/:id`、`/read/:bookId/:chapterId`、`/user/login`；`/search` 在 M3。
创作端移出后本站**没有任何需要 `access` 的路由**：`requestErrorConfig.ts` 的
`PROTECTED_PREFIXES = ['/studio']`（`src/requestErrorConfig.ts:16`）随之失去用途，
`/user/login` 一期只作为"二期跨设备进度同步"的预留口保留（现在没有页面消费它）。
真要清理就在 M3 一并处理，别单开一次改动。

## 5. 登录与权限（"按现有拓展"的具体含义）

复用现有链路，不改后端鉴权模型：

- 登录：`POST /api/auth/login`，body `{username, password, client: 'admin'}` → `Result<LoginResponse>`（字段 `id/token/username/nickname/role/approvalStatus`）。
- token 存放：与 admin 一致，`localStorage['token']`；`src/requestErrorConfig.ts` 的 `requestInterceptors` 注 `Authorization: Bearer <token>`。
- 初始化：`getInitialState` → `GET /api/users/me` → `Result<User>`。
- 401：`errorHandler` 清 token 并跳 `/user/login?redirect=<原路径>`，redirect 必须过同源校验（沿用 admin 的 `getSafeRedirectUrl`）。
- 权限位：`access.ts` 保留 `canAdmin`/`canUser`，创作路由写 `access: 'canAdmin'`。

三条必须写进实施约定的坑：

1. **不新增 `client` 值**。后端 `ClientConstants` 只认 `admin`/`app`，且 admin 只允许 `admin|superadmin` 角色。创作端就是管理员在用，沿用 `admin` 即可；读者侧因为是 `permitAll`，压根不需要 token。这样"按现有拓展"= 零鉴权改动。
2. **游客可浏览、绝不强制跳登录**。阅读三页在无 token 时必须正常渲染；只有进 `/studio` 才要求登录。这条是既有产品约定（小程序端同样如此），历史上因为强制跳转导致过返回白屏。
3. **fork 后要处理两处 admin 残留**：`mock/user.ts` 里 mock 的 `GET /api/currentUser`、`POST /api/login/account` 与真实接口不一致，开着会造成"登录假成功"，直接删；`app.tsx` 的 `isAdminRole` 目前会把非 admin 用户清 token 踢回登录页——游客浏览不能被它拦，需要把它的作用域收窄到 `/studio`。

后端要插回的授权规则（删除前是这样，`091ce5d` 之后文件已变，按现状重插）：

```java
.requestMatchers(HttpMethod.GET,
    "/books", "/books/genres", "/books/*",
    "/books/*/chapters", "/books/*/chapters/*",
    "/books/*/characters", "/books/*/characters/*").permitAll()
...
.requestMatchers("/books/**").access(ADMIN_CLIENT)   // 非 GET
```

## 6. 阅读页（移动端的主战场）

功能条款：

- 正文来自 `GET /api/books/:bookId/chapters/:chapterId`（`Result<BookChapter>`，含 `content`）。
- 上下章导航用目录数据在前端算，不新增接口。
- 进度：`localStorage` 存 `novel.progress.<bookId> = {chapterId, scrollTop}`；书架卡上显示"读到第 N 章"。二期若要跨设备再入库（新表 `book_read_progress`，一期不建）。
- 排版可调：字号 5 档（15–23px）、行距 2 档、亮/暗/护眼三主题，选择存 `localStorage`，跟随系统 `prefers-color-scheme` 为初值。

性能与体验硬指标（不达标不算完成）：

| 指标 | 目标 | 怎么测 |
| --- | --- | --- |
| 章节列表响应体 | 100 章的书，目录接口 ≤ 50 KB | 必须做后端改造，见 §7-①；用 Network 面板量 |
| 阅读页首屏 | 375×667、Fast 3G 下 LCP ≤ 2.5 s | Lighthouse 移动端 |
| 正文滚动 | 3000 字单章滚动无可见掉帧 | 不做逐段 setState；正文按 block 虚拟化，滚动只更新一次进度（历史上 Taro 端逐 token setData 是 O(n²) 的教训，同类问题） |
| 触摸目标 | ≥ 44×44 px | 走查 |
| 安全区 | iPhone 刘海/底部横条不遮正文与控制条 | `env(safe-area-inset-*)` + `viewport-fit=cover` |
| 无障碍 | 正文对比度 ≥ 4.5:1；字号/主题按钮有 `aria-label`；图片有 `alt` | WCAG AA 走查 |

## 7. 接口契约：恢复项 vs 净新增

**原样恢复**（`b23a633^` 的 `/api/books/**`，15 个前端 service 函数一一对应）：
`GET /books/genres`、`GET /books`（`page/size/genre/status/keyword`，Spring `Page` 信封，前端取 `content/totalElements`，页码 0 起）、`GET|POST|PUT|DELETE /books[/:id]`、`GET|POST /books/:bookId/chapters`、`GET|PUT|DELETE /books/:bookId/chapters/:chapterId`、角色同构。删除一律软删（`deletedAt`）。

业务规则保持不变：状态白名单 `{ongoing, completed, paused}`；`chapterIndex` 留空＝最大序号 +1；章节字数＝`content.replaceAll("\\s","").length()`；书的 `wordCount` 在章节增改删后用 `IFNULL(SUM(word_count),0)` 重算；删书级联软删章节与人物；`NovelGenres.ALL` 十项（玄幻/武侠/科幻/言情/悬疑/历史/都市/游戏/恐怖/其他）。

**净新增（不是恢复，是这次要写的代码）**：

1. **目录轻量投影**。删除前的 `GET /books/:bookId/chapters` 返回 `List<BookChapter>`，**含每章完整 `content`**——桌面表格无所谓，手机上读一本书会把几十万字一次拉下来，直接否掉阅读体验。方案：新增 `ChapterBrief` 投影（`id/chapterIndex/title/wordCount/createdAt`），`GET /books/:bookId/chapters` 默认走 brief，正文只在单章接口给。这是本 PRD 里唯一改既有契约的点，需要 admin 端确认无人依赖旧返回。
2. **agent-novel 的落库通道**。历史代码里 `NovelStore` 只有进程内 `MockNovelStore`，注释写着"未来接 Java novel REST"但从未实现。这次要写 `HttpNovelStore`：`save_book/save_chapters/save_characters/list_books` 打到 `/api/books/**`，鉴权用一次性服务凭据而不是把管理员密码写进环境变量（具体方式实施前定，倾向 `SecurityConfig` 里已有的 `/talk/internal/**` 那种内部路径）。
3. **封面**。旧 `BookForm` 的封面是手填 URL 文本框。项目里已有 COS 上传链路（头像/菜谱封面都是"地址入库、文件进对象存储"），创作工作台（admin-web `/novel`）建书时改成走 COS 上传，落库只存公网 URL——不新造第二套上传。

## 8. 数据模型与库表状态

三表结构照删前恢复进 `services/api/api-bootstrap/src/main/resources/schema.sql`：`book`（`id/author_id/title/description/cover_image/genre/status/word_count/deleted_at/created_at/updated_at`，`idx_book_author`）、`book_chapter`（`id/book_id/chapter_index/title/content/word_count/deleted_at/…`）、`book_character`（`id/book_id/name/description/avatar/…`）。实体已是 MyBatis-Plus 形态，与现基础设施兼容。

**必须先核再动工的一件事**：那次删除只删了 `schema.sql` 里的建表语句，**没有 DROP**。本地 Docker MySQL 和线上库里的 `book*` 三张表很可能还在、且带旧数据。恢复脚本要做的是"表存在则跳过、不存在则建"，并先出一份现状（表在不在、有多少行、字段是否与旧 entity 对得上）。核过之后才能决定是留数据还是清库重灌。

## 9. 恢复动作清单（按不能 revert 的前提手工做）

| # | 动作 | 冲突面 |
| --- | --- | --- |
| 1 | `git show b23a633^:…` 捞 `services/api/novel/**`（19 文件） | 无，模块自洽 |
| 2 | 父 `services/api/pom.xml` 加回 `<module>novel</module>`，`api-bootstrap` 加 `po-novel` 依赖 | 现 modules 是 shared/identity/recipe/api-bootstrap |
| 3 | `schema.sql` 追加三表 | 追加位置变了（现尾部是 recipe 之后的新表） |
| 4 | `SecurityConfig` 插回 books 授权规则 | 文件被 `091ce5d` 改过，白名单行号与结构都变了，按现状插 |
| 5 | `packages/types/src/novel.ts` + `index.ts` 追加导出 | `index.ts` 已含 RecipeBrief 等新导出，只能追加 |
| 6 | 前端页面从 admin 迁到 novel-web | 不照搬：只取数据层与状态映射（`statusColorMap`/`genreColorMap`/`buildBookInitialValues`），UI 按 §4、§6 重写 |
| 7 | `services/agent-novel/**` + `chat/app/agent.py` 装配 | 旧测试测的是"WS 端到端 conceive→outline→interrupt→resume yes→已归档入库"；chat 现按 `_builtin_agents` 只装 cooking（agent.py:237-254），要按新形态追加 novel 插槽并重写 `test_novel_wiring.py` |
| 8 | CI 与脚本 | `.github/workflows/ci.yml` 删过 agentnovel 的安装与 pytest 步骤；根 `package.json` 删过 `agentnovel:test`；`scripts/run-service.mjs` 删过 agentnovel 分支 |
| 9 | `infra/nginx/nginx.conf` + `docker-compose.yml` | compose 里 `web:` 服务用的就是 `apps/admin-web/Dockerfile` + 单份 nginx.conf，novel-web 的部署位需要你拍板（§11-Q2） |
| 10 | LangGraph 检查点 | 若沿用 novel 的 interrupt 人工确认，需要 redis-stack（带 JSON+Search 模块），普通 redis 会静默退化成内存态 |

## 10. 里程碑

- **M0 核现状**：出"三张表是否存在 + 行数 + 字段差"报告；确认部署形态。不写业务代码。
- **M1 后端恢复**：§9 的 1–5 步 + `ChapterBrief` 投影；验收 = `mvnw` 编译过、`GET /api/books/genres` 在带 token 与不带 token 两种情况下都返回 200，`POST /api/books` 不带 token 返回 401/403。
- **M2 阅读端（移动优先）**：`novel-web` 骨架 + 书架/详情/阅读三页；验收 = §6 全部指标在真机 iPhone 与 375px 安卓上通过。**骨架已落地并通过本地测量，见 §14；真机验收仍未做。**
- **M3 检索与清理**：`/search` 筛选 + 把因创作端移出而失效的 `/studio` 相关残留（`PROTECTED_PREFIXES`、登录页文案）收干净。**原"M3 创作端 /studio 四页"取消**，创作工作台改由 `NOVEL_AGENT_PRD.md` §10 + 里程碑 N5 交付（含 COS 封面上传，见 §9-③）。
- **M4 创作链路**：`agent-novel` + `HttpNovelStore` + chat 装配 + wiring 测试；验收 = 在 chat 里说"帮我写一本玄幻小说"，走完 interrupt 确认后 `/api/books` 能查到新书且 web 端读得到。
- **M5 部署**：镜像/容器与 nginx 接上，留一份台账文档 + 一个可重跑的部署脚本。**已交付（2026-10-10）**：`apps/novel-web/Dockerfile` + `apps/novel-web/nginx/novel.conf.template` + `scripts/deploy-novel.sh`（`pnpm novel:deploy`），台账见 `apps/novel-web/DEPLOY_CLOUDRUN.md`。

## 11. 验收标准（关键场景）

- Given 未登录的用户，When 打开 `/read/1/1`，Then 正文完整渲染、无跳登录、控制台无 401。
- Given 一本 100 章的书，When 打开 `/book/1`，Then 目录响应 ≤ 50 KB，且**不出现正文**。
- Given 读到第 7 章滚动到 40% 处，When 关闭并同日重开 `/`，Then 该书卡片显示"第 7 章"，点进去回到原滚动位置。
- Given 字号调到最大（23px）且 320px 宽，When 渲染 3000 字章节，Then 无横向滚动条、无文字截断。
- Given 管理员在 **admin-web `/novel/new`** 新建书并录一章，When 读者打开本站 `/`，Then 该书可见，且 `wordCount` 等于该章去空格字数。（原"在 `/studio` 新建"场景随创作端移出而改写；跨站验收：管理端写入 → 阅读端可读）
- Given 非 admin 角色用户持有 token，When 访问 `POST /api/books`，Then 403 且前端提示"没有访问权限"，不跳登录页。

## 12. 风险

| 风险 | 处置 |
| --- | --- |
| 线上/本地遗留 `book*` 表结构与旧 entity 不一致，恢复后读写错位 | M0 先核库再动代码，禁止盲建表 |
| `ChapterBrief` 投影改了既有契约 | 全仓 grep 确认无调用方依赖旧返回，单独一个 commit 便于回退 |
| JWT 24h、无刷新、无服务端登出 | 一期沿用（阅读不受影响，创作端掉线重登）；若你要求长会话，另开需求补 refresh，不在本 PRD 里偷偷做 |
| `git revert` 想走捷径 | 明令禁止：会把 agent-cooking 与 cooking-app 移动端一起删掉 |
| AI 生成的整本书质量不可控 | M4 保留旧设计里的 interrupt 人工确认，不自动入库 |

## 13. 还需要你拍板

1. **旧数据要不要留**：`book*` 三表若有旧行，是清掉重新长，还是保留并在页面上标注"历史数据"。
2. **部署形态**：✅ **已定（2026-10-10）**——独立容器 + 根路径（`apps/novel-web/Dockerfile` 自带 Nginx，`/api` 反代到 api 服务），与 `config.ts` 里 `PUBLIC_PATH='/'` 的假设一致；不走 `/novel/` 子路径，避免阅读分享链接带前缀。台账与可重跑脚本见 `apps/novel-web/DEPLOY_CLOUDRUN.md`、`scripts/deploy-novel.sh`（即 M5）。
3. **`/studio` 放哪**：✅ **已定（2026-10-03）**——回 admin-web，做成 `/novel/**` 创作工作台，与现有管理 UI 整合；理由与页面方案见 `NOVEL_AGENT_PRD.md` §10。本站不再规划创作页。
4. **M4 的落库鉴权方式**：内部路径 + 服务凭据，还是给 agent 单设一个 admin 账号。倾向前者，但这会动 `SecurityConfig`，需要你同意。

## 14. M2 实现日志（骨架已落地，实测口径如下）

跑通命令：`pnpm novel:dev`（默认档，关 mock、经 `config/proxy.ts` 打真后端 8080）、
`pnpm novel:mock`（`apps/novel-web/mock/novel.ts` 顶掉 `/api/books*`，不需要后端，但那 4 本书是假的，
不要用它判断数据对不对）、`pnpm novel:typecheck`、`pnpm novel:lint`、`pnpm novel:build`。

搭骨架时撞到并固定下来的四条，后续 M3/M4 别再撞：

1. **全站外壳必须走 `src/layouts/index.tsx`**，不能放 `app.tsx` 的 `rootContainer`：那里在 Router 与
   initialState 的 Provider 之外，`useLocation` / `useModel` 会抛错整站白屏（这次真炸过一次）。
2. **请求不设绝对 baseURL**：始终同域打 `/api`，dev 由 proxy/mock 接。写死 127.0.0.1:8080 会同时绕过
   mock 层与代理，本地看到的接口行为失真。
3. **Umi 默认 viewport 带 `user-scalable=no`** 且没有 `viewport-fit=cover`，既禁了系统级缩放又让安全区
   取值失效；已用 `config.ts` 的 `metas` 覆盖（实测构建产物里只有一条 viewport，不重复）。
4. **阅读页工具栏在 375px 与 320px 下都折成两行（113px 高）**，`.reader` 的 `padding-bottom` 因此留到 132px；
   动按钮数量或尺寸时要连着改，否则末段正文会被压住。

测量口径：窄屏指标用 375/320 宽的 iframe 取 `getBoundingClientRect`（媒体查询按 iframe 视口生效），
不是肉眼看图。已量化通过：书架两列无横向溢出、点区 ≥44px、目录 12 条 52px 行、滚动位置跨会话恢复、
字号/行距/主题三档持久化。

仍未验的（不要当成已通过）：真机 iOS Safari 与微信内置浏览器的安全区与 `100dvh` 表现；
§6 的 Fast 3G LCP ≤2.5s（当前 `umi.js` gzip 289 KB，主要成本在 React/Umi 与 antd 运行时本身，
mock 环境测不出真实网络指标）。

**未接 CI**：`.github/workflows/ci.yml` 的 Frontend job 目前只跑 `admin:lint`/`admin:build`，
novel-web 的 `novel:lint`/`novel:typecheck`/`novel:build` 还不在门禁里。该文件已有未提交的改动，
所以这一步留到 M5 一起接，避免和别人的在途修改混在同一个 diff 里。
