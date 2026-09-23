"""子图全链路：经 supervisor + InMemorySaver 走通 offline 链路。

覆盖：
- 构思 → 大纲 → 逐章生成/审稿 → 归档 interrupt → resume 确认/拒绝 → mock 入库；
- 审稿低分触发修订循环（revise 携带审稿意见重写本章）；
- 修订次数用尽强制定稿（无死循环）；
- thinking 领域事件按 pipeline 阶段上报。
"""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import Field

from po_agent_core import (
    AgentCoreSettings,
    AgentRunner,
    EventType,
    RouteDecision,
    VerticalAgent,
)
from po_agent_core.supervisor.graph import build_supervisor_graph
from po_agent_novel import (
    NOVEL_UTTERANCES,
    MockNovelStore,
    OfflineNovelModel,
    build_novel_agent,
)
from po_agent_novel.graph import STAGE_ROLES, _approved, build_novel_graph
from po_agent_novel.schemas import Reflection


class _StaticRouter:
    """固定路由到 novel：路由行为已在 agent-core 侧覆盖，此处只测子图。"""

    def route(self, text: str) -> RouteDecision:
        return RouteDecision(intent="novel", score=1.0, source="test")


class ScriptedNovelModel(OfflineNovelModel):
    """可编程审稿 + 记录正文提示词的离线模型。

    ``low_scores`` 按 reflect 调用次序出队，用尽后回到离线行为（恒 9 分）。
    """

    low_scores: list[int] = Field(default_factory=list)
    prompts: list[str] = Field(default_factory=list)

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is Reflection:

            async def run(prompt: str | list) -> Reflection:
                score = self.low_scores.pop(0) if self.low_scores else 9
                return Reflection(score=score, comment=f"scripted：{score} 分，冲突不足。")

            return RunnableLambda(func=run)  # type: ignore[arg-type]
        return super().with_structured_output(schema, **kwargs)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        self.prompts.append(str(messages[-1].content))
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


# 记录「哪个角色的模型被调用了」，按调用次序累积；每个用例开头清空。
_ROLE_CALLS: list[str] = []


class RoleTaggedModel(OfflineNovelModel):
    """自报家门的离线模型：每次被调用就把自己的 tag 记进 _ROLE_CALLS。

    走离线实现（不联网）所以能进常规单测；目的是断言「阶段 → 模型」的绑定
    真的生效，而不只是配置解析对了。
    """

    tag: str = ""

    def _record(self) -> None:
        _ROLE_CALLS.append(self.tag)

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        inner = super().with_structured_output(schema, **kwargs)

        async def run(prompt: str | list) -> Any:
            self._record()
            return await inner.ainvoke(prompt)

        return RunnableLambda(func=run)  # type: ignore[arg-type]

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        self._record()
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


def _settings() -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, llm_api_key="")


def _build(
    model: OfflineNovelModel | None = None,
    store: MockNovelStore | None = None,
    **agent_kwargs: Any,
):
    store = store or MockNovelStore()
    agent = build_novel_agent(
        _settings(), chat_model=model or OfflineNovelModel(), store=store, **agent_kwargs
    )
    graph = build_supervisor_graph(
        [agent], _StaticRouter(), OfflineNovelModel(), checkpointer=InMemorySaver()
    )
    return graph, store


async def _run(runner: AgentRunner, graph, payload, config) -> list:
    return [event async for event in runner.astream(graph, payload, config=config)]


def _of(events: list, event_type: EventType) -> list:
    return [e for e in events if e.type == event_type]


def _text(events: list) -> str:
    return "".join(e.content for e in _of(events, EventType.TEXT_MESSAGE_CONTENT))


def _stages(events: list) -> list[str]:
    progress = [e for e in events if e.type in (EventType.THINKING, EventType.PLAN)]
    return [e.payload.get("stage") for e in progress]


async def _drive_to_interrupt(runner: AgentRunner, graph, thread: str):
    """跑 run1 直至归档 interrupt：返回 config、interrupt 事件与 run1 全部事件。"""
    config = {"configurable": {"thread_id": thread}}
    events = await _run(
        runner, graph, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config
    )
    interrupts = _of(events, EventType.INTERRUPT)
    assert len(interrupts) == 1, f"应有且仅有一次归档确认 interrupt：{_stages(events)}"
    assert _of(events, EventType.RUN_FINISHED), "interrupt 后本次 run 应以 done 收尾"
    return config, interrupts[0], events


# ---------- 归档确认 / 拒绝 ----------


async def test_offline_full_chain_confirm_archive() -> None:
    graph, store = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, interrupt_event, _ = await _drive_to_interrupt(runner, graph, "novel-confirm")

    payload = interrupt_event.payload["value"]
    assert payload["chapter_count"] == 3
    assert payload["hint"]

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert _of(resumed, EventType.RUN_FINISHED)
    reply = _text(resumed)
    assert "已归档入库" in reply
    assert "第1章" in reply and "第3章" in reply

    books = await store.list_books()
    assert len(books) == 1
    assert books[0].chapter_count == 3
    assert books[0].character_count == 1

    # 终态核对：线程内消息与 novel 命名空间 artifacts
    snapshot = await graph.aget_state(config)
    assert "已归档入库" in snapshot.values["messages"][-1].content
    novel_ns = snapshot.values["artifacts"]["novel"]
    assert novel_ns["book_id"] == books[0].book_id
    assert novel_ns["idea"].title == books[0].title


async def test_offline_full_chain_decline_archive() -> None:
    graph, store = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-decline")

    resumed = await _run(runner, graph, Command(resume="no"), config)
    reply = _text(resumed)
    assert "暂不归档" in reply
    assert "第3章" in reply  # 拒绝归档不吞正文
    assert await store.list_books() == []


# ---------- 修订循环 ----------


async def test_low_score_triggers_revision_loop() -> None:
    model = ScriptedNovelModel(low_scores=[4, 5])
    graph, store = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "novel-loop")
    assert _stages(run1).count("revise") == 2  # 第 1 章两轮修订

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert _of(resumed, EventType.RUN_FINISHED)

    write_prompts = [p for p in model.prompts if "正在为《" in p]
    revise_prompts = [p for p in model.prompts if "按审稿意见修改章节" in p]
    assert len(write_prompts) == 3  # 三章各一次初稿
    assert len(revise_prompts) == 2
    assert any("冲突不足" in p for p in revise_prompts)  # 修订提示词携带审稿意见

    books = await store.list_books()
    assert books[0].chapter_count == 3  # 修订不阻碍链路走完


async def test_revision_exhausted_forces_finalize() -> None:
    model = ScriptedNovelModel(low_scores=[3] * 30)
    graph, store = _build(model=model, max_revisions=1)
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-forced")

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert _of(resumed, EventType.RUN_FINISHED)

    revise_prompts = [p for p in model.prompts if "按审稿意见修改章节" in p]
    assert len(revise_prompts) == 3  # 每章恰好一轮修订，用尽后强制定稿
    books = await store.list_books()
    assert books[0].chapter_count == 3


# ---------- 领域事件 / 确认解析 ----------


async def test_thinking_events_report_pipeline_stages() -> None:
    graph, _ = _build()
    runner = AgentRunner(timeout_seconds=30)
    events = await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="帮我写一本玄幻小说")]},
        {"configurable": {"thread_id": "novel-stages"}},
    )
    stages = _stages(events)
    assert "conceived" in stages
    assert "outlined" in stages
    assert stages.count("chapter_done") == 3
    assert _stages(events).count("revise") == 0  # 离线占位评分恒达标，无修订


@pytest.mark.parametrize(
    "value,expected",
    [
        ("yes", True),
        (" YES ", True),
        ("确认", True),
        (True, True),
        ("no", False),
        ("", False),
        (None, False),
    ],
)
def test_approved_parsing(value: Any, expected: bool) -> None:
    assert _approved(value) is expected


# ---------- 分阶段模型 ----------


async def test_stage_models_are_taken_by_role() -> None:
    """节点按声明的角色取模型，而非全图共用一个实例（阶段换模型的落点）。"""
    _ROLE_CALLS.clear()
    # 每个角色一个自报家门的模型：谁被调用就会在 _ROLE_CALLS 里留下自己的角色名。
    stage_models = {role: RoleTaggedModel(tag=role) for role in STAGE_ROLES}
    graph = build_novel_graph(stage_models, MockNovelStore())
    agent = VerticalAgent(
        name="novel",
        description="角色绑定测试",
        graph=graph,
        utterances=NOVEL_UTTERANCES,
    )
    sup = build_supervisor_graph(
        [agent], _StaticRouter(), OfflineNovelModel(), checkpointer=InMemorySaver()
    )
    runner = AgentRunner(timeout_seconds=30)
    config = {"configurable": {"thread_id": "novel-role-binding"}}
    await _run(runner, sup, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config)
    await _run(runner, sup, Command(resume="yes"), config)

    # 预期次序：构思/大纲 → plan；三章各「正文 → 审稿」交替；归档的角色抽取 → judge。
    assert _ROLE_CALLS[:2] == ["plan", "plan"]
    loop_calls = _ROLE_CALLS[2:-1]
    assert loop_calls[0::2] == ["write"] * len(loop_calls[0::2])
    assert loop_calls[1::2] == ["judge"] * len(loop_calls[1::2])
    assert _ROLE_CALLS[-1] == "judge"


def test_missing_stage_role_rejected_at_assembly() -> None:
    """缺角色在装配期就报错（并点名缺失角色），不留到运行期才炸。"""
    stage_models = {role: RoleTaggedModel(tag=role) for role in STAGE_ROLES if role != "judge"}
    with pytest.raises(ValueError, match="judge"):
        build_novel_graph(stage_models, MockNovelStore())
