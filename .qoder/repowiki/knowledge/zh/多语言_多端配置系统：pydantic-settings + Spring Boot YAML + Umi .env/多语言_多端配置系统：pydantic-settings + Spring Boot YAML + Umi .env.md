---
kind: configuration_system
name: 多语言/多端配置系统：pydantic-settings + Spring Boot YAML + Umi .env
category: configuration_system
scope:
    - '**'
source_files:
    - docker-compose.yml
    - .env.example
    - services/chat/app/config.py
    - services/agent-core/src/po_agent_core/config.py
    - services/agent-cooking/src/po_agent_cooking/config.py
    - services/api/api-bootstrap/src/main/resources/application.yaml
    - apps/admin-web/config/config.ts
    - apps/admin-web/.env.example
---

## 总体方案

仓库是一个 pnpm monorepo，包含 Java (Spring Boot) API、Python (FastAPI + LangGraph) Chat/Agent 服务、React 管理后台与两个移动端（Expo / 微信小程序）。各子项目各自维护自己的运行时配置，通过 `docker-compose.yml` 在本地统一注入环境变量。

| 组件 | 配置框架/格式 | 加载入口 | 命名空间前缀 |
|---|---|---|---|
| FastAPI chat 服务 | `pydantic_settings.BaseSettings` | `app/config.py::get_settings()` | `PY_SERVER_` |
| agent-core 核心库 | `pydantic_settings.BaseSettings` + `ModelSlot` | `services/agent-core/src/po_agent_core/config.py` | `AGENT_CORE_` |
| agent-cooking 垂直 Agent | `pydantic_settings.BaseSettings` | `services/agent-cooking/src/po_agent_cooking/config.py` | `COOKING_` |
| Spring Boot API | `application.yaml` + `application-local.yaml` | `services/api/api-bootstrap/src/main/resources/application.yaml` | 无（Spring 标准） |
| 前端 admin-web | Umi `.env` + `config/config.ts` | `apps/admin-web/.env.example` → `UMI_APP_*` | `UMI_APP_` |
| 编排层 | `docker-compose.yml` + 根 `.env.example` | `docker compose up` | 透传到各容器 |

## 关键文件

- `docker-compose.yml`：定义 mysql / redis / api / chat / web 五个服务，把根目录 `.env` 中的变量以 `SPRING_*`、`PY_SERVER_*`、`AGENT_CORE_*`、`COOKING_*` 等前缀注入到对应容器。
- `.env.example`：仓库级单点文档，集中列出所有可配项（MySQL、JWT、讯飞 TTS、腾讯云 COS、网关端口、LLM provider、checkpointer、embedding、COOKING_API_BASE_URL），是新增配置的权威清单。
- `services/chat/app/config.py`：宿主 Settings，只承载 host/port/CORS 等“进程怎么监听”的参数；明确与 `AGENT_CORE_*` 分家，避免凭据散落。
- `services/agent-core/src/po_agent_core/config.py`：全局 LLM/embedding/checkpointer/router 配置，支持 `llm_roles` 按角色覆盖默认槽位（`__` 双下划线嵌套分隔符）。
- `services/agent-cooking/src/po_agent_cooking/config.py`：仅承载菜谱数据源 URL、超时、检索条数等垂直领域参数。
- `services/api/api-bootstrap/src/main/resources/application.yaml`：Spring Boot 主配置，全部敏感值用 `${ENV:默认}` 占位，生产密钥由微信云托管环境变量注入；`application-local.yaml` 用于本地 IDE 运行。
- `apps/admin-web/config/config.ts`：Umi 构建期配置，通过 `define` 把 `UMI_APP_API_BASE_URL`、`COMMIT_HASH` 等编译进浏览器代码。
- `apps/admin-web/.env.example`：前端开发时代理目标地址模板。

## 架构约定

1. **环境变量命名空间隔离**：每个 Python 模块使用独立的 `env_prefix`（`PY_SERVER_` / `AGENT_CORE_` / `COOKING_`），同一份 `.env` 文件里键互不干扰。注释中明确说明这是刻意设计，避免凭据散落到 host/port 同一处。
2. **`.env` 文件共享但解析隔离**：所有 Python 服务的 `BaseSettings.model_config.env_file = ".env"` 指向当前工作目录的 `.env`；由于 `extra="ignore"`，一个 Settings 类会忽略不属于自身前缀的键，从而允许多个 Settings 从同一个文件读取。
3. **进程级缓存**：chat 服务的 `get_settings()` 用 `functools.lru_cache` 包装，确保 `.env` 只解析一次；测试需先调用 `cache_clear()` 再注入自定义环境变量。
4. **多模型增量配置**：`AgentCoreSettings.llm_roles` 通过 `env_nested_delimiter="__"` 解析形如 `AGENT_CORE_LLM_ROLES__WRITE__MODEL=qwen-max` 的变量，未声明的角色一律回落默认槽位——“不配就是单模型”，多模型是增量而非必答题。
5. **跨 provider 密钥不回退**：当角色覆盖的 `provider` 与默认槽位不同时，`api_key` 不会复用默认槽位密钥，缺省时直接报错并指明应配置哪个变量。
6. **Spring Boot 纯环境变量驱动**：`application.yaml` 中所有业务字段都写成 `${ENV_KEY:default}`，没有 profile 分支；生产部署（微信云托管）直接把键值作为平台环境变量注入，无需切换 profile 文件。
7. **前端构建期注入**：Umi 在 `config/config.ts` 的 `define` 块中把 `UMI_APP_API_BASE_URL`、`COMMIT_HASH` 等编译进产物；注释明确指出 Umi 的 dev server 不自动监听 `.env`，修改后需重启。
8. **依赖健康检查**：compose 中 `depends_on` 配合 `condition: service_healthy`，mysql/redis 启动后才拉起 api，api/chat 就绪后才拉起 web 网关。
9. **降级优先于失败**：LLM/embedding 未配置时聊天服务走离线模式；Redis Stack 不可用时 checkpointer 静默降级为 memory；TTS/COS 未配置时接口返回可读错误而不阻断启动。

## 约束与规则

- **敏感信息不进仓库**：根 `.env`、`application-local.yaml`、`services/api/application-prod.json` 均被 `.gitignore` 排除；`.env.example` 仅提供占位值。
- **JWT_SECRET 必须 Base64 且解码后 ≥ 32 字节**：`.env.example` 注释明确要求 jjwt HMAC-SHA256 的输入长度，并提供生成示例。
- **Redis 必须使用 Redis Stack**：compose 注释写明普通 `redis:7-alpine` 缺少 JSON/RediSearch 模块，会导致 setup 报 unknown command 并静默降级为 memory checkpointer。
- **Spring Boot 数据库建表走 `schema.sql`**：`spring.sql.init.mode=always`，替代 JPA `ddl-auto: update`，脚本幂等（`CREATE TABLE IF NOT EXISTS`）。
- **CORS 来源写逗号分隔字符串**：`cors_origins` 显式定义为 `str` 而非 `list[str]`，因为 pydantic-settings 对复杂类型的环境变量要求 JSON 语法，逗号分隔更便于 `.env` 维护；属性方法会过滤空项和空格。
- **后端 API 统一 `/api` 前缀**：`server.servlet.context-path=/api` 是前后端 REST 契约的一部分，Nginx 网关将 `^~ /api/` 原样转发。
- **前端 dev 不读取仓库根 `.env`**：Umi 只加载 `apps/admin-web/.env`，因此本地直连后端时需分别配置 `apps/admin-web/.env` 中的 `UMI_APP_API_BASE_URL` 与 `UMI_APP_WS_BASE_URL`。
- **模型装配期取定，运行中不热切换**：`.env.example` 注释明确“改完 .env 重启服务（模型在装配期取定，运行中不热切换）”。