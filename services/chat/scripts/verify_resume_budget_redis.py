"""不打模型、只验一件事：恢复轮能不能从**真实 Redis 检查点**里读回插槽名。

为什么单独要有这个脚本：:data:`app.agent._RUN_BUDGET_BY_AGENT` 给 novel 的专属预算，
在恢复轮上是靠 :meth:`Orchestrator._forced_agent` 从 checkpoint 里读回 ``forced_agent``
才生效的。单测用的是 ``InMemorySaver``，而线上是 ``RedisSaver``——两者对
``aget_state`` 的语义并不天然相同，更要紧的是 :func:`app.agent._init_checkpointer`
在连不上 Redis 时会**静默降级成 memory**（这正是本仓库记过的那类坑：检查点看起来能用，
进程一重启就没了）。所以这里第一件事就是把 saver 的真实类型钉住，再验读回。

全程用离线装配（novel 插槽跑 ``OfflineNovelModel``、chitchat 跑 ``EchoChatModel``），
不消耗任何模型额度，也不落库。

用法（cwd 必须是 services/chat，pydantic-settings 从本目录 .env 读 Redis 配置）：
    NOVEL_PERSIST_ENABLED=false .venv/Scripts/python.exe -X utf8 scripts/verify_resume_budget_redis.py
退出码：0=断言全过；1=降级成了非 Redis 检查点（结论不可信）；2=读回或预算判错。
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid

# 必须早于任何 app / 领域包导入：归档那一步会按这个开关决定走 HTTP 还是留在进程内
os.environ.setdefault("NOVEL_PERSIST_ENABLED", "false")

from app.agent import EchoChatModel, build_orchestrator  # noqa: E402
from po_agent_core.config import AgentCoreSettings  # noqa: E402
from po_agent_core.events import EventType  # noqa: E402
from po_agent_novel import build_novel_agent  # noqa: E402


def _offline_settings() -> AgentCoreSettings:
    """novel 插槽的离线装配：不给 key，装配内部必然退到 OfflineNovelModel。"""
    return AgentCoreSettings(_env_file=None, llm_api_key="")


async def main() -> int:
    tid = uuid.uuid4().hex
    o = await build_orchestrator(
        chat_model=EchoChatModel(),
        agents=[build_novel_agent(_offline_settings())],
    )
    try:
        saver = type(o.graph.checkpointer).__name__
        print(f"checkpointer 实际类型：{saver}")
        if "Redis" not in saver:
            print("结论：不是 Redis 检查点（多半是连不上被降级），本脚本的结论不成立")
            return 1

        hung = False
        async for event in o.run("构思一个故事并写出第一章", conversation_id=tid, agent="novel"):
            name = event.type if isinstance(event.type, str) else event.type.value
            if name == EventType.INTERRUPT.value:
                hung = True
            if name == EventType.RUN_ERROR.value:
                print(f"发起轮就出错：{event.content} {event.payload}")
                return 2
        if not hung:
            print("结论：离线链路没在 interrupt 上挂起，测不到恢复轮（装配变了？）")
            return 2

        # 恢复轮拿到的预算，取决于这一步能不能读回插槽名
        config = o._config(tid)
        forced = await o._forced_agent(config)
        budget = o._run_budget(forced)
        print(f"读回 forced_agent={forced!r} 恢复轮预算={budget}s")
        if forced != "novel" or budget != 3600.0:
            print("结论：没读回插槽名，或预算退回了默认值 → 长批次的恢复轮仍会被掐成「运行超时」")
            return 2

        # 反向对照：一条从没点名的线程读回来必须是 None，否则「读回」是恒真而非真读
        none_forced = await o._forced_agent(o._config(uuid.uuid4().hex))
        print(f"陌生线程读回={none_forced!r} 默认预算={o._run_budget(none_forced)}s")
        if none_forced is not None or o._run_budget(none_forced) != o.runner.timeout_seconds:
            print("结论：陌生线程也读出了插槽名，这条断言失去意义")
            return 2

        finished = False
        async for event in o.resume(tid, "yes"):
            name = event.type if isinstance(event.type, str) else event.type.value
            if name == EventType.RUN_ERROR.value:
                print(f"恢复轮出错：{event.content} {event.payload}")
                return 2
            if name == EventType.RUN_FINISHED.value:
                finished = True
        print("结论：真实 Redis 检查点上，恢复轮读回了插槽并按专属预算跑完收尾" if finished else "结论：恢复轮没收尾")
        return 0 if finished else 2
    finally:
        await o.aclose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
