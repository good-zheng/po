#!/usr/bin/env python
"""续写链路的分层探针：把「连不上」拆成四道门，一次跑完并只打结论。

为什么需要它：管理端创作面板的连接错误现在分三种情形（见 `apps/admin-web` 的
`useNovelRun.ts`），但它们指向三个不同的进程——chat 服务本身、管理端容器到 chat 的
`/ws/chat` 反代、chat 到 Java 的验票通道。浏览器侧只看得见「连接没建起来」，
分不出是哪一层；这个脚本从服务端侧逐层验，几十秒给出「第几层断」的答案。

默认不消耗任何模型额度：匿名连接上那条续写帧根本进不了图（帧级闸门拦下），
带真实票据的连接只验握手、不发 `message` 帧。

密钥纪律：内部令牌只报「配置长度」，票据值与书本正文一律不打；打印的全是
状态码、`Result.code`、布尔结论和长度。

用法（cwd 必须是 `services/chat`，配置从本目录 `.env` 读）：
    .venv/Scripts/python.exe scripts/probe_novel_channel.py --book-id 14
云上那条反代：
    .venv/Scripts/python.exe scripts/probe_novel_channel.py --book-id 14 \\
        --ws wss://<管理端域名>/ws/chat
验完整握手（票据从浏览器 DevTools 的 WS 请求 URL 里复制，60 秒内有效）：
    .venv/Scripts/python.exe scripts/probe_novel_channel.py --book-id 14 --ticket <票据>

退出码：0 = 全部通过；1 = 有 FAIL；2 = 依赖或参数问题。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from urllib.parse import urlencode

try:
    import httpx
    import websockets
except ImportError:  # 依赖装在 chat 的 venv 里，用错解释器时要说清而不是抛栈
    print("需要 httpx 与 websockets：请在 services/chat/.venv 里运行本脚本")
    sys.exit(2)

from app.config import get_settings

OK = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"

# 续写帧的形状与前端一致：bookId 走 context（保留键，不进模型可见文本）
PROBE_CONTENT = "探针：这一帧只用来验闸门，不应进入生成"


class Report:
    """逐层记账，最后按层给结论——排查时先问「第几层 FAIL」而不是看尾巴。"""

    def __init__(self) -> None:
        self.rows: list[tuple[str, str, int, str]] = []

    def add(self, layer: str, status: str, detail: str) -> None:
        print(f"[{status}] {layer}：{detail}")
        self.rows.append((layer, status, len(self.rows), detail))

    def exit_code(self) -> int:
        failed = [r for r in self.rows if r[1] == FAIL]
        print(
            f"\n结论：{len(self.rows) - len(failed)} 层通过，{len(failed)} 层失败"
            + ("；先修第一条失败再看后面的，后面的失败多半是它的连带" if failed else "，链路完整")
        )
        return 1 if failed else 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="续写链路分层探针（不打印密钥）")
    p.add_argument("--book-id", type=int, default=None, help="用于验内网读口的书 id；省略则跳过该层")
    p.add_argument("--ws", default=None, help="WS 地址，默认 ws://127.0.0.1:<PY_SERVER_PORT>/ws/chat")
    p.add_argument("--ticket", default=None, help="真实握手票据：额外验带票握手能否建起连接")
    p.add_argument("--actor-uid", type=int, default=None, help="内网读口带 X-Actor-Uid 时用的作者 id")
    p.add_argument("--timeout", type=float, default=8.0, help="单层网络超时（秒）")
    return p.parse_args()


# ── 第 1 层：chat 进程活着吗 ─────────────────────────────────

def probe_chat_health(rep: Report, chat_base: str, timeout: float) -> None:
    url = f"{chat_base}/api/health"
    try:
        r = httpx.get(url, timeout=timeout)
    except httpx.HTTPError as exc:
        rep.add("1 chat 进程", FAIL, f"{url} 打不通（{type(exc).__name__}）——服务没起、端口不对，或云托管实例已缩容")
        return
    if r.status_code != 200:
        rep.add("1 chat 进程", FAIL, f"{url} 回 {r.status_code}——进程在但路由不对（镜像版本？）")
        return
    body = r.json()
    rep.add(
        "1 chat 进程",
        OK,
        f"agent_core_version={body.get('agent_core_version')}（健康检查不触碰编排，只证明进程存活）",
    )


# ── 第 2/3 层：WS 反代 + 续写闸门 ────────────────────────────

async def _recv_until(ws, wanted: str, timeout: float) -> dict:
    """收到某类帧为止；把中途的其它帧类型攒起来，便于识别「闸门没生效」。"""
    seen: list[str] = []
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout)
        frame = json.loads(raw)
        kind = frame.get("type")
        if kind == wanted:
            return frame
        seen.append(kind or "?")
        if len(seen) > 20:
            raise TimeoutError(f"没等到 {wanted}，前 20 帧是 {seen}")


async def probe_ws_anonymous(rep: Report, ws_url: str, book_id: int | None, timeout: float) -> None:
    try:
        ws = await websockets.connect(ws_url, open_timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - 反代失败的形态太多，异常类型本身才是信息
        rep.add(
            "2 WS 反代",
            FAIL,
            f"匿名连接 {ws_url} 都没建起来（{type(exc).__name__}: {exc}）"
            "——本机查 uvicorn 是否 --host 0.0.0.0；云上查管理端容器的 location ^~ /ws/chat 与 ADMIN_CHAT_UPSTREAM",
        )
        return
    rep.add("2 WS 反代", OK, f"{ws_url} 匿名握手成功（不带票据即可 accept）")

    async with ws:
        await ws.send(json.dumps({"type": "ping", "content": "probe"}))
        try:
            pong = await _recv_until(ws, "pong", timeout)
        except (TimeoutError, asyncio.TimeoutError) as exc:
            rep.add("2 WS 反代", FAIL, f"连上了却收不到 pong（{exc}）——主循环没跑起来，看 chat 日志")
            return
        rep.add("2 WS 反代", OK, f"心跳通了：pong={pong.get('content')!r}")

        if book_id is None:
            rep.add("3 续写闸门", SKIP, "没给 --book-id，无法构造带 bookId 的续写帧")
            return
        # 期望：一帧 error 且连接不断。真收到 run_started 说明这条链路上跑的是
        # 没有闸门的旧代码——匿名对等方此刻就能往别人的书里追加章节。
        await ws.send(
            json.dumps(
                {
                    "type": "message",
                    "content": PROBE_CONTENT,
                    "agent": "novel",
                    "context": {"bookId": str(book_id), "auto": True},
                }
            )
        )
        try:
            gate = await _recv_until(ws, "error", timeout)
        except (TimeoutError, asyncio.TimeoutError) as exc:
            rep.add("3 续写闸门", FAIL, f"续写帧没有立刻回 error（{exc}）——闸门未生效或该帧已进图，会烧模型额度")
            return
        text = gate.get("content") or ""
        if "身份" not in text:
            rep.add("3 续写闸门", FAIL, f"回了 error 但不是闸门那句：{text[:80]!r}")
            return
        # 闸门只拦这一帧、不关连接：再用一次心跳证明整条连接还活着
        await ws.send(json.dumps({"type": "ping", "content": "after-gate"}))
        still = True
        try:
            await _recv_until(ws, "pong", timeout)
        except (TimeoutError, asyncio.TimeoutError):
            still = False
        rep.add(
            "3 续写闸门",
            OK if still else FAIL,
            f"匿名续写帧被 error 拦下且连接未关：{text[:60]!r}"
            + ("" if still else "（拦完把连接也弄断了，客户端其它插槽会话会被牵连）"),
        )


async def probe_handshake_ticket(rep: Report, ws_url: str, ticket: str, timeout: float) -> None:
    url = f"{ws_url}?ticket=<省略>"
    try:
        ws = await websockets.connect(f"{ws_url}?{urlencode({'ticket': ticket})}", open_timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        # 被拒的握手在 accept 之前关闭：真实 uvicorn 把它落成 HTTP 403（websockets 的
        # InvalidStatus），而浏览器只看得见 onerror + close(1006)——4401 那个码过不去
        # HTTP 升级，所以这一层只能从服务端侧验，前端拿不到它。
        status = getattr(getattr(exc, "response", None), "status_code", None)
        rep.add(
            "4 带票握手",
            FAIL,
            f"带票连接没建起来（{type(exc).__name__}"
            + (f" HTTP {status}" if status else "")
            + f"，尝试地址 {url}）——票据多半已过 60 秒；"
            "换一张新票仍如此，则是 chat 验不通 Java 的 /novel/internal/chat-ticket/verify"
            "（第 5 层会指出令牌是否一致）",
        )
        return
    # 刻意不发 message 帧：这条连接已绑定作者，一发续写帧就真的开始生成了
    async with ws:
        await ws.send(json.dumps({"type": "ping", "content": "ticketed"}))
        try:
            await _recv_until(ws, "pong", timeout)
        except (TimeoutError, asyncio.TimeoutError) as exc:
            rep.add("4 带票握手", FAIL, f"握手建起来了却收不到 pong（{exc}）")
            return
    rep.add("4 带票握手", OK, "握手验票通过、连接已绑定该作者（只验握手，未发送生成帧，不消耗额度）")


# ── 第 5 层：chat → Java 的验票通道 ─────────────────────────

def probe_verify_channel(rep: Report, settings, timeout: float) -> None:
    token = settings.internal_token
    if not token:
        rep.add("5 验票通道", FAIL, "PY_SERVER_INTERNAL_TOKEN 未配置——需要身份的帧一律被拒，续写必然连不上")
        return
    rep.add("5 验票通道", OK, f"令牌已配置（长度 {len(token)}，值不外泄）")
    url = f"{settings.api_base_url.rstrip('/')}/novel/internal/chat-ticket/verify"
    try:
        r = httpx.post(url, json={"ticket": "probe-not-a-ticket"},
                       headers={"X-Internal-Token": token}, timeout=timeout)
    except httpx.HTTPError as exc:
        rep.add("5 验票通道", FAIL, f"{url} 打不通（{type(exc).__name__}）——Java 不可达，或地址少了 /api 前缀")
        return
    if r.status_code == 404:
        rep.add("5 验票通道", FAIL, "404——Java 跑的是没有该端点的旧镜像")
        return
    try:
        body = r.json()
    except ValueError:
        rep.add("5 验票通道", FAIL, f"HTTP {r.status_code} 且响应不是 JSON（前面有网关兜底页？）")
        return
    code = body.get("code")
    message = str(body.get("message") or "")
    if body.get("success"):
        # 假票被判成功是安全问题，不是「通了」
        rep.add("5 验票通道", FAIL, f"一张假票竟然验过：code={code}（验票逻辑失效）")
        return
    if "令牌" in message:
        rep.add("5 验票通道", FAIL, f"内网令牌被 Java 拒（message={message!r}）——两侧值不一致，chat 的 PY_SERVER_INTERNAL_TOKEN 必须等于 app.internal-token")
        return
    rep.add("5 验票通道", OK, f"通道可达且令牌被接受：HTTP {r.status_code} code={code} message={message!r}（假票被拒正是期望）")


# ── 第 6 层：内网书本读口（续写第一步要读的东西） ───────────

def probe_book_read(rep: Report, settings, book_id: int, actor_uid: int | None, timeout: float) -> None:
    headers = {"X-Internal-Token": settings.internal_token}
    if actor_uid is not None:
        headers["X-Actor-Uid"] = str(actor_uid)
    url = f"{settings.api_base_url.rstrip('/')}/novel/internal/books/detail"
    try:
        r = httpx.get(url, params={"bookId": book_id}, headers=headers, timeout=timeout)
    except httpx.HTTPError as exc:
        rep.add("6 书本读口", FAIL, f"{url} 打不通（{type(exc).__name__}）")
        return
    try:
        body = r.json()
    except ValueError:
        rep.add("6 书本读口", FAIL, f"HTTP {r.status_code} 非 JSON")
        return
    data = body.get("data") or {}
    if not body.get("success"):
        rep.add(
            "6 书本读口",
            FAIL,
            f"code={body.get('code')} message={body.get('message')!r}"
            + ("（带 X-Actor-Uid 时 403 是归属不符；不带则 Java 整段跳过归属校验——这正是续写帧要求握手身份的原因）"),
        )
        return
    rep.add(
        "6 书本读口",
        OK,
        f"bookId={data.get('bookId')} 章数={data.get('chapterCount')} 标题长度={len(str(data.get('title') or ''))}"
        f"（{'带' if actor_uid is not None else '不带'} X-Actor-Uid；正文不外泄）",
    )


async def main() -> int:
    args = parse_args()
    settings = get_settings()
    chat_base = f"http://127.0.0.1:{settings.port}"
    ws_url = args.ws or f"ws://127.0.0.1:{settings.port}/ws/chat"
    rep = Report()
    print(f"目标：{ws_url} ｜ Java：{settings.api_base_url} ｜ 书：{args.book_id}\n")

    probe_chat_health(rep, chat_base, args.timeout)
    await probe_ws_anonymous(rep, ws_url, args.book_id, args.timeout)
    if args.ticket:
        await probe_handshake_ticket(rep, ws_url, args.ticket, args.timeout)
    else:
        rep.add("4 带票握手", SKIP, "未给 --ticket（真实票据 60 秒过期，只能现场从浏览器复制）")
    probe_verify_channel(rep, settings, args.timeout)
    if args.book_id is not None:
        probe_book_read(rep, settings, args.book_id, args.actor_uid, args.timeout)
    else:
        rep.add("6 书本读口", SKIP, "未给 --book-id")
    return rep.exit_code()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
