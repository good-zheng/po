import asyncio

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agent import EchoChatModel, Orchestrator
from app.main import create_app
from po_agent_core import AgentCoreSettings, AgentRunner, FallbackIntentRouter
from po_agent_core.supervisor.graph import build_supervisor_graph
from po_agent_core.supervisor.state import CoreState


def build_orchestrator_async(**kwargs):
    from app.agent import build_orchestrator

    settings = AgentCoreSettings(
        _env_file=None, checkpointer="memory", llm_api_key="", **kwargs
    )
    return asyncio.run(build_orchestrator(settings))


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app(orchestrator=build_orchestrator_async()))


def drain_until_done(websocket) -> tuple[str, list[dict]]:
    """收帧直到 done：返回 (token 拼接, 全部帧)。"""
    tokens = ""
    frames: list[dict] = []
    while True:
        frame = websocket.receive_json()
        frames.append(frame)
        if frame["type"] == "token":
            tokens += frame["content"]
        elif frame["type"] == "done":
            return tokens, frames
        elif frame["type"] == "error":
            pytest.fail(f"unexpected error frame: {frame}")


def test_chat_streams_tokens_then_done(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "你好"})
        tokens, frames = drain_until_done(websocket)
        assert tokens == "你说的是：你好"
        # 编排事件帧按协议透传：run_started 先于 token，step 携带节点名
        types = [f["type"] for f in frames]
        assert types[0] == "run_started"
        assert "step" in types
        nodes = [f["payload"]["node"] for f in frames if f["type"] == "step" and "node" in f["payload"]]
        assert "chitchat" in nodes


def test_run_started_carries_conversation_id(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "message", "content": "hi", "conversation_id": "conv-42"}
        )
        frame = websocket.receive_json()
        assert frame["type"] == "run_started"
        assert frame["payload"]["thread_id"] == "conv-42"
        drain_until_done(websocket)


def test_chat_pong(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "ping", "content": "1"})
        assert websocket.receive_json() == {"type": "pong", "content": "1", "payload": {}}


def test_chat_invalid_frame_returns_error(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "unknown"})
        frame = websocket.receive_json()
        assert frame["type"] == "error"


def test_chat_disconnect_is_clean(client: TestClient) -> None:
    # The TestClient context exit sends a disconnect and re-raises any
    # unhandled server-side exception, so leaving mid-stream must not fail.
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "hi"})


# ---------- 会话记忆（同 conversation_id 多轮共享 thread 状态） ----------


class HistoryCountModel(BaseChatModel):
    """回显历史消息数：验证 checkpointer 的多轮记忆。"""

    @property
    def _llm_type(self) -> str:
        return "history-count-model"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=f"共{len(messages)}条消息")
                )
            ]
        )


def test_same_conversation_shares_thread_state() -> None:
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    graph = build_supervisor_graph(
        [], FallbackIntentRouter(), HistoryCountModel(), checkpointer=InMemorySaver()
    )
    orchestrator = Orchestrator(
        graph=graph, runner=AgentRunner(timeout_seconds=10), settings=settings
    )
    client = TestClient(create_app(orchestrator=orchestrator))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "message", "content": "第一轮", "conversation_id": "conv-mem"}
        )
        tokens, _ = drain_until_done(websocket)
        assert tokens == "共1条消息"  # 仅本轮 human

        websocket.send_json(
            {"type": "message", "content": "第二轮", "conversation_id": "conv-mem"}
        )
        tokens, _ = drain_until_done(websocket)
        assert tokens == "共3条消息"  # 上一轮 human/ai + 本轮 human


def test_different_conversations_isolated() -> None:
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    graph = build_supervisor_graph(
        [], FallbackIntentRouter(), HistoryCountModel(), checkpointer=InMemorySaver()
    )
    orchestrator = Orchestrator(
        graph=graph, runner=AgentRunner(timeout_seconds=10), settings=settings
    )
    client = TestClient(create_app(orchestrator=orchestrator))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "message", "content": "A", "conversation_id": "conv-a"}
        )
        tokens, _ = drain_until_done(websocket)
        assert tokens == "共1条消息"

        websocket.send_json(
            {"type": "message", "content": "B", "conversation_id": "conv-b"}
        )
        tokens, _ = drain_until_done(websocket)
        assert tokens == "共1条消息"  # 新会话，互不污染


# ---------- interrupt / resume ----------


def build_interrupt_orchestrator() -> Orchestrator:
    builder = StateGraph(CoreState)

    async def confirm(state: CoreState) -> dict:
        value = interrupt({"question": "确认执行？"})
        return {"messages": [AIMessage(content=f"已执行:{value}")]}

    builder.add_node("confirm", confirm)
    builder.add_edge(START, "confirm")
    builder.add_edge("confirm", END)
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    return Orchestrator(
        graph=builder.compile(checkpointer=InMemorySaver()),
        runner=AgentRunner(timeout_seconds=10),
        settings=settings,
    )


def test_interrupt_then_resume_flow() -> None:
    client = TestClient(create_app(orchestrator=build_interrupt_orchestrator()))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "message", "content": "执行", "conversation_id": "conv-int"}
        )
        frames = []
        while True:
            frame = websocket.receive_json()
            frames.append(frame)
            if frame["type"] == "interrupt":
                break
        assert frame["content"] == "确认执行？"
        # interrupt 后本次 run 以 done 收尾（线程挂起而非结束），
        # 必须先消费完 run1 的帧再 resume，否则 done 会混入 run2
        tokens, _ = drain_until_done(websocket)
        assert tokens == ""

        websocket.send_json(
            {"type": "resume", "content": "yes", "conversation_id": "conv-int"}
        )
        tokens, resumed = drain_until_done(websocket)
        assert tokens == "已执行:yes"
        assert all(f["type"] != "interrupt" for f in resumed)


def test_resume_without_conversation_id_is_invalid(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "resume", "content": "yes"})
        frame = websocket.receive_json()
        assert frame["type"] == "error"


# ---------- 编排降级链 ----------


def test_build_orchestrator_falls_back_to_echo_model() -> None:
    orchestrator = build_orchestrator_async()
    assert "chitchat" in orchestrator.graph.nodes  # graph 可用
    assert orchestrator.settings.checkpointer == "memory"


def test_echo_model_replies_last_user_message() -> None:
    from langchain_core.messages import HumanMessage

    reply = EchoChatModel().invoke([HumanMessage(content="回显我")])
    assert reply.content == "你说的是：回显我"
