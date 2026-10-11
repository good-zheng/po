"""长批次的运行预算：按插槽给，并且恢复轮不从默认值重算。

这两组用例锁的是同一个事故的两个半边：一次「写 3 章」实测 322 秒，而
``AgentRunner`` 的构造值是 300 秒 —— 长批次会在写作中途被掐成一条「运行超时」
的错误帧。另一半更要紧：作者按「先问问我」发起时，计划闸门会把发起轮截断，
**剩下几章全部写在 ``resume`` 里**，而 resume 帧不带 ``agent``，所以预算必须从
checkpoint 里读回来，否则修复只覆盖了两种触发方式中的一种。

对照实现：``app/agent.py`` 的 ``_RUN_BUDGET_BY_AGENT`` / ``_run_budget`` /
``_forced_agent``。
"""

import asyncio
from typing import Any

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent import _RUN_BUDGET_BY_AGENT, Orchestrator
from po_agent_core import AgentCoreSettings, AgentRunner, VerticalAgent
from po_agent_core.supervisor.state import CoreState

DEFAULT_BUDGET = 300.0
NOVEL_BUDGET = _RUN_BUDGET_BY_AGENT["novel"]


class RecordingRunner:
    """只记录每轮实际下发的预算，不真的跑图。

    形状与 ``AgentRunner.astream`` 一致（同为 async generator、同样的关键字参数），
    所以这里断言的是宿主传给编排核心的契约，而不是宿主自己的算术。
    """

    def __init__(self) -> None:
        self.timeout_seconds = DEFAULT_BUDGET
        self.budgets: list[float | None] = []

    async def astream(
        self,
        graph: Any,
        state: Any,
        *,
        config: dict | None = None,
        timeout_seconds: float | None = None,
    ):
        self.budgets.append(timeout_seconds)
        return
        yield  # pragma: no cover - 这一行让上面的函数成为 async generator


class StubGraph:
    """带 ``aget_state`` 的最小图替身：恢复轮的预算完全由它返回的插槽名决定。"""

    def __init__(self, values: dict[str, Any] | None = None, *, error: bool = False):
        self._values = values if values is not None else {}
        self._error = error

    async def aget_state(self, config: dict) -> Any:
        if self._error:
            raise ValueError("No checkpointer set")

        class _Snapshot:
            values = self._values

        return _Snapshot()


def _noop_graph():
    builder = StateGraph(CoreState)

    async def noop(state: CoreState) -> dict:
        return {"messages": [AIMessage(content="ok")]}

    builder.add_node("noop", noop)
    builder.add_edge(START, "noop")
    builder.add_edge("noop", END)
    return builder.compile(checkpointer=InMemorySaver())


def _slot(name: str) -> VerticalAgent:
    return VerticalAgent(name=name, description=f"{name} 插槽", graph=_noop_graph())


def build_orchestrator(
    *, graph: Any = None, agents: dict[str, VerticalAgent] | None = None
) -> tuple[Orchestrator, RecordingRunner]:
    runner = RecordingRunner()
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    orchestrator = Orchestrator(
        graph=graph if graph is not None else _noop_graph(),
        runner=runner,  # type: ignore[arg-type] - 只验预算契约，不跑真 runner
        settings=settings,
        agents=agents if agents is not None else {n: _slot(n) for n in ("novel", "chitchat")},
    )
    return orchestrator, runner


async def _drain(stream) -> None:
    async for _ in stream:
        pass


# ---------- 发起轮 ----------


def test_novel_run_gets_its_own_budget() -> None:
    """点名 novel 的一轮拿专属预算：默认 300 秒跑不完一次 3 章的批次。"""
    orchestrator, runner = build_orchestrator()

    async def scenario() -> None:
        await _drain(
            orchestrator.run(
                "写第四章", agent="novel", context={"bookId": "12", "chapterCount": 3}
            )
        )

    asyncio.run(scenario())
    assert runner.budgets == [NOVEL_BUDGET]
    assert NOVEL_BUDGET > DEFAULT_BUDGET


def test_short_slots_keep_the_default_budget() -> None:
    """专属预算只给长批次插槽：chitchat 与没点名插槽仍用构造值。

    把 3600 秒抬成全局默认的后果是「真卡死的问答要空等一小时才见错误帧」，
    这条断言就是那道边界。
    """
    orchestrator, runner = build_orchestrator()

    async def scenario() -> None:
        await _drain(orchestrator.run("今天写点什么", agent="chitchat"))
        await _drain(orchestrator.run("今天写点什么"))

    asyncio.run(scenario())
    assert runner.budgets == [DEFAULT_BUDGET, DEFAULT_BUDGET]


def test_uninstalled_slot_falls_back_to_the_default_budget() -> None:
    """点名一个没装配的插槽时父图会退回普通编排，预算也跟着退回默认值。

    判据必须与 ``run`` 里「写不写 forced_agent」是同一个，否则会出现「按 novel
    放宽预算、实际由 chitchat 跑」这种两边不一致的轮次。
    """
    orchestrator, runner = build_orchestrator(agents={"chitchat": _slot("chitchat")})

    async def scenario() -> None:
        await _drain(orchestrator.run("写第四章", agent="novel"))

    asyncio.run(scenario())
    assert runner.budgets == [DEFAULT_BUDGET]


# ---------- 恢复轮 ----------


def test_resume_buys_the_same_budget_as_the_interrupted_run() -> None:
    """resume 从 checkpoint 读回插槽名：闸门之后的几章正是长跑真正发生的地方。"""
    orchestrator, runner = build_orchestrator(graph=StubGraph({"forced_agent": "novel"}))

    async def scenario() -> None:
        await _drain(orchestrator.resume("thread-1", "yes"))

    asyncio.run(scenario())
    assert runner.budgets == [NOVEL_BUDGET]


def test_resume_without_a_forced_slot_keeps_the_default_budget() -> None:
    orchestrator, runner = build_orchestrator(graph=StubGraph({"messages": []}))

    async def scenario() -> None:
        await _drain(orchestrator.resume("thread-2", "yes"))

    asyncio.run(scenario())
    assert runner.budgets == [DEFAULT_BUDGET]


def test_resume_survives_an_unreadable_checkpoint() -> None:
    """读不回插槽名不是事故：按默认预算照常恢复，作者的确认必须发得出去。

    没挂 checkpointer 时 ``aget_state`` 抛 ValueError，存储抖动时抛别的——两类都不能
    变成「resume 直接报错」。这里只要求异常不外泄，预算取哪个值由上面那条用例负责。
    """
    orchestrator, runner = build_orchestrator(graph=StubGraph(error=True))

    async def scenario() -> None:
        await _drain(orchestrator.resume("thread-3", "yes"))

    asyncio.run(scenario())
    assert runner.budgets == [DEFAULT_BUDGET]


def test_forced_agent_survives_in_a_real_checkpoint() -> None:
    """恢复轮预算的前提：``forced_agent`` 真的活在同一 thread 的 checkpoint 里。

    上面几条用的是图替身，桩验不了 LangGraph 的行为——``run`` 把插槽名塞进 state，
    恢复时 ``aget_state`` 必须还能读回来，否则「resume 也按 novel 预算」这句话就是空的。
    这一条打真图真 runner（InMemorySaver、离线节点），锁的是那个库的语义，而不是我们对它的假设。
    """
    settings = AgentCoreSettings(_env_file=None, checkpointer="memory", llm_api_key="")
    orchestrator = Orchestrator(
        graph=_noop_graph(),
        runner=AgentRunner(timeout_seconds=30),
        settings=settings,
        agents={"novel": _slot("novel")},
    )

    async def scenario() -> str | None:
        await _drain(orchestrator.run("写第四章", conversation_id="t-real", agent="novel"))
        return await orchestrator._forced_agent(orchestrator._config("t-real"))

    assert asyncio.run(scenario()) == "novel"
