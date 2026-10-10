"""无 LLM 时的离线降级模型。

沿用工程既有的「静默降级」文化：没有 API Key 时聊天服务照常启动，言外卡片
照常出内容，只是洞察来自关键词规则而不是模型。用户在界面上看到的是一张
可用的卡片，而不是 500——排障看日志，不看行为。

关键词表刻意保持很小：它的作用是「没配模型时不至于空白」，不是真做情绪分析。
"""

from __future__ import annotations

import json

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult

# 触发词 → 情绪标签。命中即采用，未命中走中性。
EMOTION_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("随你", "你看着办", "随便", "都行"), "回避 · 不愿表态"),
    (("不行", "不对", "怎么会", "怎么搞的", "又"), "不满 · 带指责"),
    (("快点", "多久", "还没", "催", "急"), "着急 · 催促"),
    (("谢谢", "辛苦", "不错", "很好"), "正向 · 认可"),
    (("为什么", "怎么回事", "解释"), "质疑 · 要求说明"),
)

OFFLINE_TAG = "offline"


def _strip_meta(text: str) -> str:
    """去掉宿主拼的上下文前缀（``[场景: ...]`` 这类元信息）。"""
    lines = [line for line in text.splitlines() if not line.strip().startswith("[")]
    return "\n".join(lines).strip() or text.strip()


def _detect_emotion(text: str) -> str:
    for keywords, label in EMOTION_RULES:
        if any(keyword in text for keyword in keywords):
            return label
    return "中性 · 信息不足"


def _build_reply(text: str, emotion: str) -> dict:
    """离线版洞察：只给通用但确实能用的三套话术。"""
    return {
        "intent": "（离线模式）无法判断真实意图，以下为通用应对",
        "subtext": "未配置语言模型，已降级为规则建议",
        "emotion": emotion,
        "risk": "离线建议未经语义分析，重要对话请自行判断",
        "suggestions": [
            {"style": "稳妥", "text": "我这边先确认一下，回头给你准信。", "why": "争取时间再做判断"},
            {"style": "共情", "text": "我理解你的意思，咱们慢慢说。", "why": "先接住情绪再谈事"},
            {"style": "推进", "text": "那我先按这个方向处理，有问题随时叫停。", "why": "给默认路径减少来回"},
        ],
        "followups": ["你能再说具体一点吗？"],
    }


class OfflineTalkModel(BaseChatModel):
    """离线降级：把最后一条用户消息按关键词规则转成结构化 JSON。"""

    @property
    def _llm_type(self) -> str:
        return "offline-talk-model"

    @staticmethod
    def _reply(messages: list) -> str:
        last_user = next(
            (m for m in reversed(messages) if isinstance(m, HumanMessage)), None
        )
        text = last_user.content if last_user else ""
        if not isinstance(text, str):
            text = str(text)
        body = _strip_meta(text)
        payload = _build_reply(body, _detect_emotion(body))
        # 与在线模式输出同构：纯 JSON，前端解析路径完全一致
        return json.dumps(payload, ensure_ascii=False)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self._reply(messages)))]
        )

    async def _agenerate(
        self, messages, stop=None, run_manager=None, **kwargs
    ) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self._reply(messages)))]
        )
