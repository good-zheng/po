# 叮叮厨 · 项目与个人介绍站

`po` monorepo 里的一个应用：静态站点，介绍「叮叮厨」（菜谱 + AI 做菜助手）、「言外 EchoTalk」（实时沟通洞察）与「言外书斋」（长文本一致性链路）三个项目，以及做它们的人。

## 来源与许可

- 模板：[AstroWind](https://github.com/arthelokyo/astrowind)（MIT，`LICENSE.md` 保留）。
- 引入方式：`git clone --depth 1`，取上游提交 `14e1a691f80548dcc36370847b1a02c0d0b12821`（2026-09-12），随后删除内层 `.git` 与 `package-lock.json`，并入 pnpm workspace。
- 已改写：`src/config.yaml`、`src/navigation.ts`、`src/pages/*`、`src/data/post/*`，以及博客列表/分类/标签页与 404 页的界面文案。模板自带的 demo 页面（`homes/`、`landing/`、`pricing`、`services`、`terms`、`privacy`）与示例文章已删除。
- 未改写：`src/components/`（widget 与通用组件）、`vendor/integration/`（把 `config.yaml` 编译成虚拟模块 `astrowind:config`）。升级时对比这几处与上游的差异即可。`layouts/PageLayout.astro` 只动了一处：不再默认渲染 `Announcement`（模板自带的「NEW Astro v7 is now available!」置顶条，会把自己的仓库链接推到访客面前）。需要公告条时，在页面里填 `announcement` slot 或直接把 `<Announcement />` 加回来。

## 命令（在仓库根执行）

| 目的                              | 命令                         |
| --------------------------------- | ---------------------------- |
| 本地开发                          | `pnpm brand:dev`             |
| 构建静态产物                      | `pnpm brand:build`           |
| 预览构建产物                      | `pnpm brand:preview`         |
| 类型 + lint + 格式检查            | `pnpm brand:check`           |
| 重新生成插画位图（OG 与博客封面） | `pnpm brand:assets`          |
| 镜像构建并推送云托管仓库          | `pnpm brand:deploy`          |
| 同上，用官方 Docker Hub 基础镜像  | `pnpm brand:deploy:official` |

产物在 `apps/brand/dist/`。改动之后走一遍 `pnpm brand:check && pnpm brand:build`。上线流程见 `DEPLOY_CLOUDRUN.md`（镜像 → 微信云托管内置仓库 → 控制台从镜像部署，端口 8080、健康检查 `/healthz`）。

排障：若 `astro dev` 报 `[astro] Unable to load your Astro config` 且提示 `Failed to load url /vendor/integration/index.ts`，`vendor/` 其实存在，是 Vite 依赖缓存过期所致（`git checkout` / `git restore` 整棵目录、或 `pnpm install` 之后最常见）。删 `apps/brand/.astro` 和 `apps/brand/node_modules/.vite` 再启动即可；`pnpm brand:build` 不受此影响。

## 目录要点

- `src/config.yaml`：站名、URL、SEO 元数据、博客路由与主题。
- `src/navigation.ts`：页头与页脚链接。
- `src/links.ts`：已上线项目的真实地址（言外书斋阅读端、管理后台）。首页作品卡、「叮叮厨的构成」里的管理后台卡、`novel.astro` 的页头按钮、`resume.astro` 的代表项目卡与 CTA、页脚「线上入口」组都从这里取，换域名或补 TLS 只改这一处。地址一律从云托管控制台抄，别按规律推。阅读端现在只有 http 通（`curl https://novel.dingdingchu.site/` 拿不到响应，证书配好就把 scheme 改成 https）；管理后台 http 会被平台 308 回 https，所以直接写 https。外链由 `Projects.astro` 按 `^https?://` 自动补 `target="_blank" rel="noopener noreferrer"`，页脚靠链接上的 `target` 字段，`CallToAction` 的 action 靠 `Button.astro` 对 `target` 的处理。
- `src/pages/index.astro`：首页由 widget 组合而成，锚点 `#products` / `#projects` / `#screens` / `#architecture` / `#quick-start` / `#decisions` / `#story` / `#faqs` / `#cta` 与导航、页脚对应。`#products` 是三件作品的入口卡，`#projects` 往下仍是叮叮厨的构成，`#screens` 是叮叮厨的真机截图，`#quick-start` 与 `#decisions` 同样只讲叮叮厨；`Stats` 那块的标题已限定为「叮叮厨的数字」，别把它读成整仓库的总数。
- `src/pages/yanwai.astro`：言外 EchoTalk 的产品页，锚点 `#why` / `#versus` / `#pipeline` / `#insight` / `#sample` / `#shot` / `#decisions` / `#reuse` / `#status` / `#faqs`。内容以 `apps/echo-talk` 与 `services/api/talk`、`services/agent-talk` 的现有代码为准；性能目标值一律标注为「未实测」，不写成结论。
- `src/pages/novel.astro`：言外书斋（长文本一致性链路）的项目页，路由仍是 `/novel`，锚点 `#why` / `#versus` / `#pipeline` / `#canon` / `#decisions` / `#reuse` / `#status` / `#faqs`。内容以 `services/agent-novel`、`services/api/novel`、`apps/admin-web/src/pages/novel`、`apps/novel-web` 的现有代码为准；节点数、规则数、注入预算、表数与 2026-10-10 那次三章实测的入库形状都取自仓库与 `NOVEL_AGENT_PRD.md` §15.19，「50 章盲读冲突率」这条验收线尚未测出，页面上只写「还没测」。这一页的强调色是琥珀 `#F59E0B` 加正典蓝 `#60A5FA`（言外页用靛蓝与青），与叮叮厨的橙紫并行，别混用。
- `src/pages/resume.astro`：简历页。`#career` 时间线已按本人 2026-10 版简历 PDF 填实（六段任职 + 一段暂离 + 两段教育，倒序），不再有占位条目；`ghost` 字段现在没有条目在用，组件仍保留该形态。这一页的数字分两类，页首 `Note` 已写明：三件作品的能在仓库与线上接口核对，任职期间的百分比与绩效只在 PDF 与背调里。
- `src/data/post/*.md`：开发手记。front matter 的 `category` 与 `tags` 会生成分类页与标签页，值请写 ASCII——中文会被罗马化成带调号的拼音 slug。
- `~/` 是 `src/` 的别名。
- 图片走 `src/components/common/Image.astro`：远程 CDN 地址由 unpic 改写，本地图片由 Astro 内置 Sharp 处理。
- 插画全是手写 SVG：源文件在 `src/assets/illustrations/`（只作生成源，不参与打包）和 `src/assets/images/`（被页面直接引用）。配色跟着主题走——蓝 `#0161EF`、紫 `#6D28D9`、橙 `#FB923C`、深蓝底 `#0B1220`。
- Astro 默认拒绝栅格化 SVG 源（`UnsupportedImageFormat`，构建直接失败）。所以页面直接引用的 SVG 必须带 `format: 'svg'` 直通；而博客封面与 OG 图所在的模板组件写死了 `format="webp"`，只能先用 `scripts/gen-rasters.mjs` 转成位图。改完 `src/assets/illustrations/` 下的任何 SVG，跑 `pnpm brand:assets` 再把产物一起提交。
- 画面里不放可读文字（OG 图与 `src/assets/images/screenshots/` 下的真机截图除外），避免被误读成真实产品截图。
- widget 的 `icon` 必须存在于 `@iconify-json/tabler`，否则 `astro build` 在渲染阶段直接报 `Unable to locate "tabler:xxx" icon!`（`tabler:captions`、`tabler:zigzag` 就没有）。拿不准时读 `node_modules/@iconify-json/tabler/icons.json` 的 `icons` 与 `aliases` 键名核对。
- `Content` 只用于「文字 + 配图」的两栏版式：它把文字列写死成 `md:basis-1/2`，右列无论有没有 `image` 都占掉一半宽度。没有配图的清单段落要用 `Features`（整宽网格，`columns` 控列数），否则正文会被挤进左半边、右半留白，长描述的中文条目在窄栏里还会撑出大片空隙。段落式的收尾陈述放不进 `Features`（它没有 `content` 插槽），用紧随其后的 `Note` 色带承载。

## 有意留下的占位

页面里的 `TODO` 不是遗漏：

- `src/config.yaml` 的站点域名与社交账号。**部署前必须换成真实域名**，sitemap、Open Graph 与 RSS 的绝对链接都由它生成。镜像构建可以不脏仓库：`SITE_URL=https://真实域名 pnpm brand:deploy` 会在容器里改写 `src/config.yaml`（域名烘进产物，换域名要重新构建）。仓库里这份仍是 `https://example.com`，而 `www.dingdingchu.site` 已经有一个旧构建在线上跑着——`curl -s https://www.dingdingchu.site/ | grep -o 'https://example.com[^"]*'` 能看到 canonical 与 og:url 都指向占位域名。下次部署带上 `SITE_URL` 才会一起改掉，否则新页面上线了、SEO 绝对地址还是错的。
- 真机截图与录屏：`src/assets/images/screenshots/`（叮叮厨首页与 AI 助手、言外会话页）和 `public/demo/`（首页滚动录屏 + 它的 poster）。截图必须放在 `src/assets/images/` 下面——`Image` 的字符串路径由 `src/utils/images.ts` 里的 `import.meta.glob('~/assets/images/**')` 解析，放在别的目录会被当成远程 URL 直接交给 Sharp，构建时报 `LocalImageUsedWrongly`。竖屏素材不放进 `Gallery`——那个组件写死 `aspect-[4/3] object-cover`，一张 9:20 的手机屏会被裁掉八成；录屏也不走 `Video` 组件，它把画面框死成 `aspect-video`，竖屏会被压扁。两处都改用页面里的原生元素（`Content` 的 `image` 插槽套 `Image`；`<video preload="none">` 配 poster，点了才下载）。poster 由 `pnpm brand:assets` 从首页截图烘出来，换截图后重跑。
- 项目卡片区与插画仍是示意 SVG，等三端有公网访问后可替换（直接换 `src/assets/images/` 下的同名文件，比例已按 16:9 与 16:10 对齐）。
- 另一段录屏（首页切「最多点赞」排序）没有放上来：那几帧里扬州三丁包、镇江肴肉显示的是无封面占位图，等缺封面的菜谱补齐之后再替换，否则等于把未完成的数据摆到门面里。
- 言外的公开体验入口与录屏。产品页只写仓库里已存在的页面、接口与表；提审通过后再放入口，体验码会失效所以不写。
- 简历页有意**不**公开的字段：年龄、性别、籍贯、期望薪资，以及 PDF 原件本身。前三项写进公开页会被搜索引擎与 HR 系统长期抓取，薪资数字写死还会削掉议价空间；PDF 不放 `public/` 是因为它含这些字段，而且站内下载要换简历就得重建镜像。现在的口径是「来信单独发」，见页面顶部 `Note` 与底部 `CallToAction`。若哪天要挂下载，先确认 PDF 已去掉这些字段。
- 简历 PDF 里印的 `github.com/good-zheng/po` 对未登录访客返回 404（私有或未建），所以站内任何地方都不挂这个链接；改成公开仓库后再补进 `src/links.ts`。同一份 PDF 写的「微信小程序搜索：叮叮厨」也与站内口径不符——小程序目前是体验版，页面里不写成「可搜索」。
- 站名仍是「叮叮厨」。`src/config.yaml` 的 `site.name` 会同时影响页头 Logo、OG 站点名与 Organization 结构化数据，页头那个 🍳 硬编码在 `src/components/Logo.astro`；若要改成个人品牌名，这三处一起动。言外页与简历页都设了 `ignoreTitleTemplate: true`，避免标题被拼成「言外 · 叮叮厨」。

联系方式（手机 / 邮箱 / 微信）集中在 `src/contact.ts`，联系页、关于页、简历页与页脚图标都从这里取，改一处即可。现在的值是 2026-10 投递版简历 PDF 上那一套：邮箱 `185736951@qq.com`，微信位填的是手机号（PDF 里电话与微信是同一个号）。注意 `mailto` 在静态站上会被爬虫直接抓到，垃圾邮件会变多；需要时可改成图片或被 JS 拼装的形式。改邮箱时 `contact.astro` 的 meta description 也由这张表生成，不用单独动。

## 上游自带的工作流文件

`.agents/`、`AGENTS.md`、`CLAUDE.md` 描述的是模板自身的约定。与本项目冲突的部分（英文文案、示例内容）以本 README 为准。

与部署相关的上游文件已经处理过：

- 已删除 `docker-compose.yml` 与 `.dockerignore`——上游假设「目录即仓库」，而本项目的镜像以仓库根为构建上下文（pnpm workspace 的 `--frozen-lockfile` 需要看到全部 importer），忽略规则统一在根 `.dockerignore`。
- `netlify.toml`、`.stackblitzrc` 保留但未接线：本项目走微信云托管，不走 Netlify。
- `.github/workflows/actions.yaml` 是**死文件**：GitHub 只执行仓库根的 `.github/workflows/`，嵌在 app 里的不会被触发；它用的还是 `npm ci`，而本目录已没有 `package-lock.json`。介绍站的校验挂在根 `.github/workflows/ci.yml` 里。
