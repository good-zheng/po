# 小说业务线建表迁移（N1）

`services/api/api-bootstrap/src/main/resources/schema.sql` 在每次应用启动时都会被执行（`spring.sql.init.mode: always`，见 `application.yaml:19-21`），但它全篇是 `CREATE TABLE IF NOT EXISTS`——**对已经存在的表什么都不做**。本地库里的 `book` / `book_chapter` / `book_character` 是早先 JPA `ddl-auto: update` 建的，列宽比恢复出来的 DDL 窄，而且没有新加的两列。重启应用修不好这个，所以要跑这个脚本。

出处：`NOVEL_AGENT_PRD.md` §13-N1；新列的用途见 §5.6、§10.5。

## 不跑会怎样

| 现象 | 后果 |
| --- | --- |
| `book_chapter.content` 还是 `TEXT` | 上限 64KB。utf8mb4 下中文 3 字节，**约 2.1 万字就被静默截断**——没有报错，正文尾巴直接没了。长篇小说必踩 |
| 缺 `book_chapter.status` | 章节没有 draft / pending_review / committed 之分，正典出处的可信度分界（§10.5）无法落地，`updateById` 还会因为未知列报错 |
| 缺 `book_chapter.revision` | 作者手改正文后无法定位是哪一版（黄金集样本与断言出处按 `(chapterId, revision)` 引用），改一洗就把评测基线洗没了 |
| 缺 `book.summary` | Tier-0 常驻注入的世界观摘要没地方存，只能塞进 `description`（那是对外简介文案，语义不同） |
| `title` / `genre` / `name` 列宽偏窄 | 长书名、长人物名会被截断或报 1406 |

## 命令

```bash
node scripts/novel-migrate.mjs --dry-run   # 只打印将要执行的增量，不碰库
node scripts/novel-migrate.mjs             # 执行增量 + 应用 schema.sql + 核对结果
```

预期输出末尾是 `正典层已存在 12/12 张表`，再往下列出 15 张表的行数。本地当前状态（2026-10-03 已执行）：`book` 3 行、`book_chapter` 6 行、`book_character` 6 行、12 张正典表 0 行，9 条增量全部落在预期内。

## 凭据

连接信息从 `services/api/api-bootstrap/src/main/resources/application-local.yaml` 的 `spring.datasource` 段解析。这份文件是 gitignore 的，**口令只留在进程环境里**（用 `MYSQL_PWD` 传，不走命令行——命令行参数会在进程列表里被看见，mysql 自己也会告警），任何输出都不打印口令。

换机器时如果这份文件不存在，脚本会直接报错让你从 IDE 那份复制过来，不会回退到默认口令。

## 它只做加法

`ADD COLUMN` / 放宽 `MODIFY COLUMN` / `CREATE TABLE`，仅此三类。不会 `DROP`、不会改数据、不会收紧宽度或类型——`author` 在本地是 `varchar(100)`（比 DDL 的 `varchar(64)` 宽），`created_at` 是 `datetime(6)`，这些都保持原样。判定依据来自 `information_schema`，所以脚本重复跑是安全的：第二次会打印「无增量」。

正典层的 12 张表（`canon_entry`、`character_state`、`foreshadow`、`alias`、`timeline_anchor`、`style_profile`、`scene_plan`、`review_finding`、`gen_job`、`chapter_summary`、`canon_proposal`、`chapter_revision`）由 `schema.sql` 建，本地它们本来就不存在，所以走的是建表分支而不是 ALTER。

但「建表分支」只在表还不存在时兜住一切：表一旦建出来，`schema.sql` 就对它什么都不做了，之后往这几张表里加的新列必须进 `EXPECTED`，否则改完实体和 DDL、本地库照样缺列，而应用层只会在写那一列时报未知列。`chapter_summary` 的 `from_chapter/to_chapter/source_version` 和 `canon_proposal.decided_basis` 就是这么补进来的（2026-10-04 已执行，增量 1 条）。

## 全新环境

空库不用跑这个脚本——起一次 api 服务，`schema.sql` 会把它那 27 张表建全（其中小说线 15 张：3 张书 + 12 张正典），此时列宽就是新 DDL 的宽度，脚本会报「无增量」。要在 CI 或本地快速起库时用镜像源拉 MySQL：见 `docker-compose.yml` 与项目知识 *Network mirrors*。

## 应用侧的配套改动

数据列扩了，别忘了这三处（都已改）：

- `services/api/novel/.../entity/Book.java` — `summary`
- `services/api/novel/.../entity/BookChapter.java` — `status`、`revision`
- `packages/types/src/novel.ts` — 同上三个字段，前端契约要跟实体一起动

`ChapterRequest` 刻意**没有**开 `status` / `revision`，`BookRequest` 也没开 `summary`：章节的复核状态由服务端在保存与裁定流程里推进，版本号只能由保存动作加，世界观摘要走 N5b 的正典编辑端点，都不能让调用方直接 `PUT` 覆盖。注意 `BookRequest` 里那个 `status` 是书的创作状态（ongoing / completed / paused），跟 `book_chapter.status` 的 draft / pending_review / committed 同名不同义，别混着写。

## 迁移完怎么确认接口通了

`scripts/novel-smoke.mjs` 打的是 HTTP 层，用来验「CRUD 通」这个退出条件：

```bash
node scripts/novel-smoke.mjs                        # 只跑公开读接口
node scripts/novel-smoke.mjs --token=<管理端JWT>      # 再加一轮建书→建章→建角色→改→读回→删
```

令牌从浏览器 devtools 的请求头 `Authorization` 里复制，**不要写进仓库或命令行历史**（也可以 `PO_TOKEN=xxx` 传）。写接口要 `ADMIN_CLIENT`——管理端客户端 + admin/super_admin 角色两个都命中，用 App 端登录拿到的令牌会 403，那是预期行为不是 bug。

脚本会先对照组打一次 `/api/recipes`：如果菜谱 200 而 `/api/books` 404，说明进程里跑的还是不含 novel 模块的旧构建（404 的 trace 是 `NoResourceFoundException: No static resource books`），**需要从 IDE 重启 api 服务**——这一步不归脚本管，命令行里杀不掉 IDE 起的进程。

改章节后脚本会专门读回来检查 `title/content/wordCount/status/revision` 有没有丢：全局 `update-strategy: always`（`application.yaml:50`）会把没传的列刷成 NULL，talk 模块的 `session_id cannot be null` 就是这么来的，所以这一项是这道防线的哨兵。

响应信封是 `Result{code,success,data,message}`，成功 `code=1`；业务失败仍是 HTTP 200 但 `success=false`，所以脚本按 `success` 判而不按状态码判。
