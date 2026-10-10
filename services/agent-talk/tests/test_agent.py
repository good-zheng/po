"""插槽装配的契约测试。

重点不是模型效果，而是「宿主拿到的确实是一个合规的 VerticalAgent」：
名称、描述、已编译子图、路由语料缺一不可，否则 supervisor 会在装配期抛错。
"""

from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from po_agent_core import AgentCoreSettings, VerticalAgent
from po_agent_talk import (
    TALK_AGENT_NAME,
    TALK_DESCRIPTION,
    TALK_ROLE,
    TALK_UTTERANCES,
    build_talk_agent,
)


def test_build_talk_agent_contract() -> None:
    """缺 API Key 时也应装配成功（降级离线模型），断言的是契约而非模型。"""
    agent = build_talk_agent(AgentCoreSettings())
    assert isinstance(agent, VerticalAgent)
    assert agent.name == TALK_AGENT_NAME
    assert agent.name == "talk"
    assert agent.description == TALK_DESCRIPTION
    assert isinstance(agent.graph, CompiledStateGraph)
    # 语料为空则该 Agent 完全不参与意图路由
    assert len(agent.utterances) == len(TALK_UTTERANCES) > 0
    assert agent.metadata["role"] == TALK_ROLE


def test_utterances_cover_three_intents() -> None:
    """语料要覆盖「他什么意思 / 我怎么回 / 帮我分析」三类说法。"""
    joined = " ".join(TALK_UTTERANCES)
    assert "什么意思" in joined
    assert "怎么回" in joined or "怎么回复" in joined
    assert "潜台词" in joined or "暗示" in joined
