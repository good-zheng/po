---
name: goodzheng-java-dev
description: 为 po monorepo 的 Java Spring Boot 后端任务选择本地约定和按需开源参考。用于 services/api 的 REST API、Controller、Service、MyBatis-Plus、MySQL、JWT、Redis、事务、配置与测试。
---

# Po Java 路由

## 项目基线

目标服务为 `services/api/`：Java 17、Spring Boot 4.1.1、同步 Spring MVC、MySQL、Redis（Jedis）、jjwt，对外路径前缀 `/api`（`server.servlet.context-path`，actuator 同前缀）。Maven reactor 多模块：

| 模块 | 职责 |
| --- | --- |
| `shared/` | 公共 DTO、`Result<T>` 响应包装、异常 |
| `identity/` | 用户、认证、JWT |
| `recipe/` | 菜谱与分类 |
| `novel/` | 小说 |
| `api-bootstrap/` | 启动模块（application.yaml、DataInitializer） |

先读目标模块的 `pom.xml`、相邻 Controller/Service/Mapper 和测试，再选择下列参考。

## 二级披露路由

所有 Spring Boot 参考均来自：`../../skill-sources/spring-boot-skills/skills/spring-boot-4/`。

| 任务 | 读取的上游 skill |
| --- | --- |
| REST API、Controller、DTO、分页、错误契约 | `rest-api-conventions/SKILL.md` |
| 分层职责、模块组织 | `layered-architecture/SKILL.md` |
| MyBatis-Plus 实体、Mapper、Wrapper、分页 | 无上游 skill，按下方「本地硬约束」持久层约定执行 |
| Redis 缓存或会话 | `spring-data-redis/SKILL.md` |
| JWT、认证或授权 | `spring-security-jwt/SKILL.md` |
| 事务、幂等、重试 | `transactional-patterns/SKILL.md`、`idempotency-patterns/SKILL.md` 或 `resilience-retry/SKILL.md` 中最匹配的一份 |
| 配置、`application.yaml`、环境属性 | `configuration-properties/SKILL.md` |
| 单元、集成或架构测试 | `testing-pyramid/SKILL.md` |
| 指标、健康检查、可观测性 | `production-observability/SKILL.md` |

一个问题只选一份最直接的参考；需要第二份时说明两个关注点为何不可分割。

## 本地硬约束

- 对外接口继续使用 `shared` 模块的 `Result<T>` 响应包装和现有业务码；不要因上游参考改成另一套全局错误协议。
- 持久层现状：业务模块（identity/recipe/novel）统一 MyBatis-Plus（`mybatis-plus-spring-boot4-starter`，版本在根 pom `dependencyManagement` 统一管理）。约定：Mapper 是各模块 `repository` 包下的 `@Mapper` 接口（继承 `BaseMapper<T>`，仅存于本模块的表）；实体用 `@TableName`/`@TableId(type = IdType.AUTO)`，创建时间 `@TableField(updateStrategy = FieldStrategy.NEVER)`，更新时间 `@TableField(fill = FieldFill.UPDATE)`（由 `api-bootstrap` 的 `AuditMetaObjectHandler` 填充）；Controller/Service 的 `Page`/`Pageable` 来自 spring-data-commons，Service 内用 `shared` 模块的 `MyBatisPages` 做分页转换；分页依赖 `api-bootstrap` 的 `MybatisPlusInterceptor`（PaginationInnerInterceptor）；全局 `update-strategy: always`（等价原 JPA merge 全字段；3.5.9 起已无 IGNORED）。表结构以 `api-bootstrap/src/main/resources/schema.sql` 为准（`spring.sql.init.mode: always` 幂等建表），不再由 JPA 自动建表。新表/新字段先改 schema.sql 再改实体。复杂 SQL（连表、resultMap、动态 SQL）用 XML mapper：放各业务模块 `src/main/resources/mapper/XxxMapper.xml`，文件名与 Mapper 接口同名，namespace 为接口全限定名，由 `mybatis-plus.mapper-locations: classpath*:mapper/**/*.xml` 加载；简单 CRUD 继续用 Wrapper。示例：recipe 模块 `RecipeMapper.xml` 的 `selectDetailWithChildren`（LEFT JOIN 子表 + 带 ing_/stp_ 列前缀的 collection resultMap，一次查询带出食材和步骤）。
- 本项目是 Spring MVC，不为普通接口引入 WebFlux、R2DBC 或 Spring Security OAuth2 Resource Server。
- 本地 JWT 基于 jjwt 与现有 token 服务；上游 JWT skill 仅作安全和结构参考，不能替换既有身份协议。
- 修改实体关系、事务边界、软删除或权限前，先追踪已有查询过滤与调用方。
- 验证：仓库根 `pnpm api:verify`（等价 `mvn -f services/api/pom.xml verify`）；本地起服务依赖 MySQL/Redis，用根目录 `.env` + `docker compose up -d mysql redis`。
