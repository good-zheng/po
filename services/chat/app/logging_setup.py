"""把日志落到磁盘，让「进程静默退出」与「连接没收到终态帧就断」变成可归因事件。

为什么需要它：uvicorn 的默认 logging 配置只给 ``uvicorn`` / ``uvicorn.error`` /
``uvicorn.access`` 挂了 stderr handler；``app.*`` 与 ``po_agent_*`` 的记录要么走
logging 的 lastResort 兜底，要么撞上第三方在 import 时 ``basicConfig`` 挂到 root 的
stderr handler（本项目里是 redisvl 依赖的 ``aurelio_sdk``）——总之**没有任何一份落到
磁盘**。终端一关（或进程被杀）就什么都不剩。2026-10-12 的 novel 长跑事故正是这样：
进程在 ``write`` 节点在飞时整体退出，客户端只看到「open 之后连接断开」，服务端磁盘上
零记录，「谁结束了进程」无从判定。

落盘后的判读方式（本模块与 lifespan/WS 生命周期日志共同构成）：

- 有 ``chat 关闭`` 这一行：优雅退出（Ctrl+C、``--reload`` 重启、容器收到信号）；
- 日志戛然而止、没有关闭行：进程被硬杀或崩溃；
- 连接结束行（``WS 连接结束``）出现而本轮没有 ``done``：是链路/客户端先断；
- 两者都没有而 checkpoint 停在中途：服务端进程本身没了。

只落诊断所需的结构化事实，不落凭据：票据、token、``AGENT_CORE_*`` 的值一律不进日志。
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path

# 5MB × 5 份：本机一整天长跑的 WS 生命周期与异常堆栈够用，又不致于吃满磁盘。
_MAX_BYTES = 5 * 1024 * 1024
_BACKUP_COUNT = 5
_FORMAT = "%(asctime)s %(levelname)-8s %(name)s | %(message)s"
# 打在自己 handler 上的标记：判断「本模块是否已经挂过」不能靠类型匹配——pytest 的
# 日志插件、容器里的 json-file driver 都可能已经在 root 上放了 StreamHandler。
_MARK = "_po_chat_sink"
_MARK_FILE = "file"
_MARK_STREAM = "stream"


def _already_mounted(mark: str) -> bool:
    return any(getattr(h, _MARK, None) == mark for h in logging.root.handlers)


def configure_logging(log_file: str, level: str = "INFO") -> logging.Handler | None:
    """给 root（以及 ``uvicorn``）挂一个滚动文件 handler，返回该 handler。

    ``log_file`` 为空字符串即整体关闭落盘，且不改动 root logger——测试与「只想看
    stderr」的场景走这条分支，行为与本模块存在之前完全一致。

    落盘失败（目录不可写、磁盘满、容器只读根）只 warn 不抛：日志是诊断手段，
    不能因为它把服务启动搞挂。

    幂等：同一进程里重复 ``create_app()``（用例、``--reload`` 的子进程重导入）
    命中同一个文件路径时复用已挂的 handler，不会把每一行写两遍。
    """
    if not log_file:
        return None
    target = Path(log_file)
    resolved = target.resolve()
    for handler in logging.root.handlers:
        base = getattr(handler, "baseFilename", None)
        if getattr(handler, _MARK, None) == _MARK_FILE and base is not None and Path(base).resolve() == resolved:
            return handler
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.handlers.RotatingFileHandler(
            target, maxBytes=_MAX_BYTES, backupCount=_BACKUP_COUNT, encoding="utf-8"
        )
    except OSError as exc:
        logging.getLogger(__name__).warning(
            "日志文件 %s 不可写：本次运行只输出到 stderr，故障将无法事后归因（%s）", target, exc
        )
        return None
    handler.setLevel(level.upper())
    handler.setFormatter(logging.Formatter(_FORMAT))
    setattr(handler, _MARK, _MARK_FILE)
    logging.root.addHandler(handler)
    # uvicorn 的 logger 是 propagate=False，自己的记录不会上浮到 root，所以直接并挂
    # 同一个 handler 拿到启动/关闭/重载行。同时把 propagate 显式断掉：万一这个进程里
    # 没跑过 uvicorn 的 dictConfig（测试、嵌入式用法）它就是默认 True，同一条记录会
    # 经 root 再落一遍文件。
    uvicorn_logger = logging.getLogger("uvicorn")
    if handler not in uvicorn_logger.handlers:
        uvicorn_logger.addHandler(handler)
    uvicorn_logger.propagate = False
    # root 默认 WARNING：装配信息与 WS 生命周期都是 INFO，不降级别就落不下来。
    if logging.root.level > handler.level:
        logging.root.setLevel(handler.level)
    # root 一旦有了 handler，logging 的 lastResort 兜底就不再兜底——不补 stderr 的话
    # app.* 的日志会从终端消失，比原来更难用。
    # 但只补「确实没有控制台」的情况：``redisvl``/``aurelio_sdk`` 在 import 时会调
    # ``logging.basicConfig`` 给 root 挂一个 stderr handler（顺带把 root 降到 INFO），
    # 再挂一个就是每行终端打两遍。
    if not (_already_mounted(_MARK_STREAM) or _has_console_handler()):
        stream = logging.StreamHandler()
        stream.setLevel(handler.level)
        stream.setFormatter(logging.Formatter(_FORMAT))
        setattr(stream, _MARK, _MARK_STREAM)
        logging.root.addHandler(stream)
    return handler


def _has_console_handler() -> bool:
    """root 上是否已有写 sys.stderr / sys.stdout 的控制台 handler。"""
    for h in logging.root.handlers:
        stream = getattr(h, "stream", None)
        if stream is sys.stderr or stream is sys.stdout:
            return True
    return False
