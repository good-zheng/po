import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.schemas import WSInFrame, WSOutFrame

router = APIRouter()


async def _send_frame(websocket: WebSocket, frame: WSOutFrame) -> None:
    await websocket.send_json(frame.model_dump())


@router.websocket("/ws/chat")
async def chat(websocket: WebSocket) -> None:
    """Echo-style streaming chat endpoint.

    Inbound frames: {"type": "message", "content": "..."} or {"type": "ping"}.
    Outbound frames: token chunks followed by done, or pong/error.
    """
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_json()
            try:
                frame = WSInFrame.model_validate(raw)
            except ValidationError:
                await _send_frame(websocket, WSOutFrame(type="error", content="invalid frame"))
                continue

            if frame.type == "ping":
                await _send_frame(websocket, WSOutFrame(type="pong", content=frame.content))
                continue

            reply = f"你说的是：{frame.content}"
            for char in reply:
                await _send_frame(websocket, WSOutFrame(type="token", content=char))
                await asyncio.sleep(0.02)
            await _send_frame(websocket, WSOutFrame(type="done"))
    except WebSocketDisconnect:
        return
