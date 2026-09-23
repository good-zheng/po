"""embedding 不可用时的本地降级路由：字符 bigram 重叠打分，零网络依赖。

HybridRouter 需要 DenseEncoder（网络服务）；key 缺失或接口不可达时，
垂直 Agent 不应整体退化为纯聊天，改用本路由器保住「能路由到领域」的
底线。打分量纲与稠密余弦不同，阈值独立默认，不与 ``router_threshold``
混用。
"""

from __future__ import annotations

from semantic_router import Route

from po_agent_core.routing.decisions import FALLBACK_INTENT, RouteDecision

# 覆盖率量纲（0~1）下的经验值：utterance 语料较短，命中一半左右的字符组合
# 即认为语义相关；调高会漏召，调低会把闲聊误判成业务请求
KEYWORD_THRESHOLD = 0.2


def _bigrams(text: str) -> set[str]:
    """取相邻两字符组成的集合。

    中文无需分词即可表达局部词序：去空白后滑窗，
    单字文本（不足 2 字符）返回空集，这类查询不会命中任何语料。
    """
    normalized = "".join(str(text).split())
    return {normalized[i : i + 2] for i in range(len(normalized) - 1)}


class KeywordIntentRouter:
    """本地关键词路由器：查询对语料 utterance 的 bigram 覆盖率取最大值。

    覆盖率 = |查询∩语料| / |语料|（分母是语料而非查询，用户长句包含
    utterance 表达即视为命中，不被查询长度稀释）。无命中返回
    ``intent=None``，由 supervisor 兜底 chitchat。
    """

    def __init__(
        self,
        routes: list[Route],
        *,
        threshold: float = KEYWORD_THRESHOLD,
        fallback_intent: str = FALLBACK_INTENT,
    ) -> None:
        if not routes:
            raise ValueError("routes 不能为空")
        self._routes = routes
        self._threshold = threshold
        self._fallback_intent = fallback_intent
        # 语料在构造期一次性切好：路由本身是纯计算，避免每次请求重复切分
        self._corpus: dict[str, list[set[str]]] = {
            route.name: [_bigrams(u) for u in route.utterances if _bigrams(u)]
            for route in routes
        }

    @property
    def route_names(self) -> list[str]:
        return [route.name for route in self._routes]

    def route(self, text: str) -> RouteDecision:
        query = _bigrams(text)
        # 同一个 Agent 的多条 utterance 各自打分，取最相似的一条作为该 Agent 的得分
        best_name: str | None = None
        best_score = 0.0
        for name, utterances in self._corpus.items():
            for grams in utterances:
                coverage = len(query & grams) / len(grams)
                if coverage > best_score:
                    best_name, best_score = name, coverage
        if best_name is not None and best_score >= self._threshold:
            return RouteDecision(intent=best_name, score=best_score, source="keyword")
        # 未达阈值仍返回最高分，便于宿主日志定位「差一点命中」的查询
        return RouteDecision(intent=None, score=best_score, source="keyword")
