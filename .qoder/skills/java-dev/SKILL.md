---
name: goodzheng-java-dev
description: 为 po monorepo 的 Java Spring Boot 后端任务选择本地约定和按需开源参考。用于 services/api 的 REST API、Controller、Service、MyBatis-Plus、MySQL、JWT、Redis、内网正典通道、ASR 网关、novel/talk 模块、配置与测试。
---

# Po Java 路由

## 项目基线

目标服务为 `services/api/`：Java 17、Spring Boot 4.1.1、同步 Spring MVC、MySQL、Redis（Jedis）、jjwt，对外路径前缀 `/api`（`server.servlet.context-path`，actuator 同前缀）。Maven reactor 多模块：

| 模块 | 职责 |
| --- | --- |
| `shared/` | 公共 DTO、`Result<T>` 响应包装、异常、`MyBatisPages` |
| `identity/` | 用户、认证、JWT、`SecurityConfig` |
| `recipe/` | 菜谱与分类（含 seed SQL 与 `static/covers/`，见 `tools/README-covers.md`） |
| `talk/` | 言外会话/话语、TTS 票据、讯飞 ASR 网关（`talk/asr/`：`AsrTicketService`、`AsrHandshakeInterceptor`、`TalkWebSocketConfig` → `/ws/asr`） |
| `novel/` | 长篇小说：`/books**` 读者与创作接口、`/novel/**` 工作台（`NovelStudioController`）、`/novel/internal/**` agent 正典写入通道（`NovelInternalController`） |
| `api-bootstrap/` | 启动模块（application.yaml、`application-prod.json`、schema.sql、DataInitializer、AuditMetaObjectHandler、MybatisPlusInterceptor） |

包根是 `com.goodzheng.po.<module>`（不是 `com.po.*`）。先读目标模块的 `pom.xml`、相邻 Controller/Service/Mapper 和测试，再选择下列参考。

## 二级披露路由

Spring Boot 参考均来自 `../../skill-sources/spring-boot-skills/skills/spring-boot-4/`（按主题一个子目录，子目录内是 `SKILL.md` + `examples/` + `templates/`；当前无顶层 `SKILL.md`，别去读 `spring-boot-4/SKILL.md`）。该镜像在 git 里是 gitlink，目录空了取不回内容，恢复方式见 `../project-router/SKILL.md`；读不到就走下表「本地替代」列，不要因为没有上游 skill 就停住。

| 任务 | 上游 skill（缺失时走本地替代） |
| --- | --- |
| REST API、Controller、DTO、分页、错误契约 | `rest-api-conventions/SKILL.md` → 本地：`shared` 的 `Result`/异常 + 同模块相邻 Controller |
| 分层职责、模块组织 | `layered-architecture/SKILL.md` → 本地：`services/api/README.md` 的模块表 |
| MyBatis-Plus 实体、Mapper、Wrapper、分页 | 本来就没有上游 skill，按下方「本地硬约束」持久层约定执行 |
| Redis 缓存或会话 | `spring-data-redis/SKILL.md` → 本地：`api-bootstrap` 的 Redis 配置类与既有调用方 |
| JWT、认证或授权 | `spring-security-jwt/SKILL.md` → 本地：`identity/security/SecurityConfig.java` 与 `novel/ChatTicketAndActorScopeTest` |
| 事务、幂等、重试 | `transactional-patterns`/`idempotency-patterns`/`resilience-retry` 中最匹配的一份 → 本地：`novel/service/impl/CanonTxWriter.java`（幂等靠库层唯一键 + 查回覆盖） |
| 配置、`application.yaml`、环境属性 | `configuration-properties/SKILL.md` → 本地：`application.yaml` + 本节「内部令牌」一条 |
| 单元、集成或架构测试 | `testing-pyramid/SKILL.md` → 本地：各模块 `src/test/java` 现有用例（多为 `ReflectionTestUtils` 直调 Controller/Service，不起完整上下文） |
| 指标、健康检查、可观测性 | `production-observability/SKILL.md` → 本地：`GET /actuator/health` 与 `@Slf4j` 既有日志 |

一个问题只选一份最直接的参考；需要第二份时说明两个关注点为何不可分割。

## 本地硬约束

- 对外接口继续使用 `shared` 模块的 `Result<T>` 响应包装和现有业务码；不要因上游参考改成另一套全局错误协议。
- 持久层现状：业务模块（identity/recipe/talk/novel）统一 MyBatis-Plus（`mybatis-plus-spring-boot4-starter`，版本在根 pom `dependencyManagement` 统一管理）。约定：Mapper 是各模块 `repository` 包下的 `@Mapper` 接口（继承 `BaseMapper<T>`，仅存于本模块的表）；实体用 `@TableName`/`@TableId(type = IdType.AUTO)`，创建时间 `@TableField(updateStrategy = FieldStrategy.NEVER)`，更新时间 `@TableField(fill = FieldFill.UPDATE)`（由 `api-bootstrap` 的 `AuditMetaObjectHandler` 填充）；Controller/Service 的 `Page`/`Pageable` 来自 spring-data-commons，Service 内用 `shared` 模块的 `MyBatisPages` 做分页转换；分页依赖 `api-bootstrap` 的 `MybatisPlusInterceptor`（PaginationInnerInterceptor）；全局 `update-strategy: always`（等价原 JPA merge 全字段；3.5.9 起已无 IGNORED）。表结构以 `api-bootstrap/src/main/resources/schema.sql` 为准（`spring.sql.init.mode: always` 幂等建表），不再由 JPA 自动建表。新表/新字段先改 schema.sql 再改实体。复杂 SQL（连表、resultMap、动态 SQL）用 XML mapper：放各业务模块 `src/main/resources/mapper/XxxMapper.xml`，文件名与 Mapper 接口同名，namespace 为接口全限定名，由 `mybatis-plus.mapper-locations: classpath*:mapper/**/*.xml` 加载；简单 CRUD 继续用 Wrapper。示例：recipe 模块 `RecipeMapper.xml` 的 `selectDetailWithChildren`（LEFT JOIN 子表 + 带 ing_/stp_ 列前缀的 collection resultMap，一次查询带出食材和步骤）。
- 本项目是 Spring MVC，不为普通接口引入 WebFlux、R2DBC 或 Spring Security OAuth2 Resource Server。
- 认证与开放面（`identity/security/SecurityConfig.java` 为准）：`/auth/login|register|wechat-login|openid-login|app-register` 公开；内容浏览（`GET /recipes*`、`/recipe-categories*`、`/files/**`、静态资源）与 `GET /actuator/health` 对游客开放，其余 actuator 端点仅管理端；`/tts`、`/tts/prefetch` 需登录（消耗讯飞额度，音频产物是 COS 公网 URL，播放器不经过本服务）。`/auth/openid-login` 只接受请求体 `loginCode` 走 jscode2session，禁止再从请求头取 openid——免域名 `wx.request` 渠道不注入 `X-WX-OPENID`，头部信任等于任意冒充。改开放面必须同步 `apps/cooking-mini` 的 AuthGuard 策略（浏览免登录、做菜/聊天需登录、tab 页用缺省页不强跳）。
- 本地 JWT 基于 jjwt 与现有 token 服务；上游 JWT skill 仅作安全和结构参考，不能替换既有身份协议。
- 内网通道（`/novel/internal/**`、`/talk/internal/**`）在 `SecurityConfig` 里是 `permitAll`，鉴权完全靠 Controller 自校 `X-Internal-Token`：令牌读 `app.internal-token`（`application.yaml` 为 `${APP_INTERNAL_TOKEN:}`，真值只写在 gitignore 的 `application-local.yaml`）。**空白即拒绝**（`internalToken.isBlank()` 直接 401），所以云托管上没配 `APP_INTERNAL_TOKEN` 的表现是「模型全跑完、最后归档那一步 401」，不是启动失败。改这条通道时值不进代码/日志/skill/文档，只写变量名。
- `/ws/asr` 在 matcher 里是 `permitAll`，真实校验发生在握手拦截器 `talk/asr/AsrHandshakeInterceptor` 读 `?ticket=`——小程序 WS 不能带自定义请求头，票据只能拼 query。新增 WS 端点要沿用「matcher 放行 + 握手期验票」，别以为 `permitAll` 就是公开端点。
- 修改实体关系、事务边界、软删除或权限前，先追踪已有查询过滤与调用方。
- 验证：仓库根 `pnpm api:verify`（等价 `mvn -f services/api/pom.xml verify`）；本地起服务依赖 MySQL/Redis，用根目录 `.env` + `docker compose up -d mysql redis`。
