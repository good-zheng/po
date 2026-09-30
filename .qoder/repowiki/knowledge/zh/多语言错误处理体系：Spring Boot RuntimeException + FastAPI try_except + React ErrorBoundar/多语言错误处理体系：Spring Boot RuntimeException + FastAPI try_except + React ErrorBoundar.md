---
kind: error_handling
name: 多语言错误处理体系：Spring Boot RuntimeException + FastAPI try/except + React ErrorBoundary
category: error_handling
scope:
    - '**'
source_files:
    - services/agent-core/src/po_agent_core/errors.py
    - services/chat/app/main.py
    - services/api/identity/src/main/java/com/goodzheng/po/identity/controller/UserController.java
    - services/api/api-bootstrap/src/main/java/com/goodzheng/po/controller/FileController.java
    - apps/admin-web/src/requestErrorConfig.ts
    - apps/admin-web/src/components/ErrorBoundary/index.tsx
---

## 1. 总体方案

本仓库是 pnpm monorepo，包含 Java Spring Boot API、Python FastAPI Chat 服务、React 管理后台与 React Native / Taro 小程序。错误处理在各层采用各自语言的惯用模式，没有跨语言统一错误码或全局异常处理器。

- **Java (Spring Boot)**：控制器/服务中直接 `throw new RuntimeException("...中文消息...")`，未见自定义 Exception 基类、`@ControllerAdvice` / `@RestControllerAdvice` 或统一 ErrorCode 枚举；由 Spring 默认将未捕获异常转为 HTTP 500。
- **Python (FastAPI + agent-core)**：使用标准 `try/except` + 自定义 `AgentCoreError` / `AgentCoreConfigError` 两级异常，用于驱动 LLM 配置降级链。
- **前端 (admin-web / cooking-app / cooking-mini)**：通过 UmiJS `errorConfig.errorThrower` + `errorHandler` 统一处理 Axios 响应错误，并配合自实现的 `ErrorBoundary` 组件拦截 React 渲染期异常。

## 2. 关键文件

- `services/api/shared/src/main/java/com/goodzheng/po/shared/dto/` — shared 模块（未发现统一的 ApiResponse / GlobalException，DTO 目录为空）。
- `services/api/identity/src/main/java/com/goodzheng/po/identity/controller/UserController.java` — 业务异常集中抛出的位置，全部为 `throw new RuntimeException(...)`。
- `services/api/api-bootstrap/src/main/java/com/goodzheng/po/controller/FileController.java` — 上传校验同样抛出 `RuntimeException`。
- `services/chat/app/main.py` — FastAPI 应用工厂，仅注册 CORS middleware，无全局异常中间件。
- `services/agent-core/src/po_agent_core/errors.py` — 定义 `AgentCoreError` 与 `AgentCoreConfigError` 两个层级。
- `apps/admin-web/src/requestErrorConfig.ts` — 前端请求错误统一处理入口。
- `apps/admin-web/src/components/ErrorBoundary/index.tsx` — React 渲染期错误边界。

## 3. 架构与约定

### 3.1 Java 后端

- 所有业务校验失败均以 `throw new RuntimeException("中文消息")` 表达，例如：
  - `"用户不存在"`、`"用户名已存在"`、`"管理员不能修改超级管理员"`、`"非法角色值"`、`"审批操作无效，仅支持 approved 或 rejected"` 等。
- 未见任何自定义异常类型、ErrorCode 常量、`@ControllerAdvice` 全局处理器——当前实现依赖 Spring 默认的异常到 500 的映射。
- 这意味着前端无法从 HTTP 状态码区分“参数错误”和“服务器内部错误”，只能解析 body 中的 message 字段。

### 3.2 Python 聊天服务

- `app/main.py` 只注册了 `CORSMiddleware`，没有 FastAPI 的 `exception_handler` 装饰器或全局中间件来统一包装异常。
- `po_agent_core/errors.py` 定义了双层异常：
  - `AgentCoreError`：宿主统一兜底的基础异常。
  - `AgentCoreConfigError`：配置缺失/非法（如缺少 API Key），被上层装配逻辑捕获以驱动降级（回退到显式模型 / 关键词路由），注释明确说明这是「预期内的控制流」而非让服务启动失败。
- `agent-cooking` 中 `except AgentCoreError as exc:` 捕获该异常，体现宿主对核心异常的兜底策略。

### 3.3 前端 admin-web

- `requestErrorConfig.ts` 定义了 `ErrorShowType` 枚举（`SILENT | WARN_MESSAGE | ERROR_MESSAGE | NOTIFICATION | REDIRECT`）以及 `ResponseStructure`（`success/data/code/message/showType`），作为前后端约定的响应契约。
- `errorThrower` 在 `success === false` 时构造 `new Error(message)` 并设置 `name = 'BizError'`、`info = { code, message, showType, data }`，下游 `errorHandler` 根据 `showType` 分支调用 `message.warning/error` 或 `notification.open`，或在 `REDIRECT` 时跳转 `/user/login`。
- 对网络层错误：401 → 清 token + 重定向登录；403 → 提示无权限；离线 → 国际化文案；其他 → 显示 status 或重试提示。
- `ErrorBoundary` 组件：
  - 通过 `getDerivedStateFromError` 捕获渲染期异常。
  - 识别 `ChunkLoadError` / `Failed to fetch dynamically imported module` 等 chunk 加载失败，区分在线/离线场景给出不同文案。
  - 监听 `online/offline` 事件，在线后自动 reload 以重新拉取失败的 chunk。
  - 提供 Retry（重建 lazy key）、Reload Page、Back Home 三个操作按钮。
  - `componentDidCatch` 中 `console.error('[ErrorBoundary]', error, info.componentStack)` 输出堆栈。

### 3.4 移动端 (cooking-app / cooking-mini)

- 通过 `throw new Error('useAuth 必须在 AuthProvider 内使用')` 等断言式错误，确保 Hook 在正确 Provider 上下文中调用。
- 未看到类似 admin-web 的全局请求错误处理封装。

## 4. 观察到的约定与约束

- **Java 层**：业务异常一律以 `RuntimeException` + 中文消息字符串抛出，未见强制规范文档，但现有代码完全遵循这一模式（UserController、FileController 均如此）。由于没有全局异常处理器，这些异常最终表现为 HTTP 500，前端需自行解析 body。
- **Python agent-core**：异常层级刻意限制为两层（见 `errors.py` 注释），宿主必须能 `except AgentCoreError` 统一兜底，同时可单独捕获 `AgentCoreConfigError` 做降级决策。
- **前端请求契约**：`requestErrorConfig.ts` 中 `ResponseStructure` 是前后端约定格式（`success/data/code/message/showType`），`errorThrower` 强制把非 success 响应包装成 `name='BizError'` 的错误对象，下游 handler 据此分支展示。
- **前端渲染异常**：所有页面通过 `<ErrorBoundary>` 包裹（`app.tsx` 中替换 ProLayout 默认 ErrorBoundary），chunk 加载失败具备自动重试/重载能力，且区分在线/离线状态。
- **Chat 服务**：`main.py` 注释明确说明 `build_orchestrator` 内部已含完整降级链，因此 lifespan 层不需要 try/except，保证服务即使 LLM Key 缺失也能正常监听端口。