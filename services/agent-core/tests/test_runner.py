"""AgentRunner 测试：事件流翻译、超时、异常、interrupt、custom 事件（全离线）。"""

import asyncio

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import interrupt
from typing_extensions import Annotated, TypedDict

from po_agent_core.events import EventType
from po_agent_core.runner.runner import AgentRunner


class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def compile_graph(*nodes: tuple[str, object], checkpointer=None) -> object:
    builder = StateGraph(ChatState)
    for name, fn in nodes:
        builder.add_node(name, fn)
    builder.add_edge(START, nodes[0][0])
    for (name, _), (next_name, _) in zip(nodes, nodes[1:]):
        builder.add_edge(name, next_name)
    builder.add_edge(nodes[-1][0], END)
    return builder.compile(checkpointer=checkpointer)


async def collect(runner: AgentRunner, graph, state, config=None) -> list:
    return [event async for event in runner.astream(graph, state, config=config)]


def types_of(events: list) -> list:
    return [event.type for event in events]


# ---------- 基本生命周期与文本流 ----------


async def test_lifecycle_events_wrap_the_run() -> None:
    model = FakeListChatModel(responses=["你好世界"])

    async def chat(state: ChatState) -> dict:
        reply = await model.ainvoke(state["messages"])
        return {"messages": [reply]}

    graph = compile_graph(("chat", chat))
    events = await collect(AgentRunner(timeout_seconds=5), graph, {"messages": [HumanMessage(content="hi")]})

    assert events[0].type is EventType.RUN_STARTED
    assert events[-1].type is EventType.RUN_FINISHED
    text = "".join(
        event.content
        for event in events
        if event.type is EventType.TEXT_MESSAGE_CONTENT
    )
    assert text == "你好世界"
    step_nodes = [
        event.payload["node"]
        for event in events
        if event.type is EventType.STEP and "node" in event.payload
    ]
    assert "chat" in step_nodes
    # 流式 token 与 updates 全量消息按 id 去重：文本只出现一次
    text_events = [e for e in events if e.type is EventType.TEXT_MESSAGE_CONTENT]
    assert text_events


async def test_run_started_carries_thread_id() -> None:
    async def chat(state: ChatState) -> dict:
        return {"messages": [AIMessage(content="ok")]}

    graph = compile_graph(("chat", chat))
    events = await collect(
        AgentRunner(),
        graph,
        {"messages": [HumanMessage(content="hi")]},
        config={"configurable": {"thread_id": "t-9"}},
    )
    assert events[0].payload["thread_id"] == "t-9"


# ---------- 工具调用事件 ----------


async def test_tool_call_events_from_updates() -> None:
    async def call_tool(state: ChatState) -> dict:
        return {
            "messages": [
                AIMessage(
                    content="",
                    tool_calls=[
                        {"name": "search", "args": {"q": "武侠"}, "id": "call-1"}
                    ],
                )
            ]
        }

    async def tool_result(state: ChatState) -> dict:
        return {
            "messages": [ToolMessage(content="结果内容", name="search", tool_call_id="call-1")]
        }

    graph = compile_graph(("call", call_tool), ("result", tool_result))
    events = await collect(AgentRunner(), graph, {"messages": [HumanMessage(content="查")]})

    assert EventType.TOOL_CALL_START in types_of(events)
    start = next(e for e in events if e.type is EventType.TOOL_CALL_START)
    assert start.payload["tool_call_id"] == "call-1"
    assert start.payload["name"] == "search"

    end = next(e for e in events if e.type is EventType.TOOL_CALL_END)
    assert end.payload["tool_call_id"] == "call-1"
    result = next(e for e in events if e.type is EventType.TOOL_CALL_RESULT)
    assert result.content == "结果内容"
    assert result.payload["status"] == "success"


async def test_tool_call_args_from_streaming_chunks() -> None:
    """流式模型输出 tool_call_chunks 时，args 增量翻译为 TOOL_CALL_ARGS。

    覆写 ``_astream``（而非公共 ``astream``）以保留 LangChain 回调机制，
    否则 LangGraph 的 messages 流模式收不到任何 chunk。
    """

    class FakeToolCallModel(FakeListChatModel):
        async def _astream(  # type: ignore[override]
            self, messages, stop=None, run_manager=None, **kwargs
        ):
            from langchain_core.messages import AIMessageChunk
            from langchain_core.outputs import ChatGenerationChunk

            yield ChatGenerationChunk(
                message=AIMessageChunk(
                    content="",
                    tool_call_chunks=[
                        {"name": "search", "args": '{"q":', "id": "call-2", "index": 0}
                    ],
                )
            )
            yield ChatGenerationChunk(
                message=AIMessageChunk(
                    content="",
                    tool_call_chunks=[
                        {"name": None, "args": ' "武侠"}', "id": None, "index": 0}
                    ],
                )
            )

    async def chat(state: ChatState) -> dict:
        final = None
        async for chunk in FakeToolCallModel(responses=["x"]).astream(
            state["messages"]
        ):
            final = chunk if final is None else final + chunk
        return {"messages": [final] if final is not None else []}

    graph = compile_graph(("chat", chat))
    events = await collect(AgentRunner(), graph, {"messages": [HumanMessage(content="查")]})
    args = "".join(e.content for e in events if e.type is EventType.TOOL_CALL_ARGS)
    assert args == '{"q": "武侠"}'
    # 首个 chunk 携带工具名：TOOL_CALL_START 在 args 之前
    types = types_of(events)
    assert types.index(EventType.TOOL_CALL_START) < types.index(EventType.TOOL_CALL_ARGS)


# ---------- custom 事件 ----------


async def test_custom_writer_events_pass_through() -> None:
    async def node(state: ChatState) -> dict:
        writer = get_stream_writer()
        writer({"type": "thinking", "content": "规划中", "payload": {"stage": 1}})
        writer({"type": "plan", "content": "三步计划"})
        writer({"anything": "else"})
        return {"messages": [AIMessage(content="done")]}

    graph = compile_graph(("node", node))
    events = await collect(AgentRunner(), graph, {"messages": [HumanMessage(content="go")]})

    thinking = next(e for e in events if e.type is EventType.THINKING)
    assert thinking.content == "规划中"
    assert thinking.payload == {"stage": 1}
    plan = next(e for e in events if e.type is EventType.PLAN)
    assert plan.content == "三步计划"
    custom_steps = [
        e for e in events if e.type is EventType.STEP and "custom" in e.payload
    ]
    assert custom_steps and custom_steps[0].payload["custom"] == {"anything": "else"}


# ---------- interrupt ----------


async def test_interrupt_translated_to_event() -> None:
    async def confirm(state: ChatState) -> dict:
        value = interrupt({"question": "确认归档？", "options": ["yes", "no"]})
        return {"messages": [AIMessage(content=f"恢复:{value}")]}

    graph = compile_graph(("confirm", confirm), checkpointer=InMemorySaver())
    runner = AgentRunner()
    config = {"configurable": {"thread_id": "t-int"}}
    events = [
        e
        async for e in runner.astream(
            graph, {"messages": [HumanMessage(content="归档")]}, config=config
        )
    ]

    interrupt_events = [e for e in events if e.type is EventType.INTERRUPT]
    assert len(interrupt_events) == 1
    assert interrupt_events[0].content == "确认归档？"
    assert interrupt_events[0].payload["value"]["options"] == ["yes", "no"]
    assert events[-1].type is EventType.RUN_FINISHED

    # 恢复执行：Command(resume=...) 后 interrupt 不再触发
    from langgraph.types import Command

    resumed = [
        e
        async for e in runner.astream(
            graph, Command(resume="yes"), config=config
        )
    ]
    text = "".join(
        e.content for e in resumed if e.type is EventType.TEXT_MESSAGE_CONTENT
    )
    assert text == "恢复:yes"
    assert all(e.type is not EventType.INTERRUPT for e in resumed)


# ---------- 超时与异常 ----------


async def test_timeout_emits_run_error() -> None:
    async def slow(state: ChatState) -> dict:
        await asyncio.sleep(2.0)
        return {"messages": [AIMessage(content="too late")]}

    graph = compile_graph(("slow", slow))
    runner = AgentRunner(timeout_seconds=0.1)
    events = await collect(runner, graph, {"messages": [HumanMessage(content="hi")]})

    assert types_of(events) == [EventType.RUN_STARTED, EventType.RUN_ERROR]
    assert events[-1].payload["error_type"] == "TimeoutError"
    assert events[-1].payload["timeout_seconds"] == 0.1


async def test_node_exception_emits_run_error() -> None:
    async def boom(state: ChatState) -> dict:
        raise ValueError("节点炸了")

    graph = compile_graph(("boom", boom))
    events = await collect(AgentRunner(), graph, {"messages": [HumanMessage(content="hi")]})

    assert types_of(events) == [EventType.RUN_STARTED, EventType.RUN_ERROR]
    assert events[-1].content == "节点炸了"
    assert events[-1].payload["error_type"] == "ValueError"


def test_invalid_timeout_rejected() -> None:
    with pytest.raises(ValueError):
        AgentRunner(timeout_seconds=0)
