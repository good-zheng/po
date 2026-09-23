"""Layer1 意图路由：semantic-router HybridRouter（稠密+BM25 混合）+ 降级链。

三层决策架构中的第一层（用户消息 → 垂直 Agent / chitchat）：

- 正常态：``IntentRouter`` 包 ``HybridRouter`` = 稠密 embedding（OpenAI 兼容
  接口）+ 稀疏 BM25（``CharTokenizer``，纯本地）混合打分；
- 降级态一：embedding 未配置或构建失败 → ``KeywordIntentRouter``（纯本地
  字符 bigram 覆盖率），垂直 Agent 仍可被路由到，不整体退化为纯聊天；
- 降级态二：没有任何路由语料（无垂直 Agent）→ ``FallbackIntentRouter``，
  一律判为未命中，由 supervisor 走 chitchat 兜底。

阈值策略：不在 semantic-router 内部做 pass/fail（BM25 分数可 > 1，
encoder 级阈值语义随编码器漂移），统一由各路由器的 ``route`` 用
``router_threshold`` 一刀切，分数不足即视为未命中（``intent=None``），
去向交由 supervisor 决定。
"""

from __future__ import annotations

import logging
from collections.abc import Iterable

from semantic_router import Route
from semantic_router.encoders import BM25Encoder
from semantic_router.encoders.base import DenseEncoder
from semantic_router.routers import HybridRouter

from po_agent_core.agents.slots import VerticalAgent
from po_agent_core.config import AgentCoreSettings
from po_agent_core.llm.factory import resolve_llm
from po_agent_core.routing.decisions import FALLBACK_INTENT, RouteDecision
from po_agent_core.routing.keyword import KeywordIntentRouter
from po_agent_core.routing.tokenizer import CharTokenizer

logger = logging.getLogger(__name__)


class IntentRouter:
    """混合意图路由器（同步调用；宿主在 async 环境用 ``asyncio.to_thread`` 包裹）。

    同步是刻意的：``HybridRouter.__call__`` 内部会发起 embedding 网络请求，
    直接放进 async 函数会阻塞事件循环，因此由宿主决定用线程池承载。
    """

    def __init__(
        self,
        routes: list[Route],
        encoder: DenseEncoder,
        *,
        threshold: float = 0.55,
        fallback_intent: str = FALLBACK_INTENT,
        sparse_encoder: BM25Encoder | None = None,
        alpha: float = 0.3,
    ) -> None:
        if not routes:
            raise ValueError("routes 不能为空")
        self._routes = routes
        self._threshold = threshold
        self._fallback_intent = fallback_intent
        # alpha 是稠密分权重（混合分 = alpha*稠密 + (1-alpha)*稀疏）：
        # 0.3 偏向 BM25，让领域术语的精确命中更稳定；
        # auto_sync="local" 表示只在进程内构建索引，不推送到远端
        self._router = HybridRouter(
            encoder=encoder,
            sparse_encoder=sparse_encoder or BM25Encoder(tokenizer=CharTokenizer()),
            routes=routes,
            auto_sync="local",
            alpha=alpha,
        )

    @property
    def route_names(self) -> list[str]:
        return [route.name for route in self._routes]

    def route(self, text: str) -> RouteDecision:
        choice = self._router(text)
        score = float(choice.similarity_score or 0.0)
        if choice.name and score >= self._threshold:
            return RouteDecision(intent=choice.name, score=score, source="hybrid")
        return RouteDecision(intent=None, score=score, source="hybrid")


class FallbackIntentRouter:
    """降级路由器：连路由语料都没有时的末端兜底，恒判「未命中」。

    ``intent=None`` 会被 supervisor 解释为走 chitchat 兜底节点，
    因此它的存在意义是「让编排图在任何配置下都有确定去向」，
    而不是提供某种降级识别能力。
    """

    def __init__(self, fallback_intent: str = FALLBACK_INTENT) -> None:
        self._fallback_intent = fallback_intent

    @property
    def route_names(self) -> list[str]:
        return []

    def route(self, text: str) -> RouteDecision:
        return RouteDecision(intent=None, score=0.0, source="fallback")


def _create_dense_encoder(settings: AgentCoreSettings) -> DenseEncoder:
    """从配置构建稠密编码器（OpenAI 兼容 embedding 接口）。

    配置缺失时抛 ``AgentCoreConfigError``，由 ``create_intent_router``
    决定降级而非在此静默。
    """
    from semantic_router.encoders import OpenAIEncoder

    preset = _embedding_preset(settings)
    model = settings.embedding_model or preset
    api_key = settings.embedding_api_key or settings.llm_api_key
    base_url = (
        settings.embedding_base_url or settings.llm_base_url or _provider_base_url(settings)
    )
    if not model or not api_key:
        from po_agent_core.errors import AgentCoreConfigError

        raise AgentCoreConfigError(
            "semantic-router 决策层缺少 embedding 配置，"
            "请设置 AGENT_CORE_EMBEDDING_API_KEY（或 AGENT_CORE_LLM_API_KEY）；"
            "当前已降级为兜底路由"
        )
    kwargs: dict[str, object] = {"name": model, "openai_api_key": api_key}
    if base_url:
        kwargs["openai_base_url"] = base_url
    try:
        return OpenAIEncoder(**kwargs)
    except KeyError:
        # 上游 bug：__init__ 尾部的 tiktoken.encoding_for_model 不认识
        # 非 OpenAI 模型名（如 qwen 的 text-embedding-v4）直接 KeyError。
        # _token_encoder 仅用于超长文本截断，回退通用编码即可。
        return _openai_encoder_with_tokenizer_fallback(kwargs)


def _openai_encoder_with_tokenizer_fallback(kwargs: dict[str, object]) -> "DenseEncoder":
    """保留上游初始化逻辑，仅令 tiktoken 模型名查找支持回退。"""
    import tiktoken

    from semantic_router.encoders import OpenAIEncoder

    original = tiktoken.encoding_for_model

    def _lookup_with_fallback(model_name: str):
        try:
            return original(model_name)
        except KeyError:
            return tiktoken.get_encoding("cl100k_base")

    tiktoken.encoding_for_model = _lookup_with_fallback  # type: ignore[assignment]
    try:
        return OpenAIEncoder(**kwargs)  # type: ignore[arg-type]
    finally:
        tiktoken.encoding_for_model = original  # type: ignore[assignment]


def _provider_base_url(settings: AgentCoreSettings) -> str:
    from po_agent_core.llm.factory import PROVIDER_PRESETS

    return PROVIDER_PRESETS.get(settings.llm_provider, {}).get("base_url", "")


def _embedding_preset(settings: AgentCoreSettings) -> str:
    from po_agent_core.llm.factory import PROVIDER_PRESETS

    return PROVIDER_PRESETS.get(settings.llm_provider, {}).get("embedding_model", "")


def routes_from_agents(agents: Iterable[VerticalAgent]) -> list[Route]:
    """从垂直 Agent 插槽派生 Layer1 路由语料。

    ``utterances`` 为空的 Agent 不建 Route（不参与意图路由）。
    """
    return [
        Route(name=agent.name, utterances=list(agent.utterances))
        for agent in agents
        if agent.utterances
    ]


def create_intent_router(
    settings: AgentCoreSettings,
    routes: list[Route],
    *,
    encoder: DenseEncoder | None = None,
    threshold: float | None = None,
) -> IntentRouter | FallbackIntentRouter:
    """按配置构建意图路由器；embedding 缺失或构建失败时降级并记录告警。

    降级语义（宿主启动不因路由层失败而中断）：

    - ``routes`` 为空：无路由目标，直接兜底；
    - 稠密编码器构建失败（缺 key/未知 provider）：本地关键词路由；
    - ``HybridRouter`` 装配失败（如启动时 embedding 接口不可达）：
      本地关键词路由——垂直 Agent 在无 embedding 环境仍可被路由到，
      不整体退化为纯聊天。

    ``encoder`` 允许显式注入（测试或自定义编码器），
    缺省时尝试从 ``settings`` 解析，失败则降级。
    """
    if not routes:
        # 没有垂直 Agent 就没有路由目标，此时「兜底」才是正确行为
        logger.warning("意图路由无可用路由语料，降级为兜底模式")
        return FallbackIntentRouter()
    if encoder is None:
        try:
            encoder = _create_dense_encoder(settings)
        except Exception as exc:  # 降级路径：任何配置解析失败都不阻断启动
            logger.warning("稠密编码器不可用，意图路由降级为本地关键词模式：%s", exc)
            return KeywordIntentRouter(routes)
    # 触发一次 LLM 配置解析以在日志中尽早暴露配置问题（不产生网络请求）
    try:
        resolve_llm(settings)
    except Exception as exc:
        logger.warning("LLM 配置未就绪（仅告警）：%s", exc)
    try:
        return IntentRouter(
            routes,
            encoder,
            threshold=settings.router_threshold if threshold is None else threshold,
        )
    except Exception as exc:  # HybridRouter 装配涉及 embedding 接口调用
        logger.warning("HybridRouter 装配失败，意图路由降级为本地关键词模式：%s", exc)
        return KeywordIntentRouter(routes)
