"""N6 长测监控：把装配事件汇总成「注入 token / 裁剪 / 降级」三类指标。

统计口径全部来自链路已经在发的事件（`plan_compiled` / `context_compiled` /
`chat_context_compiled` 与对应的 `*_failed`），因此它既能离线跑（内存库 + 估算 token，
零模型消耗），也能在真跑 50 章时接同一份事件流，两套数字可比。

刻意**不**在这里编造耗时与模型计费：宿主目前没有发这两类事件，等真接上再补，
不要用估算值冒充监控。
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Mapping

#: PRD §6 的四层预算总和，也是 §12 的「P95 注入 ≤ 4k」那条退出条件的尺子。
INJECTION_LIMIT_TOKENS = 4000

#: stage 名 → 装配路径。三条路径的预算与用途不同，混在一起算 P95 没有意义：
#: 计划侧是全量 as-of 视图（判「登记过没有」），写作侧按场景卡实体收窄，对话侧带参照章尾段。
INJECTION_STAGES: dict[str, str] = {
    "plan_compiled": "plan",
    "context_compiled": "write",
    "chat_context_compiled": "chat",
}

#: 失败留痕与成功事件刻意异名（§15.13 偏差 #9），这里同步分流。
DEGRADATION_STAGES: dict[str, str] = {
    "plan_context_failed": "plan",
    "context_failed": "write",
    "chat_context_failed": "chat",
}

_TIER_KEYS = ("world", "tier1", "tier2", "openForeshadows", "dropped", "refs")


@dataclass(slots=True)
class InjectionSample:
    """一次装配的读数。`chapter` 在对话侧取 `as_of`（那轮讨论没有「本章」）。"""

    path: str
    chapter: int
    tokens: int
    tiers: dict[str, int] = field(default_factory=dict)
    narrowed: bool | None = None
    empty_by_entities: bool | None = None

    @property
    def over_limit(self) -> bool:
        return self.tokens > INJECTION_LIMIT_TOKENS


@dataclass(slots=True)
class DegradationSample:
    path: str
    chapter: int


def percentile(values: list[int], p: float) -> int:
    """最近秩（ceil(p·n)）：样本少时也给出整数，报告里不必解释插值。"""
    if not values:
        return 0
    ordered = sorted(values)
    rank = max(1, math.ceil(p * len(ordered)))
    return ordered[min(rank, len(ordered)) - 1]


class RunMetrics:
    """按 `payload["stage"]` 认领事件；不认识的一律返回 `False` 让调用方继续透传。"""

    def __init__(self) -> None:
        self.injections: list[InjectionSample] = []
        self.degradations: list[DegradationSample] = []
        self.ignored = 0

    def observe(self, payload: Mapping[str, Any]) -> bool:
        stage = payload.get("stage")
        if not isinstance(stage, str):
            self.ignored += 1
            return False
        if stage in INJECTION_STAGES:
            self.injections.append(self._injection(INJECTION_STAGES[stage], payload))
            return True
        if stage in DEGRADATION_STAGES:
            self.degradations.append(
                DegradationSample(
                    path=DEGRADATION_STAGES[stage],
                    chapter=_as_int(payload.get("chapter"), default=0),
                )
            )
            return True
        self.ignored += 1
        return False

    def _injection(self, path: str, payload: Mapping[str, Any]) -> InjectionSample:
        # 对话侧发的是 as_of，生成侧发的是 chapter：两者都是「第几章的那一次装配」
        chapter = _as_int(payload.get("chapter"), default=0) or _as_int(payload.get("as_of"), default=0)
        return InjectionSample(
            path=path,
            chapter=chapter,
            tokens=_as_int(payload.get("tokens"), default=0),
            tiers={key: _as_int(payload.get(key), default=0) for key in _TIER_KEYS},
            narrowed=payload.get("narrowed") if isinstance(payload.get("narrowed"), bool) else None,
            empty_by_entities=(
                payload.get("tier1_empty_by_entities")
                if isinstance(payload.get("tier1_empty_by_entities"), bool)
                else None
            ),
        )

    @property
    def over_limit(self) -> list[InjectionSample]:
        return [sample for sample in self.injections if sample.over_limit]

    def by_path(self) -> dict[str, list[InjectionSample]]:
        grouped: dict[str, list[InjectionSample]] = defaultdict(list)
        for sample in self.injections:
            grouped[sample.path].append(sample)
        return dict(grouped)

    def summary(self) -> dict[str, Any]:
        paths: dict[str, Any] = {}
        for path, samples in sorted(self.by_path().items()):
            tokens = [sample.tokens for sample in samples]
            narrowed = [s for s in samples if s.narrowed is not None]
            empty = [s for s in narrowed if s.empty_by_entities]
            paths[path] = {
                "samples": len(samples),
                "p50_tokens": percentile(tokens, 0.50),
                "p95_tokens": percentile(tokens, 0.95),
                "max_tokens": max(tokens, default=0),
                "over_limit": sum(1 for sample in samples if sample.over_limit),
                "mean_tiers": {
                    key: round(sum(s.tiers[key] for s in samples) / len(samples), 2)
                    for key in _TIER_KEYS
                },
                # 「设定 0 条」里有多少是真的空、有多少是 key 打错：§8-⑧ 的收窄遥测
                "empty_narrow_rate": round(len(empty) / len(narrowed), 3) if narrowed else None,
            }
        degradations: dict[str, int] = defaultdict(int)
        for item in self.degradations:
            degradations[item.path] += 1
        return {
            "limit_tokens": INJECTION_LIMIT_TOKENS,
            "paths": paths,
            "degradations": dict(degradations),
            "degradation_rate": round(
                len(self.degradations) / (len(self.degradations) + len(self.injections)), 4
            )
            if (self.degradations or self.injections)
            else None,
            "ignored_events": self.ignored,
            "ok": not self.over_limit,
        }

    def to_json(self) -> str:
        return json.dumps(self.summary(), ensure_ascii=False, indent=2)

    def to_markdown(self) -> str:
        report = self.summary()
        lines = [
            f"注入上限：{report['limit_tokens']} token（估算口径 `context.approx_tokens`）",
            "",
            "| 装配路径 | 样本 | P50 | P95 | 最大 | 超限 | 降级 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        for path, row in report["paths"].items():
            lines.append(
                f"| {path} | {row['samples']} | {row['p50_tokens']} | {row['p95_tokens']} "
                f"| {row['max_tokens']} | {row['over_limit']} | {report['degradations'].get(path, 0)} |"
            )
        lines.append("")
        lines.append(f"- 降级率：{report['degradation_rate']}")
        lines.append(f"- 未认领事件：{report['ignored_events']}")
        lines.append(f"- 判据（任何一次装配都不得超限）：{'PASS' if report['ok'] else 'FAIL'}")
        return "\n".join(lines)


def _as_int(value: object, *, default: int) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else default


__all__ = [
    "DEGRADATION_STAGES",
    "INJECTION_LIMIT_TOKENS",
    "INJECTION_STAGES",
    "DegradationSample",
    "InjectionSample",
    "RunMetrics",
    "percentile",
]
