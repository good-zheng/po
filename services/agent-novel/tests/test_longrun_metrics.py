"""N6 长测监控的离线半程：50 章规模下的注入上限、降级计数、幂等重放与 as-of 边界。

跑的是**真的装配与真的写入路径**（``compile_context`` + ``InMemoryCanonStore.append_assertions``），
只有模型不在环内。「任意累计章数下注入 ≤ 4k（P95）」这条退出条件本来就只取决于编译器与库，
不取决于写正文的那个模型——所以这一半可以零消耗常驻 CI，另外一半（真实召回、真实耗时、
真实计费）必须等作者点头才跑。

刻意不发模型调用、不连 MySQL：这里成立的是**预算与语义**，不是模型质量。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from po_agent_novel.context import compile_context
from po_agent_novel.metrics import (
    DEGRADATION_STAGES,
    INJECTION_LIMIT_TOKENS,
    INJECTION_STAGES,
    RunMetrics,
    percentile,
)
from po_agent_novel.schemas import (
    AliasCandidate,
    AssertionCandidate,
    BookIdea,
    ChapterDraft,
    ChapterExtraction,
    ChapterOutline,
    ForeshadowPlantCandidate,
)
from po_agent_novel.store import (
    ChapterSnapshot,
    ExtractionSource,
    InMemoryCanonStore,
    SceneSummary,
)

BOOK_ID = "7"
CHAPTER_COUNT = 50

# 实体池固定：注入预算与「书里到底有多少设定」无关，章数才是自变量
ENTITY_KEYS = (
    "char:shen",
    "char:lu",
    "char:gui",
    "place:tower",
    "place:ferry",
    "item:lantern",
    "rule:curfew",
)
# 只在第 30 章才确立的一句话：第 10 章的注入块里绝不该出现
LATE_MARKER = "青崖关的雪线以北从未有人过冬"


def _idea() -> BookIdea:
    return BookIdea(
        title="长夜灯火",
        genre="悬疑",
        summary="验夜人沈研在封城法令下追查灯灭之谜，代价是她必须先撒一个谎。",
    )


def _content(index: int) -> str:
    """一章约一千二百字的合成正文：段数与长度都按生产量级，不是玩具语料。"""
    lines = [f"第 {index + 1} 章：夜色从桥洞那边压过来，{ENTITY_KEYS[index % 3]}的脚步声先到。"]
    for part in range(11):
        lines.append(
            f"这一段是第 {index + 1} 章的第 {part + 1} 节，灯下的人把{ENTITY_KEYS[(index + part) % 7]}"
            "说了一遍又一遍，谁也不肯先承认自己听见了什么。风从塔顶下来，把话说得很轻。"
        )
    if index == 29:
        lines.append(f"只有走到关口才知道：{LATE_MARKER}。")
    return "\n\n".join(lines)


def _outline() -> list[ChapterOutline]:
    return [
        ChapterOutline(
            title=f"第 {i + 1} 章 灯下",
            summary=f"沈研在城中第 {i + 1} 处现场取证，与{ENTITY_KEYS[i % 7]}的口径第一次对不上。",
            arc=f"弧{i // 10 + 1}",
        )
        for i in range(CHAPTER_COUNT)
    ]


def _extraction(index: int) -> ChapterExtraction:
    content = _content(index)
    # 字段名是 camelCase：这条模型的字段直接对齐 Java 的落库载荷，中间没有 snake 翻译表
    assertions = [
        AssertionCandidate(
            kind="character",
            subjectKey=ENTITY_KEYS[(index + k) % len(ENTITY_KEYS)],
            predicate=f"seen_at_ch{index + 1}",
            objectText=f"第 {index + 1} 章第 {k + 1} 次出现在桥上",
            restatement=f"第 {index + 1} 章里，该实体被人在现场看见（第 {k + 1} 次）。",
            # 证据必须逐字在正文里：装配与闸门都按这条判「写了」还是「以为写了」
            evidenceQuote=content.split("\n\n")[k + 1][:24],
        )
        for k in range(5)
    ]
    if index == 29:
        assertions.append(
            AssertionCandidate(
                kind="location",
                subjectKey="place:qinya",
                predicate="winter_passable",
                objectText=LATE_MARKER,
                restatement=f"青崖关的冬季通行性：{LATE_MARKER}。",
                evidenceQuote=LATE_MARKER,
            )
        )
    aliases = [
        # 每 7 章复用一次同一个称谓：别名表的 (book, aliasText) 唯一约束会跳过，
        # 这正是长测要统计的「归并处置」而非模型侧的归并质量
        AliasCandidate(
            entityKey=ENTITY_KEYS[index % len(ENTITY_KEYS)],
            aliasText="桥上看灯的人" if index % 7 == 0 else f"桥上看灯的人（第 {index + 1} 章）",
        )
    ]
    foreshadows = (
        [ForeshadowPlantCandidate(content=f"第 {index + 1} 章埋下：灯芯里藏着的名字是谁的。", dueByArc=2)]
        if index % 5 == 0
        else []
    )
    return ChapterExtraction(
        assertions=assertions, stateChanges=[], aliases=aliases, foreshadows=foreshadows
    )


def _source(index: int) -> ExtractionSource:
    return ExtractionSource(
        chapter_id=f"ch{index + 1}",
        content_hash=f"hash{index + 1:04d}",
        prompt_version="v1",
        model="offline",
    )


async def _build() -> tuple[InMemoryCanonStore, list[ChapterDraft], list[ChapterOutline]]:
    """写一本 50 章的书：正典、场景/章级摘要、每 12 章闭一次旧区间。"""
    store = InMemoryCanonStore()
    outline = _outline()
    drafts: list[ChapterDraft] = []
    assertion_ids: list[str] = []
    for index in range(CHAPTER_COUNT):
        content = _content(index)
        drafts.append(
            ChapterDraft(index=index + 1, title=outline[index].title, content=content)
        )
        outcome = await store.append_assertions(
            BOOK_ID, index + 1, _extraction(index), _source(index)
        )
        assertion_ids.extend(outcome.assertion_ids)
        await store.save_chapter_summaries(
            BOOK_ID,
            f"ch{index + 1}",
            index + 1,
            [
                SceneSummary(scene_no=1, content=f"第 {index + 1} 章第一场：桥上取证，口径不符。"),
                SceneSummary(scene_no=2, content=f"第 {index + 1} 章第二场：回去之后谁也没睡。"),
            ],
            digest=f"第 {index + 1} 章摘要：沈研第一次决定不说出自己听见的话。",
        )
        if index and index % 12 == 0 and assertion_ids:
            # 闭旧区间：as-of 才答得出「这条事实当时还成立吗」，也才让长测的 Tier-1 不是单调堆积
            await store.close_assertion_range(assertion_ids[index % len(assertion_ids)], index, "改口")
    return store, drafts, outline


async def _payloads(
    store: InMemoryCanonStore,
    drafts: Sequence[ChapterDraft],
    outline: Sequence[ChapterOutline],
    index: int,
) -> list[dict[str, Any]]:
    """按发射方的形状产出三条装配路径的事件载荷（与 graph.py / chat.py 同键）。"""
    world_rows = await store.load_snapshot(BOOK_ID, as_of_chapter=1, kinds=["world_rule"])
    entities = [ENTITY_KEYS[index % len(ENTITY_KEYS)], ENTITY_KEYS[(index + 1) % len(ENTITY_KEYS)]]
    emitted: list[dict[str, Any]] = []
    for stage, kwargs in (
        ("plan_compiled", {"entities": None}),
        ("context_compiled", {"entities": entities}),
        # 对话侧带参照章：同一颗编译器，尾部标签与任务区都换了口径。
        # as-of 的取值与生成侧**刻意不同**：生成侧的 index 是「要写的这一章」（前面几章已定稿），
        # 对话侧的 index 就是参照章本身——编译器禁止参照章晚于 as-of。
        (
            "chat_context_compiled",
            {
                "index": index + 1,
                "chapters": drafts[: index + 1],
                "entities": None,
                "task_chapter": ChapterSnapshot(
                    chapter_id=f"ch{index + 1}",
                    index=index + 1,
                    title=outline[index].title,
                    content=drafts[index].content,
                ),
            },
        ),
    ):
        overrides = kwargs.pop("index", None)
        compiled = await compile_context(
            store,
            book_id=BOOK_ID,
            idea=_idea(),
            outline=outline,
            index=overrides if overrides is not None else index,
            chapters=kwargs.pop("chapters", drafts[:index]),
            world=world_rows,
            style=None,
            **kwargs,
        )
        payload: dict[str, Any] = {
            "stage": stage,
            "chapter": index + 1,
            **compiled.counts,
            "tokens": compiled.tokens,
        }
        if stage == "context_compiled":
            payload["entities"] = entities
            payload["narrowed"] = True
            payload["tier1_empty_by_entities"] = compiled.counts["tier1"] == 0
        elif stage == "chat_context_compiled":
            payload["path"] = "chat"
            payload["as_of"] = index + 1
            payload.pop("chapter")
        emitted.append(payload)
    return emitted


async def test_fifty_chapter_injection_stays_under_the_cap() -> None:
    store, drafts, outline = await _build()
    metrics = RunMetrics()
    for index in range(len(outline)):
        for payload in await _payloads(store, drafts, outline, index):
            assert metrics.observe(payload), payload["stage"]

    report = metrics.summary()
    assert len(metrics.injections) == CHAPTER_COUNT * 3
    # 预算是硬上限：只要有一次越界，「P95 ≤ 4k」就只是平均数好看
    assert not metrics.over_limit, metrics.to_markdown()
    for path, row in report["paths"].items():
        assert row["p95_tokens"] <= INJECTION_LIMIT_TOKENS, path
        assert row["max_tokens"] <= INJECTION_LIMIT_TOKENS, path
    # 与书长解耦的真实形状：注入块随章数增长，然后在 Tier 预算上**贴顶走平**。
    # 逐程增量并不单调（被保留行的构成每章都在换），所以断言落在「最后一程不再涨」，
    # 而不是「一定越涨越慢」——后者是编出来的漂亮曲线。
    for path, samples in metrics.by_path().items():
        p95 = [
            percentile([s.tokens for s in samples if 10 * k < s.chapter <= 10 * (k + 1)], 0.95)
            for k in range(CHAPTER_COUNT // 10)
        ]
        assert p95[-1] <= p95[-2] + 64, (path, p95)
        assert p95[-1] <= INJECTION_LIMIT_TOKENS, path
        # 预算在真的裁剪：章数上去 → dropped 上去，否则上面的走平只是语料没长起来
        early_drops = [s.tiers["dropped"] for s in samples if s.chapter <= 10]
        late_drops = [s.tiers["dropped"] for s in samples if s.chapter > CHAPTER_COUNT - 10]
        assert max(late_drops) > max(early_drops), path
    assert report["ok"] is True


async def test_as_of_holds_the_late_fact_back() -> None:
    """第 10 章看不见第 30 章才确立的事实——长测的「回溯续写不泄漏后文」。

    在**收窄路径**上验：全量 as-of 视图在 50 章规模下必然被 Tier-1 预算裁掉大部分行，
    拿「某条事实有没有出现在块里」判 as-of 会把它误判成泄漏。
    """
    store, drafts, outline = await _build()

    early = await store.load_snapshot(BOOK_ID, as_of_chapter=10)
    late = await store.load_snapshot(BOOK_ID, as_of_chapter=40)
    assert not any(entry.object_text == LATE_MARKER for entry in early)
    assert any(entry.object_text == LATE_MARKER for entry in late)

    async def narrowed_block(index: int) -> str:
        compiled = await compile_context(
            store,
            book_id=BOOK_ID,
            idea=_idea(),
            outline=outline,
            index=index,
            chapters=drafts[:index],
            entities=["place:qinya"],
        )
        return compiled.block

    assert LATE_MARKER not in await narrowed_block(9)
    assert LATE_MARKER in await narrowed_block(40)


async def test_replay_of_all_fifty_chapters_writes_nothing() -> None:
    """重放安全 3×：同一版正文重投 50 章，一次都不该落库（幂等键在章粒度上）。"""
    store, _, _ = await _build()
    before = await store.load_snapshot(BOOK_ID, as_of_chapter=CHAPTER_COUNT)
    for _ in range(3):
        for index in range(CHAPTER_COUNT):
            outcome = await store.append_assertions(
                BOOK_ID, index + 1, _extraction(index), _source(index)
            )
            assert outcome.applied is False
    after = await store.load_snapshot(BOOK_ID, as_of_chapter=CHAPTER_COUNT)
    assert [entry.id for entry in after] == [entry.id for entry in before]


async def test_alias_uniqueness_is_counted_not_silent() -> None:
    """称谓撞唯一约束时走 skipped：长测要能报出这一笔，而不是以为都插进去了。"""
    store = InMemoryCanonStore()
    inserted = skipped = 0
    for index in range(CHAPTER_COUNT):
        outcome = await store.append_assertions(
            BOOK_ID, index + 1, _extraction(index), _source(index)
        )
        inserted += outcome.inserted
        skipped += outcome.skipped
    # 每 7 章重复一次同一个称谓：首次认定进库，其余各算一次 skipped
    repeats = len([i for i in range(CHAPTER_COUNT) if i % 7 == 0]) - 1
    assert skipped == repeats
    assert inserted > 0


def test_collectors_separate_degradation_from_injection() -> None:
    metrics = RunMetrics()
    assert metrics.observe({"stage": "context_compiled", "chapter": 1, "tokens": 900}) is True
    assert metrics.observe({"stage": "context_failed", "chapter": 7}) is True
    assert metrics.observe({"stage": "chat_context_failed", "chapter": 3}) is True
    # 未登记的事件必须被退回，让调用方继续透传（而不是静默算进指标）
    assert metrics.observe({"stage": "worldbuild_failed"}) is False
    assert metrics.observe({}) is False
    summary = metrics.summary()
    assert summary["degradations"] == {"write": 1, "chat": 1}
    assert summary["ignored_events"] == 2
    # 分母是「装配尝试」= 成功 + 失败，不是全部事件：三次尝试里两次读不回库
    assert summary["degradation_rate"] == round(2 / 3, 4)


def test_percentile_is_nearest_rank() -> None:
    assert percentile([], 0.95) == 0
    assert percentile([10], 0.95) == 10
    # 40 个样本的 P95 = 第 38 个（ceil(0.95*40)=38），不是插值出来的假数
    assert percentile(list(range(1, 41)), 0.95) == 38


_STAGE_LITERAL = re.compile(r'(?:stage|fail_stage)="([a-z_]+)"|"stage":\s*"([a-z_]+)"')
_EMITTERS = (
    Path(__file__).resolve().parents[1] / "src/po_agent_novel/graph.py",
    Path(__file__).resolve().parents[1] / "src/po_agent_novel/chat.py",
)


def _emitted_assembly_stages() -> set[str]:
    found: set[str] = set()
    for path in _EMITTERS:
        for match in _STAGE_LITERAL.finditer(path.read_text(encoding="utf-8")):
            stage = match.group(1) or match.group(2)
            if stage.endswith("_compiled") or stage.endswith("context_failed"):
                found.add(stage)
    return found


def test_monitored_stages_are_the_ones_the_link_emits() -> None:
    """stage 名是字面耦合：发射方改名而监控没跟上 = 指标悄悄归零，比报错更坏。"""
    emitted = _emitted_assembly_stages()
    monitored = set(INJECTION_STAGES) | set(DEGRADATION_STAGES)
    assert emitted == monitored, f"发射方 {sorted(emitted)} / 监控 {sorted(monitored)}"
