"""WS 握手票据与作者作用域（PRD §15.13 偏差 #12 的收口）。

分两层测，各锁一个失效形态：

- **单元层**（:func:`app.ws_auth.resolve_actor`）：锁「校验失败还放行」。这一层全部走
  ``httpx.MockTransport``，不发真实请求，也不需要 Spring 在场。
- **协议层**（``/ws/chat``）：锁「身份没接到数据层」和「把别人插槽一起关掉」——
  前者靠图内节点回读 ``current_actor()``，后者靠匿名连接仍能跑 cooking 与心跳。

票据本身由 Java 签也由 Java 验，本文件不测票据内容：那部分契约在
``ChatTicketAndActorScopeTest``（services/api/novel）里钉。
"""

from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from starlette.websockets import WebSocketDisconnect

import app.routers.ws as ws_router
from app.agent import Orchestrator
from app.config import Settings
from app.main import create_app
from app.ws_auth import WsActor, resolve_actor, ticket_from
from po_agent_core import AgentCoreSettings, AgentRunner, VerticalAgent
from po_agent_core.supervisor.state import CoreState

# ── 单元：票据 → 身份 ──────────────────────────────────────────────


def _settings(**overrides: object) -> Settings:
    conf = {"_env_file": None, "api_base_url": "http://backend/api", "internal_token": "tk"}
    return Settings(**{**conf, **overrides})  # type: ignore[arg-type]


def _backend(
    reply: httpx.Response | Exception, calls: list[httpx.Request]
) -> httpx.MockTransport:
    def handle(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        if isinstance(reply, Exception):
            raise reply
        return reply

    return httpx.MockTransport(handle)


def _ok(uid: object) -> httpx.Response:
    return httpx.Response(200, json={"code": 200, "success": True, "data": {"uid": uid}})


def test_ticket_from_reads_query_and_treats_blank_as_missing() -> None:
    assert ticket_from(SimpleNamespace(query_params={"ticket": " t-1 "})) == "t-1"
    # 空串与缺省同义：客户端拼 URL 时很容易留下 `?ticket=`，那不该走「坏票即拒」分支
    assert ticket_from(SimpleNamespace(query_params={"ticket": "  "})) is None
    assert ticket_from(SimpleNamespace(query_params={})) is None


def test_valid_ticket_becomes_an_actor() -> None:
    calls: list[httpx.Request] = []
    actor = asyncio.run(resolve_actor("t-1", _settings(), transport=_backend(_ok(7), calls)))

    assert actor == WsActor(uid=7)
    assert str(calls[0].url) == "http://backend/api/novel/internal/chat-ticket/verify"
    assert calls[0].headers["X-Internal-Token"] == "tk"
    assert json.loads(calls[0].content) == {"ticket": "t-1"}


def test_missing_internal_token_never_calls_the_backend() -> None:
    """没配内网令牌时不留半个请求：novel-chat 拒连，但其余插槽照旧匿名可用。"""
    calls: list[httpx.Request] = []
    settings = _settings(internal_token="")

    assert asyncio.run(resolve_actor("t-1", settings, transport=_backend(_ok(7), calls))) is None
    assert calls == []


def test_business_rejection_is_no_identity() -> None:
    calls: list[httpx.Request] = []
    reply = httpx.Response(200, json={"code": 403, "success": False, "message": "握手票据无效"})

    assert asyncio.run(resolve_actor("t-1", _settings(), transport=_backend(reply, calls))) is None


def test_backend_unreachable_is_no_identity() -> None:
    """后端抖动按「没有身份」处理：把它当「当作匿名继续」等于票据形同虚设。"""
    calls: list[httpx.Request] = []

    assert (
        asyncio.run(
            resolve_actor(
                "t-1", _settings(), transport=_backend(httpx.ConnectError("boom"), calls)
            )
        )
        is None
    )


@pytest.mark.parametrize("uid", ["7", None, True, 1.5])
def test_non_integer_uid_is_no_identity(uid: object) -> None:
    calls: list[httpx.Request] = []

    assert asyncio.run(resolve_actor("t-1", _settings(), transport=_backend(_ok(uid), calls))) is None


# ── 协议：/ws/chat 握手与帧级闸门 ──────────────────────────────────


def build_probe() -> tuple[Orchestrator, dict]:
    """直连插槽的探针：记录图内实际看到的作者身份。

    这里读的是 ``po_agent_novel.current_actor()``——握手与数据层之间唯一的接线就是那个
    contextvar，节点里回读等于端到端验「身份真的跨过了编排层」。
    """
    from po_agent_novel import current_actor

    builder = StateGraph(CoreState)
    seen: dict = {}

    async def probe(state: CoreState) -> dict:
        seen["actor"] = current_actor()
        return {"messages": [AIMessage(content="ok")]}

    builder.add_node("probe", probe)
    builder.add_edge(START, "probe")
    builder.add_edge("probe", END)
    compiled = builder.compile(checkpointer=InMemorySaver())
    slot = VerticalAgent(name="novel-chat", description="探针插槽", graph=compiled)
    orchestrator = Orchestrator(
        graph=compiled,
        runner=AgentRunner(timeout_seconds=10),
        settings=AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key=""),
        agents={slot.name: slot},
    )
    return orchestrator, seen


def _stub_resolve(who: WsActor | None):
    async def resolve(ticket: str | None, settings: Settings | None = None) -> WsActor | None:
        return who if ticket == "t-ok" else None

    return resolve


def _client(orchestrator: Orchestrator) -> TestClient:
    return TestClient(create_app(orchestrator=orchestrator))


def drain(websocket) -> list[dict]:
    frames: list[dict] = []
    while True:
        frame = websocket.receive_json()
        frames.append(frame)
        if frame["type"] in ("done", "error"):
            return frames


def test_anonymous_connection_cannot_start_novel_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator, seen = build_probe()
    monkeypatch.setattr(ws_router, "resolve_actor", _stub_resolve(WsActor(uid=7)))
    client = _client(orchestrator)

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "主角的眼睛", "agent": "novel-chat"})
        frames = drain(websocket)

    assert [f["type"] for f in frames] == ["error"]
    assert "ticket" in frames[0]["content"]
    # 关键断言：闸门在编排之前，探针节点根本没被跑到
    assert seen == {}


def test_anonymous_resume_for_a_named_agent_is_also_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """闸门判的是 ``frame.agent`` 而不是帧类型：带名字的 resume 同样被挡在编排之前。

    反过来说它也管不到「不带 agent 的 resume」（协议里那一栏是可选的），那条缺口
    登记在 PRD §15.16-2，靠这里钉住「只要客户端报了名字就一定拦」。
    """
    orchestrator, seen = build_probe()
    monkeypatch.setattr(ws_router, "resolve_actor", _stub_resolve(WsActor(uid=7)))
    client = _client(orchestrator)

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json(
            {"type": "resume", "content": "确认", "conversation_id": "t-1", "agent": "novel-chat"}
        )
        frames = drain(websocket)

    assert [f["type"] for f in frames] == ["error"]
    assert seen == {}


def test_ticketed_connection_runs_with_the_author_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator, seen = build_probe()
    monkeypatch.setattr(ws_router, "resolve_actor", _stub_resolve(WsActor(uid=7)))
    client = _client(orchestrator)
    with client.websocket_connect("/ws/chat?ticket=t-ok") as websocket:
        websocket.send_json({"type": "message", "content": "主角的眼睛", "agent": "novel-chat"})
        frames = drain(websocket)

    assert frames[-1]["type"] == "done"
    assert seen["actor"] == 7


def test_bad_ticket_is_rejected_at_handshake(monkeypatch: pytest.MonkeyPatch) -> None:
    orchestrator, seen = build_probe()
    monkeypatch.setattr(ws_router, "resolve_actor", _stub_resolve(WsActor(uid=7)))
    client = _client(orchestrator)

    with pytest.raises(WebSocketDisconnect) as raised:
        with client.websocket_connect("/ws/chat?ticket=t-bad"):
            pass

    # TestClient 在收到 accept 之前的 close 时抛这个异常：能拿到它就说明连接从没被接受，
    # 而 4401 是客户端「该去换一张新票」的信号（区别于 1006 那类网络断连）。
    assert raised.value.code == ws_router.HANDSHAKE_REJECTED_CODE
    assert seen == {}


def test_other_slots_stay_anonymous(monkeypatch: pytest.MonkeyPatch) -> None:
    """只强制 novel-chat：cooking 与心跳在匿名连接上照旧，否则现网小程序当场断聊。"""
    orchestrator, seen = build_probe()
    monkeypatch.setattr(ws_router, "resolve_actor", _stub_resolve(WsActor(uid=7)))
    client = _client(orchestrator)

    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "ping", "content": "1"})
        assert websocket.receive_json()["type"] == "pong"

        websocket.send_json({"type": "message", "content": "番茄炒蛋", "agent": "cooking"})
        frames = drain(websocket)

    assert frames[-1]["type"] == "done"
    # 匿名连接绑的是「无身份」，不是某位作者：数据层因此不带 X-Actor-Uid
    assert seen["actor"] is None
