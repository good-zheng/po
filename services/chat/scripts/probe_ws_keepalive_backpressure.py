"""探针：长 run 期间「入站帧没人收」会不会把连接拖死。

现象（2026-10-12 的事故）：管理端创作台写第四章，每一次都在 open 之后恰好 60 秒
断开，前端只有「生成连接已断开：这一轮停在了中断处」而没有 error 帧。四条失败连接
在 chat.log 里都是 ``WebSocketDisconnect code=1006``，而 Redis checkpoint 时间轴证明
图真的在跑（最后一跳落在断连前 2 秒）。

机制（uvicorn 0.54 的 websockets-sansio 实现，``websockets_sansio_impl.py:290-300,
551-556``）：``handle_text()`` 把一条消息塞进 ASGI 队列后立刻 ``pause_reading()``，
只有应用再次 ``receive()`` 且队列空了才 ``resume_reading()``。于是「服务端在发事件、
没空 receive」时，客户端的心跳帧会永远躺在队列里，读通道被背压关死；服务端随后发出
的保活 ping 等不到 PONG（PONG 也得靠同一条读通道进来），``ws_ping_timeout``（默认
20 秒）到期 → ``conn.fail(1011, "keepalive ping timeout")`` → TCP 直接关掉、没有关闭
握手。心跳帧最早在 +30s 进队，断连于是稳定发生在 +60s。

本探针把这三件事分开验：
1. **默认参数**（心跳 30 秒 + 长跑 75 秒）：修复前必炸，修复后应收到 done；
2. ``--no-heartbeat``：长跑期间客户端一帧都不发 —— 用来证明「有入站帧才会卡死」；
3. ``--server-ping-timeout 300``：把服务端保活窗口抬到心跳之上 —— 这是**止血带**，
   它能活着，但读通道依旧停着（下一帧业务数据仍然进不来），所以不是修复。

用法（cwd 必须是 services/chat，全程离线：桩编排器、不联网、不打模型）：
    .venv/Scripts/python.exe -X utf8 scripts/probe_ws_keepalive_backpressure.py
    .venv/Scripts/python.exe -X utf8 scripts/probe_ws_keepalive_backpressure.py --no-heartbeat
    .venv/Scripts/python.exe -X utf8 scripts/probe_ws_keepalive_backpressure.py --server-ping-timeout 300

退出码：0=长跑正常收尾（收到 done），1=连接被撕或挂到上限仍没收到 done。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from collections.abc import AsyncIterator

import uvicorn
import websockets

import app.main as main_module
from app.config import get_settings
from app.main import create_app
from po_agent_core.events import AgentEvent, EventType

PORT = 5098
DEFAULT_TOTAL = 75.0
DEFAULT_BEAT = 30.0
DEFAULT_CLIENT_LIMIT = 120.0


class SlowOrchestrator:
    """只用来占住 ws.py 的流式分支：静默跑 ``total`` 秒再收尾，不碰图、不碰模型。

    刻意一个事件都不发：真实的「写一章」中间就是几十秒没有任何帧（模型在出正文之前
    图上没有节点完成），这正是主循环长时间不 ``receive()`` 的形态。
    """

    def __init__(self, total: float, settings) -> None:
        self.total = total
        self.settings = settings

    async def run(self, *_args, **_kwargs) -> AsyncIterator[AgentEvent]:
        yield AgentEvent(
            type=EventType.RUN_STARTED, content="", payload={"thread_id": "probe-backpressure"}
        )
        await asyncio.sleep(self.total)
        yield AgentEvent(type=EventType.STEP, content="本章写完", payload={"node": "write"})
        yield AgentEvent(type=EventType.RUN_FINISHED, content="", payload={})

    async def resume(self, conversation_id: str, _value: str) -> AsyncIterator[AgentEvent]:
        async for event in self.run():
            yield event

    async def aclose(self) -> None:
        pass


def keep_injected_orchestrator() -> None:
    """让 lifespan 不要覆盖注入的桩编排器（否则探针跑的是真模型，白烧额度）。"""

    async def _aenter(self) -> None:  # noqa: ANN001 - 与 lifespan 同签名
        self.orchestrator = self.app.state.orchestrator

    main_module.AppLifespan.__aenter__ = _aenter


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--total", type=float, default=DEFAULT_TOTAL, help="桩长跑的秒数")
    parser.add_argument(
        "--beat", type=float, default=DEFAULT_BEAT, help="客户端应用层心跳间隔（秒）"
    )
    parser.add_argument(
        "--no-heartbeat", action="store_true", help="长跑期间客户端一帧都不发"
    )
    parser.add_argument(
        "--server-ping-timeout",
        type=float,
        default=None,
        help="覆盖 uvicorn 的 ws_ping_timeout（止血带对照用）",
    )
    args = parser.parse_args()
    beat = None if args.no_heartbeat else args.beat

    keep_injected_orchestrator()
    app = create_app(orchestrator=SlowOrchestrator(args.total, get_settings()))
    extra = {} if args.server_ping_timeout is None else {"ws_ping_timeout": args.server_ping_timeout}
    config = uvicorn.Config(
        app, host="127.0.0.1", port=PORT, log_level="warning", access_log=False, **extra
    )
    server = uvicorn.Server(config)
    serve_task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.05)

    limit = max(args.total, beat or 0.0) + DEFAULT_CLIENT_LIMIT / 2
    started = time.monotonic()
    frames: list[str] = []
    outcome = "未收尾"
    try:
        # 复刻浏览器形状：客户端不主动发 WS 控制 ping（ping_interval=None），
        # 只每 30 秒发一帧应用层 JSON 心跳——与管理端 useNovelRun 完全一致。
        async with websockets.connect(
            f"ws://127.0.0.1:{PORT}/ws/chat",
            open_timeout=10,
            ping_interval=None,
            ping_timeout=None,
        ) as ws:
            # 不带 bookId：帧级闸门只拦「带书的续写帧」，这里要测的是流式分支本身
            await ws.send(json.dumps({"type": "message", "content": "写第四章", "agent": "novel"}))

            async def reader() -> None:
                nonlocal outcome
                async for raw in ws:
                    frame = json.loads(raw)
                    now = time.monotonic() - started
                    frames.append(f"+{now:.1f}s {frame['type']}")
                    if frame["type"] == "done":
                        outcome = "收到 done，长跑正常收尾"
                        return
                    if frame["type"] == "error":
                        outcome = f"收到 error：{frame.get('content')}"
                        return

            async def beater() -> None:
                while True:
                    await asyncio.sleep(beat)
                    await ws.send(json.dumps({"type": "ping", "content": "beat"}))

            reader_task = asyncio.create_task(reader())
            watch_dog = asyncio.create_task(asyncio.sleep(limit))
            beater_task = asyncio.create_task(beater()) if beat else None
            targets = {reader_task, watch_dog}
            if beater_task is not None:
                targets.add(beater_task)
            finished, pending = await asyncio.wait(targets, return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
            if reader_task in pending:
                outcome = f"挂满 {limit:.0f}s 连接仍在（没收到 done）"
            elif reader_task in finished:
                exc = reader_task.exception()
                if exc is not None:
                    outcome = (
                        f"+{time.monotonic() - started:.1f}s 读通道异常 "
                        f"{type(exc).__name__}: {exc}"
                    )
                elif outcome == "未收尾":
                    outcome = "读通道自然结束（服务端关了连接，没收到 done）"
    finally:
        server.should_exit = True
        await serve_task

    print(f"长跑={args.total}s 心跳={'关' if beat is None else f'{beat}s'} "
          f"服务端 ws_ping_timeout={args.server_ping_timeout or '默认(20s)'}")
    print(f"客户端帧序列：{frames}")
    print(f"结论：{outcome}")
    return 0 if outcome.startswith("收到 done") else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
