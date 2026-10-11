# 小说内部通道冒烟测（N2 + N3）

`node scripts/novel-internal-smoke.mjs` 验的是 **agent-novel 落库时真正打的那条链路**——
`services/api` 的 `/novel/internal/**`，不是管理端的 `/books/**`。
出处：`NOVEL_AGENT_PRD.md` §13-N2（退出条件「写 N 章能抽出断言并入库；重放不重复」）
与 §13-N3（层级摘要树的写入与「整段已知」过滤）。

Python 侧的对应实现是 `services/agent-novel/src/po_agent_novel/http_store.py`，
它照这份契约发请求；冒烟脚本用同一份载荷，所以「脚本绿了」等价于「Agent 的写入端点通了」。

## 为什么要单独验这条链路

- 管理端 `/books/**` 要的是 JWT（24 小时过期），Agent 不能复用——它的写入发生在
  用户早已断开的那次流式跑完之后，手里没有用户令牌；
- 所以内部端点在 `SecurityConfig` 里是 `permitAll`，**由 Controller 自己校验
  `X-Internal-Token`**（见 `NovelInternalController.denyUnlessInternal`）；
- 正典是只追加的：写坏了不能靠 UPDATE 修，只能靠幂等键把重放挡住。
  「重放不重复」这条性质只有在真库上打一次才算验过，单测里那是内存实现。

## 两端令牌必须一致

| 端 | 配置项 | 本地开发落在 |
| --- | --- | --- |
| Java | `app.internal-token`（读环境变量 `APP_INTERNAL_TOKEN`） | `application-local.yaml` 的 `app.internal-token`，或 IDE 运行配置里的环境变量 |
| Python | `NOVEL_INTERNAL_TOKEN`（前缀 `NOVEL_`，见 `NovelStoreSettings`） | `services/chat/.env` |

两边任意一边没配，Java 一律拒绝（它对「未配置」和「不匹配」都给 `code=403`，
所以「忘了配」不会伪装成「配错了」）。`application-local.yaml` 与 `services/chat/.env`
都已 gitignore：**令牌值不要提交，也不要写进命令行历史**（脚本支持 `--token=` 与环境变量两种传法，
默认直接从那份 gitignored 的 yaml 里读，全程不打印内容）。

给本地开发起一个一次性令牌的例子：

```bash
openssl rand -hex 24          # 拿这个值，分别填进下面两处
```

```yaml
# services/api/api-bootstrap/src/main/resources/application-local.yaml（gitignored）
app:
  internal-token: <上面生成的值>
```

```ini
# services/chat/.env（gitignored）
NOVEL_INTERNAL_TOKEN=<同一个值>
NOVEL_API_BASE_URL=http://localhost:8080/api
NOVEL_AUTHOR_ID=3
```

`NOVEL_AUTHOR_ID` 必须是本地 `sys_user` 表里存在的 id：内部通道建书要落到某个用户名下
（`book.author_id NOT NULL`，但服务端**不校验外键**——写了不存在的 id 也能建书成功，
只是这本书在书架上按作者查就成了孤儿；本地 `sys_user` 从 id=3(admin) 起）。
冒烟脚本默认用 3，可用 `PO_AUTHOR_ID=<id>` 覆盖。归档发起人进不到这条链路之前先用它兜底。
容器部署时 `NOVEL_API_BASE_URL` 由 `docker-compose.yml` 覆盖为 `http://api:8080/api`。

## 命令

```bash
node scripts/novel-internal-smoke.mjs                      # 令牌从 application-local.yaml 读
node scripts/novel-internal-smoke.mjs --token=<内网令牌>
PO_API_BASE=http://127.0.0.1:8080/api node scripts/novel-internal-smoke.mjs
```

按顺序验这几件事，每件事都是一条独立的失败模式：

1. 对照组 `GET /api/recipes` —— 通，说明 api 服务在跑；
2. **缺令牌的内部调用必须 `code=403`** —— 闸门本身；
3. `POST /novel/internal/books?authorId=3`（带 `summary`）→ 写章 → 建角色 ——
   `book.summary` 是 Tier-0 注入用的世界观摘要，`description` 是对外简介，
   写章端点是**按章号落位**而不是「永远新插一行」：那一行空着（作者排的待写占位）就被填掉且行 id 不变，
   已有正文则整轮 `code=400 第 N 章已有正文`（PRD §15.23）——所以第 3 步的第 1-5 章只有在**每次都新建一本
   带时间戳的书**时才互不撞号，指着现成的 bookId 重跑会从第 1 章起全部报错，这是预期而不是通道坏了；
   建书响应回显实体，两者写串或互相覆盖在这里就看得见；
4. `POST /novel/internal/assertions:append`（断言 + 伏笔 + 称谓 + 状态四路）；
5. **同一载荷再打一次 → `applied=false`** —— 这就是「重放不重复」；
6. 换章号、换幂等键再打一次 → 必须真的写进去；
7. `GET /novel/internal/canon/snapshot?asOf=1` 与 `asOf=2` —— 第 2 章的事实不该被第 1 章看见，
   并且快照里 `authority` 必须全是 `model`（作者手改与正文回读是另两条更高的权限，N5b 才有）；
8. `GET /novel/internal/canon/foreshadows/open`、`GET /novel/internal/canon/aliases`；
9. `POST /novel/internal/summaries` 三种载荷形状各打一次：`scene`（带 `sceneNo`，从 1 起）、
   `chapter`（`sceneNo` 恒 **0**）、`arc`（不带 `chapterId`，带 `bookId` + `fromChapter`/`toChapter`）
   —— 与 `http_store.HttpCanonStore` 逐字对齐，脚本绿即后端认这份形状；
10. `GET /novel/internal/canon/summaries?upto=1` —— 本章的 scene + chapter 行必须在，
    而**覆盖 1~2 章的弧摘要必须不在**：摘要读侧按「整段已知」过滤，区间与 `upto` 相交即剧透
    （这与第 7 步断言的「相交即可见」刻意相反，两种语义搞混过一次就要重写注入逻辑）；
11. 同 `arcNo` 再打一次 → 仍只有 1 行且内容更新（覆盖式 upsert，resume 重放不双写）、
    `summariesWritten=1`；`levels=chapter` 只回章级行；未知 `levels` 值必须 `code=400`。

结尾输出 `通过 N，失败 0`；失败项会带上 `Result` 信封里的 `code` 与 `message`。
2026-10-03 真库首跑：**通过 44，失败 0**（本地 MySQL + bookId=12）。

## 看到的失败怎么解读

| 现象 | 原因 |
| --- | --- |
| `连不上 http://127.0.0.1:8080/api` | api 服务没起。起服务是 IDE 的事，脚本不代管 |
| `/api/recipes` 200 而内部端点 404（`NoResourceFoundException: No static resource novel/internal/...`） | 进程里跑的还是没有 novel 模块的旧构建，**从 IDE 重启**；`spring-boot-devtools` 只在 class 落到 `target/classes` 时才自动重启 |
| 第 2 步没被拒 | 令牌闸门失效，最严重的一项，别往下跑 |
| 第 5 步 `applied=true` | 幂等键没生效（`gen_job` 表缺唯一索引，或键的四个维度少了一维），重放会写成双份 |
| 第 7 步快照为空但第 4 步成功 | 断言的 `status` 不是 `confirmed`（`todo` 是「未知即缺口」，读侧刻意不注入），或 `validFromChapter` 大于查询的 `asOf` |
| 第 9 步 `chapter` 级报「章节不存在」 | `chapterId` 用的是内存实现那种 `book-<hex>` 假 id，或章节行已软删；摘要必须挂在真实章节行上，服务端要从它推区间端点与 `sourceVersion` |
| 第 10 步在 `upto=1` 读到了弧摘要 | 「整段已知」过滤失效（`to_chapter` 没进 WHERE，或弧行写成了 `to_chapter IS NULL`）。后果是把第 2 章的剧情注入进第 1 章的上下文——**这是剧透，不是性能问题** |
| 第 10 步章级行的 `sceneNo` 不是 0 | Java 侧写成了 NULL：唯一索引不比较 NULL，重放就会插出并行（见 §15.2 偏差 #3） |
| 第 11 步弧摘要行数变 2 | upsert 判定没按 `(bookId, level='arc', sceneNo=arcNo)` 命中，而是每次都 insert |

## 它会写库

内部通道没有删除端点（正典只追加，删除会毁掉 as-of 查询的地基），所以每跑一次留一本书：
`book.title = 冒烟正典 <UTC 时间戳>`，正典四张表各若干行，外加 `chapter_summary` 的
scene/chapter/arc 行（第 9~11 步产出）。清理用管理端令牌走公开写接口：

```bash
curl -X DELETE http://127.0.0.1:8080/api/books/<脚本末行打印的 bookId> \
  -H "Authorization: Bearer <管理端 JWT>"
```

章节与角色随 `book` 的外键级联删除；正典表**不会**跟着删（`canon_entry` 只按
`(bookId, asOf)` 读，书没了自然读不到）。

## 与 Agent 实跑的分界

这个脚本只打到 HTTP + 库这一层，不含模型。整条链路的实跑是：

```bash
pnpm chat:start        # 起 FastAPI，novel 插槽随之注册（未装包则只跳过本插槽）
# 管理端 /novel 工作台或 WS 里说一句「帮我写一本小说」
```

跑到归档 `interrupt` 时回 `yes`，日志里应出现 `已归档：<bookId>` 与一行
`正典入库 N 条…；层级摘要 M 行、弧级 K 段`（离线模式下 N 可以是 0，见 README「降级」）。
每章进 `generate` 前还会发一条 `context_compiled` 事件，带本章注入的 token 数与
Tier-1/Tier-2 条数——L1 是否真的在喂正典，看这条比看正文快。
把 `NOVEL_PERSIST_ENABLED=false` 设进 `services/chat/.env` 可以让成稿与正典都留在进程内，
用于无后端时验证链路本身（此时归档前的注入走 overlay，一次库读都不发生）。

## 一个已知暴露面（未处理，需要拍板）

网关 `infra/nginx/nginx.conf` 把整个 `/api/**` 反代给 Spring，所以
`/api/novel/internal/**` 与 `/api/talk/internal/**` 也能从公网域名打到，
保护只剩 `X-Internal-Token` 这一层。Agent 侧走的是 compose 内网
（`http://api:8080/api`）或本地 8080，不经网关，因此在 nginx 里加一条
`location ^~ /api/novel/internal/ { return 403; }` 不影响本地与 compose 链路——
但云托管上 chat 回调 api 用的是公网域名还是内网域名没有核实过，加之前要确认，
所以这里只记录、不擅自改。
