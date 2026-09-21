---
kind: configuration_system
name: 多端配置体系：Spring YAML + Python .env + 前端环境变量
category: configuration_system
scope:
    - '**'
source_files:
    - java_server/po/src/main/resources/application.yaml
    - java_server/po/src/main/java/com/goodzheng/po/util/JwtUtil.java
    - py_server/app/config.py
    - py_server/.env.example
    - web_client/po-admin/config/defaultSettings.ts
    - web_client/po-admin/.env
    - web_client/shadcn-admin/.env.example
---

## 1. 使用的系统与工具

本仓库包含三个独立的服务/前端，各自采用其生态的标准配置方式：
- **Java Spring Boot**（`java_server/po`）：使用 `application.yaml` 作为唯一配置文件，通过 `spring.profiles.active=dev` 激活开发环境；使用 `@Value` 注入自定义属性（如 JWT），并启用 Actuator 暴露健康与指标端点。
- **Python FastAPI**（`py_server`）：使用 `pydantic-settings`（`app/config.py` 的 `Settings` 类，`SettingsConfigDict(env_file=".env", env_prefix="PY_SERVER_")`）从 `py_server/.env` 加载 `PY_SERVER_HOST`、`PY_SERVER_PORT`、`PY_SERVER_CORS_ORIGINS` 等键，`lru_cache` 缓存单例；提供 `.env.example` 作为模板。
- **前端**：`web_client/po-admin` 使用 Vite/Ant Design Pro 的 `config/defaultSettings.ts` 管理布局与主题 token；`web_client/shadcn-admin` 通过 `.env` / `.env.example` 中的 `VITE_CLERK_PUBLISHABLE_KEY` 注入构建期常量。

## 2. 关键文件

| 组件 | 配置文件 | 作用 |
|---|---|---|
| Java 后端 | `java_server/po/src/main/resources/application.yaml` | 服务器端口、上下文路径 `/api`、数据源、JPA、Redis、日志、Actuator、JWT 密钥与过期时间、业务元信息 |
| Java 后端 | `java_server/po/src/main/java/com/goodzheng/po/util/JwtUtil.java` | 通过 `@Value("${jwt.secret}")`、`@Value("${jwt.expiration}")` 消费 YAML 中的 JWT 配置 |
| Python 后端 | `py_server/app/config.py` | pydantic-settings `Settings` 类，`PY_SERVER_` 前缀环境变量 + `.env` 加载，`get_settings()` 单例 |
| Python 后端 | `py_server/.env.example` | 示例运行参数（HOST/PORT/CORS_ORIGINS） |
| 前端 po-admin | `web_client/po-admin/config/defaultSettings.ts` | Ant Design Pro 布局、主题色、内容宽度等 UI 配置 |
| 前端 shadcn-admin | `web_client/shadcn-admin/.env.example` | Vite 构建期变量 `VITE_CLERK_PUBLISHABLE_KEY` |

## 3. 架构与约定

- **按服务隔离**：每个子项目独立维护自己的配置，不存在跨服务共享的配置中心或统一配置库。Java 与 Python 之间通过 HTTP 调用，不共享配置。
- **Spring Boot 单文件 YAML**：所有配置集中在 `application.yaml`，未拆分 `application-dev.yaml` / `application-prod.yaml`，仅通过 `spring.profiles.active=dev` 预留了环境切换入口。
- **环境变量优先**：Python 侧明确声明“均可通过环境变量覆盖”，即 `.env` 是默认值来源，真实部署时应以操作系统环境变量为准；`.env.example` 作为可被 git 追踪的模板。
- **敏感信息处理**：JWT 密钥硬编码在 `application.yaml` 中（`jwt.secret`），未走环境变量；Python 侧当前无密钥类配置（LLM Key 等未来引入时须经 `.env`，不得写入代码）。两者均未引入密钥管理服务。
- **上下文路径统一**：Spring Boot 将 `server.servlet.context-path` 设为 `/api`，使前后端可通过同一域名下的 `/api` 前缀访问后端 API。
- **前端配置分层**：po-admin 使用 TypeScript 常量对象 `defaultSettings.ts` 描述 UI 行为；shadcn-admin 使用 Vite 约定的 `VITE_*` 环境变量在构建时注入。

## 4. 约定与约束

- **Spring Boot**：
  - 自定义配置必须放在 `application.yaml` 的顶层 key 下（当前为 `app.*` 与 `jwt.*`），并通过 `@Value` 注入到 Bean 中。
  - 日志输出至 `logs/application.log`，且已启用 gzip 归档（由日志轮转策略生成 `.gz` 文件）。
  - Actuator 仅暴露 `health,info,metrics,prometheus` 四个端点，生产环境不应扩大暴露范围。
- **Python FastAPI**：
  - 新增配置项应添加到 `app/config.py` 的 `Settings` 类（带类型注解与默认值），自动获得 `PY_SERVER_` 前缀环境变量覆盖能力，保持 `.env.example` 同步更新。
  - 配置消费统一经 `get_settings()`（`lru_cache` 单例）；LLM 类配置未来引入时必须保留离线降级路径。
- **前端**：
  - po-admin 的 `NODE_ENV` 在 `.env` 中设置为 `development`，用于控制构建/代理行为。
  - shadcn-admin 遵循 Vite 的 `VITE_` 前缀约定，仅允许在 `.env` 中声明构建期可见的变量。

总体而言，该仓库没有统一的配置中心或配置抽象层，而是让每个技术栈沿用自身生态的最佳实践：Spring 的 YAML + `@Value`、FastAPI 的 pydantic-settings（`.env` + `PY_SERVER_` 前缀）、以及前端各自的构建期环境变量机制。