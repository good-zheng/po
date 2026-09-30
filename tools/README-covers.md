# 菜谱封面：本地静态目录 与 腾讯云 COS 双轨

## 现状

| 批次 | 道数 | 封面位置 | 库里存的值 |
| --- | --- | --- | --- |
| 湘/川/赣/家常（旧） | 117 | jar 内 `api-bootstrap/src/main/resources/static/covers/` | `/api/covers/<slug>.jpg` |
| 粤/鲁/闽/苏/浙/徽（新） | 100 | 腾讯云 COS 桶 `po/covers/<slug>.jpg` | `https://<bucket>.cos.<region>.myqcloud.com/po/covers/<slug>.jpg` |

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
只补空封面，重复执行安全。

## 补齐剩下的 84 张封面

1. 查缺哪些（本地 root 密码见 gitignored 的 `application-local.yaml`，别写进文档或脚本）：
   ```
   mysql -h127.0.0.1 -P3306 -uroot -p --default-character-set=utf8mb4 po -e \
     "SELECT category, title, id FROM recipe WHERE cover_image_url IS NULL ORDER BY category, id"
   ```
   或直接看 `py tools/cos-upload.py` 打印的 `缺源图 <slug>` 行。
2. 用 ImageGen 按对应 `cover.visual` 生图（size 1536x1024，name 用 slug 原值），落到 `vibe_images/`。
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

## 配置与密钥

- 桶/地域/前缀：环境变量 `COS_BUCKET` / `COS_REGION` / `COS_KEY_PREFIX`，缺省取 `application.yaml` 里的项目默认值。
- 密钥：`COS_SECRET_ID` / `COS_SECRET_KEY`，没有则回读 `application-local.yaml` 的 `cos.secret-id/secret-key`（该文件已 gitignore）。
  脚本本身不写死任何密钥。
- 依赖：`Pillow`（`py -m pip install pillow -i https://pypi.tuna.tsinghua.edu.cn/simple`）。
- Windows 下解释器用 `py`，`python` 是 Microsoft Store 占位程序，会静默失败。

## 新增菜系要做的事

在 `tools/seed-sql.py` 的 `FILES` 里加一行 `('recipes-xxx.json', 'data-xxx.sql', 'cos')`，
`cos-upload.py` 的 `COS_FILES` 同步加上文件名；`region` 必须与 `recipe_category.name` 一致，
新食材名要在 `seed/ingredient-images.json` 里有映射（脚本会直接报错提示缺哪个）。
