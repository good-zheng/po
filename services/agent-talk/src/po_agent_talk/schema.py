"""言外 Agent 的结构化输出契约。

模型输出的 JSON 在这里落地为 :class:`TalkAnalysis`：既用于渲染小程序卡片，
也用于回写 Spring Boot（字段名与 ``InternalSuggestionRequest`` 一一对应）。

:func:`parse_analysis` 对模型输出做宽容解析——LLM 偶发地带代码围栏或前后
寒暄，这里只取最外层 JSON 对象，解析失败返回 ``None`` 交由上层降级。
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, Field

# 三条建议的固定风格：前端卡片配色、顺序、朗读顺序都依赖这个取值
STYLE_SAFE = "稳妥"
STYLE_EMPATHY = "共情"
STYLE_PUSH = "推进"
SUGGESTION_STYLES: tuple[str, ...] = (STYLE_SAFE, STYLE_EMPATHY, STYLE_PUSH)


class SuggestionItem(BaseModel):
    """一条可照说的回复。"""

    style: str = ""
    text: str = ""
    why: str = ""


class TalkAnalysis(BaseModel):
    """一轮洞察：四段解读 + 三条建议 + 可追问。"""

    intent: str = ""
    subtext: str = ""
    emotion: str = ""
    risk: str = ""
    suggestions: list[SuggestionItem] = Field(default_factory=list)
    followups: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """转成可 JSON 序列化的字典（字段名对齐 Java 侧入参）。"""
        return {
            "intent": self.intent,
            "subtext": self.subtext,
            "emotion": self.emotion,
            "risk": self.risk,
            "suggestions": [item.model_dump() for item in self.suggestions],
            "followups": list(self.followups),
        }


def parse_analysis(text: str) -> TalkAnalysis | None:
    """从模型输出里抠出 JSON 并校验；失败返回 ``None``。

    宽容处理三种常见噪声：markdown 代码围栏、前后说明文字、末尾多余逗号。
    """
    if not text:
        return None
    raw = text.strip()
    if raw.startswith("```"):
        # 去掉围栏首行与末尾的 ```（围栏语言标记可能是 json / JSON）
        lines = raw.splitlines()
        if lines:
            lines = lines[1:]
        while lines and lines[-1].strip().startswith("```"):
            lines.pop()
        raw = "\n".join(lines).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    try:
        return TalkAnalysis.model_validate(data)
    except Exception:
        return None
