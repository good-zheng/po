"""长跑期间「读通道必须一直开着」的回归用例。

为什么要有这一支：2026-10-12 管理端「写第四章」每次都失败，chat.log 里全是
「open 之后恰好 60 秒 WebSocketDisconnect code=1006」。根因不在模型也不在反代——
uvicorn 0.54 的 websockets-sansio 实现把一条消息交给应用之后就 ``pause_reading()``，
只有应用再次 ``receive()`` 且队列为空才恢复读。旧版 ``_loop`` 在发事件的那几分钟里
没人再调用 ``receive()``，于是客户端每 30 秒一发的心跳帧永远躺在队列里、读通道被
背压关死，服务端自己发出的 keepalive ping 等不到 PONG，20 秒后以 1011
``keepalive ping timeout`` 撕掉这条还在正常生成的连接（非 1000 关闭码 = 前端只看得见
「生成连接已断开」，没有任何 error 帧）。

``_loop`` 现在把「读」交给常驻泵任务，所以这里断言的是**每个事件发出时都还有人挂在
receive 上**（采样值 ≥ 1），而不是打 uvicorn 的内部。端到端那一层由
``scripts/probe_ws_keepalive_backpressure.py`` 在真实 uvicorn 栈上复核：默认保活参数下
旧代码在 +60s 被 1011 关掉，新代码能收到 ``done``。

顺带锁住两件事：泵不改变协议时序（本轮仍旧一路发到 ``done`` 才处理排队的 ping），
以及主循环退出时不留下僵尸读任务。
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.config import get_settings
from app.routers.ws import _loop
from po_agent_core.events import AgentEvent, EventType

MESSAGE_FRAME = {"type": "message", "content": "写第四章", "agent": "novel"}
PING_FRAME = {"type": "ping", "content": "beat"}


class RecordingSocket:
    """只实现 ``_loop`` 用到的 receive/send，并记录「此刻有没有人挂在 receive 上」。"""

    def __init__(self, inbound: list[dict[str, Any]]) -> None:
        self._inbound = list(inbound)
        self.sent: list[dict[str, Any]] = []
        self.parked = 0
        self.receive_calls = 0

    async def receive_json(self) -> dict[str, Any]:
        self.receive_calls += 1
        if self._inbound:
            return self._inbound.pop(0)
        # 无帧可读时才叫「挂着等」：这一头挂住，ASGI 侧才处于 resume_reading 状态
        self.parked += 1
        try:
            await asyncio.sleep(3600)
        finally:
            self.parked -= 1
        raise AssertionError("不可达：sleep 只会被 cancel")

    async def send_json(self, payload: dict[str, Any]) -> None:
        self.sent.append(payload)


class SlowOrchestrator:
    """桩编排器：每两个事件之间让出一次事件循环，并在那一刻采样读通道状态。"""

    def __init__(self, socket: RecordingSocket) -> None:
        self.socket = socket
        self.samples: list[int] = []
        self.settings = get_settings()

    async def run(
        self,
        _text: str,
        *,
        conversation_id: str | None = None,
        **_kwargs: Any,
    ) -> AsyncIterator[AgentEvent]:
        yield AgentEvent(type=EventType.RUN_STARTED, content="", payload={"thread_id": conversation_id})
        for index in range(3):
            await asyncio.sleep(0.01)
            self.samples.append(self.socket.parked)
            yield AgentEvent(type=EventType.STEP, content=f"第 {index + 1} 段", payload={"node": "write"})
        yield AgentEvent(type=EventType.RUN_FINISHED, content="", payload={})

    async def resume(self, conversation_id: str, _value: str) -> AsyncIterator[AgentEvent]:
        async for event in self.run("", conversation_id=conversation_id):
            yield event


async def _drive(inbound: list[dict[str, Any]]) -> tuple[RecordingSocket, SlowOrchestrator]:
    socket = RecordingSocket(inbound)
    orchestrator = SlowOrchestrator(socket)
    loop_task = asyncio.create_task(_loop(socket, orchestrator, None))  # type: ignore[arg-type]
    try:
        for _ in range(500):
            await asyncio.sleep(0.01)
            types = [frame.get("type") for frame in socket.sent]
            if "done" in types and "pong" in types:
                break
    finally:
        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass
    return socket, orchestrator


def _types(socket: RecordingSocket) -> list[str]:
    return [str(frame.get("type")) for frame in socket.sent]


def test_reader_stays_parked_while_a_run_is_streaming() -> None:
    """证伪点：旧版 ``_loop`` 在 ``async for event`` 期间没人 receive，采样全是 0。"""

    async def scenario() -> None:
        socket, orchestrator = await _drive([MESSAGE_FRAME, PING_FRAME])
        assert _types(socket)[0] == "run_started"
        assert orchestrator.samples, "桩编排器没采样到任何事件"
        assert all(sample >= 1 for sample in orchestrator.samples), (
            f"发事件时读通道没人挂着（采样={orchestrator.samples}）。uvicorn 会在投完一条"
            "消息后 pause_reading，对端的 PONG 于是读不到，20 秒后 keepalive ping timeout "
            "以 1011 撕掉这条还在生成的连接"
        )
        # message 与 ping 都要被吃掉，之后还有一次「挂着等」的 receive
        assert socket.receive_calls >= 3

    asyncio.run(scenario())


def test_pump_keeps_serial_frames_and_answers_queued_ping_after_done() -> None:
    """协议时序不变：本轮照旧发到 done 为止，排队的心跳在 done 之后才被回。"""

    async def scenario() -> None:
        socket, _orchestrator = await _drive([MESSAGE_FRAME, PING_FRAME])
        assert _types(socket) == ["run_started", "step", "step", "step", "done", "pong"]

    asyncio.run(scenario())


def test_loop_exit_cancels_the_pump() -> None:
    """主循环退出时收掉泵：还挂在 ``receive()`` 上就是随连接泄漏的僵尸读任务。

    泵平时靠挂在 receive 上让读通道保持打开（这正是修复本身），所以连接结束后必须
    由 ``_loop`` 的 ``finally`` 取消它——否则每条关掉的连接都留下一个活任务，而它引用的
    socket 永远回收不了。
    """

    async def scenario() -> None:
        socket, _orchestrator = await _drive([MESSAGE_FRAME, PING_FRAME])
        for _ in range(5):
            await asyncio.sleep(0)  # 让泵任务的取消善后跑完（parked 减一发生在它的 finally 里）
        assert socket.parked == 0, f"主循环退出后仍有人挂在 receive 上（parked={socket.parked}）"

    asyncio.run(scenario())
