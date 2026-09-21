import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_chat_streams_tokens_then_done(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "你好"})
        tokens = ""
        while True:
            frame = websocket.receive_json()
            if frame["type"] == "token":
                tokens += frame["content"]
            elif frame["type"] == "done":
                break
            else:
                pytest.fail(f"unexpected frame: {frame}")
        assert tokens == "你说的是：你好"


def test_chat_pong(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "ping", "content": "1"})
        assert websocket.receive_json() == {"type": "pong", "content": "1"}


def test_chat_invalid_frame_returns_error(client: TestClient) -> None:
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "unknown"})
        frame = websocket.receive_json()
        assert frame["type"] == "error"


def test_chat_disconnect_is_clean(client: TestClient) -> None:
    # The TestClient context exit sends a disconnect and re-raises any
    # unhandled server-side exception, so leaving mid-stream must not fail.
    with client.websocket_connect("/ws/chat") as websocket:
        websocket.send_json({"type": "message", "content": "hi"})
