---
kind: logging_system
name: 日志系统：Spring Boot Logback + Python 标准输出，无结构化日志框架
category: logging_system
scope:
    - '**'
source_files:
    - java_server/po/src/main/resources/application.yaml
    - py_server/app/main.py
    - py_server/app/routers/ws.py
    - java_server/po/logs/application.log
---

## 1. 使用的系统与框架

- **Java 后端（Spring Boot）**：使用 Spring Boot 内置的 Logback 日志框架，通过 `application.yaml` 中的 `logging.*` 配置项进行集中式配置。未引入 SLF4J/Log4j2 等第三方日志门面或实现。
- **Python 后端（FastAPI/Uvicorn）**：无应用层日志调用；仅依赖 Uvicorn 的访问日志（每个 HTTP/WS 请求一行 INFO）与异常堆栈输出，没有封装统一的 logger 模块。
- **前端**：未观察到专门的前端日志系统，仅依赖浏览器控制台输出。

## 2. 关键文件与位置

- `java_server/po/src/main/resources/application.yaml`：定义全局日志级别、控制台与文件输出格式、日志文件名。
- `py_server/app/main.py`、`py_server/app/routers/`：代码中无日志调用；Uvicorn 运行时输出访问日志到控制台。
- `java_server/po/logs/`：应用运行期生成的日志文件目录（包含按日期滚压缩的 `.gz` 归档）。

## 3. 架构与约定

### Java（Spring Boot）
- **日志级别策略**：根日志级别为 `INFO`；包 `com.example` 设为 `DEBUG`（注意该包名与实际项目包 `com.goodzheng.po` 不一致，因此业务代码默认以 INFO 及以上级别输出）。可通过 `spring.profiles.active: dev` 切换环境。
- **输出格式**：控制台与文件共用同一 pattern：`%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level %logger{36} - %msg%n`，包含时间、线程名、级别、logger 名和消息。
- **文件输出**：日志写入 `logs/application.log`，由 Spring Boot 默认滚动策略管理（仓库中存在按日期命名的 `.log.YYYY-MM-DD.0.gz` 归档文件，说明已启用按天滚动）。
- **业务代码中未见显式日志调用**：当前 Controller/Service 层未发现 `@Slf4j`、`Logger` 字段或 `System.out` 等日志语句，所有日志均来自 Spring/Tomcat/框架自身。

### Python（FastAPI/Uvicorn）
- **访问日志**：由 Uvicorn 自动输出（`INFO: <client> "<method> <path> HTTP/1.1" <status>`），应用代码零日志调用。
- **异常输出**：未捕获异常由 Uvicorn 打印堆栈到标准错误；WebSocket 断连（WebSocketDisconnect）在端点内静默处理。
- **无文件输出**：未配置日志文件，日志仅输出到控制台（由进程管理器/部署环境收集）。
- **无结构化日志**：日志消息为纯字符串，未使用 JSON 结构化格式或自定义字段。

## 4. 约定与约束

- **日志位置集中化**：Java 侧通过 `application.yaml` 统一管理，Python 侧依赖 Uvicorn 内建访问日志，应用代码避免散落的 `print`。
- **日志级别分层**：Java 区分 root/INFO 与特定包的 DEBUG；Python 未做细粒度级别控制。
- **文件滚动**：Java 侧已产生按日期的 gzip 归档日志，表明滚动策略生效；Python 侧未配置文件输出，日志仅输出到标准输出（由部署容器/进程管理器收集）。
- **无统一日志门面**：Java 未使用 SLF4J 注解（如 `@Slf4j`），Python 未封装独立 logger 模块，Java 直接用框架 logger、Python 依赖 Uvicorn 输出。
- **无链路追踪/上下文字段**：日志中不包含 request ID、用户 ID、trace ID 等结构化字段，排查跨服务问题时依赖手动关联。
- **安全注意**：`application.yaml` 中包含明文数据库密码、JWT secret 等敏感信息，不应提交至版本库。