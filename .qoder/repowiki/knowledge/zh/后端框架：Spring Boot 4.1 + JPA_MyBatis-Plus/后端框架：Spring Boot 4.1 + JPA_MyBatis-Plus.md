---
kind: external_dependency
name: 后端框架：Spring Boot 4.1 + JPA/MyBatis-Plus
slug: spring-boot-4
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
---

### Spring Boot 4.1
- 作为 `java_server/po` 的父工程，Java 17 编译目标
- 通过 `spring-boot-starter-data-jpa`、`spring-boot-starter-webmvc`、`spring-boot-starter-validation`、`spring-boot-starter-actuator`、`spring-boot-devtools` 等 starter 组合使用
- Redis 客户端显式替换为 Jedis（排除默认 lettuce）
- Actuator + Micrometer Prometheus 暴露监控指标
- 构建插件：spring-boot-maven-plugin + maven-compiler-plugin（配置 Lombok annotationProcessorPaths）

注意：项目同时依赖 JPA 和 MyBatis-Plus，新增实体时需注意 ORM 选择一致性。