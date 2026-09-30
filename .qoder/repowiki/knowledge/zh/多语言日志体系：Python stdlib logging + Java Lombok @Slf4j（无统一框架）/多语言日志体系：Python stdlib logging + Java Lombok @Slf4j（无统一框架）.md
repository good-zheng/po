---
kind: logging_system
name: 多语言日志体系：Python stdlib logging + Java Lombok @Slf4j（无统一框架）
category: logging_system
scope:
    - '**'
source_files:
    - services/agent-core/src/po_agent_core/memory/checkpointer.py
    - services/chat/app/routers/ws.py
    - services/agent-cooking/src/po_agent_cooking/agent.py
    - services/agent-cooking/src/po_agent_cooking/tools.py
    - services/agent-core/src/po_agent_core/memory/store.py
    - services/agent-core/src/po_agent_core/routing/router.py
    - services/agent-core/src/po_agent_core/supervisor/graph.py
    - services/api/recipe/src/main/java/com/goodzheng/po/recipe/controller/TtsController.java
    - services/api/recipe/src/main/java/com/goodzheng/po/recipe/tts/TtsAudioStore.java
    - services/api/recipe/src/main/java/com/goodzheng/po/recipe/tts/XfyunTtsService.java
    - services/api/identity/src/main/java/com/goodzheng/po/identity/wechat/WeChatService.java
    - services/api/api-bootstrap/src/main/java/com/goodzheng/po/config/DataInitializer.java
    - services/api/application-prod.json
---

## 1. 使用的系统/方案

本仓库是 Python + Java + TypeScript 的混合 monorepo，**没有跨语言的统一日志框架**。各服务各自使用其生态的标准日志实现：

- **Python 服务**（`services/chat`、`services/agent-core`、`services/agent-cooking`）：全部使用 Python 标准库 `logging` 模块，通过 `logger = logging.getLogger(__name__)` 获取命名 logger。
- **Java API 服务**（`services/api`，Spring Boot 项目）：通过 Lombok 注解 `@Slf4j` 注入 `log` 字段，底层由 SLF4J + Logback 提供（Spring Boot 默认依赖），但仓库中未发现自定义的 `application.yaml` / `logback-spring.xml` 配置，仅有一个被 `.gitignore` 排除的 `application-prod.json` 环境变量备忘文件。
- **前端**（`apps/admin-web`、`apps/cooking-app`、`apps/cooking-mini`）：未使用服务端日志；错误处理走 UI 提示（antd `message.error`）或 `console.error`。

## 2. 关键文件

- `services/agent-core/src/po_agent_core/memory/checkpointer.py` — Python 端 logger 定义与 `info` 级别的使用示例（"checkpointer 就绪：memory/sqlite/redis"）。
- `services/chat/app/routers/ws.py` — WebSocket 路由中的异常日志入口，使用 `logger.exception("WS 聊天处理异常")` 输出堆栈。
- `services/agent-cooking/src/po_agent_cooking/agent.py`、`tools.py` — agent 与工具层的 logger 实例化点。
- `services/agent-core/src/po_agent_core/memory/store.py`、`routing/router.py`、`supervisor/graph.py` — agent-core 各子模块的 logger 实例化点。
- `services/api/recipe/src/main/java/com/goodzheng/po/recipe/controller/TtsController.java`、`TtsAudioStore.java`、`XfyunTtsService.java`、`identity/wechat/WeChatService.java`、`api-bootstrap/config/DataInitializer.java` — Java 端通过 `@Slf4j` 使用 `log.info/warn/error/debug` 的典型位置。
- `services/api/application-prod.json` — Spring Boot 生产环境配置备忘（含 `SPRING_PROFILES_ACTIVE: prod`），但非日志配置。

## 3. 架构与约定

### Python 侧
- 每个模块在文件顶部 `import logging` 后声明 `logger = logging.getLogger(__name__)`，形成以包路径为名的分层 logger 树。
- 日志级别使用较为朴素：`logger.info(...)` 用于初始化/就绪事件（如 checkpointer 策略选择），`logger.debug(...)` 用于调试信息（如 router 决策分数），`logger.exception(...)` 用于捕获并输出完整堆栈（ws 路由异常分支）。
- 没有集中式 formatter/handler 配置；日志格式与输出目标由宿主进程（FastAPI/Uvicorn、LangGraph runner）决定。
- 结构化字段不是通过 JSON 字段传递，而是直接拼接在消息字符串中（例如 `logger.info("checkpointer 就绪：%s", strategy)`、`logger.debug("路由决策：text=%r intent=%r score=%.3f", ...)`）。

### Java 侧
- 所有需要日志的类加 `@Slf4j` 注解（Lombok 生成 `private static final Logger log;`），调用 `log.info/warn/error/debug("...", args...)`。
- 日志内容以中文为主，参数用 SLF4J `{}` 占位符传入，避免字符串拼接开销。
- 未发现全局日志配置文件（搜索 `application.yaml` / `logback` 无匹配），因此沿用 Spring Boot 默认 Logback 配置。

### 前端
- 不产生服务端日志。请求错误通过 umi-request 拦截器调用 antd `message.error` 展示给用户。

## 4. 约定与约束

- **约定（描述性）**：Python 模块统一采用 `logger = logging.getLogger(__name__)` 模式；Java 类统一采用 `@Slf4j` + `log.*` 模式；日志消息以中文书写，SLF4J 参数使用 `{}` 占位符。
- **约束（可验证）**：Python 端未发现第三方日志库（loguru、structlog、logbook 等）的 import；Java 端未发现自定义 `application.yaml` 或 `logback-spring.xml` 文件，也未见 `logging.` 前缀的显式配置代码——日志行为完全由框架默认值驱动。
- **约束（可验证）**：`services/api/application-prod.json` 明确标注 `_comment` 说明该文件已被 `.gitignore` 排除、勿提交，且只包含 Spring Boot 环境变量备忘，不包含任何日志相关键（如 `logging.level`、`logging.file`）。
- **约束（可验证）**：WebSocket 路由中对客户端断连异常做了特殊处理——捕获 `WebSocketDisconnect` 和内部 `_ClientGone` 后直接 return，不调用 `logger.exception`，从而避免把正常断线记录为错误（见 `ws.py` 第 181-183 行）。