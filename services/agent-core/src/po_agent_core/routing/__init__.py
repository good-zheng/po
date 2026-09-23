"""决策层：Layer1 意图路由（semantic-router Hybrid + 关键词/兜底降级）。

统一入口 ``create_intent_router(settings, routes)``：按配置与可用性返回
``IntentRouter``（混合）/ ``KeywordIntentRouter``（本地关键词）/
``FallbackIntentRouter``（兜底）之一，三者都实现同一个 ``route(text)``
调用形态并返回 ``RouteDecision``，supervisor 无需感知具体实现。
"""

from po_agent_core.routing.keyword import KEYWORD_THRESHOLD, KeywordIntentRouter
from po_agent_core.routing.router import (
    FALLBACK_INTENT,
    FallbackIntentRouter,
    IntentRouter,
    RouteDecision,
    create_intent_router,
    routes_from_agents,
)
from po_agent_core.routing.tokenizer import CharTokenizer

__all__ = [
    "FALLBACK_INTENT",
    "KEYWORD_THRESHOLD",
    "CharTokenizer",
    "FallbackIntentRouter",
    "IntentRouter",
    "KeywordIntentRouter",
    "RouteDecision",
    "create_intent_router",
    "routes_from_agents",
]
