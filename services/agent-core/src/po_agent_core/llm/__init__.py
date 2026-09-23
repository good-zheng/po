"""LLM / Embedding 工厂：统一 OpenAI 兼容协议接入，消灭散落的客户端构建。

对外入口是 ``factory.create_chat_model`` / ``factory.create_embeddings``：
只做参数解析与客户端构造，不发起网络请求，因此不会在 import 或装配期阻塞。

``create_chat_model(settings, role=...)`` 按用途（plan/write/judge…）解析模型，
角色到模型的映射来自 ``AgentCoreSettings.llm_roles``；未配置的角色回落默认槽位。
"""
