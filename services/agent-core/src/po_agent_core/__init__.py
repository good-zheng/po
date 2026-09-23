"""po-agent-core：po monorepo 的智能体编排核心库（框架无关）。

铁律：本包禁止 import 任何 Web 框架（fastapi/flask/uvicorn/starlette），
重资源延迟到显式工厂创建，领域逻辑经垂直 Agent 插槽注入。
（该约束由测试里的 AST 扫描强制，新增模块不要引入框架依赖。）

一次请求的流转：宿主用 ``AgentCoreSettings`` 读配置 → ``create_intent_router``
建 Layer1 意图路由 → ``build_supervisor_graph`` 把垂直 Agent 子图挂成节点并
compile（挂上 checkpointer）→ ``AgentRunner.astream`` 运行图、把 LangGraph 流
翻译成 ``AgentEvent`` → 宿主再把事件翻译成自己的对外协议（WS 帧 / A2A / MCP）。

顶层 re-export 即公开 API：宿主只从这里 import，子模块内部结构可自由演进。
"""

__version__ = "0.1.0"

from po_agent_core.agents import VerticalAgent, VerticalAgentError
from po_agent_core.config import AgentCoreSettings, ModelRole, ModelSlot
from po_agent_core.errors import AgentCoreConfigError, AgentCoreError
from po_agent_core.events import AgentEvent, EventType
from po_agent_core.llm.factory import create_chat_model, create_embeddings
from po_agent_core.memory import CheckpointerManager, StoreManager, user_namespace
from po_agent_core.routing import (
    CharTokenizer,
    FallbackIntentRouter,
    IntentRouter,
    KeywordIntentRouter,
    RouteDecision,
    create_intent_router,
    routes_from_agents,
)
from po_agent_core.runner import AgentRunner
from po_agent_core.supervisor import CoreState, build_supervisor_graph
from po_agent_core.tools import ToolRegistry, ToolRegistrationError

__all__ = [
    "__version__",
    # 配置与错误
    "AgentCoreSettings",
    "ModelRole",
    "ModelSlot",
    "AgentCoreError",
    "AgentCoreConfigError",
    # 事件协议
    "AgentEvent",
    "EventType",
    # LLM 工厂
    "create_chat_model",
    "create_embeddings",
    # 记忆
    "CheckpointerManager",
    "StoreManager",
    "user_namespace",
    # 决策层
    "CharTokenizer",
    "IntentRouter",
    "KeywordIntentRouter",
    "FallbackIntentRouter",
    "RouteDecision",
    "create_intent_router",
    "routes_from_agents",
    # 编排
    "VerticalAgent",
    "VerticalAgentError",
    "CoreState",
    "build_supervisor_graph",
    "AgentRunner",
    # 工具
    "ToolRegistry",
    "ToolRegistrationError",
]
