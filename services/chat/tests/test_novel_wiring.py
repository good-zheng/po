"""P5 宿主接线测试：novel 插槽装配 + WS 帧协议对小说链路的透传。

- 装配：``build_orchestrator()`` 默认注册 novel 插槽；``agents=[]`` 显式
  不装配；
- 端到端：NovelOnlyRouter 把消息固定路由到 novel，经 WS 帧驱动
  构思→大纲→生成→interrupt 归档确认→resume 入库（离线模型，零网络）。
"""

import asyncio

from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import InMemorySaver

from app.agent import EchoChatModel, Orchestrator, build_orchestrator
from app.main import create_app
from po_agent_core import AgentCoreSettings, AgentRunner, RouteDecision
from po_agent_core.supervisor.graph import build_supervisor_graph


def _settings() -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")


class NovelOnlyRouter:
    """恒路由到 novel：路由决策本身在 agent-core/agent-novel 侧已覆盖。"""

    def route(self, text: str) -> RouteDecision:
        return RouteDecision(intent="novel", score=1.0, source="test")


def _build_async(**kwargs):
    return asyncio.run(build_orchestrator(_settings(), **kwargs))


# ---------- 装配 ----------


def test_default_orchestrator_registers_novel_slot() -> None:
    orchestrator = _build_async()
    assert "novel" in orchestrator.graph.nodes
    assert "chitchat" in orchestrator.graph.nodes


def test_explicit_empty_agents_skips_builtin_slots() -> None:
    orchestrator = _build_async(agents=[])
    assert "novel" not in orchestrator.graph.nodes
    assert "chitchat" in orchestrator.graph.nodes


# ---------- WS 端到端：novel 全链路帧协议 ----------


def _novel_orchestrator() -> Orchestrator:
    from po_agent_novel import build_novel_agent

    agent = build_novel_agent(_settings())
    graph = build_supervisor_graph(
        [agent],
        NovelOnlyRouter(),
        EchoChatModel(),
        checkpointer=InMemorySaver(),
    )
    return Orchestrator(
        graph=graph, runner=AgentRunner(timeout_seconds=30), settings=_settings()
    )


def test_ws_novel_chain_interrupt_and_archive() -> None:
    client = TestClient(create_app(orchestrator=_novel_orchestrator()))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "message", "content": "帮我写一本玄幻小说", "conversation_id": "nov-1"}
        )

        stages: list[str] = []
        interrupt_frame = None
        while True:
            frame = websocket.receive_json()
            if frame["type"] in ("thinking", "plan") and "stage" in frame["payload"]:
                stages.append(frame["payload"]["stage"])
            if frame["type"] == "interrupt":
                interrupt_frame = frame
                break
        assert "conceived" in stages
        assert "outlined" in stages
        assert interrupt_frame["payload"]["value"]["title"]

        # run1 在 interrupt 后以 done 收尾（线程挂起），先 drain 再 resume
        tail = []
        while True:
            frame = websocket.receive_json()
            tail.append(frame["type"])
            if frame["type"] == "done":
                break
        assert "token" not in tail  # 归档前不产出正文 token

        websocket.send_json(
            {"type": "resume", "content": "yes", "conversation_id": "nov-1"}
        )
        tokens = ""
        resumed_types = []
        while True:
            frame = websocket.receive_json()
            resumed_types.append(frame["type"])
            if frame["type"] == "token":
                tokens += frame["content"]
            elif frame["type"] == "done":
                break
        assert "已归档入库" in tokens
        assert "第1章" in tokens
        assert "interrupt" not in resumed_types


def test_default_orchestrator_routes_novel_without_embedding() -> None:
    """无 embedding/LLM key 的默认装配下，关键词降级路由仍能把小说意图
    送进 novel 离线链路（P5 验收：降级环境垂直 Agent 不失效）。"""
    orchestrator = _build_async()  # 默认装配：novel 插槽 + 关键词降级路由
    client = TestClient(create_app(orchestrator=orchestrator))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "message", "content": "帮我写一本玄幻小说", "conversation_id": "nov-2"}
        )
        nodes = []
        while True:
            frame = websocket.receive_json()
            if frame["type"] == "step" and "node" in frame["payload"]:
                nodes.append(frame["payload"]["node"])
            if frame["type"] == "interrupt":
                break
        # subgraphs=True 透传子图节点 step：novel 链路在跑即路由命中
        assert "conceive" in nodes
        assert "chitchat" not in nodes
