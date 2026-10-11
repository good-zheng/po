"""一次性探针：run 超时到期时，RUN_ERROR 到底能不能变成客户端可见的 error 帧。

现象：管理端 novel 长跑在 write 节点里被掐断，前端只得到「连接断开」而没有 error 帧。

两个场景分别对应超时可能落到的位置：
- inside-generator：到期时任务正 await 在 graph.astream 内部（节点还在跑）；
- inside-send：到期时任务正 await 在消费侧的 ``websocket.send_json``（一帧在途）。

复刻 app/routers/ws.py ``_loop`` 的 try/except 结构，只观察收到了哪些帧类型，不联网、不落库。
"""

import asyncio

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph

from app.agent import Orchestrator
from app.routers.ws import _ClientGone, _send_event
from po_agent_core import AgentCoreSettings, AgentRunner
from po_agent_core.supervisor.state import CoreState

TIMEOUT = 0.5
HANG = 3.0


def build_graph(with_custom_event: bool):
    builder = StateGraph(CoreState)

    async def ping(state: CoreState) -> dict:
        if with_custom_event:
            get_stream_writer()({"stage": "pinged"})
        return {"messages": []}

    async def hang(state: CoreState) -> dict:
        await asyncio.sleep(HANG)
        return {"messages": []}

    builder.add_node("ping", ping)
    builder.add_node("hang", hang)
    builder.add_edge(START, "ping")
    builder.add_edge("ping", "hang")
    builder.add_edge("hang", END)
    return builder.compile(checkpointer=InMemorySaver())


class FakeSocket:
    """只实现 _send_frame 用到的 send_json；delay 用来把超时点挪到「一帧正在发送」上。"""

    def __init__(self, delay: float) -> None:
        self.delay = delay
        self.types: list[str] = []

    async def send_json(self, payload: dict) -> None:
        await asyncio.sleep(self.delay)
        self.types.append(payload["type"])


async def run_case(name: str, *, with_custom_event: bool, send_delay: float) -> None:
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    orchestrator = Orchestrator(
        graph=build_graph(with_custom_event),
        runner=AgentRunner(timeout_seconds=TIMEOUT),
        settings=settings,
    )
    socket = FakeSocket(send_delay)
    escaped: BaseException | None = None
    try:
        # 消费侧循环结构照抄 app/routers/ws.py 的 _loop（含 _send_event 的帧映射）
        async for event in orchestrator.run("go", conversation_id="conv-probe"):
            await _send_event(socket, event)
    except asyncio.CancelledError as exc:
        escaped = exc
    except _ClientGone as exc:
        escaped = exc
    except Exception as exc:  # noqa: BLE001 - 探针要看清上抛的是什么
        escaped = exc
    print(
        f"[{name}] send_delay={send_delay}s 收到帧={socket.types} "
        f"逃逸异常={type(escaped).__name__ if escaped else '无'}"
    )


async def main() -> None:
    await run_case("inside-generator", with_custom_event=False, send_delay=0.0)
    await run_case("inside-send", with_custom_event=True, send_delay=TIMEOUT * 2)


if __name__ == "__main__":
    asyncio.run(main())
