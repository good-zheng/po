# `services/api` — Spring Boot 业务后端

Java 17 + Spring Boot 4.1.1 的 Maven 多模块**单体**（一个进程、一个 jar），对外前缀
`server.servlet.context-path=/api`。持久层 MyBatis-Plus + MySQL，缓存 Jedis/Redis，认证 jjwt。
不是微服务，别按服务拆分来理解模块——模块只是编译边界。

## 命令（仓库根执行）

```bash
pnpm api:start    # -pl api-bootstrap -am spring-boot:run（同一次 reactor 构建会编 shared/identity/recipe/talk/novel）
pnpm api:verify   # mvn verify，全模块（CI 的 api job 跑的就是这个）
pnpm api:install  # -pl api-bootstrap -am install -DskipTests；一般不需要，api:start 自带构建
pnpm api:deploy   # 构建并推送镜像到微信云托管内置仓库，见 DEPLOY_CLOUDRUN.md
```

Windows 上不能直接 `./mvnw`：`scripts/run-service.mjs` 按平台选 `mvnw.cmd` 并用 shell 执行，
同时经 `scripts/jdk.mjs` 定位 JDK（优先现有 `JAVA_HOME`，否则在 `~/.jdks/` 里按 pom 的 `java.version` 挑 17）。
绕过脚本手敲 `./mvnw` 时终端必须自备 `JAVA_HOME`，且在 Git Bash 里只能用 shell 版 `./mvnw`。

本地起依赖：根目录 `.env` + `docker compose up -d mysql redis`。Redis 必须是 **redis-stack**
（LangGraph 的 checkpointer 要 JSON+Search 模块，普通 redis 会静默降级），端口与凭据见根 README。

## 模块

依赖方向 `shared ← identity ← recipe / talk / novel ← api-bootstrap`（根 `pom.xml` 的 `<modules>` 顺序即此）。
父 POM 无 main 类，`spring-boot.run.skip=true` 让 boot 目标只在 `api-bootstrap` 生效。

| 模块 | 装什么 | 代表类 |
| --- | --- | --- |
| `shared` | `Result<T>` 响应信封、`MyBatisPages` 分页转换、对象存储与讯飞签名 | `dto/Result`、`mybatis/MyBatisPages`、`storage/ObjectStorage`、`storage/CosProperties`、`xfyun/XfyunSigner` |
| `identity` | 用户、认证、JWT、微信登录 | `controller/AuthController`、`controller/UserController`、`service/impl/AuthServiceImpl`、`security/SecurityConfig`、`wechat/WeChatService` |
| `recipe` | 菜谱、分类、收藏/历史/点赞、TTS；**种子数据与封面双轨的账目在本模块 `README.md`** | `controller/RecipeController`、`controller/RecipeCategoryController`、`controller/TtsController`、`tts/XfyunTtsService`、`resources/mapper/RecipeMapper.xml` |
| `talk` | 言外会话/话语/建议 + **ASR 网关**（WebSocket） | `controller/TalkController`、`asr/AsrSocketHandler`、`asr/TalkWebSocketConfig`、`asr/XfyunAsrSession` |
| `novel` | 书架/章节/角色 + L0 正典层 + 创作工作台 + 内部写入通道 | `controller/BookController`、`BookChapterController`、`BookCharacterController`、`NovelStudioController`、`NovelInternalController`、`service/CanonTxWriter`、`service/IdempotencyGuard` |
| `api-bootstrap` | 启动模块：`application.yaml`、`schema.sql`、全局配置 | `PoApplication`、`config/AuditMetaObjectHandler`、`config/MyBatisPlusConfig`、`config/DataInitializer` |

jjwt 0.12.6 只在 `identity/pom.xml` 声明；MyBatis-Plus 3.5.17（`mybatis-plus-spring-boot4-starter` +
`mybatis-plus-jsqlparser`）在根 POM 的 `dependencyManagement` 统一管——Spring Boot 4 不托管 MyBatis-Plus，
且 3.5.9 起分页插件独立成 jsqlparser 包，两处都不能省。

## 接口（不含 `/api` 前缀）

| 前缀 | 端点 | 说明 |
| --- | --- | --- |
| `/auth` | `POST /login`、`/register`、`/app-register`、`/openid-login`、`/wechat-login` | 登录注册；`/openid-login` 只认请求体 `loginCode`，禁止从请求头取 openid |
| `/users` | `GET`、`GET /pending`、`GET/PUT/DELETE /{id}`、`GET/PUT /me`、`PUT /me/password`、`POST /me/avatar`、`PUT /{id}/role`、`/{id}/approval`、`DELETE /batch`、`PUT /batch/status` | 管理端用户与审批 |
| `/files` | `POST /upload`（`GET /files/**` 公开） | 上传；产物落 COS 返回公网 URL |
| `/recipes` | `GET`、`GET /{id}`、`/mine`、`/favorites`、`/history`、`/review`、`POST`、`PUT/DELETE /{id}`、`POST /{id}/favorite`、`DELETE /{id}/favorite`、`POST /{id}/like`、`PUT /{id}/audit` | 菜谱 CRUD 与互动 |
| `/recipe-categories` | `GET`、`POST`、`PUT/DELETE /{id}` | 分类 |
| `/tts` | `GET /tts`、`POST /tts/prefetch` | 需登录（消耗讯飞额度）；返回 COS 音频地址，不返回字节 |
| `/books` | `GET`、`GET /{id}`、`GET /genres`、`POST`、`PUT/DELETE /{id}`、`/books/{bookId}/chapters`（含 `/{chapterId}`）、`/books/{bookId}/characters`（同形） | 游客可读浏览，写操作需管理端 |
| `/talk` | `POST/GET /sessions`、`GET/PATCH/DELETE /sessions/{id}`、`POST /sessions/{id}/utterances`、`PATCH /utterances/{id}`、`GET /asr/ticket`、`POST /internal/suggestions` | 言外小程序；`/internal/**` 走内网令牌 |
| `/novel` | 工作台：`canon` 增查改与 `retire`、`aliases`、`foreshadows`、`revisions/impact`、`search`、`proposals` 与 `adopt`/`dismiss`、`style`、`reviews`、`progress`、`GET /chat-ticket`；内部：`/internal/chat-ticket/verify`、`/internal/assertions:append|:close`、`/internal/findings`、`/internal/summaries`、`/internal/canon/snapshot`、`/internal/foreshadows/open`、`/internal/aliases`、`/internal/style`、`/internal/summaries`、`/internal/books`(+`/chapters`+`/characters`) | 管理端与 Python agent 共用前缀，靠 `internal` 段与鉴权区分 |
| WebSocket | `/ws/asr`（PCM 帧上行 → 讯飞听写 → 转写下行，票据在 query） | 小程序直连本服务，不经 nginx |

## 认证与开放面

以 `identity/src/main/java/**/security/SecurityConfig.java` 为准（匹配的路径**不含** `/api` 前缀）：

- 公开：`/auth/login|register|wechat-login|openid-login|app-register`、`/error`、`GET /files/**`、
  内容浏览（`GET /recipes*`、`/recipe-categories*`、`/books*`、`/books/*/chapters*`、`/books/*/characters*`、
  `/avatars/**`、`/covers/**`、`/ingredients/**`、`/sounds/**`）、`/ws/asr`、`/talk/internal/**`、
  `/novel/internal/**`、`GET /actuator/health`。
- `ADMIN_CLIENT`（`ROLE_ADMIN`/`SUPER_ADMIN` + `CLIENT_ADMIN`）守：`/novel/**`、`/actuator/**`、`/users/**`、
  以及 `/recipes/**`、`/recipe-categories/**`、`/books/**` 的写操作与 `/recipes/review`+`audit`。其余 `authenticated`。
- 两个 `internal` 前缀虽然 permitAll，但控制器自己校验 `X-Internal-Token`（见下），不是裸露端点。
- CORS 是 `allowedOriginPatterns("*")` + 全方法全头，所以公网前端可以跨域直连；401/403 统一返回 JSON。

## 配置

`api-bootstrap/src/main/resources/application.yaml` 只放**非机密**与占位：`context-path`、
`profiles.active: [local]`、`sql.init.mode: always`、mybatis-plus（`mapper-locations: classpath*:mapper/**/*.xml`、
`id-type: auto`、`update-strategy: always`、dev 下 `StdOutImpl` 打 SQL）、multipart 10MB/100MB、
静态资源含 `file:uploads/`、actuator 暴露 `health,info,metrics,prometheus`，以及这些环境变量位：
`JWT_SECRET`/`JWT_EXPIRATION`、`APP_SEED_DEFAULT_ADMIN`、`APP_INTERNAL_TOKEN`（`app.internal-token`，默认空）、
`wechat.mini.*`、讯飞 TTS/iat 参数、COS 六项。

数据源与 Redis **不在** `application.yaml`：本机走 `application-local.yaml`（已 `.gitignore`，含本地 MySQL
root 口令与 Redis 密码，值不进任何文档与日志）；容器靠环境变量注入。

`application-prod.json` 是给微信云托管控制台抄的**本机备忘文件**（同样已 `.gitignore`、未入库），
里面是真实密钥与数据库口令。规矩：不要 `git add` 它、不要把它的值复制进 README/工单/skill、
不要打印到终端。改它要同步云托管控制台的环境变量。

> **已知缺口**：`application-prod.json` 目前没有 `APP_INTERNAL_TOKEN`，而已部署的实例也就没有它。
> `app.internal-token` 为空时控制器对内部回调一律拒绝，所以线上 Python 侧的
> `/novel/internal/**` 与 `/talk/internal/suggestions` 落库会失败（本地 `.env` + compose 是配好的）。
> 补法是在控制台按 `docker-compose.yml` 的同名变量填一致的值，两端必须完全相同。

## 持久层约定

- 表结构以 `api-bootstrap/src/main/resources/schema.sql` 为准，`CREATE TABLE IF NOT EXISTS` 幂等建表，
  当前 26 张：`sys_user`、`recipe*`（含 ingredient/step/category/favorite/like/history）、
  `talk_session/utterance/suggestion`、`book/chapter/character`、`canon_entry/proposal`、
  `character_state`、`foreshadow`、`alias`、`timeline_anchor`、`style_profile`、`scene_plan`、
  `review_finding`、`gen_job`、`chapter_summary`、`chapter_revision`。
  **它不会修正已存在的表**，老库加字段必须跑 `node scripts/novel-migrate.mjs`（说明见 `scripts/NOVEL_MIGRATE.md`）。
- 新表/新字段先改 `schema.sql` 再改实体。实体用 `@TableName` / `@TableId(type = IdType.AUTO)`，
  创建时间 `@TableField(updateStrategy = FieldStrategy.NEVER)`、更新时间 `@TableField(fill = FieldFill.UPDATE)`
  （由 `AuditMetaObjectHandler` 填充）。
- Mapper 是各模块 `repository` 包下的 `@Mapper` 接口（`BaseMapper<T>`，只服务本模块的表）；
  分页在 Service 层用 spring-data-commons 的 `Page`/`Pageable`，经 `shared` 的 `MyBatisPages` 转换，
  依赖 `api-bootstrap` 注册的 `MybatisPlusInterceptor`（PaginationInnerInterceptor 不会自动注册）。
- 复杂 SQL（连表 + resultMap）才写 XML，放各模块 `src/main/resources/mapper/XxxMapper.xml`，
  文件名与接口同名。现在只有 recipe 模块有三个：`RecipeMapper.xml`（一次查询带出食材与步骤，列名有
  `ing_`/`stp_` 前缀）、`RecipeFavoriteMapper.xml`、`RecipeHistoryMapper.xml`。简单 CRUD 用 Wrapper。
- 全局 `update-strategy: always` 是刻意的（等价原来的 JPA merge 全字段），3.5.9 起已无 `IGNORED`。

## 与其他服务的边界

- **Java 不调用 Python 服务。**本模块树里没有指向 chat 的 HTTP 客户端；`RestTemplate` 只用于微信
  `jscode2session`，`java.net.http` 用于讯飞 TTS 与 ASR。
- 方向相反：`services/chat` 里的 agent 插槽用 `X-Internal-Token` 回调本服务的
  `/talk/internal/suggestions` 与 `/novel/internal/**`。令牌由根 `.env` 的 `APP_INTERNAL_TOKEN` 一分三映射
  （`TALK_INTERNAL_TOKEN` / `NOVEL_INTERNAL_TOKEN` / `PY_SERVER_INTERNAL_TOKEN`），两端必须一致。
- `/novel/chat-ticket` 发一张 60 秒的一次性票据去开 `/ws/chat`，Python 侧调
  `/novel/internal/chat-ticket/verify` 核验。它刻意挂在 `/novel/**` 而不是 `/auth/**` 下：这样
  「能领读正典的票」与「能进创作工作台」是同一个门槛，不用再造第二条规则；票据只带 uid、不带角色，
  不能当会话令牌拿去打普通接口。
- 媒体一律「地址进库、文件进 COS」：接口返回 COS 公网 URL，播放器不经过本服务。

## 构建与部署

`Dockerfile` 是多阶段：`maven:3.9-eclipse-temurin-17` 构建（先 COPY 全部 pom 再 `dependency:go-offline`
拿缓存层，最后 `mvn -B -pl api-bootstrap -am -DskipTests package`），`eclipse-temurin:17-jre` 运行，
`EXPOSE 8080`，非 root 的 `appuser`，`/app/uploads` 为卷。构建上下文是**本目录**——
`docker-compose.yml` 的 `api: build: ./services/api` 与 `scripts/deploy-api.sh` 一致，
`docker build -f services/api/Dockerfile .` 那种根上下文写法只有 chat / admin-web / novel-web 三个镜像需要。
基础镜像与 apt 源都带国内加速 ARG，可用 `USE_OFFICIAL_IMAGES=1 pnpm api:deploy:official` 走官方名。

上线手册在 `DEPLOY_CLOUDRUN.md`（密钥来源、一键脚本、手动等价命令、四处国内加速、控制台配置、
高频坑、chat 与 Redis）。里面最要紧的一条：云托管必须显式设 `SPRING_PROFILES_ACTIVE=prod`，
否则 jar 里烘着的 `local` profile 生效，容器连的是 `localhost`。

## CI

`.github/workflows/ci.yml` 的 `api` job 用 Temurin 17 + Maven 缓存，并以 MySQL 8.4 / Redis Stack 服务容器
+ 环境变量注入（等价 `application-local.yaml`）跑 `mvn verify`——不读任何本机 yaml。

## 目录里的临时产物

`boot-package.txt`、`root-build.txt`、`recipe-compile.txt`、`recipe-clean.txt` 是 Maven 控制台输出日志，
不是配置，也未被 `.gitignore` 收录（当前处于未跟踪状态）。其中两个的 reactor 清单里没有 `po-novel`，
说明早于 novel 模块，属过期残留。可以删或加忽略规则——**这一步留给本人决定，文档只做登记**。
