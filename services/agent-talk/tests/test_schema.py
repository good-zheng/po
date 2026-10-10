"""结构化输出解析与离线降级的测试。

解析层是最需要单测的地方：模型输出带噪声（代码围栏、前后寒暄）是常态，
而这里一失败，前端拿到的就不是卡片而是空白。
"""

from __future__ import annotations

import json

import pytest

from po_agent_talk.offline import OfflineTalkModel
from po_agent_talk.schema import TalkAnalysis, parse_analysis

SAMPLE = {
    "intent": "要你给明确答复，别把决定权推回去",
    "subtext": "我不想担这个责，你来定",
    "emotion": "回避 · 略带不满",
    "risk": "真自己拍板，出问题会背锅",
    "suggestions": [
        {"style": "稳妥", "text": "我先理两个方案，下午三点前发你定夺。", "why": "给方案不给结论"},
        {"style": "共情", "text": "我知道这事不好拍板。", "why": "先接住情绪"},
        {"style": "推进", "text": "那我按 A 方案推进。", "why": "给默认路径"},
    ],
    "followups": ["你觉得哪个方案风险更小？"],
}


def test_parse_plain_json() -> None:
    analysis = parse_analysis(json.dumps(SAMPLE, ensure_ascii=False))
    assert analysis is not None
    assert analysis.intent == SAMPLE["intent"]
    assert len(analysis.suggestions) == 3
    assert analysis.suggestions[0].style == "稳妥"


def test_parse_with_code_fence() -> None:
    """模型偶发地带 ```json 围栏，必须照样能解析。"""
    fenced = "```json\n" + json.dumps(SAMPLE, ensure_ascii=False) + "\n```"
    analysis = parse_analysis(fenced)
    assert analysis is not None
    assert analysis.subtext == SAMPLE["subtext"]


def test_parse_surrounded_by_chatter() -> None:
    noisy = "好的，分析结果如下：\n" + json.dumps(SAMPLE, ensure_ascii=False) + "\n希望对你有帮助"
    assert parse_analysis(noisy) is not None


@pytest.mark.parametrize("bad", ["", "这不是 JSON", "{intent: }", "[]"])
def test_parse_invalid_returns_none(bad: str) -> None:
    assert parse_analysis(bad) is None


def test_roundtrip_to_dict() -> None:
    analysis = TalkAnalysis.model_validate(SAMPLE)
    payload = analysis.to_dict()
    assert payload["intent"] == SAMPLE["intent"]
    assert payload["suggestions"][0]["text"] == SAMPLE["suggestions"][0]["text"]


@pytest.mark.asyncio
async def test_offline_model_outputs_parseable_json() -> None:
    """离线降级必须与在线模式同构：输出仍是能解析的 JSON。"""
    from langchain_core.messages import HumanMessage

    model = OfflineTalkModel()
    result = await model.ainvoke([HumanMessage(content="[场景: 通用沟通]\n这个事你看着办吧")])
    analysis = parse_analysis(str(result.content))
    assert analysis is not None
    assert len(analysis.suggestions) == 3
    # 关键词规则应识别出「回避」
    assert "回避" in analysis.emotion


@pytest.mark.asyncio
async def test_offline_model_ignores_meta_prefix() -> None:
    """上下文前缀不能污染情绪判断。"""
    from langchain_core.messages import HumanMessage

    model = OfflineTalkModel()
    result = await model.ainvoke([HumanMessage(content="[场景: 职场]\n[说话人: 对方]\n辛苦了，做得不错")])
    analysis = parse_analysis(str(result.content))
    assert analysis is not None
    assert "认可" in analysis.emotion
