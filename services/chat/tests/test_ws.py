import asyncio

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.agent import EchoChatModel, Orchestrator
from app.main import create_app
from po_agent_core import (
    AgentCoreSettings,
    AgentRunner,
    FallbackIntentRouter,
    VerticalAgent,
)
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


# ---------- 点名插槽的那轮 interrupt，必须能在同一条 WS 上确认 ----------


def build_agent_slot_orchestrator() -> Orchestrator:
    """一张「子图内 interrupt」的插槽，复刻 novel 归档确认的装配形状。

    关键是 ``builder.compile()`` **不挂 checkpointer**：生产里 novel / novel-chat 就
    是这样，saver 由父图统一供给。路由用 :class:`FallbackIntentRouter`（恒判未命中），
    于是「这一轮真的走到了插槽」无从靠相似度蒙对——只有 ``forced_agent`` 那条确定性
    委托能到达 interrupt。
    """
    builder = StateGraph(CoreState)

    async def archive(state: CoreState) -> dict:
        value = interrupt({"question": "确认归档？"})
        return {"messages": [AIMessage(content=f"已归档:{value}")]}

    builder.add_node("archive", archive)
    builder.add_edge(START, "archive")
    builder.add_edge("archive", END)
    slot = VerticalAgent(name="novel", description="生成链路探针", graph=builder.compile())
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    graph = build_supervisor_graph(
        [slot], FallbackIntentRouter(), EchoChatModel(), checkpointer=InMemorySaver()
    )
    return Orchestrator(
        graph=graph,
        runner=AgentRunner(timeout_seconds=10),
        settings=settings,
        agents={slot.name: slot},
    )


def test_agent_frame_interrupt_resumes_on_the_same_socket() -> None:
    """message 带 ``agent`` 起的那轮 interrupt，只带 conversation_id 的 resume 就得确认。

    浏览器里的「确认归档」正是这一帧序列（`useNovelRun`：message 带 agent、resume 不带
    agent）。此前 run 直连子图、resume 打回父图，两边不是同一份 checkpoint，卡片永远点
    不动，所以这条用例同时锁两件事：委托的确定性，与 run/resume 的图对称性。
    """
    client = TestClient(create_app(orchestrator=build_agent_slot_orchestrator()))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "写完三章", "agent": "novel"})
        frames = []
        while True:
            frame = websocket.receive_json()
            frames.append(frame)
            if frame["type"] == "interrupt":
                break
        assert frame["content"] == "确认归档？"
        thread_id = next(
            f["payload"]["thread_id"] for f in frames if f["type"] == "run_started"
        )
        # interrupt 之后本轮仍要消费到 done，resume 才发得出去（服务端逐条 await 发送）
        drain_until_done(websocket)

        websocket.send_json(
            {"type": "resume", "content": "yes", "conversation_id": thread_id}
        )
        tokens, resumed = drain_until_done(websocket)
        assert tokens == "已归档:yes"
        assert all(f["type"] != "interrupt" for f in resumed)


def test_agent_frame_never_reaches_chitchat() -> None:
    """同一个 orchestrator 不传 agent 时落 chitchat（回显模型），传了才进插槽。

    和上一条配对：证明委托确实由 `agent` 决定，而不是这张图本来就只有一条路。
    """
    client = TestClient(create_app(orchestrator=build_agent_slot_orchestrator()))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "写完三章"})
        tokens, frames = drain_until_done(websocket)

    assert tokens == "你说的是：写完三章"
    assert all(f["type"] != "interrupt" for f in frames)


# ---------- 续写帧必须有握手身份（带 bookId 的 novel 帧） ----------


def test_continue_frame_without_actor_is_refused_before_the_graph() -> None:
    """匿名连接上「续写这本书」这一帧不进图：只回一条 error，且没有 run_started。

    ``bookId`` 是客户端带来的既有书目，链路会照它读回正典与已定稿正文、最后按章
    **追加写回同一本书**；而匿名连接不带 ``X-Actor-Uid``，Java 侧的归属校验整段跳过
    （只验 ``X-Internal-Token``）。放行等于让任意能连上 ``/ws/chat`` 的对等方往别人的
    书里塞一章。新建书那条路径不受影响——它读不出任何人的数据。
    """
    client = TestClient(create_app(orchestrator=build_agent_slot_orchestrator()))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "content": "开始创作第三至第十章的内容",
                "agent": "novel",
                "context": {"bookId": "12", "auto": True},
            }
        )
        frame = websocket.receive_json()
        assert frame["type"] == "error"
        assert "身份" in frame["content"]
        # 闸门只拦这一帧、不关整条连接：心跳仍要得到回应
        websocket.send_json({"type": "ping"})
        assert websocket.receive_json()["type"] == "pong"


def test_continue_frame_with_actor_reaches_the_slot(monkeypatch) -> None:
    """同一帧带票且校验通过就进插槽：闸门认的是身份，不是 agent 名。

    验票本身由 ``test_ws_handshake.py`` 负责，这里把 ``resolve_actor`` 替身成「校验通过」，
    要锁的只是「有身份 ⇒ 这一帧放行到编排」。
    """
    from app.routers import ws as ws_router
    from app.ws_auth import WsActor

    async def resolve(ticket, settings=None):
        return WsActor(uid=7)

    monkeypatch.setattr(ws_router, "resolve_actor", resolve)
    client = TestClient(create_app(orchestrator=build_agent_slot_orchestrator()))

    with client.websocket_connect("/ws/chat?ticket=t-ok") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "content": "开始创作第三至第十章的内容",
                "agent": "novel",
                "context": {"bookId": "12", "auto": True},
            }
        )
        assert websocket.receive_json()["type"] == "run_started"


# ---------- 编排降级链 ----------


def test_build_orchestrator_falls_back_to_echo_model() -> None:
    orchestrator = build_orchestrator_async()
    assert "chitchat" in orchestrator.graph.nodes  # graph 可用
    assert orchestrator.settings.checkpointer == "memory"


def test_echo_model_replies_last_user_message() -> None:
    from langchain_core.messages import HumanMessage

    reply = EchoChatModel().invoke([HumanMessage(content="回显我")])
    assert reply.content == "你说的是：回显我"


# ---------- 设定提议卡帧（§10.3 约定 1） ----------


def build_proposal_orchestrator() -> Orchestrator:
    """一张自定义事件 → 一帧 ``proposal``：未登记的事件类型会被翻译层静默丢弃。

    这条用例锁的是三处必须同时改到位的契约（``EventType`` / ``WSOutFrame.type``
    Literal / ``_EVENT_TO_FRAME``）——少改任一处，前端不会报错，只会永远收不到卡。
    """
    builder = StateGraph(CoreState)

    async def propose(state: CoreState) -> dict:
        get_stream_writer()(
            {
                "type": "proposal",
                "content": "char:hero · eye_color · 夜里会变成金色",
                "payload": {"bookId": 12, "asOfChapter": 3, "validFromChapter": 3},
            }
        )
        return {"messages": [AIMessage(content="已给出讨论结论")]}

    builder.add_node("propose", propose)
    builder.add_edge(START, "propose")
    builder.add_edge("propose", END)
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    return Orchestrator(
        graph=builder.compile(checkpointer=InMemorySaver()),
        runner=AgentRunner(timeout_seconds=10),
        settings=settings,
    )


def test_proposal_event_reaches_the_client_as_a_frame() -> None:
    client = TestClient(create_app(orchestrator=build_proposal_orchestrator()))

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "聊聊主角"})
        frames = []
        while True:
            frame = websocket.receive_json()
            frames.append(frame)
            if frame["type"] == "done":
                break
        card = [f for f in frames if f["type"] == "proposal"]
        assert len(card) == 1
        # payload 原样透传：字段名即 Java ProposalRequest，前端不需要翻译表
        assert card[0]["payload"] == {"bookId": 12, "asOfChapter": 3, "validFromChapter": 3}


# ---------- 定位键通道：configurable 而不是提示词前缀 ----------


def build_probe_orchestrator() -> tuple[Orchestrator, dict]:
    """直连插槽的探针：记录模型实际收到的文本与 ``configurable.context``。"""
    builder = StateGraph(CoreState)
    seen: dict = {}

    async def probe(state: CoreState, config) -> dict:
        seen["text"] = state["messages"][-1].content
        seen["context"] = (config.get("configurable") or {}).get("context")
        return {"messages": [AIMessage(content="ok")]}

    builder.add_node("probe", probe)
    builder.add_edge(START, "probe")
    builder.add_edge("probe", END)
    compiled = builder.compile(checkpointer=InMemorySaver())
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    slot = VerticalAgent(name="novel-chat", description="探针插槽", graph=compiled)
    orchestrator = Orchestrator(
        graph=compiled,
        runner=AgentRunner(timeout_seconds=10),
        settings=settings,
        agents={slot.name: slot},
    )
    return orchestrator, seen


def test_reserved_context_keys_never_reach_the_prompt(monkeypatch) -> None:
    """bookId/chapterId 与 utteranceId 同类：只走 configurable，不进模型可见文本。

    「读哪本书」如果以文本形态出现，模型就能复述、作者也能手填一个假 id 去试库读——
    定位必须只由服务端手里的那份帧决定。非保留键（theme）仍按原样拼进前缀，
    这条豁免不能反过来把旧行为改掉。

    续写的四个控制键（fromChapter / chapterCount / auto / tailChapterId）同属保留键：
    「写哪几章」与「要不要问作者」是图的行为参数，让模型在文本里看到一份、图里执行
    另一份，产出就会与承诺分叉。

    握手带票据：novel-chat 是需要身份的插槽（``app/ws_auth.AUTH_REQUIRED_AGENTS``），
    匿名连接上这一帧根本不会进图，测不到上下文通道。验票本身由
    ``test_ws_handshake.py`` 负责，这里只把它替身成「校验通过」。
    """
    from app.routers import ws as ws_router
    from app.ws_auth import WsActor

    async def resolve(ticket, settings=None):
        return WsActor(uid=7)

    monkeypatch.setattr(ws_router, "resolve_actor", resolve)
    orchestrator, seen = build_probe_orchestrator()
    client = TestClient(create_app(orchestrator=orchestrator))

    context = {
        "bookId": "12",
        "chapterId": "34",
        "utteranceId": "u-1",
        "fromChapter": "4",
        "chapterCount": "3",
        "auto": True,
        "tailChapterId": "99",
        "theme": "dark",
    }
    with client.websocket_connect("/ws/chat?ticket=t-ok") as websocket:
        websocket.send_json(
            {
                "type": "message",
                "content": "主角的眼睛是什么颜色",
                "agent": "novel-chat",
                "conversation_id": "conv-probe",
                "context": context,
            }
        )
        tokens, _ = drain_until_done(websocket)

    assert tokens == "ok"
    assert seen["context"] == context
    for key in ("bookId", "chapterId", "utteranceId", "fromChapter", "chapterCount", "auto"):
        assert key not in seen["text"]
    assert "[theme: dark]" in seen["text"]
