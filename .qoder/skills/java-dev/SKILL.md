---
name: goodzheng-java-dev
description: 为 goodzheng-pro 的 Java Spring Boot 4 后端任务选择本地约定和按需开源参考。用于 java_server/po 的 REST API、Controller、Service、JPA、MyBatis-Plus、MySQL、JWT、Redis、事务、配置与测试。
---

# Goodzheng Java 路由

## 项目基线

目标服务为 `java_server/po/`：Java 17、Spring Boot 4.1.1、同步 Spring MVC、MySQL、JPA/Hibernate 与 MyBatis-Plus 并存、Jedis、jjwt。先读目标模块的 `pom.xml`、相邻 Controller/Service/Repository 和测试，再选择下列参考。

## 二级披露路由

所有 Spring Boot 参考均来自：`../../skill-sources/spring-boot-skills/skills/spring-boot-4/`。

| 任务 | 读取的上游 skill |
| --- | --- |
| REST API、Controller、DTO、分页、错误契约 | `rest-api-conventions/SKILL.md` |
| 分层职责、模块组织 | `layered-architecture/SKILL.md` |
| JPA 实体、Repository、关联与查询 | `spring-data-jpa/SKILL.md` |
| Redis 缓存或会话 | `spring-data-redis/SKILL.md` |
| JWT、认证或授权 | `spring-security-jwt/SKILL.md` |
| 事务、幂等、重试 | `transactional-patterns/SKILL.md`、`idempotency-patterns/SKILL.md` 或 `resilience-retry/SKILL.md` 中最匹配的一份 |
| 配置、`application.yml`、环境属性 | `configuration-properties/SKILL.md` |
| 单元、集成或架构测试 | `testing-pyramid/SKILL.md` |
| 指标、健康检查、可观测性 | `production-observability/SKILL.md` |

一个问题只选一份最直接的参考；需要第二份时说明两个关注点为何不可分割。

## 本地硬约束

- 对外接口继续使用项目的 `Result<T>` 响应包装和现有业务码；不要因上游参考改成另一套全局错误协议。
- 每个新持久化功能先在 JPA 或 MyBatis-Plus 中选定一个主要访问路径，不在同一简单 CRUD 流程中混用。
- 本项目是 Spring MVC，不为普通接口引入 WebFlux、R2DBC 或 Spring Security OAuth2 Resource Server。
- 本地 JWT 基于 jjwt 与现有 token 服务；上游 JWT skill 仅作安全和结构参考，不能替换既有身份协议。
- 修改实体关系、事务边界、软删除或权限前，先追踪已有查询过滤与调用方；完成后执行相关 Maven 测试或编译验证。
