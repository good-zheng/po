"""一次性探针：把 LangGraph checkpoint id（UUIDv6，时间有序）解码成时间轴。

用途：判断一次失败的 novel 运行里，最后一个 superstep 落盘的时刻与运行开始时刻的
间隔，用来对照 AgentRunner 的 run_timeout_seconds 预算。只读 Redis，不写任何东西。
"""

import datetime as dt
import subprocess
import sys

GREG = 122192928000000000  # 1582-10-15 与 unix 纪元之间以 100ns 计的偏移


def decode(checkpoint_id: str) -> str:
    # UUIDv6 布局：60 位时间戳被拆成 time_high(高 32 位) / time_mid(中 16 位) /
    # time_low(低 12 位，紧跟版本号的那半字节)
    h = checkpoint_id.replace("-", "")
    ts = int(h[0:8], 16) << 28 | int(h[8:12], 16) << 12 | int(h[13:16], 16)
    unix = (ts - GREG) / 1e7
    return dt.datetime.fromtimestamp(unix, dt.timezone(dt.timedelta(hours=8))).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )[:-3]


def main(thread: str) -> None:
    out = subprocess.run(
        ["docker", "exec", "po-redis", "redis-cli", "--scan", "--pattern", f"checkpoint:{thread}:*"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(":")
        rows.append((decode(parts[-1]), ":".join(parts[2:-1]), parts[-1]))
    rows.sort()
    for when, ns, cid in rows:
        print(f"{when}  {ns:<40} {cid}")
    if len(rows) > 1:
        first = dt.datetime.strptime(rows[0][0], "%Y-%m-%d %H:%M:%S.%f")
        last = dt.datetime.strptime(rows[-1][0], "%Y-%m-%d %H:%M:%S.%f")
        print(f"\n首个 checkpoint 到最后一个：{(last - first).total_seconds():.1f}s")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "3b919bfef8c345f6a39a87d353b6a446")
