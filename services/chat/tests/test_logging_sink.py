"""日志落盘 sink 的回归测试（对应 2026-10-12 novel 长跑「静默断连」事故）。

事故现象是「连接 open 过、再没有任何终态帧就断了」，而服务端磁盘上零记录——
uvicorn 只给 ``uvicorn*`` 配了 stderr handler，``app.*`` 的日志靠 logging 的
lastResort 兜底打到终端，进程一没就查不到。这里的用例锁住三件事：

1. ``app.*`` 的记录真的会落到文件（旧行为：文件根本不存在）；
2. 挂 handler 是幂等且可关闭的（重复 ``create_app`` 不重复写，空路径完全不动 root）；
3. WS 在「客户端断开」这条静默分支上留下一行连接结束记录（旧行为：直接 return，
   日志里什么都没有）——有这行 = 链路/客户端先断，没这行 = 服务端进程自己没了。

用例都会改动进程级 logging 状态，故统一用 ``restore_logging`` 夹具收尾。
"""

from __future__ import annotations

import asyncio
import logging
import sys

import pytest
from fastapi import WebSocketDisconnect

from app.config import get_settings
from app.logging_setup import _MARK, _MARK_STREAM, configure_logging
from app.main import create_app
from app.routers import ws as ws_router


@pytest.fixture(autouse=True)
def restore_logging():
    """清掉用例挂上的 handler，并把 root 级别与 propagate 恢复原状。"""
    root_before = list(logging.root.handlers)
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_before = list(uvicorn_logger.handlers)
    uvicorn_propagate_before = uvicorn_logger.propagate
    level_before = logging.root.level
    yield
    for handler in [h for h in logging.root.handlers if h not in root_before]:
        logging.root.removeHandler(handler)
        handler.close()
    for handler in [h for h in uvicorn_logger.handlers if h not in uvicorn_before]:
        uvicorn_logger.removeHandler(handler)
    uvicorn_logger.propagate = uvicorn_propagate_before
    logging.root.setLevel(level_before)


def read_log(path) -> str:
    return path.read_text(encoding="utf-8")


def test_app_logger_record_lands_in_file(tmp_path) -> None:
    target = tmp_path / "logs" / "chat.log"

    handler = configure_logging(str(target))

    assert handler is not None
    assert target.exists()  # 旧行为：这里连文件都不会被创建
    logging.getLogger("app.agent").error("装配降级：checkpointer=memory")
    # 生命周期行都是 INFO（root 默认 WARNING 会把它们挡掉），落盘判读全靠这几行
    logging.getLogger("app.main").info("chat 启动（pid=4242）")
    handler.flush()
    content = read_log(target)
    assert "装配降级" in content
    assert "chat 启动" in content


def test_uvicorn_record_lands_in_file_exactly_once(tmp_path) -> None:
    target = tmp_path / "chat.log"
    handler = configure_logging(str(target))
    assert handler is not None

    logging.getLogger("uvicorn.error").info("Finished server process [12345]")
    handler.flush()

    content = read_log(target)
    assert "Finished server process" in content
    # uvicorn 的 logger 默认 propagate=False（记录不上浮到 root）；本模块显式保持
    # 这一点并直接并挂同一个 handler。若上浮没被断掉，同一条会经 root 再落一遍。
    assert logging.getLogger("uvicorn").propagate is False
    assert content.count("Finished server process") == 1


def test_stderr_handler_added_for_terminal_visibility(tmp_path) -> None:
    def ours(mark: str) -> list[logging.Handler]:
        # pytest 的日志插件本身往 root 挂了 StreamHandler，所以只数带本模块标记的。
        return [h for h in logging.root.handlers if getattr(h, _MARK, None) == mark]

    assert ours(_MARK_STREAM) == []
    assert configure_logging(str(tmp_path / "chat.log")) is not None

    # root 一旦有了 handler，logging 的 lastResort 兜底就失效——不补 stderr 的话
    # app.* 的日志会从终端消失，比原来更难用。
    assert len(ours(_MARK_STREAM)) == 1
    assert logging.root.level <= logging.INFO

    # 重复装配（--reload 的子进程、多个 create_app）不再叠加第二个 stderr handler
    configure_logging(str(tmp_path / "other.log"))
    assert len(ours(_MARK_STREAM)) == 1


def test_existing_console_handler_is_not_duplicated(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 真实进程里 redisvl/aurelio_sdk 在 import 时会 logging.basicConfig，给 root 挂
    # 一个写 sys.stderr 的 handler。此时再补一个，终端每行都会打两遍。
    console = logging.StreamHandler(sys.stderr)
    logging.root.addHandler(console)
    try:
        assert configure_logging(str(tmp_path / "chat.log")) is not None
        assert not any(getattr(h, _MARK, None) == _MARK_STREAM for h in logging.root.handlers)
    finally:
        logging.root.removeHandler(console)


def test_configuring_twice_does_not_duplicate_lines(tmp_path) -> None:
    target = tmp_path / "chat.log"
    first = configure_logging(str(target))
    handlers_before = list(logging.root.handlers)
    second = configure_logging(str(target))

    assert second is first
    assert logging.root.handlers == handlers_before
    logging.getLogger("app.routers.ws").error("同一条只写一次")
    first.flush()
    assert read_log(target).count("同一条只写一次") == 1


def test_empty_log_file_leaves_logging_untouched(tmp_path, caplog: pytest.LogCaptureFixture) -> None:
    handlers_before = list(logging.root.handlers)
    level_before = logging.root.level

    with caplog.at_level(logging.WARNING):
        assert configure_logging("") is None

    assert logging.root.handlers == handlers_before
    assert logging.root.level == level_before
    assert not (tmp_path / "chat.log").exists()
    # 空路径是「设计上关掉」而不是「试着打开然后失败」：走后者会每进程启动都刷一条
    # 不可写告警，把真正的落盘故障淹掉。
    assert caplog.records == []


def test_unwritable_target_warns_instead_of_raising(tmp_path, caplog: pytest.LogCaptureFixture) -> None:
    blocker = tmp_path / "not-a-dir"
    blocker.write_text("占位：把它当父目录必然失败", encoding="utf-8")
    handlers_before = list(logging.root.handlers)

    with caplog.at_level(logging.WARNING):
        assert configure_logging(str(blocker / "chat.log")) is None

    assert "不可写" in caplog.text
    # 挂了一半的 handler 不能留在 root 上（否则启动失败还会污染后续日志）
    assert logging.root.handlers == handlers_before


def test_create_app_wires_the_sink(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    # 真实运行路径：默认 .env 之外只靠 Settings 的默认值就会落盘；这里把路径换成
    # 临时目录，断言 create_app() 确实挂上了指向它的文件 handler。
    target = tmp_path / "wired.log"
    monkeypatch.setenv("PY_SERVER_LOG_FILE", str(target))
    monkeypatch.delenv("PY_SERVER_LOG_LEVEL", raising=False)
    get_settings.cache_clear()

    create_app()

    logging.getLogger("app.main").info("create_app 已接线")
    assert target.exists()
    assert "create_app 已接线" in read_log(target)


def test_client_disconnect_leaves_a_connection_end_line(
    caplog: pytest.LogCaptureFixture,
) -> None:
    class _Socket:
        async def receive_json(self) -> dict:
            raise WebSocketDisconnect(code=1006)

    with caplog.at_level(logging.INFO, logger="app.routers.ws"):
        # 走到 except (WebSocketDisconnect, _ClientGone) 分支：orchestrator/actor 用不到
        asyncio.run(ws_router._loop(_Socket(), None, None))  # type: ignore[arg-type]

    # 旧行为：这条分支静默 return，日志里一行都没有——于是「进程被杀」与
    # 「客户端先断」在事后完全无法区分。
    assert "WS 连接结束" in caplog.text
    assert "1006" in caplog.text
