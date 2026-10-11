# `@po/types` — 跨端契约包

前后端共用的 TypeScript 类型，**只有类型、没有运行时代码**（`src/index.ts` 全是 `export type`）。
五个前端应用都从这里取请求/响应形状，改一处就能让所有端同时报错，从而暴露契约漂移。

本包是私有的（`package.json` 里 `private: true`），不发 npm。

## 命令

```bash
pnpm types:build      # 仓库根执行；tsc -p tsconfig.json → dist/
pnpm --filter @po/types typecheck
```

`exports` 只指向 `dist/`（`./dist/index.d.ts` 与 `./dist/index.js`），`dist/` 被 `.gitignore` 排除，
所以**凡是依赖本包的构建都必须先跑 `types:build`**——根脚本 `admin:dev` / `admin:build` / `novel:dev` /
`novel:build` / `echo:dev` / `echo:build` 都把它写成前置步骤；`mini:dev` / `mini:build` 没有，
CI 的 mini job 里单独补了一次。新克隆后直接跑前端命令会报找不到模块。

## 文件与内容

| 文件 | 行数 | 承载的契约 |
| --- | --- | --- |
| `src/api.ts` | 14 | `Result<T>` 响应信封、`PageResponse<T>` 分页壳 |
| `src/identity.ts` | 49 | `LoginClient`（`'admin' \| 'app'`）、登录/注册/资料/改密请求、`UserItem` |
| `src/recipe.ts` | 154 | 菜谱与分类、食材/步骤、收藏/历史/点赞、审核状态与排序 |
| `src/chat.ts` | 55 | 聊天消息、`ChatRequestParams`（其中 `agent` 字段用于绕过意图路由）、`ChatTicket` 握手票、`/ws/chat` 的入站帧与出站帧类型 |
| `src/novel.ts` | 464 | 书架/章节/角色、正典断言（`CanonEntry` 及其 kind/status/authority）、提案、审稿 finding、改稿影响、统一检索结果、风格档案、生成进度 |
| `src/index.ts` | 72 | 纯 re-export，是唯一对外入口 |

新增类型时在领域文件里写，然后在 `src/index.ts` 补一行 `export type`——只在领域文件导出而忘了
index，消费方拿不到；只在 index 导出而领域文件没有，`tsc` 会直接报。

## 谁在用

| 应用 | 用到的领域 |
| --- | --- |
| `apps/admin-web` | novel（工作台与台账）、recipe、identity、api、chat（聊天页的 WS 帧） |
| `apps/novel-web` | novel（阅读三页）、identity、api |
| `apps/cooking-app` | recipe、identity、api、chat |
| `apps/cooking-mini` | recipe、identity、api |
| `apps/echo-talk` | api、identity（会话/转写形状仍写在 `src/lib/api/talk.ts` 本地，尚未收进来） |

## 约定

- **变更顺序**：改字段先改本包与 `services/api` 的 DTO（或 Python 服务的 schema），再改前端调用。
  反过来的话，前端会先按猜测的形状上线，等真接口返回才炸。
- 字段名对齐 Java 侧序列化后的**小驼峰**结果，不要写 snake_case；分页字段以 `PageResponse` 为准。
- 只放类型，不放常量、枚举运行时值、校验函数或 axios 实例——那些属于各应用或后端。
- 没有代码生成：后端 `Result<T>`、实体与这里的类型是**人工对齐**的两份，所以本包的价值在于
  让漂移在编译期显现，而不是消除漂移。改后端字段时记得同时改这里，CI 的 `frontend` job 会替你确认。
- `echo-talk` 的会话/转写类型仍在应用内，属于已知欠账，不是「不该收进来」。
