#!/usr/bin/env python
"""小说生成链路的命令行驱动（走宿主父图：路由 → novel 子图 → resume 归档）。

为什么需要它：这是一条不打浏览器、不经 WS 帧协议的 headless 通道，用于真机
端到端实测与成本核对（消耗真实模型额度，所以只在作者要求时跑）。它走的路径与
前端 `/ws/chat` 完全同构——`run(agent="novel")` 仍在父图上执行，由 route 节点
按 `forced_agent` 确定性委托 novel 子图，`resume` 打回同一张父图、共用同一个
thread_id 命中检查点。历史上这里刻意不传 `agent`（当时传了会直连子图，
而子图没有 checkpointer，归档那次 interrupt 在 WS 上永远确认不了）；
父图统一后这条限制不存在了，传 `agent` 反而更稳：不依赖路由相似度。

用法（cwd 必须是 services/chat，pydantic-settings 从本目录 .env 读配置）：
    .venv/Scripts/python.exe scripts/run_novel_generation.py --chapters 3
输出：终端只打事件类型与摘要，全文写 ``--out``（默认 .tmp-novel-run.md）。
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import uuid
from pathlib import Path

from app.agent import build_orchestrator
from po_agent_core.events import EventType
from po_agent_novel import build_novel_agent, set_actor

APPROVE = "yes"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="生成 N 章小说并落库")
    p.add_argument("--idea", default="构思一个故事并写出前三章", help="立意输入（一句话或简介）")
    p.add_argument("--chapters", type=int, default=3)
    p.add_argument("--words", type=int, default=1200)
    p.add_argument("--out", default=".tmp-novel-run.md")
    p.add_argument("--max-resumes", type=int, default=6, help="最多确认几次 interrupt")
    return p.parse_args()


async def drive(o, idea, tid, log, max_resumes):
    """走宿主的真实路径：父图 run（`agent="novel"` 确定性委托）+ resume 确认归档。

    ``agent`` 在这里是安全的，因为 :meth:`Orchestrator.run` 并不换图：它把插槽名
    塞进 ``forced_agent``，仍然 stream 父图，所以 interrupt 落在父图持有的
    checkpointer 里，``resume`` 打回父图就能确认——与浏览器那条链路一致。
    直连 ``agents["novel"].graph`` 才是跑不通的：``build_novel_graph`` 刻意不挂
    checkpointer（作为子节点时由父图供给），子图自己跑起来的 interrupt 无从 resume。
    """
    async def stream(agen, label):
        interrupted = False
        async for e in agen:
            name = e.type if isinstance(e.type, str) else e.type.value
            if name == EventType.INTERRUPT.value:
                interrupted = True
            if name in (EventType.TEXT_MESSAGE_CONTENT.value, EventType.RUN_ERROR.value):
                print(f"[{label}] {name}: {e.content[:80]}")
                log.write(f"\n## {name}\n{e.content}\n")
            else:
                print(f"[{label}] {name}: {e.content[:120]}")
                log.write(f"\n## {name}\n{e.content}\n")
        return interrupted

    hung = await stream(o.run(idea, conversation_id=tid, agent="novel"), "run")
    rounds = 0
    while hung and rounds < max_resumes:
        rounds += 1
        print(f">>> 第 {rounds} 次确认（{APPROVE}）")
        hung = await stream(o.resume(tid, APPROVE), f"resume{rounds}")
    return rounds


async def main() -> int:
    args = parse_args()
    tid = uuid.uuid4().hex
    print(f"thread_id={tid}")
    out_path = Path(args.out)
    out_path.write_text(f"# 生成运行 {tid}\n\n立意：{args.idea}\n\n", encoding="utf-8")

    o = await build_orchestrator(
        # 章数/字数与默认值不同才显式重建插槽：默认（3 章 / 1200 字）直接用宿主装配的那份
        agents=None
        if (args.chapters == 3 and args.words == 1200)
        else [build_novel_agent(chapter_count=args.chapters, chapter_words=args.words)]
    )
    try:
        if "novel" not in o.agents:
            print("装配里没有 novel 插槽（多半是 po-agent-novel 没装或装配失败），中止")
            return 2
        # 作者作用域：内网写回按 uid 校验书本归属
        set_actor(int(os.environ.get("NOVEL_AUTHOR_ID", "0") or "0"))
        with out_path.open("a", encoding="utf-8") as log:
            rounds = await drive(o, args.idea, tid, log, args.max_resumes)
        print(f"\n确认轮数={rounds}；全文与事件已写入 {out_path.resolve()}")
        return 0
    finally:
        await o.aclose()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
