# `apps/admin-web/cloudflare-worker` — 上游模板自带的 demo

Ant Design Pro 模板里的示例 Mock API（包名 `pro-api`，`wrangler dev` / `wrangler deploy`），
给模板的 dashboard / list / profile 页面供数。**本项目不使用它**：业务后端是 `services/api`
（Spring Boot，`/api`）与 `services/chat`（FastAPI），管理端经 `apps/admin-web/.env` 的
`UMI_APP_API_BASE_URL` 直连它们。

它仍被 `pnpm-workspace.yaml` 的 `apps/*/cloudflare-worker` 声明收进 workspace，所以 `pnpm install` 会装它、
CI 会解析它的 `tsconfig`。不要往这里加业务接口，也不要按它反推前端契约。

要彻底去掉需要同时改 `pnpm-workspace.yaml` 与锁文件；管理端并没有 import 它，唯一残留是
`config/proxy.ts` 的 `test` 档仍把 `/api/` 指向上游在线 demo（`pro-api.ant-design-demo.workers.dev`）——
本项目只跑 `dev` 档（目标取 `UMI_APP_API_BASE_URL`），`test` / `pre` 两档未被使用。
删除属于一次独立决策，此文档只做登记，未执行删除。
