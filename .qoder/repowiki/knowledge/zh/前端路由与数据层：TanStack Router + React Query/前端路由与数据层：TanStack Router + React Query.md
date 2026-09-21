---
kind: external_dependency
name: 前端路由与数据层：TanStack Router + React Query
slug: tanstack-router-react-query
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

### TanStack Router + React Query
- 文件路由系统（`src/routes/`），受保护路由组 `_authenticated` 通过 `beforeLoad` 钩子检查 JWT token（无 token 或过期则重定向至 `/sign-in`，携带 `redirect` 参数）
- API 请求统一通过 Axios 实例（`src/lib/axios.ts`），baseURL `/api`，请求拦截器自动附加 JWT，响应拦截器处理 401（toast → 清除 token → 跳转登录页）
- Vite dev server 通过 `server.proxy` 将 `/api` 代理到 `http://localhost:8080`（后端 Spring Boot）