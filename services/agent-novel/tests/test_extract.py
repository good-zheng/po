"""extract 节点与证据闸门：机制②「逐字证据」与机制③「未知即缺口」的行为。

覆盖：
- ``filter_extraction`` 纯函数口径（放行的唯一条件是逐字命中，只容忍空白差异）；
- 抽取失败的那章不 commit 新事实，但链路照旧走完并归档；
- 无证据断言在图上也丢得掉，且绝不进正典；
- 正典只在用户确认归档之后才写；书级圣经作为基线排在各章增量之前入库；
- 实体键跨章累积，回灌进下一章的抽取提示词。
- 圣经种子的入库载荷形状：todo 缺口原样透传、只有死者写 ``is_alive``、关系走复合键。
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from langgraph.types import Command
from pydantic import Field

from po_agent_core import AgentRunner, EventType
from po_agent_novel import InMemoryCanonStore, OfflineNovelModel, content_hash
from po_agent_novel.graph import bible_extraction, filter_extraction
from po_agent_novel.schemas import (
    AliasCandidate,
    AssertionCandidate,
    ChapterExtraction,
    ForeshadowPlantCandidate,
    StateChangeCandidate,
    WorldBible,
    WorldCharacterEntry,
    WorldRelationEntry,
    WorldRuleEntry,
)
from test_graph import (
    _build,
    _drive_to_interrupt,
    _of,
    _run,
    _stages,
    _text,
)

_CONTENT = "夜色压得很低，风里裹着一点铁锈味。\n他数到第七块砖的时候停了下来。"
_PROGRESS = (EventType.THINKING, EventType.PLAN)


def _assertion(subject_key: str, evidence: str, **kwargs: Any) -> AssertionCandidate:
    return AssertionCandidate(
        kind="character",
        subjectKey=subject_key,
        predicate="eye_color",
        objectText="墨绿",
        restatement=f"{subject_key} 的眼睛是墨绿色。",
        evidenceQuote=evidence,
        **kwargs,
    )


def _stage_events(events: list, stage: str) -> list:
    return [
        e
        for e in events
        if e.type in _PROGRESS and (e.payload or {}).get("stage") == stage
    ]


# ---------- 闸门纯函数 ----------


def test_filter_keeps_verbatim_and_drops_invented() -> None:
    extraction = ChapterExtraction(
        assertions=[
            _assertion("char:a", "他数到第七块砖的时候停了下来。"),
            _assertion("char:b", "她天生一双墨绿色的眼睛。"),  # 正文里没有
        ]
    )
    kept, dropped = filter_extraction(extraction, _CONTENT)
    assert dropped == 1
    assert [a.subjectKey for a in kept.assertions] == ["char:a"]


def test_filter_tolerates_whitespace_only() -> None:
    # 模型常把正文里的换行排成空格：只归一化空白；用字差异仍算伪造
    grounded = ChapterExtraction(
        assertions=[_assertion("char:a", "夜色压得很低， 风里裹着一点铁锈味。")]
    )
    assert filter_extraction(grounded, _CONTENT)[1] == 0

    tampered = ChapterExtraction(
        assertions=[_assertion("char:a", "夜色压得很低，风里裹着一点锈味。")]
    )
    kept, dropped = filter_extraction(tampered, _CONTENT)
    assert (dropped, len(kept.assertions)) == (1, 0)


def test_filter_drops_blank_evidence() -> None:
    extraction = ChapterExtraction(assertions=[_assertion("char:a", "  ")])
    kept, dropped = filter_extraction(extraction, _CONTENT)
    assert (dropped, len(kept.assertions)) == (1, 0)


def test_filter_returns_original_object_when_nothing_dropped() -> None:
    extraction = ChapterExtraction(
        assertions=[_assertion("char:a", "夜色压得很低")],
        aliases=[AliasCandidate(entityKey="char:a", aliasText="少年")],
    )
    kept, dropped = filter_extraction(extraction, _CONTENT)
    assert kept is extraction and dropped == 0


def test_gap_assertion_survives_the_gate() -> None:
    """机制③：status=todo 的缺口只要证据逐字成立就原样放行，读侧自然不注入。"""
    extraction = ChapterExtraction(
        assertions=[_assertion("rule:menwei", "他数到第七块砖的时候停了下来。", status="todo")]
    )
    kept, dropped = filter_extraction(extraction, _CONTENT)
    assert dropped == 0 and kept.assertions[0].status == "todo"


# ---------- 图上行为 ----------


class CountingCanonStore(InMemoryCanonStore):
    """记录写入调用次数的正典 store。

    用于「写库只发生在归档确认之后」这条断言：interrupt 挂起时父图 state 里还没有
    novel 命名空间（子图节点未完成），拿不到候选，只能从数据层侧观察。
    """

    def __init__(self) -> None:
        super().__init__()
        self.append_calls = 0

    async def append_assertions(self, *args: Any, **kwargs: Any) -> Any:
        self.append_calls += 1
        return await super().append_assertions(*args, **kwargs)


class ExtractionModel(OfflineNovelModel):
    """在离线占位抽取之上改写脚本。

    逐字证据沿用占位结果（它本就摘自本章正文），用例因此只需关心「这条该不该活下来」，
    不必自己拼正文——离线正文按提示词哈希取句，测试里无法预知。
    """

    mode: str = "confirmed"  # confirmed | failing
    prompts: list[str] = Field(default_factory=list)

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is not ChapterExtraction:
            return super().with_structured_output(schema, **kwargs)
        inner = super().with_structured_output(schema, **kwargs)

        async def run(prompt: str | list) -> ChapterExtraction:
            self.prompts.append(str(prompt))
            base = await inner.ainvoke(prompt)
            assert base.assertions, "离线占位抽取应产出一条摘自正文的证据"
            if self.mode == "failing":
                raise RuntimeError("结构化输出违约（用例注入）")
            return ChapterExtraction(
                assertions=[
                    _assertion("char:probe", base.assertions[0].evidenceQuote),
                    _assertion("char:phantom", "正文里根本没有写过的一句话"),
                ],
                aliases=[AliasCandidate(entityKey="char:probe", aliasText="探子")],
                stateChanges=[StateChangeCandidate(charKey="char:probe", isAlive=True)],
                foreshadows=[ForeshadowPlantCandidate(content="残卷缺的一页去了哪", dueByArc=2)],
            )

        return RunnableLambda(func=run)  # type: ignore[arg-type]


async def test_extraction_failure_leaves_chapter_without_facts() -> None:
    graph, store, canon = _build(model=ExtractionModel(mode="failing"))
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "extract-fail")

    assert len(_stage_events(run1, "extract_failed")) == 3
    assert len(_stage_events(run1, "extract_filtered")) == 0

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert _of(resumed, EventType.RUN_FINISHED)  # 抽取失败不阻断归档
    book_id = (await store.list_books())[0].book_id
    assert await canon.load_snapshot(book_id, 3) == []
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    # 各章抽取全失败，入库的只剩圣经基线那一条 todo 缺口：它不是「已确立设定」，
    # 所以 load_snapshot 依然为空——占位世界不能反过来约束后面的章。
    assert archived.payload["canon_inserted"] == archived.payload["seed_rows"] == 1
    assert archived.payload["canon_failed"] == []
    assert "正典入库 1 条（含书级圣经基线 1 条）" in _text(resumed)

    ns = (await graph.aget_state(config)).values["artifacts"]["novel"]
    assert [entry["extraction"] for entry in ns["extractions"]] == [None, None, None]


async def test_hallucinated_assertion_never_reaches_canon() -> None:
    graph, store, canon = _build(model=ExtractionModel())
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "extract-gate")

    filtered = _stage_events(run1, "extract_filtered")
    assert len(filtered) == 3
    assert {e.payload["dropped"] for e in filtered} == {1}
    assert all("丢弃" in e.content for e in filtered)  # 静默丢弃等于没有闸门

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    book_id = (await store.list_books())[0].book_id
    snapshot = await canon.load_snapshot(book_id, 3)
    assert [a.subject_key for a in snapshot] == ["char:probe"] * 3
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    # 每章 1 断言 + 1 状态 + 1 伏笔 = 9，加第 1 章的称谓 1 条、圣经基线 1 条 = 11；
    # 称谓「探子」全书只允许指向一个实体，第 2、3 章的重复登记各算一次唯一冲突跳过
    # （不覆盖、也不静默吞掉）
    assert archived.payload["canon_inserted"] == 11
    assert archived.payload["seed_rows"] == 1
    assert archived.payload["canon_skipped"] == 2
    line = _text(resumed)
    assert "正典入库 11 条（含书级圣经基线 1 条）" in line and "2 条因唯一冲突跳过" in line
    assert len(await canon.load_open_foreshadows(book_id, 3)) == 3


async def test_canon_writes_only_after_confirmation() -> None:
    graph, store, canon = _build(model=ExtractionModel(), canon=CountingCanonStore())
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "extract-timing")

    # 跑到 interrupt 时三章都抽完了，但一次正典写入都没发生
    assert len(_stage_events(run1, "extracted")) == 3
    assert canon.append_calls == 0
    assert await store.list_books() == []

    resumed = await _run(runner, graph, Command(resume="no"), config)
    assert "暂不归档" in _text(resumed)
    assert canon.append_calls == 0
    assert await store.list_books() == []


async def test_entity_keys_accumulate_across_chapters() -> None:
    model = ExtractionModel()
    graph, _, _ = _build(model=model)
    await _run(
        AgentRunner(timeout_seconds=30),
        graph,
        {"messages": [HumanMessage(content="帮我写一本玄幻小说")]},
        {"configurable": {"thread_id": "extract-keys"}},
    )
    # 第一章的提示词就已经带着圣经键：世界构建的产物是「动笔前登记」的那一批实体，
    # 抽取者若看不见它，就会给同一条规则另造一个 key。
    assert "已登记实体键" in model.prompts[0] and "rule:offline" in model.prompts[0]
    assert "char:probe" not in model.prompts[0]
    # 第二章起回灌上一章登记的键，压制「同一人物第二个 key」
    assert "char:probe" in model.prompts[1]


async def test_extraction_runs_once_per_finalized_chapter() -> None:
    model = ExtractionModel()
    graph, _, _ = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "extract-hash")
    await _run(runner, graph, Command(resume="yes"), config)

    ns = (await graph.aget_state(config)).values["artifacts"]["novel"]
    assert [entry["chapter"] for entry in ns["extractions"]] == [1, 2, 3]
    assert [entry["content_hash"] for entry in ns["extractions"]] == [
        content_hash(chapter.content) for chapter in ns["chapters"]
    ]
    assert len(model.prompts) == 3  # 修订循环里的废稿不抽（离线正文无 blocker，故不进修补回环）
    assert _stages(run1).count("extracted") == 3


# ---------- 圣经种子：书级设定的入库载荷 ----------
#
# worldbuild 的产物复用同一条 append_assertions 通道（没有新库接口），因此它的
# 「形状」必须由单测钉住：哪一行进正典、哪一行只进待补清单，决定的是下一章
# 闸门按什么口径判「这条事实存在过」。

_BIBLE = WorldBible(
    logline="送信少年发现收信人已经死了三年。",
    rules=[
        WorldRuleEntry(
            subjectKey="rule:rain_curfew",
            predicate="forbids",
            objectText="雨夜出门",
            restatement="雨夜全城宵禁。",
            status="todo",
        )
    ],
    characters=[
        WorldCharacterEntry(key="char:hero", name="沈昭", role="主角", anchor="送信的少年"),
        WorldCharacterEntry(
            key="char:dead", name="柳衡", role="死者", anchor="三年前的账房", alive=False
        ),
    ],
    relations=[
        WorldRelationEntry(
            fromKey="char:hero", toKey="char:dead", relation="查案", restatement="沈昭在查柳衡的死因。"
        )
    ],
)


def test_bible_seed_keeps_a_todo_gap_as_a_gap() -> None:
    """status 原样透传：作者自己标的缺口不许在入库这一刻被他「确认」。"""
    payload = bible_extraction(_BIBLE)
    rule = next(a for a in payload.assertions if a.subjectKey == "rule:rain_curfew")
    assert rule.status == "todo"
    # 设定是动笔前的作者约定，此刻没有正文可引：出处写「书级圣经」而不是假造一句正文
    assert rule.evidenceQuote == "书级圣经：雨夜全城宵禁。"


def test_bible_seed_registers_anchor_and_one_primary_alias_per_character() -> None:
    payload = bible_extraction(_BIBLE)
    assert {a.subjectKey for a in payload.assertions if a.predicate == "anchor"} == {
        "char:hero",
        "char:dead",
    }
    assert {(a.entityKey, a.aliasText, a.isPrimary) for a in payload.aliases} == {
        ("char:hero", "沈昭", True),
        ("char:dead", "柳衡", True),
    }


def test_bible_seed_writes_is_alive_only_for_the_dead() -> None:
    """不对称只写一边：漏记活人无后果，漏记死者会让他在全书每一章合法地开口。"""
    alive = [(a.subjectKey, a.objectText) for a in bible_extraction(_BIBLE).assertions if a.predicate == "is_alive"]
    assert alive == [("char:dead", "false")]


def test_bible_seed_puts_relations_on_a_composite_key() -> None:
    """关系挂人物键会让同一个人的两段关系撞成「同一谓词两个值」——自己造的假冲突。"""
    relation = next(a for a in bible_extraction(_BIBLE).assertions if a.kind == "relation")
    assert (relation.subjectKey, relation.predicate) == ("rel:char:hero:char:dead", "relation_to")


def test_bible_seed_fits_a_full_world_bible() -> None:
    """设定扎实的圣经不能被抽取载荷的预算卡死：最坏摊平是 24+12+12+24=72 条断言。

    现场翻车过一次——worldbuild 问出一本 37 条设定的圣经，``ChapterExtraction``
    按 20 条卡它，整轮生成在动笔前就崩了。圣经每条都是作者契约，既不许截断
    （截了就是假缺口、闸门跟着漏判），也不该为一次抽取的预算换个容器。
    """
    bible = WorldBible(
        logline="一名失业程序员用代码修补崩塌的世界。",
        rules=[
            WorldRuleEntry(
                subjectKey=f"rule:{i}",
                predicate="governs",
                objectText=f"规则{i}",
                restatement=f"世界受规则{i}约束。",
            )
            for i in range(24)
        ],
        characters=[
            WorldCharacterEntry(
                key=f"char:{i}", name=f"人物{i}", role="配角", anchor="街角的目击者", alive=False
            )
            for i in range(12)
        ],
        relations=[
            WorldRelationEntry(
                fromKey=f"char:{i}", toKey=f"char:{(i + 1) % 12}", relation="猜忌", restatement=f"人物{i}猜忌下一位。"
            )
            for i in range(24)
        ],
    )
    payload = bible_extraction(bible)
    assert len(payload.assertions) == 72
    assert len(payload.aliases) == 12
