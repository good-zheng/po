"""路由层测试：全部离线（稠密编码器用字符袋 fake，BM25 用 CharTokenizer）。"""

from typing import Any, List

import pytest
from semantic_router import Route
from semantic_router.encoders import OpenAIEncoder
from semantic_router.encoders.base import DenseEncoder
from langgraph.graph import END, START, StateGraph

from po_agent_core.agents import VerticalAgent
from po_agent_core.config import AgentCoreSettings
from po_agent_core.errors import AgentCoreConfigError
from po_agent_core.routing.router import (
    FallbackIntentRouter,
    IntentRouter,
    RouteDecision,
    _create_dense_encoder,
    create_intent_router,
    routes_from_agents,
)
from po_agent_core.routing.keyword import KEYWORD_THRESHOLD, KeywordIntentRouter
from po_agent_core.supervisor.state import CoreState

ROUTES = [
    Route(
        name="poem_write",
        utterances=["写一首诗", "续写诗句", "创作一首唐诗", "帮我写首现代诗"],
    ),
    Route(name="chitchat", utterances=["你好", "讲个笑话", "今天天气怎么样", "无聊了"]),
]


class BagOfCharsEncoder(DenseEncoder):
    """字符袋稠密编码器：共享字符越多余弦相似度越高，可离线验证路由行为。"""

    name: str = "bag-of-chars"

    def __call__(self, docs: List[Any]) -> List[List[float]]:
        out = []
        for doc in docs:
            vec = [0.0] * 64
            for ch in str(doc):
                if not ch.isspace():
                    vec[ord(ch) % 64] += 1.0
            out.append(vec)
        return out


def make_router(threshold: float) -> IntentRouter:
    return IntentRouter(ROUTES, BagOfCharsEncoder(), threshold=threshold)


def test_route_matches_domain_intent() -> None:
    router = make_router(threshold=0.3)
    decision = router.route("帮我写一首关于江南春色的诗")
    assert decision.intent == "poem_write"
    assert decision.source == "hybrid"
    assert decision.score >= 0.3


def test_route_matches_chitchat() -> None:
    router = make_router(threshold=0.3)
    decision = router.route("你好呀，今天天气怎么样")
    assert decision.intent == "chitchat"


def test_route_below_threshold_falls_back_to_none() -> None:
    router = make_router(threshold=99.0)
    decision = router.route("帮我写一首关于江南春色的诗")
    assert decision.intent is None
    assert decision.source == "hybrid"


def test_route_names_property() -> None:
    assert make_router(threshold=0.3).route_names == ["poem_write", "chitchat"]


def test_empty_routes_rejected() -> None:
    with pytest.raises(ValueError):
        IntentRouter([], BagOfCharsEncoder())


def test_fallback_router_always_returns_none() -> None:
    router = FallbackIntentRouter()
    decision = router.route("写一首诗")
    assert decision == RouteDecision(intent=None, score=0.0, source="fallback")
    assert router.route_names == []


def no_key_settings() -> AgentCoreSettings:
    return AgentCoreSettings(
        _env_file=None,
        llm_provider="qwen",
        llm_api_key="",
        embedding_api_key="",
    )


def test_create_dense_encoder_from_qwen_preset() -> None:
    settings = AgentCoreSettings(
        _env_file=None, llm_provider="qwen", llm_api_key="sk-test"
    )
    encoder = _create_dense_encoder(settings)
    assert isinstance(encoder, OpenAIEncoder)
    assert encoder.name == "text-embedding-v4"
    # 上游不存 openai_base_url 属性，base_url 只落在 client 上
    assert str(encoder._client.base_url) == "https://dashscope.aliyuncs.com/compatible-mode/v1/"


def test_create_dense_encoder_missing_key_raises() -> None:
    with pytest.raises(AgentCoreConfigError):
        _create_dense_encoder(no_key_settings())


def test_create_intent_router_degrades_without_embedding_config() -> None:
    router = create_intent_router(no_key_settings(), ROUTES)
    assert isinstance(router, KeywordIntentRouter)
    # 降级后垂直 Agent 仍可被路由到，而非整体退化为纯聊天
    assert router.route("帮我写一首关于江南春色的诗").intent == "poem_write"


def test_keyword_router_routes_by_bigram_coverage() -> None:
    router = KeywordIntentRouter(ROUTES)
    assert router.route_names == ["poem_write", "chitchat"]
    decision = router.route("帮我写一首关于江南春色的诗")
    assert decision.intent == "poem_write"
    assert decision.source == "keyword"
    assert decision.score >= KEYWORD_THRESHOLD
    # 无交集的闲聊不命中 → supervisor 兜底 chitchat
    assert router.route("hello world").intent is None


def test_keyword_router_threshold_controls_no_match() -> None:
    router = KeywordIntentRouter(ROUTES, threshold=99.0)
    assert router.route("帮我写一首关于江南春色的诗").intent is None


def test_keyword_router_rejects_empty_routes() -> None:
    with pytest.raises(ValueError):
        KeywordIntentRouter([])


def test_create_intent_router_with_injected_encoder() -> None:
    settings = AgentCoreSettings(_env_file=None, llm_provider="qwen", llm_api_key="")
    router = create_intent_router(
        settings, ROUTES, encoder=BagOfCharsEncoder(), threshold=0.3
    )
    assert isinstance(router, IntentRouter)
    assert router.route("帮我写一首关于江南春色的诗").intent == "poem_write"


def test_create_intent_router_uses_settings_threshold() -> None:
    settings = AgentCoreSettings(_env_file=None, router_threshold=99.0)
    router = create_intent_router(settings, ROUTES, encoder=BagOfCharsEncoder())
    assert isinstance(router, IntentRouter)
    assert router.route("帮我写一首关于江南春色的诗").intent is None


# ---------- 从垂直 Agent 插槽派生路由 ----------


def _slot_agent(name: str, utterances: tuple[str, ...]) -> VerticalAgent:
    builder = StateGraph(CoreState)
    builder.add_node("noop", lambda state: {"messages": []})
    builder.add_edge(START, "noop")
    builder.add_edge("noop", END)
    return VerticalAgent(
        name=name,
        description="测试插槽",
        graph=builder.compile(),
        utterances=utterances,
    )


def test_routes_from_agents_builds_route_per_agent() -> None:
    agents = [
        _slot_agent("verse", ("写一首词", "帮我填词")),
        _slot_agent("poem", ("写一首诗",)),
    ]
    routes = routes_from_agents(agents)
    assert [r.name for r in routes] == ["verse", "poem"]
    assert routes[0].utterances == ["写一首词", "帮我填词"]


def test_routes_from_agents_skips_empty_utterances() -> None:
    routes = routes_from_agents([_slot_agent("verse", ("写一首词",)), _slot_agent("bare", ())])
    assert [r.name for r in routes] == ["verse"]


def test_create_intent_router_empty_routes_degrades() -> None:
    router = create_intent_router(
        AgentCoreSettings(_env_file=None, llm_api_key="sk-test"), []
    )
    assert isinstance(router, FallbackIntentRouter)


def test_create_intent_router_router_failure_degrades(monkeypatch) -> None:
    # HybridRouter 装配抛错（如启动时 embedding 接口不可达）→ 本地关键词路由而非崩溃
    def boom(*args, **kwargs):
        raise RuntimeError("embedding 接口不可达")

    monkeypatch.setattr("po_agent_core.routing.router.HybridRouter", boom)
    router = create_intent_router(
        AgentCoreSettings(_env_file=None, llm_api_key="sk-test"),
        ROUTES,
        encoder=BagOfCharsEncoder(),
    )
    assert isinstance(router, KeywordIntentRouter)
