"""子图测试：ReAct 往返、窗口裁剪、系统提示注入。"""

from __future__ import annotations

import json
from typing import Any

from conftest import ScriptedChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from po_agent_cooking import MockRecipeStore, build_cooking_graph, build_recipe_tools
from po_agent_cooking.graph import _window

_TOOL_CALL = AIMessage(
    content="",
    tool_calls=[{"id": "call-1", "name": "search_recipes", "args": {"keyword": "番茄"}}],
)


def _graph(model: ScriptedChatModel):  # type: ignore[no-untyped-def]
    return build_cooking_graph(model, build_recipe_tools(MockRecipeStore()))


async def test_react_round_trip_calls_tool_then_answers(
    make_scripted_model,
) -> None:  # type: ignore[no-untyped-def]
    """模型发起工具调用 → 工具执行 → 模型基于结果作答。"""
    model = make_scripted_model([_TOOL_CALL, AIMessage(content="给你推荐番茄炒蛋")])

    result = await _graph(model).ainvoke({"messages": [("user", "用番茄能做什么")]})
    messages = result["messages"]

    tool_messages = [m for m in messages if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    assert tool_messages[0].name == "search_recipes"
    payload = json.loads(tool_messages[0].content)
    assert payload["recipes"][0]["title"] == "番茄炒蛋"
    assert messages[-1].content == "给你推荐番茄炒蛋"
    # 第二次调模型时，上一轮的 ToolMessage 必须已在上下文里
    assert any(isinstance(m, ToolMessage) for m in model.seen[1])


async def test_system_prompt_injected_but_not_persisted(make_scripted_model) -> None:  # type: ignore[no-untyped-def]
    """系统提示每次调用都注入，但不写进 state（否则会随 checkpointer 叠加）。"""
    model = make_scripted_model([AIMessage(content="好的")])

    result = await _graph(model).ainvoke({"messages": [("user", "你好")]})

    assert isinstance(model.seen[0][0], SystemMessage)
    assert "烹饪助手" in model.seen[0][0].content
    assert not any(isinstance(m, SystemMessage) for m in result["messages"])


async def test_no_tool_call_ends_immediately(make_scripted_model) -> None:  # type: ignore[no-untyped-def]
    """模型没发起工具调用时，子图一步结束。"""
    model = make_scripted_model([AIMessage(content="直接回答")])

    result = await _graph(model).ainvoke({"messages": [("user", "你好")]})

    assert len(model.seen) == 1
    assert result["messages"][-1].content == "直接回答"


async def test_long_history_is_capped_before_model_call(make_scripted_model) -> None:  # type: ignore[no-untyped-def]
    """长会话下发给模型的上下文不能无限增长。"""
    model = make_scripted_model([AIMessage(content="回答")])
    history: list[Any] = []
    for index in range(30):
        history.append(HumanMessage(content=f"问题{index}"))
        history.append(AIMessage(content=f"回答{index}"))

    await _graph(model).ainvoke({"messages": history})

    prompt = model.seen[0]
    assert len(prompt) <= 21  # 系统提示 + 窗口上限 20
    assert prompt[1].content == "问题20"


def test_window_trims_to_human_boundary() -> None:
    """裁剪窗口必须从 HumanMessage 开始，避免出现孤儿 ToolMessage。"""
    messages = [
        HumanMessage(content="第一轮"),
        AIMessage(content="", tool_calls=[{"id": "c1", "name": "t", "args": {}}]),
        ToolMessage(content="结果", tool_call_id="c1"),
        AIMessage(content="第一轮回答"),
        HumanMessage(content="第二轮"),
        AIMessage(content="", tool_calls=[{"id": "c2", "name": "t", "args": {}}]),
        ToolMessage(content="结果2", tool_call_id="c2"),
    ]

    window = _window(messages, 4)

    assert isinstance(window[0], HumanMessage)
    assert window[0].content == "第二轮"
    # 窗口内的工具结果都能找到对应的工具调用
    assert isinstance(window[-1], ToolMessage)


def test_window_falls_back_when_no_human_message() -> None:
    """极端情况下（窗口内没有用户消息）宁可多带上下文，也不发出残缺序列。"""
    messages = [AIMessage(content=f"第{i}条") for i in range(10)]

    window = _window(messages, 3)

    assert len(window) == 10


def test_window_keeps_short_history_intact() -> None:
    messages = [HumanMessage(content="你好"), AIMessage(content="在的")]

    assert _window(messages, 20) == messages
