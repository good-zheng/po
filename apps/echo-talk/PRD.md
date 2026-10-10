# 言外 EchoTalk · 产品需求文档（PRD）

| 项 | 内容 |
| --- | --- |
| 产品名 | 言外（EchoTalk）—— 待定，见 §9 待确认 |
| 一句话定位 | 手机放着听对方说话，实时转写成字，AI 告诉你「他到底什么意思」，并给出可以直接照着说的回复 |
| 载体 | 微信小程序（独立 AppID）· 工程位置 `apps/echo-talk` |
| 后端 | 复用 `services/api`（Spring Boot 4）+ `services/chat`（FastAPI）+ `services/agent-core` |
| 语音 | 科大讯飞「语音听写（流式版）」WebAPI（`wss://iat-api.xfyun.cn/v2/iat`） |
| 文档版本 | v0.1（初稿，待评审） |
| 日期 | 2026-10-01 |

---

## 1. 背景与目标

### 1.1 问题

人在对话里真正卡住的，不是「听不清」，而是三件事：

1. **没听懂弦外之音**——对方说「你看着办吧」，到底是授权还是不满？
2. **当场想不出怎么接**——情绪上头时，脱口而出的往往是事后最后悔的那句。
3. **事后记不清**——聊完就忘，没留下可供复盘的素材。

现有方案要么只解决转写（录音笔、讯飞听见），要么只解决回复（把聊天记录贴给大模型），**没有一个是从「声音进来」到「话术出去」的完整闭环**。

### 1.2 产品目标

| 目标 | 衡量指标 |
| --- | --- |
| 转写够快够准 | 首字上屏 P95 < 1.2s；安静环境字准 > 95% |
| 洞察真的有用 | 段级建议从「成句」到「首条建议上屏」P95 < 3.5s |
| 回复能直接用 | 建议采纳率（点击「复制/朗读」）> 40% |
| 记录真的留得住 | 会话 7 日回访率 > 25% |

### 1.3 目标用户

- **主打**：需要频繁处理高难度对话的普通人——职场汇报/谈判、客户沟通、相亲与亲密关系、与长辈/房东/医生等「不对等关系」沟通。
- **次选**：需要复盘沟通质量的自我提升者（销售、HR、管理者）。

### 1.4 非目标（本期明确不做）

- 不做通话录音（微信/手机通话受系统限制，无法采集）
- 不做说话人声纹自动分离（讯飞标准听写不支持，成本过高）
- 不做多人群聊转写与会议纪要（场景不同，另立产品）
- 不做实时翻译
- 不保留原始音频（隐私红线，见 §7）

---

## 2. 用户故事与核心流程

### 2.1 主线故事（P0）

> 我打开小程序，**点「开始录音」才收音**。对面的人说了一句让我拿不准的话，屏幕上立刻浮出他的原话，
> 紧接着 AI 给出一行「他真正想说的是：……」和三张可以直接照读的回复卡片。
> 我点「朗读」，把手机递过去/照着说。聊完点「结束并保存」，这场对话落库归档，界面清空直接开下一场。

### 2.2 主流程（Happy Path）

```
进入会话页（不自动录音，麦克风只在点击后开启）
  → 点「开始录音」→ 申请麦克风授权 → 建 ASR 会话
  → [循环] 麦克风帧 → ASR 网关 → 转写实时填进底部输入框
      （未定稿的那一句会被下一次 partial 整句替换，定稿后并入正文，前面的手改内容不动）
  → 点「暂停」→ 停止上行并等最后一句定稿（等不到也按当前结果收尾），文字留在输入框
  → 点「发送」→ 落库入列 → 触发分析 → Agent 产出「洞察 + 3 条回复建议」
      （发送前可以先改错字，改完再发；这也覆盖了转写纠错）
  → 用户点「朗读」/「复制」/「换一批」
  → 点「结束并保存」→ 输入框里没发送的话一并落库 → 会话结束 → 界面清场，直接开下一场
```

### 2.3 副线故事

| # | 故事 | 优先级 |
| --- | --- | --- |
| S1 | 环境太吵/不方便录音，我手动打字输入对方刚说的话，照样拿到建议 | P0 |
| S2 | 麦克风把我和对方都录进去了，我手动切换「对方 / 我」，让分析对象正确 | P0 |
| S3 | 我发现某句转写错了，直接点文字改成正确的，重新分析 | P1 |
| S4 | 上周那次谈判我想再看看，在历史里搜关键词翻出来 | P1 |
| S5 | 我是销售，希望默认按「客户异议处理」的视角分析 | P2 |

---

## 3. 功能需求

### 3.1 功能清单

| ID | 功能 | 优先级 | 说明 |
| --- | --- | --- | --- |
| F1 | 点击开始录音 | Must | 进入会话页不录音，点「开始录音」才申请麦克风授权并收音；隐私边界优先于便利 |
| F2 | 实时语音转写填进输入框 | Must | 转写结果写进底部输入框（未定稿整句替换、定稿并入正文），不自动发送；长会话自动续录 |
| F2b | 发送前核对/改错字 | Must | 「发送」才是这一轮的提交点：落库 → 触发 agent-talk 分析；录音中也能边看边改 |
| F3 | 说话人手动切换 | Must | 顶部「对方 / 我」切换条，默认「对方」；可事后批量改 |
| F4 | 段级 AI 洞察 | Must | 意图 / 潜台词 / 情绪 / 风险点 |
| F5 | 多风格回复建议 | Must | 每轮 3 条（稳妥 / 共情 / 推进），可「换一批」 |
| F6 | 建议朗读（TTS） | Must | **复用现有讯飞 TTS 与 `/api/tts`**，零新增后端成本 |
| F7 | 文字输入对方的话 | Must | 输入框手动提交，与语音走同一分析链路 |
| F8 | 会话列表与详情 | Must | 时间倒序、标题、摘要、轮次；详情可编辑与删除 |
| F9 | 转写纠错与重分析 | Should | 编辑某句文本后重新触发该轮分析 |
| F10 | 会话搜索 | Should | 按标题/内容关键词检索 |
| F11 | 场景预设 | Could | 通用 / 职场 / 销售 / 亲密关系，切换即换分析视角 |
| F12 | 会话导出与分享 | Could | 生成图片长图或文本，分享前走内容安全检测 |
| F13 | 金句/话术收藏 | Could | 把好用的建议存进个人话术库 |

### 3.2 关键页面

#### P-1 会话页（主战场）

```
┌─────────────────────────────────┐
│ ● 录音中 00:42      [对方|我]    │  ← 状态条 + 说话人切换（默认「对方」）
├─────────────────────────────────┤
│                                 │
│  ░ 那这个事你看着办吧            │  ← 未定稿（灰）
│                                 │
│  ┌ 对方 · 00:38 ─────────────┐  │
│  │ 那这个事你看着办吧。        │  │  ← 定稿（黑），可点编辑
│  └───────────────────────────┘  │
│                                 │
│  ┌ AI 洞察 ─────────────────┐   │
│  │ 🎯 他真正想要的：          │   │
│  │    要你给明确答复，别甩回去 │   │
│  │ 💬 潜台词：               │   │
│  │   「我不想担责，你定」      │   │
│  │ 😟 情绪：回避 · 略带不满    │   │
│  │ ⚠️ 风险：真自己拍板会背锅   │   │
│  └──────────────────────────┘   │
│                                 │
│  ┌ 可以这样回 ──────────────┐   │
│  │ 【稳妥】我先梳理两个方案， │   │
│  │  下午三点前发你定夺，可以吗│ 🔊│
│  │ 【共情】我理解这事不好拍板 │   │
│  │  咱们一起定，我先出个草案  │ 🔊│
│  │ 【推进】那我按 A 方案推进，│   │
│  │  有异议你随时叫停          │ 🔊│
│  │          换一批            │   │
│  └──────────────────────────┘   │
├─────────────────────────────────┤
│ [ 输入对方说的话…        ] 发送  │  ← 手动文字输入
│         ⏸ 暂停    ■ 结束        │
└─────────────────────────────────┘
```

**交互要点**

- 「对方 / 我」切换条：点一下即切换，切换后的新句子归到新角色下；已定稿的句子可长按改角色
- 建议卡片右侧 🔊 直接朗读（复用 `Taro.createInnerAudioContext()` + 现有 `speak()` 封装）
- 「换一批」重新生成，旧的建议保留在详情里（不覆盖，体现迭代）
- 结束弹二次确认：「本次共 12 轮，预计保留 30 天」

#### P-2 历史列表（已下线）

> 2026-10-01 起本模块不做：会话数据照常落库（`talk_session` / `talk_utterance` / `talk_suggestion`），
> 但小程序不再提供翻查入口，「结束并保存」后原地清场开下一场。下面的原设计保留备查。

卡片列表：标题（AI 自动生成，如「与王总聊项目延期」）+ 时间 + 轮次 + 首句摘要。左滑删除，点击进入详情。

#### P-3 会话详情（随 P-2 一并下线）

按时间轴的对话流：对方话（左）/ 我说的话（右）/ AI 洞察卡片（居中浅底）。支持改标题、改某句角色、删除整场。

#### P-4 我的 / 设置（1:1 移植叮叮厨的个人中心）

用户卡（头像 / 昵称 + 角色标签 / `@用户名` / 手机号 / 邮箱）→ 菜单（编辑资料：头像上传、昵称、手机号、邮箱）→ 分析场景分段选择 → 退出登录。
未登录时整页显示游客占位（标题 + 提示 + 「去登录」按钮），**不自动跳登录页**：tab 页自动跳转在返回时会白屏。

登录页同样移植叮叮厨：微信一键登录 / 密码登录 / 注册三 tab，审批中与被拒分别给出色条提示；登录成功后按 `po.auth.returnTo` 回跳（tab 页 `switchTab`，普通页 `redirectTo`），无来路则回会话页。
会话页对游客开放浏览界面，只有点「开始录音」或「发送」时才引导去登录，输入框里已打的字不清空。

---

## 4. 技术方案（贴合现有工程）

### 4.0 总体架构

```
┌──────────────────────────────────────────────────────────────┐
│ 微信小程序 apps/echo-talk (Taro 4.2 + React 18)               │
│  ├ RecorderManager  PCM 16k/16bit/mono 帧                     │
│  ├ 转写区 / 洞察卡 / 建议卡 / 说话人切换                       │
│  └ 复用 cooking-mini 的 api client + session 封装              │
└───────────┬──────────────────────────────┬───────────────────┘
            │ WS /ws/asr (PCM 帧)          │ WS /ws/chat (文本)
            │ REST /talk/**               │
┌───────────▼──────────────────────────────▼───────────────────┐
│ Nginx 网关（infra/nginx）                                     │
└───────────┬──────────────────────────────┬───────────────────┘
            │                              │
┌───────────▼───────────────┐  ┌───────────▼───────────────────┐
│ services/api (Spring Boot)│  │ services/chat (FastAPI)       │
│  新增 talk 模块            │  │  新增 talk 插槽                │
│  ├ /ws/asr  ASR 网关       │  │  ├ agent-talk 垂直 Agent       │
│  ├ /talk/** 会话 CRUD      │  │  └ 结构化输出 + 流式事件       │
│  └ XfyunSigner（复用 TTS） │  │       │                        │
└───────────┬───────────────┘  └───────────┬───────────────────┘
            │ WSS 讯飞 IAT                  │ 内部 HTTP 回调落库
     ┌──────▼──────┐                       │
     │ 讯飞 v2/iat │          ┌────────────▼─────────┐
     └─────────────┘          │ MySQL + Redis Stack  │
                              └──────────────────────┘
```

### 4.1 端上：Taro 小程序 `apps/echo-talk`

**脚手架**：复制 `apps/cooking-mini` 的结构（Taro 4.2.1 + React 18.3 + Sass），共享 `@po/types`。
**直接复用**的现有资产：

| 现有文件 | 用途 |
| --- | --- |
| `src/lib/api/client.ts` | `apiClient.get/post`、`Bearer ` token 注入、401 处理 |
| `src/lib/auth/session.ts` | `po.session` 登录态（微信 `wx.login` → `/auth/openid-login`） |
| `src/lib/tts.ts` | 建议朗读，`speak()` / `prefetch()` 原样可用 |

从 `apps/cooking-mini` **移植**（同名同行为，仅配色换成言外的靛蓝）：
`lib/auth/auth-context.tsx`（`AuthProvider` / `useAuth`，401 只清会话不跳页）、
`lib/auth/auth-guard.tsx`（非 tab 页的登录门）、`lib/auth/return-path.ts`（回跳来路）、
`lib/auth/guest-placeholder.tsx`（tab 页游客占位）、`lib/api/users.ts` + `pages/profile/edit`（头像上传与资料更新）。

**录音关键实现**

```ts
const rm = Taro.getRecorderManager()
rm.start({
  sampleRate: 16000,      // 讯飞要求 16k
  numberOfChannels: 1,    // 单声道
  encodeBitRate: 48000,
  format: 'mp3',          // 落盘格式；不影响帧数据
  frameSize: 1,           // 单位 KB，约每 1KB 触发一次回调
  duration: 600000,       // 微信硬上限 10 分钟
})
rm.onFrameRecorded(({ frameBuffer, isLastFrame }) => {
  // 关键：frameBuffer 恒为未压缩 PCM（与 format 无关），可直接喂讯飞
  enqueue(frameBuffer)     // 入队，按 40ms / 1280B 节流发送
})
```

> **已验证的事实**：微信文档与实测均表明 `onFrameRecorded` 的 `frameBuffer` 恒定是 PCM 分片，
> 与 `format` 参数（aac/mp3）无关。因此无需任何转码即可直连讯飞 —— 这是本方案能成立的关键。

**发送节流**：维护一个 `1280 字节` 缓冲区，凑满即发一次（对应 40ms @16k/16bit），不足则等待；
每帧转 Base64。这是讯飞官方推荐的发包规范。

**续录**：`duration` 上限 10 分钟，在 `onStop` 中若仍在录音态则立即重新 `start()`，实现无缝续接，
并在时间轴上标记分段序号。

**权限与合规**：`app.config.ts` 声明 `permission.scope.record`，首次进入弹微信授权框；
拒绝后降级到「文字输入模式」而不是空白页。

### 4.2 ASR 网关：`services/api` 新增 `talk` 模块

**为什么不在小程序直连讯飞**：APIKey/APISecret 绝不可下发到端上，必须服务端代理。

**复用现有鉴权**：`recipe` 模块的 `XfyunTtsService` 已实现讯飞 hmac-sha256 签名
（`host/date/request-line` → HmacSHA256 → Base64 → authorization），**签名算法与 IAT 完全一致**。
改造方式：把签名逻辑抽成 `shared` 模块的 `XfyunSigner`（`services/api/shared/src/main/java/.../xfyun/XfyunSigner.java`），
TTS 与新 ASR 共同引用。这是本次唯一的重构点，风险低。

**上行协议（小程序 → 网关）**

```jsonc
{"type":"start","sessionId":123}                        // 建连后第一帧
{"type":"frame","audio":"<base64 PCM>","seq":17}        // 音频帧
{"type":"stop","seq":180}                               // 结束
```

**下行协议（网关 → 小程序）**

```jsonc
{"type":"ready","segment":1}
{"type":"partial","text":"那这个事你","seq":12}          // 未定稿（开 dwa=wpgs 会被替换修正）
{"type":"final","text":"那这个事你看着办吧。","segment":1,"confidence":0.92}
{"type":"segment_end","reason":"eos|max60s|stop","segment":1}
{"type":"error","code":"XF_10165","message":"无效音频"}
```

**讯飞侧实现要点**

| 项 | 取值 |
| --- | --- |
| 地址 | `wss://iat-api.xfyun.cn/v2/iat` |
| 首帧 | `{common:{app_id}, business:{domain:"iat",language:"zh_cn",accent:"mandarin",dwa:"wpgs",vad_eos:5000,ptt:0}, data:{status:0,format:"audio/L16;rate=16000",encoding:"raw",audio:...}}` |
| 中间/结束帧 | `data.status = 1 / 2` |
| 发包节奏 | 每 40ms 发 1280 字节 |
| **60 秒硬限制** | 单次会话最长 60s → 到 55s 主动 `status=2` 收尾，立即重开新连接，文本按 segment 顺序拼接 |
| 动态修正 | 开 `dwa:"wpgs"`，按 `pgs` 字段（`apd` 追加 / `rpl` 替换）更新上屏文本 |

**连接数控制**：每个用户同时只允许 1 条 ASR 连接，新连接踢掉旧的（防漏资源）。
**鉴权**：微信小程序 WS 不能带自定义 header，故 `GET /talk/asr/ticket` 换取一次性短期 ticket（60s 有效、用后即焚），
WS 用 `?ticket=` 连接，避免 JWT 落进访问日志。

**降级**：讯飞不可用时网关返回 `error`，端上自动切「纯文字输入模式」并提示，不阻塞主流程。

### 4.3 Agent 侧：新增 `services/agent-talk` 垂直 Agent

**接入方式（完全遵循现有插槽契约）**

```python
VerticalAgent(
    name="talk",
    description="分析对方话语的真实意图、潜台词与情绪，给出可直接照说的回复建议",
    graph=build_talk_graph().compile(),
    utterances=("他这话什么意思", "我该怎么回", "帮我分析一下这句话", "怎么回答比较好"),
)
```

在 `services/chat/app/agent.py` 的 `_builtin_agents` 里延迟 import 登记，与 `cooking` 并列。
复用现有能力：supervisor 路由、**Redis checkpointer 的会话记忆**、事件流翻译、`timeout_seconds` 保护。

**触发时机（段级，非逐 token）**

| 触发条件 | 阈值 |
| --- | --- |
| 静音断句 | 静音持续 1.2s 且当前段 ≥ 8 字 |
| 长度兜底 | 单段累计 ≥ 30s 或 ≥ 80 字，强制定稿 |
| 手动 | 用户点「发送」或改完转写文本 |

**结构化输出**（Agent 输出严格 JSON，`done` 帧带完整对象）

```jsonc
{
  "intent":    "要你给明确答复，而不是把决定权推回去",
  "subtext":   "我不想担责，你定",
  "emotion":   { "label": "defensive", "score": 0.62, "desc": "回避 · 略带不满" },
  "risk":      "真自己拍板，出问题会背锅",
  "suggestions": [
    { "style": "稳妥", "text": "我先梳理两个方案，下午三点前发你定夺，可以吗？", "why": "给方案不给结论，保留对方决策权" },
    { "style": "共情", "text": "我知道这事不好拍板，咱们一起定，我先出个草案。", "why": "先接住情绪，再降低对方压力" },
    { "style": "推进", "text": "那我按 A 方案推进，有异议你随时叫停。", "why": "给默认路径，减少来回" }
  ],
  "followups": ["你觉得哪个方案风险更小？"]
}
```

**上下文策略**：只回传最近 6 轮（对方话 + 我的回复）+ 场景预设 + 说话人角色，避免上下文膨胀。
**降级**：沿用工程既有的静默降级文化——LLM 不可用时退化为关键词情绪规则 + 通用话术模板，界面照常出卡片。

### 4.4 `/ws/chat` 的最小改造

现有 `WSInFrame` 只有 `type / content / conversation_id`，需**向后兼容地**新增两个可选字段：

```python
class WSInFrame(BaseModel):
    type: Literal["message", "ping", "resume"]
    content: str = ""
    conversation_id: str = ""
    agent: str | None = None      # 新增：显式指定插槽，缺省走意图路由
    context: dict | None = None   # 新增：{utteranceId, scene, speaker}
```

不传时行为与现状完全一致，`cooking` 链路零影响。

### 4.5 数据模型（MySQL，沿用 `schema.sql` 现有风格）

```sql
CREATE TABLE IF NOT EXISTS `talk_session` (
  `id`           BIGINT NOT NULL AUTO_INCREMENT,
  `user_id`      BIGINT NOT NULL,
  `thread_id`    VARCHAR(64) NOT NULL COMMENT 'LangGraph thread_id，同 /ws/chat 的 conversation_id',
  `title`        VARCHAR(128) DEFAULT NULL COMMENT 'AI 生成标题',
  `scene`        VARCHAR(32) NOT NULL DEFAULT 'general' COMMENT '场景: general通用, work职场, sales销售, romance亲密',
  `status`       VARCHAR(16) NOT NULL DEFAULT 'recording' COMMENT '状态: recording进行中, ended已结束',
  `turn_count`   INT NOT NULL DEFAULT 0 COMMENT '对方话语轮次',
  `duration_ms`  BIGINT NOT NULL DEFAULT 0,
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_talk_session_thread` (`thread_id`),
  KEY `idx_talk_session_user` (`user_id`, `updated_at`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='言外-会话';

CREATE TABLE IF NOT EXISTS `talk_utterance` (
  `id`         BIGINT NOT NULL AUTO_INCREMENT,
  `session_id` BIGINT NOT NULL,
  `user_id`    BIGINT NOT NULL,
  `seq`        INT NOT NULL COMMENT '段内序号',
  `speaker`    VARCHAR(16) NOT NULL DEFAULT 'other' COMMENT '说话人: other对方, me我, unknown未知',
  `source`     VARCHAR(16) NOT NULL DEFAULT 'voice' COMMENT '来源: voice语音, text文字',
  `content`    TEXT NOT NULL,
  `edited`     TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否被用户手工纠错',
  `confidence` DOUBLE DEFAULT NULL COMMENT 'ASR 置信度',
  `start_ms`   BIGINT DEFAULT NULL,
  `end_ms`     BIGINT DEFAULT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_talk_utterance_session` (`session_id`, `seq`),
  KEY `idx_talk_utterance_user` (`user_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='言外-话语';

CREATE TABLE IF NOT EXISTS `talk_suggestion` (
  `id`           BIGINT NOT NULL AUTO_INCREMENT,
  `session_id`   BIGINT NOT NULL,
  `utterance_id` BIGINT NOT NULL,
  `user_id`      BIGINT NOT NULL,
  `model`        VARCHAR(64) DEFAULT NULL,
  `intent`       VARCHAR(512) DEFAULT NULL,
  `subtext`      VARCHAR(512) DEFAULT NULL,
  `emotion`      VARCHAR(32)  DEFAULT NULL COMMENT '情绪标签',
  `risk`         VARCHAR(512) DEFAULT NULL,
  `payload`      JSON COMMENT '完整结构化结果（含 suggestions / followups）',
  `latency_ms`   INT DEFAULT NULL,
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_talk_suggestion_utterance` (`utterance_id`),
  KEY `idx_talk_suggestion_session` (`session_id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COMMENT ='言外-建议';
```

**MySQL 与 Redis 的分工（重要）**：Redis（checkpointer）只存 LangGraph 运行时状态，是「AI 的短期记忆」；
MySQL 存业务记录，供历史列表、搜索、详情查询。两者靠 `thread_id` 对齐。Redis 挂了不影响已存记录。

### 4.6 接口清单

| 方法 | 路径 | 说明 | 鉴权 |
| --- | --- | --- | --- |
| POST | `/talk/sessions` | 创建会话，返回 `id` + `threadId` | 登录 |
| GET | `/talk/sessions?page&size&keyword` | 会话列表 | 登录（`SecurityConfig` 落 `authenticated()`） |
| GET | `/talk/sessions/{id}` | 详情（话语 + 建议） | 登录 + 归属校验 |
| PATCH | `/talk/sessions/{id}` | 改标题 / 场景 / 状态 | 同上 |
| DELETE | `/talk/sessions/{id}` | 软删 | 同上 |
| POST | `/talk/sessions/{id}/utterances` | 保存一句话（语音定稿或手输） | 登录 + 归属 |
| PATCH | `/talk/utterances/{id}` | 纠错文本 / 改说话人 | 同上 |
| GET | `/talk/asr/ticket` | 换取 ASR 一次性 ticket | 登录 |
| WS | `/ws/asr?ticket=` | PCM 上行 / 转写下行 | ticket |
| POST | `/api/internal/talk/suggestions` | chat 服务回调落库建议 | 内网 + `X-Internal-Token` |
| WS | `/ws/chat` | 复用，新增 `agent`/`context` 字段 | 登录态由 `/ws/chat` 现状决定，见 §9 |

---

## 5. 关键决策记录（ADR 摘要）

| # | 决策 | 备选 | 理由 |
| --- | --- | --- | --- |
| A1 | 段级触发（断句后分析） | 逐 token 流式 / 录完统一分析 | 半句话语境不全会拖垮洞察质量；录完再分析丧失实时感。段级是体验与成本的最优点 |
| A2 | 服务端代理讯飞 | 小程序直连 | 密钥绝不下发端上 |
| A3 | PCM 实时帧直喂讯飞 | 录完上传文件 → 语音转写 | 避免 ffmpeg 转码与上传等待，延迟从分钟级降到秒级 |
| A4 | 独立小程序 `apps/echo-talk` | 在 `cooking-mini` 加页面 | 类目、主体、隐私指引冲突；独立后复用脚手架而非复用代码包 |
| A5 | 手动切换说话人 | 声纹自动分离 | 讯飞标准听写不支持说话人分离，换服务成本陡增；手动准确率 100% |
| A6 | 复用 `/ws/chat` + 插槽 | 另建 Agent 服务 | 复用 supervisor、意图路由、checkpointer、事件流，增量最小 |
| A7 | 不留存原始音频 | 落 COS 便于复盘 | 隐私红线；转写文本已足够复盘 |

---

## 6. 里程碑

| 阶段 | 交付物 | 验收 |
| --- | --- | --- |
| **M0 · 听得见** | `apps/echo-talk` 骨架 + 微信登录 + `/ws/asr` 网关 + 实时转写上屏 + 说话人切换 | 真机上说话 1s 内见字；连续录 12 分钟不中断（自动续录 + 60s 重连无感） |
| **M1 · 看得懂** | `agent-talk` 垂直 Agent + `/ws/chat` 字段扩展 + 洞察卡 / 建议卡 + TTS 朗读 | 定稿后 3.5s 内出 3 条建议；朗读能出声 |
| **M2 · 留得住** | 三张表 + 会话 CRUD + 历史列表 / 详情 / 纠错 / 删除 / 搜索 | 关掉小程序重进，整场对话完整可查 |
| **M3 · 打磨上线** | 场景预设、换一批、空/噪/错态处理、性能优化、隐私指引与提审 | 提审通过；崩溃率 < 0.5% |

建议在 M0 只接一个「通用场景」跑通全链路，**确认效果后再推 M1 的 Agent 调性与 M3 的场景扩展**。

---

## 7. 风险与合规

| 风险 | 影响 | 应对 |
| --- | --- | --- |
| **隐私合规（最高）** | 录音类小程序审核严格 | ① 不保存原始音频，只存文本；② 首次录音前弹明确告知；③ 公众平台配置《用户隐私保护指引》声明麦克风用途；④ 提供「一键清除全部记录」；⑤ 页面常驻「录音中」红点，避免误录 |
| 微信 10 分钟录音上限 | 长对话中断 | `onStop` 自动重开并标记分段 |
| 讯飞 60s 会话上限 | 转写断档 | 55s 主动收尾重连，文本顺序拼接 |
| 远场/嘈杂环境识别率下降 | 洞察建立在错文本上 | UI 提示「靠近音源」；转写可编辑纠错后重新分析 |
| LLM 建议不当（医疗/法律/财务） | 误导用户 | 系统提示词加入边界；高敏场景输出免责提示，建议「咨询专业人士」 |
| 成本失控（ASR + LLM） | 账单 | 段级触发已是最优节流；加单用户日调用上限与熔断 |
| 内容安全 | 分享外链违规 | F12 分享前走微信 `msgSecCheck`（上线前必做） |

---

## 8. 验收标准（M0–M2 可量化项）

1. 首字上屏延迟 P95 < 1.2s（Wi-Fi + 4G 各测 20 次）
2. 安静环境转写字准 > 95%，普通室内 > 90%
3. 段级建议首条上屏 P95 < 3.5s
4. 连续录音 12 分钟，分段衔接无丢字、无重复
5. 弱网（丢包 5%）下不崩溃，断连 3s 内自动恢复
6. 历史详情与实时界面内容一致，无丢失轮次
7. 全流程无音频文件落盘（抓包 + 存储扫描验证）

---

## 9. 待确认问题

| # | 问题 | 建议 |
| --- | --- | --- |
| Q1 | 产品中文名定哪个（言外 / 会听 / EchoTalk 直用） | 倾向「言外」，取「听懂言外之意」 |
| Q2 | 小程序独立 AppID 与类目是否已有 | 需申请「工具 → 效率」类目；录音需单独说明用途 |
| Q3 | 讯飞控制台是否已开通「语音听写（流式版）」额度与当前计费档 | 需在控制台确认套餐与 QPS 限制；ASR 与现有 TTS 是否共用一个 AppID |
| Q4 | `/ws/chat` 现有是否需要登录态 | 现状未做鉴权，本次是否补（影响多用户隔离） |
| Q5 | 会话保留时长（30 天 / 永久） | 建议默认永久，提供手动清理 |
| Q6 | 是否需要 H5 版（Taro 已支持 `build:h5`） | 可低成本附赠，便于分享外链与真机快速验证 |
