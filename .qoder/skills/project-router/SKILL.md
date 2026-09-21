---
name: goodzheng-project-router
description: 为 goodzheng-pro 的跨端、需求不明确或 OpenSpec 变更请求选择前端、Spring Boot 或 Python 工作流。用于全栈功能、跨服务联调、模块归属不明、规格提案与变更实施；不用于已明确的单一领域代码任务。
---

# Goodzheng 项目调度器

## 先经过 OpenSpec 边界

仅在新能力、破坏性改动、跨模块契约变更或用户明确要求规格时，先使用现有 OpenSpec skill：

| 场景 | 使用的现有 skill |
| --- | --- |
| 澄清现有行为或调研方案 | `openspec-explore` |
| 新功能或变更提案 | `openspec-propose` |
| 已批准方案的实施 | `openspec-apply-change` |
| 修改已存在的变更 | `openspec-update-change` |
| 归档已完成变更 | `openspec-archive-change` |

普通修复、小范围重构和已明确的单模块任务不创建 OpenSpec 负担。

## 领域分流

1. 涉及 `web_client/`、React、UI、页面、路由、表格或状态管理时，读取 `../frontend-dev/SKILL.md`。
2. 涉及 `java_server/po/`、Java、Spring Boot、Controller、Service、数据库、JWT 或 Redis 时，读取 `../java-dev/SKILL.md`。
3. 涉及 `py_server/`、Python、FastAPI、WebSocket、流式聊天或 AI 对话（Flask/LangGraph 仅作迁移历史信号）时，读取 `../python-dev/SKILL.md`。
4. 跨端任务按「Java API 契约 → Python 服务契约（如涉及）→ 前端调用」顺序读取对应领域 skill；只加载当前步骤需要的上游参考。

## 渐进式披露规则

- 此 skill 只负责领域判定，不加载任何开源框架 skill。
- 领域 skill 只加载一个最匹配的上游 skill；单一问题不要全量读取来源目录。
- 上游 skill 位于 `.qoder/skill-sources/`，为只读镜像；项目适配规则始终以 `.qoder/skills/` 为准。
- 若用户已给出模块或文件路径，跳过本调度器，直接命中对应领域 skill。
