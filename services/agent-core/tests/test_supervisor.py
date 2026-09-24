"""Supervisor graph 工厂测试（FakeListChatModel + stub 路由，全离线）。"""

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from po_agent_core.agents.slots import VerticalAgent, VerticalAgentError
from po_agent_core.routing.router import RouteDecision
from po_agent_core.supervisor.graph import build_supervisor_graph
from po_agent_core.supervisor.state import CoreState


class StubRouter:
    """固定决策的桩路由器：按最后一条用户消息文本查 decisions 表。"""

    def __init__(self, decisions: dict[str, RouteDecision]) -> None:
        self._decisions = decisions
        self.seen: list[str] = []

    def route(self, text: str) -> RouteDecision:
        self.seen.append(text)
        return self._decisions.get(text, RouteDecision(intent=None, score=0.0, source="stub"))


def build_echo_agent(name: str = "echo") -> VerticalAgent:
    builder = StateGraph(CoreState)

    async def echo(state: CoreState) -> dict:
        last = state["messages"][-1].content
        return {
            "messages": [AIMessage(content=f"echo:{last}")],
            "artifacts": {name: {"ran": True}},
        }

    builder.add_node("run", echo)
    builder.add_edge(START, "run")
    builder.add_edge("run", END)
    return VerticalAgent(
        name=name, description="回显测试 Agent", graph=builder.compile()
    )


def build_graph(router: StubRouter, agents=None):
    return build_supervisor_graph(
        agents if agents is not None else [build_echo_agent()],
        router,
        FakeListChatModel(responses=["我是闲聊回复"]),
    )


async def test_delegates_to_vertical_agent() -> None:
    router = StubRouter({"写一首诗": RouteDecision("echo", 5.0, "stub")})
    graph = build_graph(router)
    state = await graph.ainvoke({"messages": [HumanMessage(content="写一首诗")]})

    assert state["intent"] == "echo"
    assert state["agent_name"] == "echo"
    assert state["route_score"] == 5.0
    assert state["messages"][-1].content == "echo:写一首诗"
    assert state["artifacts"] == {"echo": {"ran": True}}
    assert router.seen == ["写一首诗"]


async def test_falls_back_to_chitchat_when_intent_missing() -> None:
    router = StubRouter({})
    graph = build_graph(router)
    state = await graph.ainvoke({"messages": [HumanMessage(content="早上好")]})

    assert state["intent"] == ""
    assert state["agent_name"] == "chitchat"
    assert state["messages"][-1].content == "我是闲聊回复"
    # 通道默认值为空 dict：断言 chitchat 未写入任何 artifacts
    assert not state.get("artifacts")


async def test_unknown_intent_goes_to_chitchat() -> None:
    # intent 命中了不存在的 Agent 名 → 兜底，不允许路由到未注册节点
    router = StubRouter({"早上好": RouteDecision("ghost", 5.0, "stub")})
    graph = build_graph(router)
    state = await graph.ainvoke({"messages": [HumanMessage(content="早上好")]})
    assert state["messages"][-1].content == "我是闲聊回复"


async def test_multiple_agents_route_independently() -> None:
    router = StubRouter(
        {
            "A": RouteDecision("agent_a", 5.0, "stub"),
            "B": RouteDecision("agent_b", 5.0, "stub"),
        }
    )
    graph = build_graph(router, agents=[build_echo_agent("agent_a"), build_echo_agent("agent_b")])
    state = await graph.ainvoke({"messages": [HumanMessage(content="B")]})
    assert state["messages"][-1].content == "echo:B"
    assert state["artifacts"] == {"agent_b": {"ran": True}}


def test_duplicate_agent_names_rejected() -> None:
    router = StubRouter({})
    with pytest.raises(VerticalAgentError, match="名称重复"):
        build_graph(router, agents=[build_echo_agent(), build_echo_agent()])


def test_reserved_node_names_rejected() -> None:
    router = StubRouter({})
    agent = build_echo_agent("chitchat")
    with pytest.raises(VerticalAgentError, match="保留节点名"):
        build_graph(router, agents=[agent])


def test_vertical_agent_contract_validation() -> None:
    compiled = build_echo_agent().graph
    with pytest.raises(VerticalAgentError):
        VerticalAgent(name="", description="d", graph=compiled)
    with pytest.raises(VerticalAgentError):
        VerticalAgent(name="__proto", description="d", graph=compiled)
    with pytest.raises(VerticalAgentError):
        VerticalAgent(name="ok", description="", graph=compiled)
    with pytest.raises(VerticalAgentError):
        VerticalAgent(name="ok", description="d", graph="not-a-graph")  # type: ignore[arg-type]


def test_vertical_agent_utterances_validation() -> None:
    compiled = build_echo_agent().graph
    with pytest.raises(VerticalAgentError, match="空语料"):
        VerticalAgent(
            name="ok", description="d", graph=compiled, utterances=("写一首诗", "  ")
        )
    agent = VerticalAgent(
        name="ok", description="d", graph=compiled, utterances=("写一首诗",)
    )
    assert agent.utterances == ("写一首诗",)
    # 缺省：不参与意图路由
    assert build_echo_agent().utterances == ()
