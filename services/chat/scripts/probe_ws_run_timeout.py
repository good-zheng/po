"""一次性探针：真实的 uvicorn + WebSocket 栈上，run 超时会不会把 error 帧丢掉。

现象：管理端 novel 长跑被掐断，前端只看到「生成连接已断开」而没有 error 帧，
也没有服务端 traceback。用桩图（不联网、不打模型、不落库）在真实 uvicorn/ws
栈上复现「run 预算到期」这一件事，观察三样东西：
- 客户端收到的帧序列与时刻；
- 连接关闭码；
- uvicorn 侧有没有留下异常日志。

用法（cwd 必须是 services/chat）：
    .venv/Scripts/python.exe scripts/probe_ws_run_timeout.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import time

import uvicorn
import websockets
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

import app.main as main_module
from app.agent import Orchestrator
from app.main import create_app
from po_agent_core import AgentCoreSettings, AgentRunner
from po_agent_core.supervisor.state import CoreState

PORT = 5099
RUN_TIMEOUT = 2.0
HANG = 30.0


def keep_injected_orchestrator() -> None:
    """让 lifespan 不要覆盖注入的桩编排器。

    AppLifespan.__aenter__ 无条件 build_orchestrator()（见 app/main.py 的说明），
    而 uvicorn 一定会进 lifespan——不接管它，探针跑的就是真模型的真链路，
    既测不到桩节点的超时，也白烧额度。
    """

    async def _aenter(self) -> None:  # noqa: ANN001 - 与 lifespan 同签名
        self.orchestrator = self.app.state.orchestrator

    main_module.AppLifespan.__aenter__ = _aenter


def build_orchestrator(timeout_seconds: float) -> Orchestrator:
    """父子两张图：与 supervisor 挂 novel 插槽同构（``add_node(name, child_graph)``）。

    必须嵌套着测——真实链路的取消点穿的是子图，父图 astream 的清理路径与单层图不同，
    单层图跑得出来的「有 error 帧」不能代表线上。
    """
    child_builder = StateGraph(CoreState)

    async def hang(state: CoreState) -> dict:
        await asyncio.sleep(HANG)
        return {"messages": []}

    child_builder.add_node("hang", hang)
    child_builder.add_edge(START, "hang")
    child_builder.add_edge("hang", END)
    # 子图刻意不挂 checkpointer：与 po_agent_novel 的装配一致（saver 由父图供给）
    child = child_builder.compile()

    parent_builder = StateGraph(CoreState)
    parent_builder.add_node("novel", child)
    parent_builder.add_edge(START, "novel")
    parent_builder.add_edge("novel", END)
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    return Orchestrator(
        graph=parent_builder.compile(checkpointer=InMemorySaver()),
        runner=AgentRunner(timeout_seconds=timeout_seconds),
        settings=settings,
    )


async def main() -> None:
    keep_injected_orchestrator()
    app = create_app(orchestrator=build_orchestrator(RUN_TIMEOUT))
    config = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="info", access_log=False)
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    while not server.started:
        await asyncio.sleep(0.05)

    started = time.monotonic()
    frames: list[tuple[float, str]] = []
    close_info = "未关闭"
    try:
        async with websockets.connect(f"ws://127.0.0.1:{PORT}/ws/chat", open_timeout=5) as ws:
            await ws.send('{"type":"message","content":"go","conversation_id":"probe-1"}')
            while True:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=RUN_TIMEOUT + 8)
                except asyncio.TimeoutError:
                    close_info = "客户端 8s 没再收到任何帧（recv 超时）"
                    break
                if raw is None:
                    continue
                frame = json.loads(raw)
                frames.append((round(time.monotonic() - started, 2), frame["type"], str(frame.get("content"))[:40]))
    except websockets.exceptions.ConnectionClosed as exc:
        close_info = f"服务端关闭连接 rcvd={exc.rcvd} sent={exc.sent}"

    await asyncio.sleep(0.2)
    server.should_exit = True
    await task

    print(f"run 预算={RUN_TIMEOUT}s 节点睡眠={HANG}s")
    print(f"客户端帧序列：{frames}")
    print(f"连接收尾：{close_info}")
    print(f"error 帧是否送达：{'error' in [t for _, t in frames]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
