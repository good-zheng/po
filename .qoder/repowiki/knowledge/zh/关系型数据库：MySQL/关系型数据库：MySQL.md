---
kind: external_dependency
name: 关系型数据库：MySQL
slug: mysql
category: external_dependency
category_hints:
    - vendor_identity
scope:
    - '**'
---

### MySQL
- 通过 `mysql-connector-j` 驱动连接，JPA `ddl-auto: update` 自动创建/升级表结构
- 业务表包括：`user`、`recipe`、`recipe_ingredient`、`recipe_step`、`recipe_category` 等
- 软删除统一使用 `deleted_at` 字段（遵循项目规范）
- 会话中通过命令行执行 SQL 种子数据（如 `data-category.sql` 插入 25 条分类）
- 启动时需确保 MySQL 服务可访问（会话中出现本地 MySQL 无法启动的问题）