# 菜谱封面：本地静态目录 与 腾讯云 COS 双轨

菜谱批次清单的**唯一注册表是 `tools/batches.py` 的 `BATCHES`**（每项 `(seed 文件名, 输出 sql, 封面来源)`）。
`seed-sql.py` 用 `from batches import BATCHES as FILES`，`cos-upload.py` 用
`COS_FILES = [src for src, _dst, cover in BATCHES if cover == 'cos']` 从同一张表推导——
**加批次只改 `batches.py` 一处**，两个脚本不需要各自维护清单。

模块级的接口与数据约定见 `services/api/recipe/README.md`，这份文档只管封面与生图链路。

## 现状

| 批次 | 道数 | 封面位置 | 库里存的值 |
| --- | --- | --- | --- |
| 湘 A/B、川、赣（seed 静态批次） | 33+33+25+15 = 106 | jar 内 `api-bootstrap/src/main/resources/static/covers/` | `/api/covers/<slug>.jpg` |
| 更早的手工批次（`data-hunan.sql` 等，id 1-11） | 11 | 同上，slug 前缀 `classic-` | `/api/covers/classic-<slug>.jpg` |
| 粤/鲁/闽/苏/浙/徽（六系） | 18+17+17+17+16+15 = 100 | 腾讯云 COS 桶 `po/covers/<slug>.jpg` | `https://<bucket>.cos.<region>.myqcloud.com/po/covers/<slug>.jpg` |
| 东北/西北/湖北/云南/贵州/广西/山西/河南（八系） | 15 × 8 = 120 | 同上，但**大部分源图还没生**（见「封面补齐进度」） | 有源图的写绝对 URL，其余写 `NULL` |

`static/covers/` 目录里共 117 张 jpg = 106（seed 静态批次）+ 11（`classic-*`），
所以旧口径说的「117 道」是**库内旧批次菜的总数**，不是 seed 静态批次的道数。

两端（`apps/cooking-app`、`apps/cooking-mini`）的 `resolveAssetUrl` 对 `http(s)` 开头的值直接透传，
所以绝对 URL 与相对路径都能渲染，不需要改前端。

新批次封面不落 jar：容器磁盘临时且多实例不共享，图片统一走对象存储（与头像/上传/TTS 同一套业务）。

## 数据链路

```
seed/recipes-<菜系>.json  (cover.slug + cover.visual)
        │  ImageGen 按 visual 生图 1536x1024 PNG
        ▼
vibe_images/<slug>_<ts>.png          （.gitignore 已忽略，是源图不是产物）
        │  tools/cos-upload.py       PNG → JPEG(q85) → PUT po/covers/<slug>.jpg
        ▼
COS 桶公网可读
        │  tools/seed-sql.py         生成 data-*.sql（封面已就绪才写 URL，否则写 NULL）
        ▼
MySQL po.recipe.cover_image_url
```

`tools/seed-sql.py` 每次还会输出 `data-covers-backfill.sql`：一批
`UPDATE recipe SET cover_image_url = ... WHERE title = ... AND category = ... AND cover_image_url IS NULL`，
只补空封面，重复执行安全。当前那份有 104 条（六系 100 + 东北 4）——
判据是「`vibe_images/` 里有对应源图」，不是「桶里已有对象」，所以补图后重跑脚本即可让它长出来。

另有两条**旧批次专用**的回填 SQL 由 `tools/seed-backfill.py` 生成，不参与上面的链路：

- `data-cover-backfill.sql`：按 id 回填 11 道手工批次的 `/api/covers/classic-*.jpg`；
- `data-ingredient-backfill.sql`：回填旧 11 道菜食材行的 `recipe_ingredient.image_url`。

## 生图水印必须裁掉

ImageGen 出来的源图右下角会烘进「AI生成 / WORKBUDDY」水印，直接上传会带到线上。
实测 1536x1024 下文本落在 **y 963..1013**（跨 14 张求交集，位置固定），裁到 `y < 945`
（即去掉底部约 7.7%）即可干净去除；裁剪后 1536x945，两端 `aspectFill` 渲染下肉眼无差别。

```python
from PIL import Image
im = Image.open(src)
im.crop((0, 0, im.width, 945)).save(src)   # CUT=945，别用 1024
```

注意：**更早的一批 COS 封面来自另一条生图渠道**，带的是另一层很淡的「Qoder AI 生成」水印，
裁 `y < 945` 对它无效（位置不同）。这批是否已全部替换、具体涉及哪些 slug，
本地仓库里查不出来（源图目录 gitignore，桶里对象也无清单），
要核对只能拉 COS 对象列表逐张看右下角。

## 封面补齐进度

**已入库的 217 道菜封面已全部补齐（2026-10-02 记录，缺失归零）**：旧 117 走 jar 静态，六系 100 走 COS。

已生成 SQL、**尚未导入**的八批共 120 道（导入需要用户授权，本地库现在没有它们）：

| 菜系 | seed 文件 | 道数 | 源图 |
| --- | --- | --- | --- |
| 东北 | `recipes-dongbei.json` | 15 | 4 张已生并已传 COS，11 张待生 |
| 西北 / 湖北 / 云南 / 贵州 / 广西 / 山西 / 河南 | `recipes-{xibei,hubei,yunnan,guizhou,guangxi,shanxi,henan}.json` | 15 × 7 = 105 | 全部待生 |

所以待生图 = 11 + 105 = **116 张**，其余 4 道（东北）已在 COS 里等着回填。
八批的 `region`（东北菜/西北菜/湖北菜/云南菜/贵州菜/广西菜/山西菜/河南菜）在
`data-category.sql` 里**都已经有行**（2026-10-12 逐字核对过 18 批），
但 `INSERT` 语句**不可重放**，只有回填 SQL 可以——导入前先确认本地库里这几类真的存在。

想核对当前状态（本地 root 密码只存在 gitignored 的 `application-local.yaml`，别写进文档或脚本）：

```
mysql -h127.0.0.1 -P3306 -uroot -p --default-character-set=utf8mb4 po -e \
  "SELECT category, COUNT(*) FROM recipe WHERE cover_image_url IS NULL GROUP BY category"
```

## 补图标准流程

1. 查缺哪些：`py tools/cos-upload.py --only <前缀>` 会逐条打印 `缺源图 <slug>（vibe_images/<slug>_*.png）`；
   或按上一节的 SQL 看库里。
2. 用 ImageGen 按对应 `cover.visual` 生图（`size=1536x1024`、`quality=high`、`output_dir=vibe_images/`）。
   注意 ImageGen 的落盘名由提示词派生（`professional_food_photography__<时间戳>.png`），**不是** slug，
   生成后必须按 `vibe_images/<slug>_<毫秒时间戳>_<md5前8位>.png` 改名（`cos-upload.py` 靠 `_` 前的前缀认 slug）。
   然后按上一节裁掉底部水印。
3. 上传（幂等，桶里已有的自动跳过）：
   ```
   py tools/cos-upload.py            # 全部
   py tools/cos-upload.py --only hui-   # 只传某个菜系
   py tools/cos-upload.py --force    # 覆盖重传
   ```
4. 重新生成 SQL 并回填：
   ```
   py tools/seed-sql.py
   mysql -h127.0.0.1 -P3306 -uroot -p --default-character-set=utf8mb4 po \
     < services/api/recipe/src/main/resources/data-covers-backfill.sql
   ```

食材图是另一条链路：`tools/seed-img.py` 默认通配**只收 `ing-*.png`**（新菜系封面不落 jar），
要补旧批次静态封面才显式给通配，如 `py tools/seed-img.py 'xiang-*.png'`。

## 配置与密钥

- 桶/地域/前缀：环境变量 `COS_BUCKET` / `COS_REGION` / `COS_KEY_PREFIX`。
  **缺省值写死在脚本常量里**（`cos-upload.py` 与 `seed-sql.py` 各一份，与 `application.yaml` 的
  `cos.*` 默认值相同但不会去读它），换桶要三处一起改，只改 `application.yaml` 会让
  「Java 上传的」与「SQL 里写死的」落在两个桶。
- 密钥：`COS_SECRET_ID` / `COS_SECRET_KEY`，没有则回读 `application-local.yaml` 的 `cos.secret-id/secret-key`（该文件已 gitignore）。
  脚本本身不写死任何密钥，也不把值打进日志。
- 依赖：`Pillow`（`py -m pip install pillow -i https://pypi.tuna.tsinghua.edu.cn/simple`）。
- Windows 下解释器用 `py`，`python` 是 Microsoft Store 占位程序，会静默失败。

## 新增菜系要做的事

1. 写 `seed/recipes-<菜系>.json`：`region` 必须与 `recipe_category.name` 一致，
   每个新食材名要在 `seed/ingredient-images.json` 里有映射（`seed-sql.py` 会直接报错提示缺哪个；
   近似食材共用一张白底图是既有做法，配额紧张时一律用别名）。
2. **只改 `tools/batches.py`**：`BATCHES` 加一行 `('recipes-xxx.json', 'data-xxx.sql', 'cos')`，
   两个脚本自动跟上。
3. 生图 + 传 COS + 重跑 `seed-sql.py`（见「补图标准流程」）。
4. 往手工维护的 `data-category.sql` 补一类行，并在库里单独执行一次 `INSERT`
   （`recipe_category.name` 没有唯一索引，脚本重跑不会替你补）。

## 已知偏差

- `tools/seed-backfill.py` 与 `tools/seed-ingredients.py` 里的路径是**硬编码的 `D:/pro/po/...`**，
  这个仓库现在在 `D:/dev/po`，直接跑会写错位置或报错。它们只服务旧批次一次性回填，
  要复用得先把常量改成相对仓库根的形式。
- `data-hunan.sql` 是早于 seed 体系的手工文件，不在 `BATCHES` 里，`seed-sql.py` 不会重新生成它。
