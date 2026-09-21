---
kind: external_dependency
name: LLM 编排：LangChain + LangGraph
slug: langchain-langgraph
category: external_dependency
category_hints:
    - framework_behavior
scope:
    - '**'
---

### LangChain + LangGraph
- 状态：规划中，尚未在 py_server 引入（旧 Flask + LangGraph 实现已随迁移删除，`agents/chat_graph.py` 不存在）。
- 引入前须走 OpenSpec 变更（python-dev skill 硬约束）；LLM 依赖必须保留离线降级路径——旧实现用 `FakeListChatModel` 在未配置 `OPENAI_API_KEY` 时联调完整链路，该约定应延续。
- 集成点预案：WebSocket `/ws/chat` 的 token/done 帧协议天然适配流式 token 推送，LangGraph 图可作为回复生成器替换现有 echo 逻辑。
