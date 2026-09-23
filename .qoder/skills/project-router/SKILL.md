---
name: goodzheng-project-router
description: 为 po monorepo 的跨端或需求不明确任务选择管理端、Expo 移动端、Spring Boot 或 Python 工作流。用于全栈功能、跨服务联调与模块归属判定；不用于已明确的单一领域代码任务。
---

# Po 项目调度器

## 领域分流

1. 涉及 `apps/admin-web/`、React、Umi、Ant Design、页面、路由、表格或状态管理时，读取 `../frontend-dev/SKILL.md`。
2. 涉及 `apps/cooking-app/`、Expo、React Native、expo-router、NativeWind、移动端页面或 APK 构建时，读取 `../mobile-dev/SKILL.md`。
3. 涉及 `services/api/`、Java、Spring Boot、Controller、Service、数据库、JWT 或 Redis 时，读取 `../java-dev/SKILL.md`。
4. 涉及 `services/chat/`、Python、FastAPI、WebSocket、流式聊天或 AI 对话（Flask/LangGraph 仅作迁移历史信号）时，读取 `../python-dev/SKILL.md`。
5. 跨端契约类型（请求/响应 DTO）统一维护在 `packages/types/`（`@po/types`）；字段变更先更新类型包与 API 契约，再更新管理端或移动端调用。
6. 跨端任务按「Java API 契约 → Python 服务契约（如涉及）→ 管理端或移动端调用」顺序读取对应领域 skill；只加载当前步骤需要的上游参考。

## 渐进式披露规则

- 此 skill 只负责领域判定，不加载任何开源框架 skill。
- 领域 skill 只加载一个最匹配的上游 skill；单一问题不要全量读取来源目录。
- 上游 skill 位于 `.qoder/skill-sources/`，为只读镜像（由 `.qoder/scripts/sync-skill-sources.ps1` 按 pinned commit 同步，勿手改）；项目适配规则始终以 `.qoder/skills/` 为准。
- 若用户已给出模块或文件路径，跳过本调度器，直接命中对应领域 skill。

## 本地拓扑速查

- 管理端：`pnpm admin:dev` 启动 Umi 8000（`/api`、`/ws` 代理到本地后端）；后端地址在 `apps/admin-web/.env` 配置。
- 移动端：`pnpm mobile:start` 启动 Expo；API 地址在 `apps/cooking-app/.env` 的 `EXPO_PUBLIC_API_URL` 配置。Android 模拟器使用 `10.0.2.2`，真机使用开发机局域网地址。
- API 与聊天：`pnpm api:start` 在 `services/api` reactor 内以 `-pl api-bootstrap -am spring-boot:run` 构建依赖模块并启动 Spring Boot 8080（脚本自动定位 JDK 17，无需终端配置 `JAVA_HOME`；模块改动后也无需先 `pnpm api:install`）；`pnpm chat:start` 启动 FastAPI 5090。
- 部署模式：`docker compose up -d` 由 Nginx 网关统一分流（`${WEB_PORT:-8000}` 对外，`/api` 大部分给 Spring Boot，`/api/health`、`/api/items`、`/ws/chat` 给 FastAPI），仅 `web` 暴露宿主机端口。
