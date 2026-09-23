# po-agent-novel

小说创作垂直 Agent：经 `po-agent-core` 插槽接入 supervisor，一句话想法 → 完整书稿归档。

## 链路

```
conceive（构思：标题/摘要/类型）
  → outline（大纲：章标题+章梗概）
  → generate（初稿/修订稿，带上一章结尾衔接）
  → reflect（反思评分：score ≥ target 或修订次数用尽 → 定稿入列，否则回 generate）
  → ……循环至全部章完成
  → archive（interrupt 人工确认 → yes：抽取角色 + 三方法入库 → 全书正文回复）
```

- 领域状态全部放在 `CoreState.artifacts["novel"]` 命名空间，supervisor 不解释；
- 子图不挂 checkpointer，由父图统一供给（interrupt 依赖父图线程 checkpoint）；
- 领域进度经 `get_stream_writer` 发布 THINKING/PLAN 事件，AgentRunner 以
  `subgraphs=True` 透传到 WS/A2A 等传输层。

## 分阶段模型

节点按用途声明模型角色（`graph.NODE_MODEL_ROLES`，改这张表即改阶段归属）：

| 阶段 | 角色 | 可选覆盖 |
| --- | --- | --- |
| conceive / outline | `plan` | `AGENT_CORE_LLM_ROLES__PLAN__MODEL` |
| generate（初稿与修订） | `write` | `AGENT_CORE_LLM_ROLES__WRITE__MODEL`、`__WRITE__TEMPERATURE` |
| reflect / archive 角色抽取 | `judge` | `AGENT_CORE_LLM_ROLES__JUDGE__*` |

未配置的角色回落 `AGENT_CORE_LLM_*` 默认槽位（不配就是单模型）；角色可跨 provider
（此时必须自带 `API_KEY`）。任一角色解析失败则**整体**降级为 `OfflineNovelModel`
——部分降级会得到「真模型正文 + 占位审稿」的混合链路，比统一离线更难排查。
`build_novel_agent(..., chat_model=...)` 传入即所有阶段共用该实例，跳过角色解析。

## 降级

`AGENT_CORE_LLM_API_KEY` 缺失时 `build_novel_agent` 自动切换 `OfflineNovelModel`：
确定性占位构思/大纲/评分（恒 9 分，不进修订循环），正文显式标注 `【离线模式】`，
绝不冒充真实生成。未知 structured schema 抛 `ValueError`。

## 数据层（NovelStore Protocol）

`save_book` / `save_chapters` / `save_characters` / `list_books`，方法粒度对齐
Java novel 模块资源划分（book/chapter/character）。当前实现为 `MockNovelStore`
（进程内），未来逐方法替换为 HTTP 实现，子图零改动。

## 装配

```python
from po_agent_novel import build_novel_agent

agent = build_novel_agent(settings)  # VerticalAgent(name="novel", ...)
```

chat 宿主默认装配本插槽（`services/chat/app/agent.py`），无需手工注册。
意图语料由 `NOVEL_UTTERANCES`（8 条）经 `routes_from_agents` 派生进 Layer1 路由。

## 测试

```bash
pnpm agentnovel:test   # 仓库根目录；复用 services/chat/.venv，离线零网络
```

## 延伸阅读

- [链路图.md](./链路图.md) —— 启动装配 → 运行期 → 客户端往返的完整链路图（含
  interrupt/resume 时序、事件→帧映射、降级矩阵与落点索引）。
