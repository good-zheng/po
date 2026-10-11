# 言外 EchoTalk 小程序（`apps/echo-talk`）

Taro 4.2.1 + React 18 的微信小程序，`@po/echo-talk`。按住说话 → 实时转写 → 输出意图 / 潜台词 / 情绪 /
风险与三条可照读的回复。需求、决策与里程碑在 `PRD.md`（v0.1，含 ADR 摘要与验收标准），
`prototype/index.html` 是早期的静态原型，只作视觉参考，不是实现依据。

## 命令

从仓库根执行（本包只有 Taro 原生命令，无 lint/test 脚本）：

```bash
pnpm echo:dev        # types:build + taro build --type weapp --watch
pnpm echo:build      # types:build + 生产构建（一次性，用于确认编译过）
pnpm --filter @po/echo-talk dev:h5   # 浏览器版式调试（未收进根脚本）
```

`echo:*` 已带 `pnpm types:build` 前置——本包依赖 `@po/types`，而它只导出 `dist/`。
**本应用没有 CI job**（`.github/workflows/ci.yml` 的 mini job 只编 cooking-mini），改完必须自己跑一次
`pnpm echo:build`。产物在 `dist/`，微信开发者工具导入 `apps/echo-talk` 目录本身即可。

## 环境（三个地址，缺一不可）

`src/config/env.ts` 读三个 `TARO_APP_*` 变量，缺省全部回退本机地址：

| 变量 | 用途 | 缺省 |
| --- | --- | --- |
| `TARO_APP_API_BASE_URL` | Spring Boot 业务接口（会话、话语、票据） | `http://127.0.0.1:8080/api` |
| `TARO_APP_CHAT_WS_URL` | FastAPI 洞察与建议的流式通道 | `ws://127.0.0.1:5090/ws/chat` |
| `TARO_APP_ASR_WS_URL` | Spring Boot 的 ASR 网关 | `ws://127.0.0.1:8080/api/ws/asr` |

`.env.development` 里三个值都填**开发机局域网 IP**而不是 `127.0.0.1`：真机预览时 `127.0.0.1` 指向手机自己，
WebSocket 握手失败并报 `Invalid HTTP status`。换网络后 IP 变了要同步改这三行。
对应的后端也要允许局域网访问：`pnpm chat:start` 已带 `--host 0.0.0.0`，手动起 uvicorn 不带这个参数就只绑
127.0.0.1，表现是「按住说话正常、点发送后 30 秒分析超时」。

线上两条 WS 规则写在 `env.ts` 的注释里，改动前先读它：① 云托管域名只服务 TLS，必须用 `wss`，明文 `ws` 拿不到
101；② 线上直连 api 实例、不经过 `infra/nginx`，所以路径必须自带 context-path，写 `/ws/asr` 会 404。
两个域名都要进小程序后台的「socket 合法域名」，HTTP 域名进「request 合法域名」。

## 目录

```
src/app.config.ts            5 个页面 + 2 个 tab（会话 / 我的）；permission 里声明 scope.record 用途
src/pages/session/index.tsx  主流程页：录音、转写、核对、发送、洞察卡
src/pages/mine,history,profile/edit,login
src/lib/asr/recorder.ts      RecorderManager 切帧
src/lib/asr/asr-client.ts    ASR WebSocket 客户端与帧协议
src/lib/ai/talk-chat.ts      与 /ws/chat 的 talk 插槽通信
src/lib/api/                 client.ts / talk.ts / auth.ts / users.ts
src/lib/auth/                session / context / guard / return-path（与 cooking-mini 同一套 gating 约定）
src/config/env.ts            三个地址 + 场景选项（与后端 TalkConstants 对齐）
src/styles/、src/assets/icons/
```

## 实时链路（代码现状）

1. 按住才收音：`recorder.ts` 用 `Taro.getRecorderManager()`，`format: 'PCM'`（**必须大写**，写 `pcm` 会回落
   mp3）、16000Hz、单声道、`frameSize: 2`，每帧切成 1280 字节（16bit × 16k × 40ms）。
   微信单次录音有 10 分钟上限，到点自动重开，逻辑在 `recorder.ts`。
2. `asr-client.ts` 走 `Taro.connectSocket`，票据拼在 query（`?ticket=`）——**小程序 WS 不支持自定义请求头**，
   票据不能用 header 传。上行 `start` / `frame` / `stop`，下行 `ready` / `partial` / `final` / `segment_end` / `error`。
   真机握手可能「既不 open 也不 error」，所以有连接超时兜底，别删。
3. 松手即发但不关连接：`session/index.tsx` 的 `stopRecording` 只发 `stop`，把已有的中间结果先呈给用户
   （`sendHeldVoice`），迟到帧靠 `segment_end` 或 `LATE_FINAL_GRACE_MS`（3000ms）收尾后再定稿。
4. 定稿才上云：语音松手先 `commitUtterance(analyze: false)` 落库为半成品，讯飞定稿回来后 `PATCH
   /talk/utterances/{id}` 覆盖文本，再触发 `runAnalysis`。这样模型看到的永远是完整句。
5. 洞察走 `services/chat` 的 `/ws/chat`，入站帧多带两个向后兼容字段：`agent: "talk"`（显式指定插槽，跳过意图
   路由）与 `context`（场景 / 说话人 / `utteranceId`；后者只用于服务端回写定位，不会拼进提示词）。
6. 会话与话语的增删改查全在 Spring：`/talk/sessions`、`/talk/sessions/{id}`（PATCH）、
   `/talk/sessions/{id}/utterances`（POST）、`/talk/utterances/{id}`（PATCH）、`/talk/asr/ticket`（GET）。
   建议由 `po-agent-talk` 经 `POST /talk/internal/suggestions` 回写，前端不直连该内部端点。

## 隐私边界（产品要求，不是实现细节）

- 麦克风只在用户按住「开始录音」后开启；`app.config.ts` 里 `scope.record` 的 `desc` 必须填真实用途，
  且要在公众平台的「隐私保护指引」同步声明，否则不弹授权框。
- 转写结果先给用户核对，**点「发送」才开始分析**——界面文案就写着这件事。
- 会话与历史只在登录后可见；游客进 `pages/login`，tab 页未登录渲染缺省页 + 「去登录」，不自动跳转
  （与 `apps/cooking-mini` 同一套约定，不得回退成强制跳转）。

## 微信平台限制（代码里已按这些写法）

- `flex-wrap: wrap`、`gap`、`calc()` 在 WXSS 里不可靠，界面全部用行容器 + 固定百分比（
  `pages/session/index.scss`、`pages/history/index.scss`、`pages/login/index.scss` 各有注释）。
- 表情符号与字体图标不渲染，图标用 png 资源（`src/assets/icons/`）。
- `textarea` 关掉 `auto-height` 后需要自己处理滚动。
- `@/` 别名同时配在 `config/index.ts` 与 `tsconfig.json`；`webpack` 锁 `~5.95`（与
  `@tarojs/webpack5-runner` 4.2.1 不兼容更高版本）；`lazyCodeLoading: 'requiredComponents'` 必须保留
  （上传检查项）。
- `project.config.json` 的 `appid` 是真实 AppID，`miniprogramRoot` 指 `dist/`。

## 与 cooking-mini 的关系

同一底座（Spring Boot + FastAPI + `packages/types`）的第二件作品，但**不共享代码**：两个包各自有
`lib/api/client.ts`、`lib/auth/*`、`config/env.ts`。改动通用逻辑时要判断是否两边一起改，不要抽公共包——
`packages/` 目前只放类型契约。
