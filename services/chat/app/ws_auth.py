"""WS 握手的身份层：把一次性票据换成「这一连接代表哪位作者」。

为什么需要这一层：``/ws/chat`` 的 novel-chat 插槽会把某本书的正典拼进注入块，而 ``bookId``
是客户端在帧里提供的——握手不认人时，任意 WS 对等方都能拿别人的 bookId 读到别人的正典
（PRD §15.13 偏差 #12）。

为什么是票据而不是把用户 JWT 直接拼在 query 上：浏览器与微信小程序都不能给 WebSocket 握手
带请求头，而 query 会被网关访问日志原样留存——把 24 小时有效期的会话令牌放进日志，等于把
长期凭据交给日志系统。口径与 talk 模块的 ASR 票据一致：客户端先用会话令牌换一张 60 秒的
一次性票（``GET /api/novel/chat-ticket``），握手只带票。

为什么交回 Java 验而不是本服务自验：票据与用户 JWT 同钥签名，让 Python 自己校验就意味着把
``jwt.secret`` 分发到第二个进程（多一处密钥，且两处都能签）。本服务已经持
``X-Internal-Token`` 打这条内网通道，验票顺路，代价只是每次握手一次内网往返。

**失败一律按「没有身份」处理**：网络抖动、后端业务错误、载荷形状不对都不放行。这一层的
用途是给 novel-chat 把关，把它做成 best-effort 等于没有。
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

# 需要身份的插槽。刻意只收 novel-chat：其余插槽（cooking / talk / chitchat）的现网客户端
# 还没有发票据的流程，一刀切强制会在它们重新发版之前直接断掉聊天（PRD §15.16）。
# 生成用的 novel 插槽不在这里——它读的是本轮自己刚归档的书，不带别人的 bookId 进来。
AUTH_REQUIRED_AGENTS: frozenset[str] = frozenset({"novel-chat"})

VERIFY_PATH = "/novel/internal/chat-ticket/verify"


@dataclass(frozen=True, slots=True)
class WsActor:
    """握手票据解析出的作者身份（Java 侧的 user id，正典读口的归属尺子）。"""

    uid: int


def ticket_from(websocket: object) -> str | None:
    """从握手 URL 的 query 里取票据。

    单独一个函数是为了把「星型取值」这件事收在一处：Starlette 的 ``query_params`` 是
    MultiDict，同名多次时取第一个即可，而缺参与空串在这里同义（都等于「没带票」）。
    """
    params = getattr(websocket, "query_params", None)
    if not params:
        return None
    raw = params.get("ticket")
    return raw.strip() if isinstance(raw, str) and raw.strip() else None


async def resolve_actor(
    ticket: str | None,
    settings: Settings | None = None,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> WsActor | None:
    """校验票据并换回作者身份；无票、票无效、后端不可达都返回 ``None``。

    ``transport`` 只为可测性存在（与 novel 的 HTTP 数据层同一套做法）：验票要走真实网络，
    用例不该为此打桩整个 ``httpx.AsyncClient``。
    """

    if not ticket:
        return None
    conf = settings or get_settings()
    if not conf.internal_token:
        # 不静默退化成「当作匿名」之外的事：配置缺失时 novel-chat 会连不上，日志要说清原因
        logger.warning("PY_SERVER_INTERNAL_TOKEN 未配置，握手票据无法校验（novel-chat 将拒连）")
        return None
    url = f"{conf.api_base_url.rstrip('/')}{VERIFY_PATH}"
    try:
        async with httpx.AsyncClient(
            timeout=conf.ticket_timeout_seconds, transport=transport
        ) as client:
            response = await client.post(
                url, json={"ticket": ticket}, headers={"X-Internal-Token": conf.internal_token}
            )
            response.raise_for_status()
            body = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("握手票据校验调用失败：%s", exc)
        return None
    if not isinstance(body, dict) or not body.get("success", False):
        logger.warning("握手票据被拒：%s", (body or {}).get("message") if isinstance(body, dict) else body)
        return None
    data = body.get("data")
    uid = data.get("uid") if isinstance(data, dict) else None
    if isinstance(uid, bool) or not isinstance(uid, int):
        logger.warning("握手票据校验返回的 uid 不是整数：%r", uid)
        return None
    return WsActor(uid=uid)


@contextmanager
def actor_scope(uid: int | None) -> Iterator[None]:
    """把作者身份绑进当前连接的任务上下文，供 novel 数据层带上 ``X-Actor-Uid``。

    刻意延迟导入：``po-agent-novel`` 是可装卸插槽（宿主装配失败也不阻断启动，见
    ``app/agent.py``），在模块级导入会让没装它的部署直接起不来。没装时这里等于空操作——
    反正没有 novel 插槽会读到这个上下文。

    范围是整条连接：票据只在握手时校验一次，之后所有帧共用同一身份。
    这是票据那 60 秒 TTL 的真实语义——它守的是「能不能建立这条连接」，
    连接建立后中途过期不会重验（长连接上的重连由客户端负责取新票）。
    """
    try:
        from po_agent_novel import reset_actor, set_actor
    except ImportError:  # pragma: no cover - 取决于可选依赖是否安装
        yield
        return
    token = set_actor(uid)
    try:
        yield
    finally:
        reset_actor(token)
