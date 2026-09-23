"""AgentRunner：把 LangGraph 执行流翻译为统一 AgentEvent 事件流。

对应 ``services/chat/agent_run_satus.json`` 草案的事件协议——
WS 帧（P2）、A2A SSE（P4）、MCP 通知（P3）均翻译自这里的事件流，
核心库自身不感知任何传输层。

流式翻译规则（``stream_mode=["updates", "messages", "custom"]``）：

===================  ==========================
LangGraph 流         AgentEvent
===================  ==========================
updates: 节点 delta  STEP（payload.node）
updates: AIMessage   TOOL_CALL_START（未流式时）
updates: ToolMessage TOOL_CALL_END + TOOL_CALL_RESULT
updates: __interrupt__  INTERRUPT
messages: token 增量 TEXT_MESSAGE_CONTENT（打字机）
messages: tool_call_chunks  TOOL_CALL_START / TOOL_CALL_ARGS
custom: 领域事件     透传（type 合法则原样，否则包成 STEP）
超时/异常            RUN_ERROR
===================  ==========================

去重策略：OpenAI 兼容 provider 的流式 chunk 带 message id，
updates 中的完整 AIMessage 按 id 去重；id 缺失（本地 fake 模型）
按内容哈希去重。

子图透传：``astream`` 以 ``subgraphs=True`` 运行，垂直 Agent 子图
内部的节点更新 / token / custom 事件全部上浮（产出为
``(namespace, mode, chunk)`` 三元组，namespace 丢弃、事件只带节点名）。
没有这一开关，supervisor 委托子图时 get_stream_writer 发布的
领域事件对 WS / A2A / MCP 各传输层均不可见。
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import AsyncIterator, Iterable
from typing import Any

from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Interrupt

from po_agent_core.events import AgentEvent, EventType


class _RunTranslator:
    """单次运行内的流翻译状态（Runner 本身保持无状态、可并发复用）。"""

    def __init__(self) -> None:
        self._streamed_ids: set[str] = set()
        self._streamed_content_hashes: set[str] = set()
        self._announced_tool_calls: set[str] = set()
        # subgraphs=True 下同一 interrupt 会以子图与父图两级 updates 各上浮一次
        self._interrupt_ids: set[str] = set()

    # ---------- updates ----------
    def translate_updates(self, chunk: Any) -> list[AgentEvent]:
        events: list[AgentEvent] = []
        if not isinstance(chunk, dict):
            return events
        if "__interrupt__" in chunk:
            return self._translate_interrupts(chunk["__interrupt__"])
        for node, delta in chunk.items():
            if delta is None:
                continue
            # 每个有更新的节点都发一条 STEP：前端凭它展示「当前进行到哪一步」。
            # subgraphs=True 下 node 也可能是垂直 Agent 子图的内部节点名。
            events.append(
                AgentEvent(EventType.STEP, payload={"node": node})
            )
            if not isinstance(delta, dict):
                continue
            for message in delta.get("messages") or []:
                if isinstance(message, ToolMessage):
                    events.extend(self._translate_tool_message(message))
                elif isinstance(message, AIMessage):
                    events.extend(self._translate_full_ai_message(message))
        return events

    def _translate_interrupts(
        self, interrupts: Iterable[Interrupt] | Any
    ) -> list[AgentEvent]:
        events: list[AgentEvent] = []
        for interrupt in interrupts or ():
            interrupt_id = getattr(interrupt, "id", None)
            if interrupt_id:
                if interrupt_id in self._interrupt_ids:
                    continue
                self._interrupt_ids.add(interrupt_id)
            value = getattr(interrupt, "value", None)
            events.append(
                AgentEvent(
                    EventType.INTERRUPT,
                    content=_summarize_interrupt(value),
                    payload={"value": _json_safe(value)},
                )
            )
        return events

    def _translate_tool_message(self, message: ToolMessage) -> list[AgentEvent]:
        call_id = message.tool_call_id or ""
        events = [
            AgentEvent(
                EventType.TOOL_CALL_END,
                payload={"tool_call_id": call_id, "name": message.name or ""},
            ),
            AgentEvent(
                EventType.TOOL_CALL_RESULT,
                content=_content_to_str(message.content),
                payload={
                    "tool_call_id": call_id,
                    "name": message.name or "",
                    "status": message.status or "success",
                },
            ),
        ]
        self._announced_tool_calls.discard(call_id)
        return events

    def _translate_full_ai_message(self, message: AIMessage) -> list[AgentEvent]:
        """updates 模式下的完整 AIMessage：补发未流式到达的内容与工具调用。"""
        events: list[AgentEvent] = []
        content = _content_to_str(message.content)
        if message.id is not None:
            already_streamed = message.id in self._streamed_ids
        else:
            already_streamed = (
                content == ""
                or _hash_content(content) in self._streamed_content_hashes
            )
        if content and not already_streamed:
            events.append(AgentEvent(EventType.TEXT_MESSAGE_CONTENT, content=content))
        for tool_call in message.tool_calls or []:
            if tool_call["id"] in self._announced_tool_calls:
                continue
            self._announced_tool_calls.add(tool_call["id"])
            events.append(
                AgentEvent(
                    EventType.TOOL_CALL_START,
                    payload={
                        "tool_call_id": tool_call["id"],
                        "name": tool_call["name"],
                    },
                )
            )
        return events

    # ---------- messages ----------
    def translate_messages(self, chunk: Any) -> list[AgentEvent]:
        if not isinstance(chunk, tuple) or len(chunk) != 2:
            return []
        message, metadata = chunk
        if not isinstance(message, AIMessageChunk):
            return []
        events: list[AgentEvent] = []
        node = metadata.get("langgraph_node") if isinstance(metadata, dict) else None
        if message.id:
            self._streamed_ids.add(message.id)
        content = _content_to_str(message.content)
        if content:
            self._streamed_content_hashes.add(_hash_content(content))
            events.append(
                AgentEvent(
                    EventType.TEXT_MESSAGE_CONTENT,
                    content=content,
                    payload={"node": node},
                )
            )
        for tcc in message.tool_call_chunks or []:
            if tcc.get("name"):
                call_id = tcc.get("id") or tcc["name"]
                if call_id not in self._announced_tool_calls:
                    self._announced_tool_calls.add(call_id)
                    events.append(
                        AgentEvent(
                            EventType.TOOL_CALL_START,
                            payload={
                                "tool_call_id": call_id,
                                "name": tcc["name"],
                            },
                        )
                    )
            args = tcc.get("args") or ""
            if args:
                events.append(
                    AgentEvent(
                        EventType.TOOL_CALL_ARGS,
                        content=args,
                        payload={"node": node},
                    )
                )
        return events

    # ---------- custom ----------
    def translate_custom(self, chunk: Any) -> list[AgentEvent]:
        """领域侧经 ``langgraph.config.get_stream_writer`` 发布的自定义事件。"""
        if isinstance(chunk, AgentEvent):
            return [chunk]
        if isinstance(chunk, dict) and "type" in chunk:
            try:
                event_type = EventType(chunk["type"])
            except ValueError:
                pass
            else:
                return [
                    AgentEvent(
                        event_type,
                        content=str(chunk.get("content", "")),
                        payload=chunk.get("payload") or {},
                    )
                ]
        return [AgentEvent(EventType.STEP, payload={"custom": _json_safe(chunk)})]


class AgentRunner:
    """编排运行器：astream(graph, state) → AsyncIterator[AgentEvent]。

    超时治理：整次运行受 ``timeout_seconds`` 约束（默认取
    ``AGENT_CORE_RUN_TIMEOUT_SECONDS``），超时取消执行并发布 RUN_ERROR。
    """

    def __init__(self, *, timeout_seconds: float = 300.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds 必须为正数")
        self.timeout_seconds = timeout_seconds

    async def astream(
        self,
        graph: CompiledStateGraph,
        state: dict[str, Any],
        *,
        config: dict[str, Any] | None = None,
    ) -> AsyncIterator[AgentEvent]:
        translator = _RunTranslator()
        config = dict(config or {})
        thread_id = (config.get("configurable") or {}).get("thread_id")
        # thread_id 由宿主用 conversation_id 填入；前端靠它续接同一会话与 interrupt
        yield AgentEvent(
            EventType.RUN_STARTED,
            payload={"thread_id": thread_id},
        )
        try:
            async with asyncio.timeout(self.timeout_seconds):
                async for _namespace, mode, chunk in graph.astream(
                    state,
                    config,
                    stream_mode=["updates", "messages", "custom"],
                    subgraphs=True,
                ):
                    if mode == "updates":
                        events = translator.translate_updates(chunk)
                    elif mode == "messages":
                        events = translator.translate_messages(chunk)
                    elif mode == "custom":
                        events = translator.translate_custom(chunk)
                    else:  # pragma: no cover - 未知模式直接透传为 STEP
                        events = [
                            AgentEvent(EventType.STEP, payload={"custom": _json_safe(chunk)})
                        ]
                    for event in events:
                        yield event
        except TimeoutError:
            # 错误即终止帧：发完 RUN_ERROR 就 return，不再补 RUN_FINISHED，
            # 前端只需等待「唯一的终止事件」
            yield AgentEvent(
                EventType.RUN_ERROR,
                content="运行超时",
                payload={
                    "error_type": "TimeoutError",
                    "timeout_seconds": self.timeout_seconds,
                },
            )
            return
        except asyncio.CancelledError:
            # 取消不是业务错误：原样向上抛，让 WS 断连等场景能真正终止任务，
            # 而不是被翻译成一个普通错误帧吞掉
            raise
        except Exception as exc:
            yield AgentEvent(
                EventType.RUN_ERROR,
                content=str(exc),
                payload={"error_type": type(exc).__name__},
            )
            return
        yield AgentEvent(EventType.RUN_FINISHED, payload={})


def _content_to_str(content: Any) -> str:
    if isinstance(content, str):
        return content
    if content is None:
        return ""
    if isinstance(content, list):
        parts = [
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        ]
        return "".join(parts)
    return str(content)


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _summarize_interrupt(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("question") or value.get("message") or "等待用户确认")
    return "等待用户确认"


def _json_safe(value: Any) -> Any:
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        return str(value)
    return value
