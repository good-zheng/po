# 菜谱模块

## 种子数据现状

`seed/recipes-*.json` 是权威来源，`data-*.sql` 全部由 `tools/seed-sql.py` 生成，共 **326 道**：

| 批次 | 道数 | seed JSON | 生成 SQL | 封面轨 |
| --- | --- | --- | --- | --- |
| 湘菜 A / B | 33 + 33 | `seed/recipes-xiang-a.json`、`recipes-xiang-b.json` | `data-xiang-a.sql`、`data-xiang-b.sql` | jar 静态 |
| 川菜 | 25 | `seed/recipes-chuan.json` | `data-chuan.sql` | jar 静态 |
| 江西菜 | 15 | `seed/recipes-gan.json` | `data-gan.sql` | jar 静态 |
| 粤 / 鲁 / 闽 / 苏 / 浙 / 徽 | 18+17+17+17+16+15 | `seed/recipes-<拼音>.json` | `data-<拼音>.sql` | 腾讯云 COS |
| 东北菜 | 15 | `seed/recipes-dongbei.json` | `data-dongbei.sql` | 腾讯云 COS |
| 西北菜 | 15 | `seed/recipes-xibei.json` | `data-xibei.sql` | 腾讯云 COS |
| 湖北菜 | 15 | `seed/recipes-hubei.json` | `data-hubei.sql` | 腾讯云 COS |
| 云南菜 | 15 | `seed/recipes-yunnan.json` | `data-yunnan.sql` | 腾讯云 COS |
| 贵州菜 | 15 | `seed/recipes-guizhou.json` | `data-guizhou.sql` | 腾讯云 COS |
| 广西菜 | 15 | `seed/recipes-guangxi.json` | `data-guangxi.sql` | 腾讯云 COS |
| 山西菜 | 15 | `seed/recipes-shanxi.json` | `data-shanxi.sql` | 腾讯云 COS |
| 河南菜 | 15 | `seed/recipes-henan.json` | `data-henan.sql` | 腾讯云 COS |
| 早期种子 | 10 道家常菜 + 26 个分类 | — | `data-hunan.sql`、`data-category.sql` | — |
| 旧数据回填 | 11 道旧菜封面 + 45 条旧食材图 | —（写死在脚本里） | `data-cover-backfill.sql`、`data-ingredient-backfill.sql` | — |

本地库 `po` 已导入 217 道（截至 2026-09-30，缺东北/西北/湖北/云南/贵州/广西/山西/河南八批共 120 道）；封面双轨与 COS 补图流程见 `tools/README-covers.md`。

## 文件布局

```
services/api/
  recipe/src/main/resources/
    seed/                        # 种子源数据（JSON，权威来源）
      recipes-*.json             # 菜谱批次：{region, recipes[]}，每道含食材/步骤/封面 slug
      ingredient-images.json     # 食材名 → /api/ingredients/{slug}.jpg 映射（355 项，共享白底图）
    data-*.sql                   # 由 tools 脚本生成，请勿手改（data-category.sql 是手工维护的例外）
    data-category.sql            # 31 个分类：功能分类 + 菜系分类 + 饮食方式（库内目前 26 个，缺云南/贵州/广西/山西/河南）
  api-bootstrap/src/main/resources/static/
    covers/                      # 旧批次菜谱封面 JPEG（117 张）
    ingredients/                 # 食材白底图 JPEG（179 张）
```

图片 URL 约定：封面 `/api/covers/{slug}.jpg`（旧批次）或 COS 绝对地址（新批次），食材 `/api/ingredients/{slug}.jpg`。静态资源由 api-bootstrap 的 context-path `/api` + `static/` 提供，`SecurityConfig` 的 GET permitAll 已放行 `/covers/**`、`/ingredients/**`。

## 生成流水线（repo 根目录 `tools/`）

Windows 下解释器一律用 `py`（`python` 是 Microsoft Store 占位程序，会静默失败）。脚本内路径已按仓库根解析，在任何目录下运行都行。

1. **写 `seed/recipes-<批次>.json`** — 沿用现有 schema；`difficulty` 只取 1/2/3；`region` 必须与 `recipe_category.name` 完全一致；食材名必须能在 `seed/ingredient-images.json` 里查到。
2. **补食材映射** — 新食材名直接往 `seed/ingredient-images.json` 加一行（可复用既有白底图当别名，如 `酸菜 → baicai`）；确实缺图才生成源图，文件名用 `ing-<slug>_<ts>.png`。`tools/seed-ingredients.py` 只服务旧四批（路径与 IMG 表都停在湘/川/赣阶段），新批次不要跑它。
3. **`py tools/seed-img.py`** — 把 `vibe_images/` 的 PNG 压成 JPEG（quality 85）落位到 static 目录：`ing-` 前缀进 `ingredients/`（去掉前缀），其余进 `covers/`。已存在的目标跳过，可重复运行；默认通配只收 `ing-*.png`，免得把该走 COS 的新菜系封面烘进 jar。
4. **注册批次** — 只改 `tools/batches.py` 的 `BATCHES` 加一行 `('recipes-xxx.json', 'data-xxx.sql', 'cos')`；`seed-sql.py` 与 `cos-upload.py` 都从这里取清单，别再各存一份。
5. **`py tools/cos-upload.py --only xxx-`** — 封面源图 → JPEG → `po/covers/<slug>.jpg`（幂等，桶里已有的跳过）。
6. **`py tools/seed-sql.py`** — 生成 `data-*.sql`。缺封面源图时该道写 `NULL` 并打印提示，等图补齐后重跑即可；食材名缺映射直接报错终止。固定值：author_id=1、is_public=TRUE、category=region、likes=88+md5(title)%233。每次还会输出幂等的 `data-covers-backfill.sql`。
7. **新菜系还要加分类行** — `data-category.sql` 末尾追加 `('湖北菜', …, 111, …)`（该文件手工维护、不可重放），现库单独执行一次同条 INSERT。

## 导入 MySQL

`data-*.sql` 用 mysql 客户端导入（必须带 utf8mb4，否则中文乱码）：

```
mysql -h127.0.0.1 -uroot -p --default-character-set=utf8mb4 po < services/api/recipe/src/main/resources/data-dongbei.sql
```

注意：`data-*.sql` 的一批次 INSERT **不可重放**（重复导入会产生重复菜谱）；回填 SQL 幂等可重放。导入后用 `SELECT category, COUNT(*) FROM recipe GROUP BY category` 核对。

## 扩展到 1000 条的路径

目标约 1000 道，当前生成 326 道、库内 217 道。按批滚动，每批 15 道跑一次第 1 至 6 步：

1. 选题优先补 `recipe_category` 里已有、但库里道数为 0 的菜系，省掉分类改动；标题先跟库内查重：`SELECT title FROM recipe`。
2. 食材尽量落在既有 179 张白底图上（别名即可），需要新图时一次把该菜系的缺口备齐，避免反复生图。
3. 封面源图受 ImageGen 配额限制，会中断在批次中途——缺的道写 NULL，事后按 `cover.visual` 补生成再走第 5、6 步与 `data-covers-backfill.sql`。
4. 导入并验证：列表 `totalElements`、随机详情的 `coverImageUrl` / `ingredients[].imageUrl`、对应静态图 URL 返回 200。
