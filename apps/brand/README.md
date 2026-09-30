# 叮叮厨 · 项目与个人介绍站

`po` monorepo 里的一个应用：静态站点，介绍「叮叮厨」这个菜谱 + AI 做菜助手项目，以及做它的人。

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
- `src/pages/index.astro`：首页由 widget 组合而成，锚点 `#projects` / `#architecture` / `#quick-start` / `#decisions` / `#story` / `#faqs` / `#cta` 与导航、页脚对应。
- `src/data/post/*.md`：开发手记。front matter 的 `category` 与 `tags` 会生成分类页与标签页，值请写 ASCII——中文会被罗马化成带调号的拼音 slug。
- `~/` 是 `src/` 的别名。
- 图片走 `src/components/common/Image.astro`：远程 CDN 地址由 unpic 改写，本地图片由 Astro 内置 Sharp 处理。
- 插画全是手写 SVG：源文件在 `src/assets/illustrations/`（只作生成源，不参与打包）和 `src/assets/images/`（被页面直接引用）。配色跟着主题走——蓝 `#0161EF`、紫 `#6D28D9`、橙 `#FB923C`、深蓝底 `#0B1220`。
- Astro 默认拒绝栅格化 SVG 源（`UnsupportedImageFormat`，构建直接失败）。所以页面直接引用的 SVG 必须带 `format: 'svg'` 直通；而博客封面与 OG 图所在的模板组件写死了 `format="webp"`，只能先用 `scripts/gen-rasters.mjs` 转成位图。改完 `src/assets/illustrations/` 下的任何 SVG，跑 `pnpm brand:assets` 再把产物一起提交。
- 画面里不放可读文字（OG 图除外），避免被误读成真实产品截图。

## 有意留下的占位

页面里的 `TODO` 不是遗漏：

- `src/config.yaml` 的站点域名与社交账号。**部署前必须换成真实域名**，sitemap、Open Graph 与 RSS 的绝对链接都由它生成。镜像构建可以不脏仓库：`SITE_URL=https://真实域名 pnpm brand:deploy` 会在容器里改写 `src/config.yaml`（域名烘进产物，换域名要重新构建）。
- 真实产品截图。首页与项目卡片区现在是示意插画；等三端有公网访问后换成真机截图（直接替换 `src/assets/images/` 下的同名文件，比例已按 16:9 与 16:10 对齐）。

联系方式（手机 / 邮箱 / 微信）集中在 `src/contact.ts`，联系页、关于页与页脚图标都从这里取，改一处即可。注意 `mailto` 在静态站上会被爬虫直接抓到，垃圾邮件会变多；需要时可改成图片或被 JS 拼装的形式。

## 上游自带的工作流文件

`.agents/`、`AGENTS.md`、`CLAUDE.md` 描述的是模板自身的约定。与本项目冲突的部分（英文文案、示例内容）以本 README 为准。

与部署相关的上游文件已经处理过：

- 已删除 `docker-compose.yml` 与 `.dockerignore`——上游假设「目录即仓库」，而本项目的镜像以仓库根为构建上下文（pnpm workspace 的 `--frozen-lockfile` 需要看到全部 importer），忽略规则统一在根 `.dockerignore`。
- `netlify.toml`、`.stackblitzrc` 保留但未接线：本项目走微信云托管，不走 Netlify。
- `.github/workflows/actions.yaml` 是**死文件**：GitHub 只执行仓库根的 `.github/workflows/`，嵌在 app 里的不会被触发；它用的还是 `npm ci`，而本目录已没有 `package-lock.json`。介绍站的校验挂在根 `.github/workflows/ci.yml` 里。
