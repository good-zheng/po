#!/usr/bin/env python
"""一次性验证：真实的 ``app.main:app`` 生命周期是否把启动/关闭行落到磁盘。

为什么单独跑它：pytest 的 conftest 刻意把 ``PY_SERVER_LOG_FILE`` 置空（否则每个用例
都会往仓库里建日志、并给 root 叠加 handler），所以「生产默认值真的会落盘、lifespan
两行真的写进去、终端不重复打」这三件事只能在测试之外验一次。这里不监听端口、不接
WS 流量，只走 ``lifespan_context``，用的却是生产同一份模块级 ``app = create_app()``
与同一份 ``services/chat/.env``。

会真实连一次 Redis checkpointer（读配置，不调模型、不花额度）。

用法（cwd 必须是 services/chat，pydantic-settings 从本目录 .env 读配置）：
    .venv/Scripts/python.exe scripts/verify_log_sink.py
退出码 0 = 启动行、装配行、关闭行都在落盘文件里，且文件里没有凭据形态的值。

注意：本文件位于 uvicorn ``--reload`` 的监视目录（``services/chat``）内，chat 正在
长跑时保存它会掐断那一轮——这也是这次事故排查中发现的结构性坑之一。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

CHAT = Path(__file__).resolve().parents[1]
LOG = CHAT.parents[1] / ".tmp" / "logs" / "chat-sink-verify.log"

# 必须在 import app.main 之前设好：模块级 create_app() 会读 Settings 并接线日志。
os.environ["PY_SERVER_LOG_FILE"] = str(LOG)
os.environ.pop("PY_SERVER_LOG_LEVEL", None)
sys.path.insert(0, str(CHAT))
os.chdir(CHAT)

if LOG.exists():
    LOG.unlink()

from app.main import app  # noqa: E402  —— 接线发生在 import 时，必须先于本行

# 落盘里必须出现的三行（缺任何一行都说明 sink 没真正接上）
NEEDLES = ("chat 启动（pid=", "Orchestrator 就绪", "chat 关闭（pid=")
# 绝对不该出现的凭据形态（只按形态匹配，不打印命中内容）
LEAK_MARKS = ("api_key", "sk-", "akid", "eyJ", "bearer ")


async def main() -> int:
    async with app.router.lifespan_context(app):
        pass
    text = LOG.read_text(encoding="utf-8")
    print(f"--- {LOG} ---")
    print(text)
    ok = True
    for needle in NEEDLES:
        if needle not in text:
            print(f"缺少：{needle}")
            ok = False
    for mark in LEAK_MARKS:
        if mark in text.lower():
            print(f"疑似凭据泄露：{mark}")
            ok = False
    print("落盘验证：" + ("通过" if ok else "不通过"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
