"""一次性探针：write 节点卡在「HTTP 响应永不返回」上时，/ws/chat 会留下什么痕迹。

真实故障的形态是：连接建立后静默关闭，既没有 error 帧也没有服务端 traceback。
run 超时本身在探针里是能发出 error 帧的，所以要复现的是更真实的那一侧——
节点正 await 在一次网络读上（模型调用挂在没响应_conn 上），此时超时到期。

本探针不联网、不打真模型：起一个只收请求永不回包的假 LLM 服务，让真
ChatOpenAI 客户端指向它，再用真实 uvicorn 提供 /ws/chat，用真 WS 客户端收帧。
"""

from __future__ import annotations

import asyncio
import json
import os
import time

import uvicorn
import websockets
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

import app.main as main_module
from app.agent import Orchestrator
from app.main import create_app
from po_agent_core import AgentCoreSettings, AgentRunner
from po_agent_core.supervisor.state import CoreState

FAKE_LLM_PORT = 5098
CHAT_PORT = 5099
RUN_TIMEOUT = 3.0


async def start_blackhole() -> asyncio.Server:
    """收请求、永不回包的假上游：让模型调用停在 read 上。"""

    async def handle(_: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            await writer.drain()
            await asyncio.sleep(600)  # 挂着不回
        finally:
            writer.close()

    server = await asyncio.start_server(handle, "127.0.0.1", FAKE_LLM_PORT)
    return server


def keep_injected_orchestrator() -> None:
    async def _aenter(self) -> None:  # noqa: ANN001
        self.orchestrator = self.app.state.orchestrator

    main_module.AppLifespan.__aenter__ = _aenter


def build_orchestrator() -> Orchestrator:
    model = ChatOpenAI(
        model="probe",
        api_key="probe",  # 只喂给黑洞端口，不是真密钥
        base_url=f"http://127.0.0.1:{FAKE_LLM_PORT}/v1",
        timeout=60,
        max_retries=0,
    )
    builder = StateGraph(CoreState)

    async def write(state: CoreState) -> dict:
        response = await model.ainvoke(state.get("messages") or [])
        return {"messages": [response]}

    builder.add_node("write", write)
    builder.add_edge(START, "write")
    builder.add_edge("write", END)
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    return Orchestrator(
        graph=builder.compile(checkpointer=InMemorySaver()),
        runner=AgentRunner(timeout_seconds=RUN_TIMEOUT),
        settings=settings,
    )


async def main() -> None:
    blackhole = await start_blackhole()
    keep_injected_orchestrator()
    app = create_app(orchestrator=build_orchestrator())
    config = uvicorn.Config(app, host="127.0.0.1", port=CHAT_PORT, log_level="info", access_log=False)
    server = uvicorn.Server(config)
    serve = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.05)

    started = time.monotonic()
    frames: list[tuple[float, str, str]] = []
    closing = "未关闭"
    try:
        async with websockets.connect(f"ws://127.0.0.1:{CHAT_PORT}/ws/chat", open_timeout=5) as ws:
            await ws.send('{"type":"message","content":"go","conversation_id":"probe-hang"}')
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=RUN_TIMEOUT + 10)
                except asyncio.TimeoutError:
                    closing = f"{RUN_TIMEOUT + 10}s 内没有新帧（连接仍开着）"
                    break
                frame = json.loads(raw)
                entry = (round(time.monotonic() - started, 2), frame["type"], str(frame.get("content"))[:60])
                frames.append(entry)
                # 逐帧即时打印：收尾阶段若被外部因素（系统代理、连接清理）卡住，
                # 已经拿到的证据不该跟着一起丢。
                print(f"  {entry[0]:>6}s  {entry[1]:<12} {entry[2]}", flush=True)
    except websockets.exceptions.ConnectionClosed as exc:
        closing = f"服务端关闭 rcvd={exc.rcvd} sent={exc.sent} 用时={round(time.monotonic() - started, 2)}s"

    print(f"连接收尾：{closing}", flush=True)
    print(f"收到 error 帧：{any(kind == 'error' for _, kind, _ in frames)}", flush=True)
    print(f"收到 done 帧：{any(kind == 'done' for _, kind, _ in frames)}", flush=True)
    server.should_exit = True
    # 不等 serve() 收尾：黑洞里那条模型请求还挂着，优雅停机要等到它的超时才结束，
    # 而探针要的证据在上面三行里已经齐了。
    blackhole.close()
    os._exit(0)


if __name__ == "__main__":
    asyncio.run(main())
