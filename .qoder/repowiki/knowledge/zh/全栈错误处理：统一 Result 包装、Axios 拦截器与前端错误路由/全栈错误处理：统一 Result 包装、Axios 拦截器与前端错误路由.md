---
kind: error_handling
name: 全栈错误处理：统一 Result 包装、Axios 拦截器与前端错误路由
category: error_handling
scope:
    - '**'
source_files:
    - java_server/po/src/main/java/com/goodzheng/po/dto/Result.java
    - java_server/po/src/main/java/com/goodzheng/po/controller/AuthController.java
    - java_server/po/src/main/java/com/goodzheng/po/service/impl/AuthServiceImpl.java
    - py_server/app/routers/items.py
    - py_server/app/routers/ws.py
    - web_client/shadcn-admin/src/lib/axios.ts
    - web_client/shadcn-admin/src/lib/handle-server-error.ts
    - web_client/shadcn-admin/src/routes/(errors)/401.tsx
    - web_client/shadcn-admin/src/routes/(errors)/403.tsx
    - web_client/shadcn-admin/src/routes/(errors)/404.tsx
    - web_client/shadcn-admin/src/routes/(errors)/500.tsx
    - web_client/shadcn-admin/src/routes/(errors)/503.tsx
    - web_client/shadcn-admin/src/features/errors/unauthorized-error.tsx
    - web_client/shadcn-admin/src/features/errors/general-error.tsx
    - web_client/shadcn-admin/src/features/errors/not-found-error.tsx
    - web_client/shadcn-admin/src/features/errors/forbidden.tsx
    - web_client/shadcn-admin/src/features/errors/maintenance-error.tsx
---

## 1. 整体方案

本仓库是一个三端应用（Java Spring Boot 后端 + Python FastAPI 服务 + 双前端），错误处理在各层采用不同但互补的策略：
- Java 后端通过统一的 `Result<T>` 响应体封装业务错误码与消息，Controller 层用 try/catch 捕获异常并转为 `Result.error(...)`。
- Python FastAPI 路由用 Pydantic 自动校验请求（422）、`HTTPException` 表达业务错误（404 等）；WebSocket 帧协议用 `error` 帧回报非法输入。
- 前端 shadcn-admin 通过 Axios 拦截器统一处理网络错误、401 登出跳转，并提供按 HTTP 状态码划分的错误页面路由；Ant Design Pro 管理后台也有独立的请求错误配置。

## 2. 关键文件与位置

- **Java 后端**
  - `java_server/po/src/main/java/com/goodzheng/po/dto/Result.java`：统一响应体，包含 `code`、`message`、`data` 三个字段，提供 `success(data)`、`error(code, message)`、`error(message)` 等静态工厂方法。成功固定 code=200，无参 error 默认 code=500。
  - `java_server/po/src/main/java/com/goodzheng/po/controller/AuthController.java`：在 Controller 方法内 try/catch `RuntimeException`，将业务异常映射为 `Result.error(401, ...)` 或 `Result.error(400, ...)`。
  - `java_server/po/src/main/java/com/goodzheng/po/service/impl/AuthServiceImpl.java`：Service 层抛出 `RuntimeException("用户名已存在")`、`RuntimeException("用户名或密码错误")` 等业务异常，由 Controller 捕获。
  - 未发现全局异常处理器（如 `@RestControllerAdvice` / `@ExceptionHandler`），异常收敛集中在各 Controller 的局部 try/catch。

- **Python 后端**
  - `py_server/app/routers/items.py`：CRUD 路由中资源不存在抛 `HTTPException(404, "item not found")`；请求体由 Pydantic 模型校验，失败自动返回 422。
  - `py_server/app/routers/ws.py`：入站 JSON 帧校验失败（ValidationError）回发 `{"type": "error"}` 帧且连接保持；WebSocketDisconnect 静默结束。

- **前端（shadcn-admin）**
  - `web_client/shadcn-admin/src/lib/axios.ts`：创建 axios 实例，baseURL=`/api`，timeout=15s。
    - **请求拦截器**：从 `useAuthStore` 读取 JWT 并注入 `Authorization: Bearer <token>`。
    - **响应拦截器**：若后端返回 `response.data.code !== 200`，则 `Promise.reject(new Error(result.message || 'Request failed'))`；若 `status === 401`，弹出 toast 提示“登录已过期，请重新登录”，清空 store 并跳转到 `/sign-in?redirect=<原路径>`。
    - 暴露 `isTokenExpired(token)` 辅助函数，提前 30s 判定 token 过期以避免竞态。
  - `web_client/shadcn-admin/src/lib/handle-server-error.ts`：通用错误展示工具，优先取 AxiosError 响应中的 `response.data.title` 作为标题，否则显示默认 “Something went wrong!”；对 204 No Content 特殊处理为 “No content.”；开发环境额外 `console.log` 原始错误。
  - `web_client/shadcn-admin/src/routes/(errors)/`：按 HTTP 状态码划分的错误页面路由：`401.tsx` → `UnauthorisedError`、`403.tsx` → `ForbiddenError`、`404.tsx` → `NotFoundError`、`500.tsx` → `GeneralError`、`503.tsx` → `MaintenanceError`。
  - `web_client/shadcn-admin/src/features/errors/`：对应的 UI 组件，均呈现大字号状态码、英文描述文案和“Go Back”、“Back to Home”按钮。

- **前端（Ant Design Pro 管理后台）**
  - `web_client/po-admin/src/requestErrorConfig.ts`：Ant Design Pro 的 request 插件错误配置（用于管理后台的请求错误处理）。

## 3. 架构与约定

- **后端统一响应格式**：Java 所有 REST 接口返回 `Result<T>`，前端据此判断 `code === 200` 为成功，其余视为业务错误。该约定贯穿 `AuthController`、`RecipeController`、`UserController` 等控制器。
- **业务异常上抛**：Service 层通过抛出 `RuntimeException` 表达业务错误（如用户名重复、密码错误），Controller 层负责将其转换为带语义化 code 的 `Result.error(...)`，避免向客户端泄露堆栈。
- **前端集中式网络错误处理**：所有 API 调用走同一 axios 实例，401 自动登出重定向，非 200 业务码被拒绝并交由上层 `handleServerError` 或组件级 toast 展示。
- **HTTP 状态码到页面的映射**：前端以 TanStack Router 的文件路由组织错误页，`/(errors)/<code>.tsx` 对应相应状态码页面，便于扩展新的错误码视图。
- **Python 侧轻量错误处理**：未注册全局 exception handler，路由内用 `HTTPException` 表达业务错误、Pydantic 自动 422，WebSocket 用 error 帧，保持最小依赖。

## 4. 约定与约束

- Java 后端：
  - 所有响应必须通过 `Result.success(...)` 或 `Result.error(...)` 构造，禁止直接返回裸对象或字符串。
  - Service 层抛出 `RuntimeException` 表达业务错误；Controller 层必须捕获并映射为合适的 HTTP 语义 code（400/401/500）。
  - 未发现全局异常处理器，因此新增 Controller 时需遵循相同的 try/catch 模式。
- Python 后端：
  - 请求体校验失败由 Pydantic 自动返回 422 + 字段级错误详情；资源不存在抛 `HTTPException` 返回 404 + `{"detail": "..."}`；WebSocket 非法帧回 error 帧且不断开连接。
- 前端：
  - 新页面如需展示服务器错误，应复用 `handleServerError` 或直接调用 `toast.error(...)`；401 场景无需手动处理，axios 拦截器已统一处理。
  - 新增 HTTP 状态码页面需在 `src/routes/(errors)/` 下添加 `<code>.tsx` 路由，并在 `src/features/errors/` 中添加对应组件。
  - 401 重定向目标为 `/sign-in`，携带 `redirect` 查询参数以便登录后回跳。

## 5. 已知缺口

- Java 后端缺少全局异常处理器（`@RestControllerAdvice`），异常收敛分散在各 Controller，新增接口容易遗漏统一处理。
- Python 后端未注册全局 exception handler；REST（HTTPException/422）与 WebSocket（error 帧）两套错误通道风格不同，需分别对待。
- 前端错误页均为英文文案，尚未接入 i18n。
- Ant Design Pro 管理后台的错误处理位于独立工程目录，与本仓库主前端代码分离维护。