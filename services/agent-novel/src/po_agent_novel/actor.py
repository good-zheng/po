"""连接级作者身份：把 WS 握手验出的 uid 交给 HTTP 数据层带上。

为什么是 contextvar 而不是构造参数：``HttpNovelStore`` / ``HttpCanonStore`` 在装配期建一次、
被所有连接共享（见 ``agent.build_novel_agent`` 与宿主的 lifespan），而「这一帧是谁在读」是
per-connection 的——塞进构造函数等于让第一个连上的作者拥有所有连接的读视野。contextvar
由 asyncio 按任务复制，A 连接的 ``set`` 不会串到 B 连接。

为什么不配票据就拒绝：Java 侧的归属闸门是「带了 ``X-Actor-Uid`` 才校验」，因为生成链路
（``novel`` 插槽）此刻没有终端用户在场的概念。所以本模块的默认值 ``None`` 是**有意**的
放行态，而不是漏配——真正的把关在握手层（chat 服务 ``app/ws_auth.py``）：
novel-chat 插槽没有身份时那一帧根本不会进图。

这里刻意不叫 ``principal``、也不放 role/权限：唯一用途是给正典读口盖一个归属章，
多带字段只会诱使后来者把它当授权系统用。
"""

from __future__ import annotations

from contextvars import ContextVar, Token

_actor_uid: ContextVar[int | None] = ContextVar("po_agent_novel_actor_uid", default=None)


def set_actor(uid: int | None) -> Token[int | None]:
    """绑定当前上下文的作者 uid，返回可用于复原的 token。"""
    return _actor_uid.set(uid)


def current_actor() -> int | None:
    """当前上下文的作者 uid；``None`` 表示无终端用户在场的内部调用。"""
    return _actor_uid.get()


def reset_actor(token: Token[int | None]) -> None:
    """复原 :func:`set_actor` 之前的值。"""
    _actor_uid.reset(token)


__all__ = ["current_actor", "reset_actor", "set_actor"]
