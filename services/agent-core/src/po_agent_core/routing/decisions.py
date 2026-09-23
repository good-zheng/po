"""路由决策协议：无依赖的常量与数据结构，供各路由器实现共享。

单独成模块是为了打破循环依赖：``router`` 需要 import 各降级路由器
（keyword / fallback），而被它们共享的结果类型不能定义在 ``router`` 里，
否则 import 到一半就会互相引用。本模块只放数据结构，不引用任何实现。
"""

from __future__ import annotations

from dataclasses import dataclass

FALLBACK_INTENT = "chitchat"


@dataclass(frozen=True, slots=True)
class RouteDecision:
    """单次路由决策结果。

    ``intent=None`` 表示无路由命中（分数低于阈值），调用方应走兜底。
    """

    intent: str | None
    score: float
    source: str  # "hybrid" | "keyword" | "fallback"，用于日志与排查降级原因
