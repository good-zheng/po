# 菜谱模块

## 种子数据现状

库 `po` 当前共 **117 道菜谱**（湘菜 67 / 川菜 25 / 江西菜 15 / 家常菜 10），993 条食材行与 575 个步骤，全部菜谱有封面图、全部食材行有图片。

| 批次 | 内容 | seed JSON | 生成 SQL |
| --- | --- | --- | --- |
| 湘菜 A | 33 道 | `src/main/resources/seed/recipes-xiang-a.json` | `data-xiang-a.sql` |
| 湘菜 B | 33 道 | `seed/recipes-xiang-b.json` | `data-xiang-b.sql` |
| 川菜 | 25 道 | `seed/recipes-chuan.json` | `data-chuan.sql` |
| 江西菜 | 15 道 | `seed/recipes-gan.json` | `data-gan.sql` |
| 旧数据回填 | 11 道旧菜的封面 + 45 条旧食材图 | —（写死在脚本里） | `data-cover-backfill.sql`、`data-ingredient-backfill.sql` |
| 早期种子 | 10 道家常菜 + 分类 | — | `data-hunan.sql`、`data-category.sql` |

## 文件布局

```
services/api/
  recipe/src/main/resources/
    seed/                        # 种子源数据（JSON，权威来源）
      recipes-*.json             # 菜谱批次：{region, recipes[]}，每道含食材/步骤/封面 slug
      ingredient-images.json     # 食材名 → /api/ingredients/{slug}.jpg 映射（263 项，共享白底图）
    data-*.sql                   # 由 tools 脚本生成，请勿手改
  api-bootstrap/src/main/resources/static/
    covers/                      # 菜谱封面 JPEG（117 张）
    ingredients/                 # 食材白底图 JPEG（176 张）
```

图片 URL 约定：封面 `/api/covers/{slug}.jpg`，食材 `/api/ingredients/{slug}.jpg`。静态资源由 api-bootstrap 的 context-path `/api` + `static/` 提供，`SecurityConfig` 的 GET permitAll 已放行 `/covers/**`、`/ingredients/**`。

## 生成流水线（repo 根目录 `tools/`）

顺序执行，脚本内路径为绝对路径，直接 `python tools/xxx.py` 运行：

1. **`seed-ingredients.py`** — 汇总食材名到共享图片键，产出 `ingredients-image-list.tsv`（slug + 英文提示词，用于批量 AI 生图）和 `seed/ingredient-images.json`。
2. **AI 生图** — 按 tsv 提示词批量生成食材白底图、按封面 `visual` 字段生成菜品图，PNG 存入 `vibe_images/`（食材文件名带 `ing-` 前缀）。
3. **`seed-img.py`** — 把 `vibe_images/` 的 PNG 转 JPEG（quality 85）落位到 static 目录；已存在的目标文件跳过，可重复运行。
4. **`seed-sql.py`** — 从 `seed/recipes-*.json` 生成 `data-*.sql`。会校验封面文件存在、食材名必须在 ingredient-images.json 映射中，否则报错终止。固定值：author_id=1、is_public=TRUE、category=region、likes=88+md5(title)%233。
5. **`seed-backfill.py`** — 为旧数据生成幂等回填 SQL（`UPDATE ... WHERE image_url IS NULL`）。

## 导入 MySQL

`data-*.sql` 用 mysql 客户端导入（必须带 utf8mb4，否则中文乱码）：

```
mysql -h127.0.0.1 -uroot -p --default-character-set=utf8mb4 po < services/api/recipe/src/main/resources/data-xiang-a.sql
```

注意：`data-*.sql` 的一批次 INSERT **不可重放**（重复导入会产生重复菜谱）；回填 SQL 幂等可重放。导入后用 `SELECT category, COUNT(*) FROM recipe GROUP BY category` 核对。

## 扩展到 1000 条的路径

目标约 1000 道，当前 117 道，后续按批滚动补齐（每批约 100 道新 JSON + 配图）：

1. 新建 `seed/recipes-<批次>.json`（沿用现有 schema；标题不得与库内重复，`SELECT title FROM recipe` 先查重）。
2. 新食材名补进 `seed-ingredients.py` 的 IMG 表 → 重跑生成映射与生图清单，只为新增 slug 生图。
3. 跑 `seed-img.py` 转换落位，再跑 `seed-sql.py`（在 `FILES` 里注册新批次）。
4. 导入并验证：列表 `totalElements`、随机详情的 `coverImageUrl` / `ingredients[].imageUrl`、对应静态图 URL 返回 200。
