"""端到端长跑探针：真模型、真图、真 WS 栈，一次「写三章」能不能活着收尾。

**消耗真实模型额度**（DeepSeek 出稿），所以只在作者要求时跑；默认关掉落库
（`NOVEL_PERSIST_ENABLED=false`，探针不往任何一本书里写东西）。

它补的是两条修复各自够不到的那一半：

- `_pump_inbound`（`app/routers/ws.py`）：真实 uvicorn 的「投一条消息就 `pause_reading()`」
  只有真 WS 栈能测，`scripts/probe_ws_keepalive_backpressure.py` 用桩事件流测的就是这一层；
- 每轮预算（`app/agent.py` 的 `_RUN_BUDGET_BY_AGENT`）：「一次 3 章实测 322 秒」这个数是
  真跑出来的，桩不能替模型出稿。

两条必须在同一条链路上一起跑完，因为 60 秒那一刀修好之后，下一个可能掐断长跑的就是
「预算到期」——而这一层历史上从没被观察到：每一次尝试都在 60 秒就断了，没人看到过
第四分钟。

用法（cwd 必须是 services/chat）：
    .venv/Scripts/python.exe -X utf8 scripts/probe_ws_long_run.py
    .venv/Scripts/python.exe -X utf8 scripts/probe_ws_long_run.py --idea "…" --beat 30

端口默认 5091（避开开发用的 5090）。新书的章数由插槽装配决定（默认 3 章 / 每章 1200 字）。
退出码：0=收到 `done` 且全程没有 `error` 帧；1=其它任何收尾（被撕、超时、报错）。
输出只有帧类型、时间戳与正文摘要，不含任何密钥或票据。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time
from collections.abc import AsyncIterator

import uvicorn
import websockets

os.environ.setdefault("NOVEL_PERSIST_ENABLED", "false")

import app.main as main_module
from app.agent import build_orchestrator
from app.main import create_app

PORT = 5091
DEFAULT_IDEA = "一个修补匠发现自己补的是别人的人生，写出前三章"
DEFAULT_LIMIT = 900.0


def keep_injected_orchestrator() -> None:
    """让 lifespan 复用已经在跑的编排器，而不是 lifespan 里再造一个。

    这里注入的就是 `build_orchestrator()` 的产物（真模型、真 Redis checkpointer），
    接管只是为了让装配发生一次、并在探针退出时由本脚本负责 `aclose()`。
    """

    async def _aenter(self) -> None:  # noqa: ANN001 - 与 lifespan 同签名
        self.orchestrator = self.app.state.orchestrator

    main_module.AppLifespan.__aenter__ = _aenter


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--idea", default=DEFAULT_IDEA)
    parser.add_argument("--beat", type=float, default=30.0, help="应用层心跳间隔（与管理端一致）")
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--limit", type=float, default=DEFAULT_LIMIT, help="整个探针的墙钟上限")
    args = parser.parse_args()

    keep_injected_orchestrator()
    orchestrator = await build_orchestrator()
    app = create_app(orchestrator=orchestrator)
    config = uvicorn.Config(
        app, host="127.0.0.1", port=args.port, log_level="warning", access_log=False
    )
    server = uvicorn.Server(config)
    serve_task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.05)

    started = time.monotonic()
    stamps: list[float] = []
    types: list[str] = []
    outcome = "未收尾"
    try:
        async with websockets.connect(
            f"ws://127.0.0.1:{args.port}/ws/chat",
            open_timeout=15,
            ping_interval=None,
            ping_timeout=None,
        ) as ws:
            # auto=true：两处人工口都不挂起，一轮写完——本探针要测的是「活着跑完」，
            # 不是闸门；闸门那条路径由 tests/test_run_budget.py 与 resume 用例覆盖。
            # 不带 bookId：帧级闸门只拦「带书的续写帧」，这里匿名可跑。
            await ws.send(
                json.dumps(
                    {
                        "type": "message",
                        "content": args.idea,
                        "agent": "novel",
                        "context": {"auto": True},
                    }
                )
            )

            async def reader() -> None:
                nonlocal outcome
                async for raw in ws:
                    frame = json.loads(raw)
                    now = time.monotonic() - started
                    stamps.append(now)
                    kind = frame["type"]
                    types.append(kind)
                    content = str(frame.get("content") or "")[:60]
                    print(f"+{now:6.1f}s {kind:<16} {content}")
                    if kind == "done":
                        outcome = "收到 done，整批写完并收尾"
                        return
                    if kind == "error":
                        outcome = f"收到 error：{content}"
                        return

            async def beater() -> None:
                while True:
                    await asyncio.sleep(args.beat)
                    await ws.send(json.dumps({"type": "ping"}))

            reader_task = asyncio.create_task(reader())
            watch_dog = asyncio.create_task(asyncio.sleep(args.limit))
            beater_task = asyncio.create_task(beater())
            finished, pending = await asyncio.wait(
                {reader_task, watch_dog, beater_task}, return_when=asyncio.FIRST_COMPLETED
            )
            for task in pending:
                task.cancel()
            if reader_task in pending:
                outcome = f"挂满 {args.limit:.0f}s 仍没收到 done"
            elif reader_task in finished:
                exc = reader_task.exception()
                if exc is not None:
                    outcome = f"+{time.monotonic() - started:.1f}s 读通道异常 {type(exc).__name__}: {exc}"
                elif outcome == "未收尾":
                    outcome = "读通道自然结束（没收到 done）"
    finally:
        server.should_exit = True
        try:
            await asyncio.wait_for(serve_task, timeout=10)
        except asyncio.TimeoutError:
            serve_task.cancel()
        await orchestrator.aclose()

    gaps = [b - a for a, b in zip(stamps, stamps[1:])]
    print(f"\n帧数={len(stamps)} 类型分布={sorted(set(types))}")
    print(f"最长静默间隔={max(gaps) if gaps else 0:.1f}s（心跳 {args.beat:.0f}s 一帧，落在静默期里就是当年被撕的那个形状）")
    print(f"总时长={stamps[-1] if stamps else 0:.1f}s")
    print(f"结论：{outcome}")
    return 0 if outcome.startswith("收到 done") and "error" not in types else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
