---
kind: external_dependency
name: 缓存：Redis（Jedis 客户端）
slug: redis-jedis
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
---

### Redis
- 通过 `spring-boot-starter-data-redis` 接入，但显式排除了默认的 Lettuce 客户端，改用 `redis.clients:jedis`
- 当前项目中未看到实际缓存逻辑代码，仅声明了依赖；后续如需缓存能力需自行实现
- 运行时需确保 Redis 服务可用（端口及连接信息应通过配置文件注入）