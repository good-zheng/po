"""WS 流式聊天端点：AgentRunner 事件流 → JSON 帧。

帧协议（出站 ``type``）：

=====================  =====================================
AgentEvent             WS 帧
=====================  =====================================
RUN_STARTED            ``run_started``（payload.thread_id）
TEXT_MESSAGE_CONTENT   ``token``（打字机增量）
THINKING / PLAN        ``thinking`` / ``plan``
STEP                   ``step``
TOOL_CALL_*            ``tool_call_start/args/end/result``
INTERRUPT              ``interrupt``（等待 ``resume`` 帧）
PROPOSAL               ``proposal``（设定提议卡：前端渲染成「采纳/驳回」，采纳走管理端 REST）
RUN_FINISHED           ``done``
RUN_ERROR              ``error``
=====================  =====================================

入站帧：``message``（新消息）、``resume``（interrupt 后继续）、
``ping``（心跳）。``conversation_id`` 贯穿三类帧，映射 LangGraph
thread_id 实现多轮会话记忆；缺省时每条消息独立会话。

握手身份：URL 可带 ``?ticket=<一次性票据>``（由 Spring Boot ``GET /api/novel/chat-ticket``
签发，见 :mod:`app.ws_auth`）。带票且校验通过的连接被绑定到那位作者，需要身份的帧
（``agent=novel-chat``，以及带 ``bookId`` 的续写帧）才会启动编排；带坏票的连接在 accept
之前就被关掉；不带票的连接仍可匿名使用其余插槽（现网小程序没有换票流程，一刀切会直接断掉它们的聊天）。

未来帧（lifecycle 中的 ``tool_approval_request`` 等）由 P3/P5 的
MCP 工具审批流引入；前端对未知帧类型必须忽略而非报错。

在链路中的位置
--------------

上游：前端 ``apps/admin-web/src/pages/chatbot/service.ts``（dev 下经前端 ``/ws``
代理转发）；下游：:class:`app.agent.Orchestrator` → ``AgentRunner`` →
LangGraph supervisor graph。本模块是**唯一的协议翻译层**——它不做业务判断，
只把编排侧统一的 ``AgentEvent`` 按 :data:`_EVENT_TO_FRAME` 翻成帧字段，
因此帧名与 ``WSOutFrame.type`` 的 Literal 列表是这里最需要保持稳定的契约。

连接的编排实例取自 ``websocket.app.state.orchestrator``，由 lifespan 在启动时
装配一次并被所有连接共享；生产路径不注入、测试路径经 ``create_app`` 注入。

interrupt / resume 的时序（前端必须遵守）
---------------------------------------

垂直 Agent 触发人机确认时会上抛 ``INTERRUPT`` 帧，但**该次 run 随后仍会以
``done`` 收尾**（LangGraph 线程只是挂起，不是错误，也不会有 RUN_ERROR）。
因此前端必须先把这个 run 的帧消费到 ``done``，再发 ``resume`` 帧；提前发送会
让 resume 的结果与上一轮收尾帧交错。``resume`` 帧的 ``content`` 是用户的回答，
由服务端原样透传（``Command(resume=value)``），确认词的具体判定在垂直 Agent
内部完成（由各 Agent 自己的确认词表负责），本模块不做解释。

另：本文件不经 FastAPI 的校验管道，``WSInFrame`` 的校验失败需自行兜住并回
``error`` 帧（REST 侧同类错误由框架统一转 422）。
"""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.agent import Orchestrator
from app.config import Settings, get_settings
from app.schemas import WSInFrame, WSOutFrame
from app.talk import persist_talk_result
from app.ws_auth import (
    NOVEL_AGENT,
    WsActor,
    actor_scope,
    requires_actor,
    resolve_actor,
    ticket_from,
)
from po_agent_core.events import AgentEvent, EventType

logger = logging.getLogger(__name__)

router = APIRouter()

# 握手票据被拒的关闭码：4401 落在 WebSocket 保留码之外的应用自定义区间，
# 与 talk 的 ASR 票据语义一致（「凭据不对」而不是「稍后再试」），
# 客户端据此决定要不要先去换一张新票。
HANDSHAKE_REJECTED_CODE = 4401

# AgentEvent 类型 → 出站帧名的映射表：用查表代替 if/elif，新增事件只需加一行。
# 未登记的类型（如 TOOL_APPROVAL_REQUEST 这类暂无下行语义的控制事件）在
# _send_event 中直接丢弃，从而未来扩展事件流时不会顺带把内部事件泄给前端。
_EVENT_TO_FRAME: dict[EventType, str] = {
    EventType.RUN_STARTED: "run_started",
    EventType.THINKING: "thinking",
    EventType.PLAN: "plan",
    EventType.STEP: "step",
    EventType.TEXT_MESSAGE_CONTENT: "token",
    EventType.TOOL_CALL_START: "tool_call_start",
    EventType.TOOL_CALL_ARGS: "tool_call_args",
    EventType.TOOL_CALL_END: "tool_call_end",
    EventType.TOOL_CALL_RESULT: "tool_call_result",
    EventType.INTERRUPT: "interrupt",
    EventType.PROPOSAL: "proposal",
    EventType.RUN_FINISHED: "done",
    EventType.RUN_ERROR: "error",
}


class _ClientGone(Exception):
    """客户端已断开，向其发送失败。

    单独立一个类型是为了与真正的服务端异常区分：客户端中途关页/断网属于
    正常结束（外层静默 return），而其他异常需要记日志并上抛。
    """


async def _send_frame(websocket: WebSocket, frame: WSOutFrame) -> None:
    """序列化并发送单帧；把「连接已关闭」翻译为 _ClientGone。"""
    try:
        await websocket.send_json(frame.model_dump())
    except RuntimeError as exc:  # starlette：close 之后的 send
        # Starlette 在应用侧 close 之后调用 send 会抛 RuntimeError，
        # 这里转换成专用异常，避免被外层的通用异常分支当成 bug 记录。
        raise _ClientGone from exc


async def _send_event(websocket: WebSocket, event: AgentEvent) -> None:
    """按映射表把一条 AgentEvent 翻成帧并发出；未登记的 event.type 直接忽略。

    ``content`` / ``payload`` 原样透传：payload 里已有 run_started 的 thread_id、
    tool_call_* 的工具名与参数等结构化信息，翻译层不做字段裁剪或重命名。
    """
    frame_type = _EVENT_TO_FRAME.get(event.type)
    if frame_type is None:  # 控制类/未接入协议的事件（如 approval 上行帧）
        return
    await _send_frame(
        websocket,
        WSOutFrame(type=frame_type, content=event.content, payload=event.payload),
    )


def _orchestrator(websocket: WebSocket) -> Orchestrator:
    """从应用状态取共享的 Orchestrator。

    连接建立时读取一次即可（lifespan 装配与测试注入都落在同一属性上）；
    取不到说明既没跑 lifespan 也没注入替身，属于部署/测试配置错误，直接抛错。
    """
    orchestrator: Orchestrator | None = getattr(websocket.app.state, "orchestrator", None)
    if orchestrator is None:
        raise RuntimeError("orchestrator 未初始化（lifespan 未运行且未注入测试实例）")
    return orchestrator


def _settings(websocket: WebSocket) -> Settings:
    """握手层要用的宿主配置：优先取应用状态上的注入实例，回落到进程级单例。"""
    return getattr(websocket.app.state, "settings", None) or get_settings()


class _Rejected:
    """握手被拒的哨兵：连接已关闭，调用方必须直接 return 而不是 accept。"""


_REJECTED = _Rejected()


async def _handshake(websocket: WebSocket) -> WsActor | None | _Rejected:
    """建立连接前的票据校验。

    返回值三态，且刻意不用 ``None`` 同时表示「没带票」和「票不对」：
    - :class:`WsActor` —— 带票且校验通过，连接绑定到这位作者；
    - ``None`` —— 没带票，按匿名放行（cooking / talk / chitchat 的现网客户端还没有换票
      流程，握手强拒等于直接断掉它们）；
    - :class:`_Rejected` —— 带了坏票，且**已经关掉连接**，调用方直接 return。
      坏票说明客户端已经走在正确的流程上，静默降级成匿名只会让「为什么读不到我的书」
      变成一条查不出来的线上谜题。
    """
    ticket = ticket_from(websocket)
    if ticket is None:
        return None
    actor = await resolve_actor(ticket, _settings(websocket))
    if actor is not None:
        return actor
    await websocket.close(code=HANDSHAKE_REJECTED_CODE)
    logger.warning("WS 握手被拒：票据无效或校验通道不可用")
    return _REJECTED


@router.websocket("/ws/chat")
async def chat(websocket: WebSocket) -> None:
    """建立连接：握手验票 → accept → 在作者上下文里跑主循环。

    路径固定为 ``/ws/chat``（不带 ``/api``，见 :mod:`app.main`）；连接期间
    编排器实例不变，因此可在进入循环前解析一次。

    握手带 ``?ticket=`` 时连接被绑定到一位作者（见 :func:`_handshake`）：身份活在
    ``actor_scope`` 的任务上下文里，novel 数据层据此给内网读口盖上 ``X-Actor-Uid``，
    Java 侧再按 ``book.author_id`` 判归属。
    """
    handshake = await _handshake(websocket)
    if isinstance(handshake, _Rejected):
        return
    await websocket.accept()
    # accept 之后再解析编排器：连接已建立，初始化失败也能以断连而非握手失败
    # 的形式暴露，客户端更容易确认原因。
    orchestrator = _orchestrator(websocket)
    actor = handshake if isinstance(handshake, WsActor) else None
    with actor_scope(actor.uid if actor is not None else None):
        await _loop(websocket, orchestrator, actor)


async def _loop(websocket: WebSocket, orchestrator: Orchestrator, actor: WsActor | None) -> None:
    """入站帧主循环：一连接多轮，串行处理并逐条回帧。

    ``actor`` 只用于帧级闸门：需要身份的帧（:func:`app.ws_auth.requires_actor`——
    ``novel-chat`` 与带 ``bookId`` 的续写帧）在匿名连接上一律不启动编排——握手没有票据的
    连接读不到任何人的正典，让它跑到 L1 编译那一步等于把校验挪到了事后。
    """
    try:
        while True:
            raw = await websocket.receive_json()
            try:
                frame = WSInFrame.model_validate(raw)
            except ValidationError:
                # 帧结构不合法不致命：回一帧 error 后继续复用同一连接，
                # 客户端可据此修正协议而无需重连。
                await _send_frame(websocket, WSOutFrame(type="error", content="invalid frame"))
                continue

            if frame.type == "ping":
                # 心跳只回 pong，不回 run_started 等编排帧，也不触碰编排器。
                await _send_frame(websocket, WSOutFrame(type="pong", content=frame.content))
                continue

            if requires_actor(frame.agent, frame.context) and actor is None:
                # 帧级闸门（回 error 而不是关连接）：客户端可能是「先匿名连上、
                # 登录后忘了换票」，关掉整条连接会把它其它插槽的会话一起打断。
                await _send_frame(
                    websocket,
                    WSOutFrame(
                        type="error",
                        content=(
                            "续写这本书需要作者身份：先在管理端登录，再重开创作面板"
                            "（面板会自动去取一张握手票据）"
                            if frame.agent == NOVEL_AGENT
                            else f"{frame.agent} 需要握手票据：先取 /api/novel/chat-ticket 再带 ?ticket= 连接"
                        ),
                    ),
                )
                continue

            if frame.type == "resume":
                if not frame.conversation_id:
                    # resume 必须带上挂起线程的 id，否则无法定位 thread_id；
                    # 这里不回落到新建会话，以免用户以为「确认了」实际开了新线程。
                    await _send_frame(
                        websocket,
                        WSOutFrame(
                            type="error", content="resume 需要 conversation_id（interrupt 挂起的线程）"
                        ),
                    )
                    continue
                conversation_id = frame.conversation_id
                events = orchestrator.resume(frame.conversation_id, frame.content)
            else:
                # 不传 conversation_id 时由服务端生成：该 id 会随 run_started 帧
                # 的 payload.thread_id 返回，客户端需保存并在下一轮回传，
                # 否则每条消息都会落在新的 thread 上、失去多轮记忆。
                conversation_id = frame.conversation_id or uuid4().hex
                events = orchestrator.run(
                    frame.content,
                    conversation_id=conversation_id,
                    agent=frame.agent,
                    context=frame.context,
                )
            started = time.monotonic()

            # 逐条 await 发送，同一个 socket 上不存在并发写，因此无需加锁；
            # 这一串行性也是「interrupt 之后必须等 done 再发 resume」的成因。
            chunks: list[str] = []
            async for event in events:
                if event.type == EventType.TEXT_MESSAGE_CONTENT:
                    chunks.append(event.content)
                await _send_event(websocket, event)

            # 一轮结束后回写结构化结果（只有 talk 插槽会真正执行，其余是空转）
            await persist_talk_result(
                agent=frame.agent,
                context=frame.context,
                conversation_id=conversation_id,
                output="".join(chunks),
                settings=orchestrator.settings,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
    except (WebSocketDisconnect, _ClientGone):
        # 客户端正常关闭 / 发送时发现已断开：结束协程即可，不记录错误。
        return
    except Exception:
        # 其余异常（含非 JSON 文本导致的解析错误）先落日志再上抛，
        # 交给框架关闭连接；不在此处吞掉，避免故障被静默掩盖。
        logger.exception("WS 聊天处理异常")
        raise
