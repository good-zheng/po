"""子图全链路：经 supervisor + InMemorySaver 走通 offline 链路。

覆盖：
- 构思 → 书级圣经 → 大纲 → 逐章（计划 → 计划闸门 → 正文 → 抽取 → 正文闸门 → 定稿）
  → 归档 interrupt → resume 确认/拒绝 → mock 入库；
- 计划回环：场景卡的未登记实体触发重排，轮数用尽即 interrupt 交作者拍板，
  批准则继续写并把该章记进 plan_unreviewed，拒绝则停笔转归档；
- thinking 领域事件按 pipeline 阶段上报；
- L1 注入：本轮已定稿章的摘要进后续章节提示词、context_compiled 遥测、
  归档前零库读（正典/摘要都迟于归档才落库）；
- 层级摘要树：归档后 scene+chapter+arc 齐全，arc_chapters<=0 时不产弧；
  书级圣经作为正典基线在归档后入库。
- 双闸门遥测：每章一条 plan_gated + 一条 gated，规则与裁判的判定合并进同一张台账
  （只有正文侧的台账落库）。
- 放行策略：blocker 走定向修补/整章重写回环，轮数用尽或裁判失败即冻结——
  冻结章「正文入库、事实与摘要作废、台账照入库」。
"""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import Field

from po_agent_core import (
    AgentCoreSettings,
    AgentRunner,
    EventType,
    RouteDecision,
    VerticalAgent,
)
from po_agent_core.supervisor.graph import build_supervisor_graph
from po_agent_novel import (
    NOVEL_UTTERANCES,
    Budgets,
    InMemoryCanonStore,
    MockNovelStore,
    OfflineNovelModel,
    build_novel_agent,
)
from po_agent_novel.context import StyleContract
from po_agent_novel.gates import GateRules
from po_agent_novel.graph import (
    STAGE_ROLES,
    _arc_spans,
    _approved,
    build_novel_graph,
    merge_gate_rules,
)
from po_agent_novel.schemas import (
    AssertionCandidate,
    BookDraft,
    ChapterDraft,
    ChapterExtraction,
    ChapterOutline,
    Finding,
    FindingList,
    Outline,
    PlannedScene,
    SceneCard,
    WorldBible,
    WorldCharacterEntry,
    WorldRuleEntry,
)
from po_agent_novel.store import ExtractionSource, SceneSummary


class _StaticRouter:
    """固定路由到 novel：路由行为已在 agent-core 侧覆盖，此处只测子图。"""

    def route(self, text: str) -> RouteDecision:
        return RouteDecision(intent="novel", score=1.0, source="test")


class ScriptedNovelModel(OfflineNovelModel):
    """可编程场景卡 + 记录提示词的离线模型。

    ``bad_cards`` 按 plan_scene 调用次序出队，每条是一组「未登记的实体键」——
    用它把计划闸门逼进重排 / 升级分支（离线默认卡不带任何实体，永远零冲突）。
    用尽后回到离线行为（空实体卡）。``pass_cards`` 让前 N 次规划直接用离线占位卡，
    用来把冲突推到第二章（验证停笔时「已定稿的章」仍在）。

    ``bible`` 只在需要**已登记事实**的用例里给：离线占位圣经全是 ``todo``，
    读侧看不见，于是 ``check_plan_entities`` 按设计跳过（``no_registry``）——
    没有登记清单时「未登记」根本没有判据。要测重排分支必须先给它一条真正确立过的设定。
    """

    bad_cards: list[list[str]] = Field(default_factory=list)
    pass_cards: int = 0
    bible: WorldBible | None = None
    prompts: list[str] = Field(default_factory=list)
    plan_prompts: list[str] = Field(default_factory=list)

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is WorldBible and self.bible is not None:
            bible = self.bible

            async def run_bible(prompt: str | list) -> WorldBible:
                return bible

            return RunnableLambda(func=run_bible)  # type: ignore[arg-type]
        if schema is SceneCard:
            inner = super().with_structured_output(schema, **kwargs)

            async def run(prompt: str | list) -> SceneCard:
                self.plan_prompts.append(str(prompt))
                if self.pass_cards > 0:
                    self.pass_cards -= 1
                    return await inner.ainvoke(prompt)
                if self.bad_cards:
                    keys = self.bad_cards.pop(0)
                    return SceneCard(
                        entities=keys,
                        scenes=[PlannedScene(goal="占位场景", present=keys, beats=[])],
                    )
                return await inner.ainvoke(prompt)

            return RunnableLambda(func=run)  # type: ignore[arg-type]
        return super().with_structured_output(schema, **kwargs)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        self.prompts.append(str(messages[-1].content))
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


# 一份「作者已经定过」的圣经：一条世界规则 + 一个活人 + 一个开篇即死的人物。
# 三行都是 confirmed，因此进 as-of 快照，计划闸门自此有了「登记过没有」的判据；
# char:dead 的 is_alive=false 专门用来喂 check_plan_deaths（blocker）。
_REGISTERED_BIBLE = WorldBible(
    logline="送信少年在雨夜发现收信人已经死了三年。",
    rules=[
        WorldRuleEntry(
            subjectKey="rule:rain_curfew",
            predicate="forbids",
            objectText="雨夜出门",
            restatement="雨夜全城宵禁，出门即犯法。",
        )
    ],
    characters=[
        WorldCharacterEntry(key="char:hero", name="沈昭", role="主角", anchor="送信的少年，左耳失聪"),
        WorldCharacterEntry(
            key="char:dead", name="柳衡", role="死者", anchor="三年前下葬的账房", alive=False
        ),
    ],
)


def _planning_model(bad_cards: list[list[str]], **kwargs: Any) -> ScriptedNovelModel:
    return ScriptedNovelModel(bad_cards=bad_cards, bible=_REGISTERED_BIBLE, **kwargs)


class FlakyBibleModel(OfflineNovelModel):
    """前 ``failures`` 次圣经调用违约：用来验「重问一次」与「问不出的降级」。

    降级形状沿用离线占位圣经（全 ``todo``），只把失败原因换成可见的那句 ——
    「圣经没建起来」与「这本书没有设定」在后续章节的表现一模一样，
    区别只能靠事件与缺口文案留下（§8-⑧）。
    """

    failures: int = 2
    calls: int = 0

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        inner = super().with_structured_output(schema, **kwargs)
        if schema is not WorldBible:
            return inner

        async def run(prompt: str | list) -> Any:
            self.calls += 1
            if self.calls <= self.failures:
                raise RuntimeError("结构化输出违约（用例注入）")
            return await inner.ainvoke(prompt)

        return RunnableLambda(func=run)  # type: ignore[arg-type]


# 记录「哪个角色的模型被调用了」，按调用次序累积；每个用例开头清空。
_ROLE_CALLS: list[str] = []
class RoleTaggedModel(OfflineNovelModel):
    """自报家门的离线模型：每次被调用就把自己的 tag 记进 _ROLE_CALLS。

    走离线实现（不联网）所以能进常规单测；目的是断言「阶段 → 模型」的绑定
    真的生效，而不只是配置解析对了。
    """

    tag: str = ""

    def _record(self) -> None:
        _ROLE_CALLS.append(self.tag)

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        inner = super().with_structured_output(schema, **kwargs)

        async def run(prompt: str | list) -> Any:
            self._record()
            return await inner.ainvoke(prompt)

        return RunnableLambda(func=run)  # type: ignore[arg-type]

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        self._record()
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


def _settings() -> AgentCoreSettings:
    return AgentCoreSettings(_env_file=None, llm_api_key="")


def _build(
    model: OfflineNovelModel | None = None,
    store: MockNovelStore | None = None,
    canon: InMemoryCanonStore | None = None,
    **agent_kwargs: Any,
):
    """装配「supervisor + novel 子图」，返回 (graph, 成稿 store, 正典 store)。

    两个 store 都必须显式注入：``build_novel_agent`` 缺省会按 ``NOVEL_*`` 配置
    推导，而 ``persist_enabled`` 默认为真——单测不该往 8080 发真实请求。
    """
    store = store or MockNovelStore()
    canon = canon or InMemoryCanonStore()
    agent = build_novel_agent(
        _settings(),
        chat_model=model or OfflineNovelModel(),
        store=store,
        canon_store=canon,
        **agent_kwargs,
    )
    graph = build_supervisor_graph(
        [agent], _StaticRouter(), OfflineNovelModel(), checkpointer=InMemorySaver()
    )
    return graph, store, canon


async def _run(runner: AgentRunner, graph, payload, config) -> list:
    return [event async for event in runner.astream(graph, payload, config=config)]


def _of(events: list, event_type: EventType) -> list:
    return [e for e in events if e.type == event_type]


def _text(events: list) -> str:
    return "".join(e.content for e in _of(events, EventType.TEXT_MESSAGE_CONTENT))


def _stages(events: list) -> list[str]:
    progress = [e for e in events if e.type in (EventType.THINKING, EventType.PLAN)]
    return [e.payload.get("stage") for e in progress]


def _interrupts(events: list) -> list:
    return _of(events, EventType.INTERRUPT)


def _payloads(events: list, stage: str) -> list[dict]:
    """按 stage 取 THINKING 帧的 payload（plan_gated / gated 两处遥测的读法）。"""
    return [e.payload for e in _of(events, EventType.THINKING) if e.payload.get("stage") == stage]


async def _drive_to_interrupt(runner: AgentRunner, graph, thread: str):
    """跑 run1 直至归档 interrupt：返回 config、interrupt 事件与 run1 全部事件。"""
    config = {"configurable": {"thread_id": thread}}
    events = await _run(
        runner, graph, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config
    )
    interrupts = _of(events, EventType.INTERRUPT)
    assert len(interrupts) == 1, f"应有且仅有一次归档确认 interrupt：{_stages(events)}"
    assert _of(events, EventType.RUN_FINISHED), "interrupt 后本次 run 应以 done 收尾"
    return config, interrupts[0], events


# ---------- 归档确认 / 拒绝 ----------


async def test_offline_full_chain_confirm_archive() -> None:
    graph, store, _ = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, interrupt_event, _ = await _drive_to_interrupt(runner, graph, "novel-confirm")

    payload = interrupt_event.payload["value"]
    assert payload["chapter_count"] == 3
    assert payload["hint"]

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert _of(resumed, EventType.RUN_FINISHED)
    reply = _text(resumed)
    assert "已归档入库" in reply
    assert "第1章" in reply and "第3章" in reply

    books = await store.list_books()
    assert len(books) == 1
    assert books[0].chapter_count == 3
    assert books[0].character_count == 1

    # 终态核对：线程内消息与 novel 命名空间 artifacts
    snapshot = await graph.aget_state(config)
    assert "已归档入库" in snapshot.values["messages"][-1].content
    novel_ns = snapshot.values["artifacts"]["novel"]
    assert novel_ns["book_id"] == books[0].book_id
    assert novel_ns["idea"].title == books[0].title


async def test_offline_full_chain_decline_archive() -> None:
    graph, store, _ = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-decline")

    resumed = await _run(runner, graph, Command(resume="no"), config)
    reply = _text(resumed)
    assert "暂不归档" in reply
    assert "第3章" in reply  # 拒绝归档不吞正文
    assert await store.list_books() == []


# ---------- 计划回环 ----------


async def test_unregistered_plan_entity_triggers_replan() -> None:
    """场景卡挑了未登记的 key → 计划闸门判 major → 回炉重排一轮，第二张卡放行。

    计划侧把 major 也算进「必须处理」是刻意的：一个没登记的 key 放过去，下一章就是
    「正文凭空多出一个没有设定的人」，而改一张卡只要十几行文本。
    """
    model = _planning_model([["char:ghost"]])
    graph, store, _ = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "novel-replan")

    frames = _payloads(run1, "plan_gated")
    assert [f["release"] for f in frames] == ["replan", "pass", "pass", "pass"]
    # major 不占 blocker 名额，但仍然拦得住一张卡：两个计数分开才看得懂判据
    assert (frames[0]["blockers"], frames[0]["majors"]) == (0, 1)
    assert _stages(run1).count("planned") == 4  # 第 1 章多排了一次

    assert len(model.plan_prompts) == 4
    assert "出一张场景卡" in model.plan_prompts[0]
    assert "char:ghost" in model.plan_prompts[1]  # 退回意见逐字进了第二次的提示词

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert _of(resumed, EventType.RUN_FINISHED)
    books = await store.list_books()
    assert books[0].chapter_count == 3  # 重排不阻碍链路走完


async def test_dead_character_in_present_replans_before_a_word_is_written() -> None:
    """已死人物进在场名单 = blocker，而它在计划阶段只值一行文本：这正是计划闸门存在的理由。

    正文侧的同一条规则要等 1200 字写完才发现，代价是十倍，所以这里必须拦得住。
    """
    model = _planning_model([["char:dead"]])
    graph, store, _ = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    config, _, run1 = await _drive_to_interrupt(runner, graph, "novel-plan-death")

    frames = _payloads(run1, "plan_gated")
    assert [f["release"] for f in frames] == ["replan", "pass", "pass", "pass"]
    assert (frames[0]["blockers"], frames[0]["majors"]) == (1, 0)
    assert "char:dead" in model.plan_prompts[1]  # 退回意见点名那一行

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    books = await store.list_books()
    assert books[0].chapter_count == 3


async def test_plan_escalation_asks_the_author_and_marks_the_chapter() -> None:
    """重排轮数用尽 → 在计划闸门处挂起交作者；按 yes 继续写，本章标「计划未审查」。

    批准 ≠ 通过：这个留痕必须一路带到归档卡片，否则 §8-⑨ 禁的假绿灯就从人工这道口
    又溜回来了——用户看到的是「这一章按计划写了」，而不是「这一章审查过了」。

    escalate 那一帧出现在 **resume 之后**：interrupt 在 _emit 之前挂起，节点重放时
    才把「判定 = escalate / 处置 = 作者批准」这一帧发出来。
    """
    model = _planning_model([["char:ghost"], ["char:ghost"], ["char:ghost"]])
    graph, store, _ = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    config = {"configurable": {"thread_id": "novel-escalate"}}
    run1 = await _run(
        runner, graph, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config
    )
    interrupts = _interrupts(run1)
    assert len(interrupts) == 1, f"重排 2 轮后应恰好升级一次：{_stages(run1)}"
    card = interrupts[0].payload["value"]
    assert card["stage"] == "plan_approval" and card["chapter"] == 1
    assert "本章实体：char:ghost" in card["card_text"]  # 作者要看的是那张卡，不是条数
    assert [f["release"] for f in _payloads(run1, "plan_gated")] == ["replan", "replan"]
    assert card["blockers"][0]["code"] == "unregistered_entity"

    run2 = await _run(runner, graph, Command(resume="yes"), config)
    plan_frames = [
        f for f in _payloads(run2, "plan_gated") if f.get("approved") is not None
    ]
    # 判定仍然是 escalate（那张卡确实没被改平），是作者批的「照这张卡写」让它放行；
    # 两者都留在遥测里，才分得开「审查通过」与「授权继续」。
    assert plan_frames[0]["release"] == "escalate" and plan_frames[0]["approved"] is True
    # unreviewed 那一格专留给「裁判没跑成」：这里的冲突是审出来的，不是审不出，
    # 两个原因混成一个数，作者就分不清「该补设定」还是「该换模型」。
    assert plan_frames[0]["unreviewed"] is False
    archive = _interrupts(run2)[0].payload["value"]
    assert archive["plan_unreviewed"] == [1]
    assert "计划卡没走完审查" in archive["unreviewed_note"]

    run3 = await _run(runner, graph, Command(resume="yes"), config)
    assert "已归档入库" in _text(run3)
    assert "计划卡没走完审查" in _text(run3)
    books = await store.list_books()
    assert books[0].chapter_count == 3


async def test_plan_halt_before_any_chapter_writes_no_book() -> None:
    """开篇那张卡就被判停：不建 0 章的书，也不再挂第二个确认点。

    0 章书目会占住 book_id，让后续 as-of 查询从一条空区间起步——停笔必须真的停干净。
    """
    model = _planning_model([["char:ghost"], ["char:ghost"], ["char:ghost"]])
    graph, store, _ = _build(model=model, chapter_count=2)
    runner = AgentRunner(timeout_seconds=30)
    config = {"configurable": {"thread_id": "novel-halt-empty"}}
    await _run(
        runner, graph, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config
    )
    run2 = await _run(runner, graph, Command(resume="no"), config)
    assert _interrupts(run2) == [], "没有成稿就不该有归档确认点"
    assert "halted" in _stages(run2)
    assert "未能开工" in _text(run2)
    assert await store.list_books() == []


async def test_plan_halt_archives_what_is_already_committed() -> None:
    """作者拒绝对撞不平的场景卡 → 停笔转归档，已定稿的章仍是成果。

    强制停，不是强制过：这里停的是「还没写的一章」，成本与正文侧的冻结不在一个量级，
    所以没有 freeze 这条路，而是把已经写完的交出去。
    """
    model = _planning_model(
        [["char:ghost"], ["char:ghost"], ["char:ghost"]], pass_cards=1
    )
    graph, store, _ = _build(model=model, chapter_count=2)
    runner = AgentRunner(timeout_seconds=30)
    config = {"configurable": {"thread_id": "novel-halt-partial"}}
    await _run(
        runner, graph, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config
    )
    run2 = await _run(runner, graph, Command(resume="no"), config)
    card = _interrupts(run2)[0].payload["value"]
    assert (card["chapter_count"], card["halted_at"]) == (1, 2)  # 第 1 章的手稿没有丢
    assert "第 2 章的场景卡未获放行" in card["halted_note"]

    run3 = await _run(runner, graph, Command(resume="yes"), config)
    assert "已归档入库" in _text(run3) and "全书在此停笔" in _text(run3)
    books = await store.list_books()
    assert books[0].chapter_count == 1


# ---------- 世界构建的失败策略（§7 表：重问 1 次 → 降级为 todo 空条目）----------


async def test_worldbuild_retries_once_before_degrading() -> None:
    model = FlakyBibleModel(failures=1)
    graph, _, _ = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    _, _, events = await _drive_to_interrupt(runner, graph, "novel-bible-retry")

    assert model.calls == 2  # 一次违约 + 一次重问，第二次成功就不再降级
    assert "worldbuild_failed" not in _stages(events)
    assert _payloads(events, "worldbuilt")[0]["degraded"] is False


async def test_degraded_worldbuild_stays_a_visible_gap() -> None:
    """两次都问不出结果：按「设定全是缺口」继续，但缺口必须带原因且一路到归档卡片。"""
    model = FlakyBibleModel(failures=2)
    graph, store, canon = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    config, _, events = await _drive_to_interrupt(runner, graph, "novel-bible-degrade")

    failed = _payloads(events, "worldbuild_failed")
    assert len(failed) == 1 and "违约" in failed[0]["reason"]
    built = _payloads(events, "worldbuilt")[0]
    assert built["degraded"] is True and built["characters"] == 0
    assert _stages(events).count("chapter_done") == 3  # 降级不拦链路

    card = _interrupts(events)[0].payload["value"]
    assert any("世界构建未取得可用结果" in q for q in card["open_questions"])
    resumed = await _run(runner, graph, Command(resume="yes"), config)
    books = await store.list_books()
    assert books[0].chapter_count == 3
    # 降级的圣经只有 todo 行：种子照样入库（走同一条通道），但读侧一行都注入不出来
    assert canon._entries and all(
        entry.status != "confirmed"
        for entry in canon._entries
        if entry.subject_key == "rule:worldbuild_failed"
    )


# ---------- 领域事件 / 确认解析 ----------


async def test_thinking_events_report_pipeline_stages() -> None:
    graph, _, _ = _build()
    runner = AgentRunner(timeout_seconds=30)
    events = await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="帮我写一本玄幻小说")]},
        {"configurable": {"thread_id": "novel-stages"}},
    )
    stages = _stages(events)
    assert "conceived" in stages
    assert "worldbuilt" in stages
    assert "outlined" in stages
    assert stages.count("chapter_done") == 3
    # 每章一次计划 + 一次计划闸门；离线占位卡不带实体，所以没有回炉
    assert stages.count("planned") == 3
    assert stages.count("plan_gated") == 3
    assert stages.count("repaired") == 0  # 离线占位正文只越字数带，不产 blocker


@pytest.mark.parametrize(
    "value,expected",
    [
        ("yes", True),
        (" YES ", True),
        ("确认", True),
        (True, True),
        ("no", False),
        ("", False),
        (None, False),
    ],
)
def test_approved_parsing(value: Any, expected: bool) -> None:
    assert _approved(value) is expected


# ---------- 分阶段模型 ----------


async def test_stage_models_are_taken_by_role() -> None:
    """节点按声明的角色取模型，而非全图共用一个实例（阶段换模型的落点）。"""
    _ROLE_CALLS.clear()
    # 每个角色一个自报家门的模型：谁被调用就会在 _ROLE_CALLS 里留下自己的角色名。
    stage_models = {role: RoleTaggedModel(tag=role) for role in STAGE_ROLES}
    graph = build_novel_graph(stage_models, MockNovelStore())
    agent = VerticalAgent(
        name="novel",
        description="角色绑定测试",
        graph=graph,
        utterances=NOVEL_UTTERANCES,
    )
    sup = build_supervisor_graph(
        [agent], _StaticRouter(), OfflineNovelModel(), checkpointer=InMemorySaver()
    )
    runner = AgentRunner(timeout_seconds=30)
    config = {"configurable": {"thread_id": "novel-role-binding"}}
    await _run(runner, sup, {"messages": [HumanMessage(content="帮我写一本玄幻小说")]}, config)
    await _run(runner, sup, Command(resume="yes"), config)

    # 预期次序：构思/圣经/大纲 → plan；三章各「场景卡 plan → 计划裁判 judge →
    # 正文 write → 抽取 plan → 章摘要 plan → 正文裁判 judge」交替
    # （两道裁判都必须与它审的那一步**异源**：同一颗脑排的计划自己审，就是 §14 登记的
    #  「盲区一致，假绿灯」；摘要与抽取同颗规划脑，两者都是「读正文 → 结构化压缩」）；
    # 归档末尾是「角色抽取 judge → 弧摘要 plan」。
    assert _ROLE_CALLS[:3] == ["plan", "plan", "plan"]
    assert _ROLE_CALLS[3:-2] == ["plan", "judge", "write", "plan", "plan", "judge"] * 3
    assert _ROLE_CALLS[-2:] == ["judge", "plan"]


def test_missing_stage_role_rejected_at_assembly() -> None:
    """缺角色在装配期就报错（并点名缺失角色），不留到运行期才炸。"""
    stage_models = {role: RoleTaggedModel(tag=role) for role in STAGE_ROLES if role != "judge"}
    with pytest.raises(ValueError, match="judge"):
        build_novel_graph(stage_models, MockNovelStore())


# ---------- L1 注入与层级摘要（N3）----------


async def test_l1_injection_reaches_later_chapter_prompts() -> None:
    """本轮已定稿章的摘要要能进后续章节的提示词——正典迟于归档落库，靠 overlay 补。"""
    model = ScriptedNovelModel()
    graph, _, _ = _build(model=model)
    runner = AgentRunner(timeout_seconds=30)
    await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="帮我写一本玄幻小说")]},
        {"configurable": {"thread_id": "novel-l1-inject"}},
    )
    write_prompts = [p for p in model.prompts if "正在为《" in p]
    assert len(write_prompts) == 3
    # 开篇没有任何已定稿章节：注入块连「近因」这一段都不该出现
    assert "# 近因" not in write_prompts[0]
    # 第 2 章起看得见前一章的场景摘要（离线占位内容同样带标记，不当真剧情用）
    assert "# 近因" in write_prompts[1]
    assert "第 1 章·场景 1摘要" in write_prompts[1]
    assert "第 2 章·场景 1摘要" in write_prompts[2]


async def test_context_compiled_events_report_budget_usage() -> None:
    """每章一次 context_compiled 遥测：N6 的成本门禁按它统计「注入 ≤ 4k」是否成立。"""
    graph, _, _ = _build()
    runner = AgentRunner(timeout_seconds=30)
    events = await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="帮我写一本玄幻小说")]},
        {"configurable": {"thread_id": "novel-l1-telemetry"}},
    )
    frames = [e for e in _of(events, EventType.THINKING) if e.payload.get("stage") == "context_compiled"]
    assert [f.payload["chapter"] for f in frames] == [1, 2, 3]
    for frame in frames:
        assert 0 < frame.payload["tokens"] <= Budgets().total
    # 近因条数随已定稿章节递增：第 1 章为 0，第 2 章起吃到前一章的摘要
    assert [f.payload["tier2"] for f in frames] == [0, 1, 2]


async def test_summary_tree_lands_after_archive() -> None:
    """归档后正典层要有完整的摘要树：每章 scene+chapter，全书一段 arc（跨度 10 章）。"""
    graph, store, canon = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-summary-tree")
    resumed = await _run(runner, graph, Command(resume="yes"), config)

    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    assert archived.payload["summary_rows"] == 6  # 3 章 ×（1 场景 + 1 章级）
    assert archived.payload["arc_count"] == 1
    assert "层级摘要 6 行" in _text(resumed)

    books = await store.list_books()
    rows = await canon.load_summaries(
        books[0].book_id, upto_chapter=3, levels=("scene", "chapter", "arc"), limit=50
    )
    assert [r.level for r in rows].count("scene") == 3
    assert [r.level for r in rows].count("chapter") == 3
    assert [r.level for r in rows].count("arc") == 1
    # arc 的 as-of 语义是「整段已知」：它的 chapter_no 是跨度起点，写第 3 章时读不到
    assert {r.chapter_no for r in rows if r.level == "arc"} == {1}


async def test_arc_chapters_zero_disables_arc_digest() -> None:
    """跨度非正数即不产弧摘要：Tier-0 的进度线宁缺毋滥，不拿半截弧充数。"""
    graph, store, canon = _build(arc_chapters=0)
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-no-arc")
    resumed = await _run(runner, graph, Command(resume="yes"), config)
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    assert archived.payload["arc_count"] == 0
    assert archived.payload["summary_rows"] == 6  # 章级链路不受影响
    books = await store.list_books()
    rows = await canon.load_summaries(
        books[0].book_id, upto_chapter=3, levels=("arc",), limit=10
    )
    assert rows == []


class _ReadFailingCanonStore(InMemoryCanonStore):
    """所有「读」接口恒失败的正典层：用来验证新书到底有没有去打库。"""

    async def load_snapshot(self, book_id: str, **kwargs: Any) -> list:
        raise RuntimeError("canon read must not happen before archive")

    async def load_summaries(self, book_id: str, **kwargs: Any) -> list:
        raise RuntimeError("canon read must not happen before archive")

    async def load_open_foreshadows(self, book_id: str, **kwargs: Any) -> list:
        raise RuntimeError("canon read must not happen before archive")

    async def load_style_profile(self, book_id: str, **kwargs: Any) -> None:
        raise RuntimeError("canon read must not happen before archive")


async def test_fresh_book_never_reads_the_canon_store() -> None:
    """归档前 book_id 是空串：本轮已定稿章的事实全靠 overlay 带，一次库读都不该发生。

    拿空 id 去打后端会得到 400（HTTP 实现的 id 解析直接拒绝），而装配失败会被
    静默降级成「本章不带正典」——那正好是让设定漂移悄悄溜进来的那条缝。
    """
    graph, store, _ = _build(canon=_ReadFailingCanonStore())
    runner = AgentRunner(timeout_seconds=30)
    config, _, events = await _drive_to_interrupt(runner, graph, "novel-l1-no-read")

    stages = _stages(events)
    assert stages.count("context_compiled") == 3
    assert "context_failed" not in stages
    resumed = await _run(runner, graph, Command(resume="yes"), config)
    books = await store.list_books()
    assert books[0].chapter_count == 3
    assert "已归档入库" in _text(resumed)


# ---------- 双闸门（N4b）----------


class _ScriptedJudgeModel(OfflineNovelModel):
    """只替换**正文**裁判那一路的结构化产出：每章给一条「有证据、有编号」的语义判定。

    离线裁判本身恒空集（它没有判定能力，见 offline.py），所以链路里的 judge 侧
    只能靠这种替身来验证合并与落库口径。证据从提示词的正文段里取：离线占位正文
    按种子换句，硬编码一句会在某些章定位失败（那正是 unlocatable 该做的事）。
    """

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is FindingList:

            async def run(prompt: str | list) -> FindingList:
                if not _is_prose_judge(str(prompt)):
                    return FindingList()
                quote = _first_sentence(str(prompt))
                return FindingList(
                    findings=[
                        Finding(
                            code="world_rule_break",
                            severity="major",
                            checker="judge",
                            canonRefs=[1],
                            evidenceQuote=quote,
                            explanation="开篇的预兆在本章没有下文。",
                            fixInstruction="要么接住这句预兆，要么删掉它。",
                        )
                    ]
                )

            return RunnableLambda(func=run)  # type: ignore[arg-type]
        return super().with_structured_output(schema, **kwargs)


def _is_prose_judge(prompt: str) -> bool:
    """这条 FindingList 调用是不是**正文**裁判。

    三个裁判替身都被当作「所有角色共用的一颗模型」注入，因此计划裁判那一路也会
    走到它们身上。不加这道门槛，脚本里的 blocker/major 会先在计划闸门命中，
    测试看到的就是计划回环而不是它想测的正文回环（正文字符区间拿去定位场景卡，
    结局是整条 unlocatable 被作废，同样测不到东西）。
    """
    return "正文：\n" in prompt


def _first_sentence(prompt: str) -> str:
    """裁判提示词 → 正文首句（证据必须逐字来自正文，否则闸门会整条作废）。"""
    body = prompt.split("正文：\n", 1)[1].split("\n\n# 工作要点", 1)[0]
    prose = [line for line in body.splitlines() if line.strip()][-1]
    return prose[:9]


def _gated(events: list) -> list:
    return [
        e for e in _of(events, EventType.THINKING) if e.payload.get("stage") == "gated"
    ]


async def test_gate_events_cover_every_chapter_and_do_not_change_flow() -> None:
    """每章一条 gated 遥测；没有 blocker 时放行策略判「放行」，走向与归档确认点不变。

    离线正文约 120 字而目标 1200 字，字数规则必然越带命中一条 major——所以这条用例
    不需要造假数据就能看到「台账非空但链路照走」：major 只降级事实状态，不拦章节。
    """
    graph, _, _ = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, interrupt_event, events = await _drive_to_interrupt(runner, graph, "novel-gate")

    frames = _gated(events)
    assert [f.payload["chapter"] for f in frames] == [1, 2, 3]
    assert [f.payload["rule"] for f in frames] == [1, 1, 1]
    # 离线裁判跑成功了，只是没有判定能力：judge 恒 0 且 failed=False
    assert all(f.payload["judge"] == 0 for f in frames)
    assert all(f.payload["judge_failed"] is False for f in frames)
    assert all(f.payload["blockers"] == 0 for f in frames)
    # N4c 之后闸门是有裁决权的：这条用例同时是「无 blocker 即放行」的回归基线
    assert all(f.payload["release"] == "pass" for f in frames)
    assert all(f.payload["unreviewed"] is False for f in frames)
    # 放行不新增回环：repair 一次都没跑，interrupt 仍然是归档那一个
    assert _repaired(events) == []
    assert interrupt_event.payload["value"]["chapter_count"] == 3


async def test_findings_land_in_the_ledger_only_after_archive() -> None:
    """Finding 的定位键是 chapter_id，而它只在归档之后才存在（§8-⑦ 写后置）。

    拒绝归档的那一支同样要紧：成稿都没落库，台账更不该留下一行。
    """
    graph, store, canon = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, _, events = await _drive_to_interrupt(runner, graph, "novel-ledger")
    assert [f.payload["findings"] for f in _gated(events)] == [1, 1, 1]
    assert canon._findings == [], "interrupt 挂起时台账必须还是空的"

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    assert archived.payload["finding_rows"] == 3
    assert archived.payload["findings_failed"] == []
    assert "冲突台账 3 条" in archived.payload["canon_line"]
    assert [row["code"] for row in canon._findings] == ["length_out_of_band"] * 3
    assert all(row["checker"] == "rule" for row in canon._findings)
    # 每行都挂在真实的章节回执上，而不是空串或章号
    chapter_ids = {row["chapterId"] for row in canon._findings}
    assert len(chapter_ids) == 3
    assert all(str(cid).startswith("chapter-") for cid in chapter_ids)
    books = await store.list_books()
    assert books[0].chapter_count == 3


async def test_declined_archive_writes_no_ledger() -> None:
    graph, _, canon = _build()
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-ledger-decline")
    await _run(runner, graph, Command(resume="no"), config)
    assert canon._findings == []


async def test_judge_verdicts_merge_into_the_same_ledger() -> None:
    """两条来源同码不同处 → 都留行，且互相不算重复：互查的痕迹不许被抹平。

    这里是「规则查不出的语义问题」进台账的唯一路径，所以要核对三件事：
    span 由证据反推（模型没给偏移）、checker 保持 judge、与规则行合并后一起落库。
    """
    graph, _, canon = _build(model=_ScriptedJudgeModel())
    runner = AgentRunner(timeout_seconds=30)
    config, _, events = await _drive_to_interrupt(runner, graph, "novel-gate-merge")

    frames = _gated(events)
    assert [f.payload["findings"] for f in frames] == [2, 2, 2]
    assert all(f.payload["judge"] == 1 and f.payload["duplicated"] == 0 for f in frames)

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    assert archived.payload["finding_rows"] == 6
    assert sorted(str(row["code"]) for row in canon._findings) == sorted(
        ["length_out_of_band"] * 3 + ["world_rule_break"] * 3
    )
    judged = [row for row in canon._findings if row["code"] == "world_rule_break"]
    assert all(row["checker"] == "judge" for row in judged)
    # span 由证据反推：改写后的 evidenceQuote 恰好等于 text[textStart:textEnd]
    assert all(
        row["textEnd"] - row["textStart"] == len(row["evidenceQuote"]) >= 6 for row in judged
    )


# ---------- 放行策略（N4c）----------


class _BlockerJudgeModel(OfflineNovelModel):
    """每章给一条「定位得到片段」的 blocker：把闸门逼进定向修补回环。

    证据照旧从裁判提示词的正文段里取（硬编码一句会在某些章定位失败，那就整条作废、
    blocker 消失，回环根本跑不起来）。有 span 才走 patch；没有 span 的整章级 blocker
    走整章重写，那是 ``_EmptyDraftModel`` 那条用例。
    """

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is FindingList:

            async def run(prompt: str | list) -> FindingList:
                if not _is_prose_judge(str(prompt)):
                    return FindingList()
                return FindingList(
                    findings=[
                        Finding(
                            code="attribute_conflict",
                            severity="blocker",
                            checker="judge",
                            canonRefs=[1],
                            evidenceQuote=_first_sentence(str(prompt)),
                            explanation="眼睛颜色与注入的设定行相反。",
                            fixInstruction="按设定行改回黑眸。",
                        )
                    ]
                )

            return RunnableLambda(func=run)  # type: ignore[arg-type]
        return super().with_structured_output(schema, **kwargs)


class _FailingJudgeModel(OfflineNovelModel):
    """正文裁判那一路调用即抛：链路必须判「不可判定」并冻结，而不是当成没有冲突。"""

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is FindingList:

            async def run(prompt: str | list) -> FindingList:
                if not _is_prose_judge(str(prompt)):
                    return FindingList()
                raise RuntimeError("裁判超时")

            return RunnableLambda(func=run)  # type: ignore[arg-type]
        return super().with_structured_output(schema, **kwargs)


class _EmptyDraftModel(OfflineNovelModel):
    """初稿那一路回空正文：造出「没有片段可指」的整章级 blocker。

    只拦初稿提示词，修订与修补照常出占位正文——于是能看到整章重写把空章救回来，
    下一轮闸门只因字数越带记一条 major 而放行（空章才是 blocker，非空就越带了）。
    """

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        if "正在为《" in str(messages[-1].content):
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=""))])
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


def _repaired(events: list) -> list:
    return [
        e for e in _of(events, EventType.THINKING) if e.payload.get("stage") == "repaired"
    ]


async def test_span_blockers_loop_through_repair_then_freeze() -> None:
    """有片段的 blocker 走「修补 → 重抽 → 重检」，轮数用尽即冻结转人工。

    离线占位正文整段比 9 字的目标片段长出一个量级，splice_patch 的长度护栏必然拒收，
    所以这条用例看到的是「修补不落地 → 冻结」这条兜底路径，而不是假想的成功案例：
    护栏宁可不改，也不肯用「假装修好了」换掉一段没问题的正文。
    """
    graph, _, _ = _build(model=_BlockerJudgeModel())
    runner = AgentRunner(timeout_seconds=30)
    config, interrupt_event, events = await _drive_to_interrupt(
        runner, graph, "novel-patch-freeze"
    )

    frames = _gated(events)
    assert [f.payload["chapter"] for f in frames] == [1, 1, 1, 2, 2, 2, 3, 3, 3]
    assert [f.payload["release"] for f in frames] == ["patch", "patch", "freeze"] * 3
    assert all(f.payload["blockers"] == 1 for f in frames)
    # blocker 不会随修补消失（正文没换），冻结时它仍然挂在那一章上
    assert all(f.payload["findings"] == 2 for f in frames)
    assert "定向修补（第 1 轮）" in frames[0].content
    assert "冻结转人工" in frames[2].content

    repaired = _repaired(events)
    assert [e.payload["chapter"] for e in repaired] == [1, 1, 2, 2, 3, 3]
    assert all(e.payload["action"] == "patch" for e in repaired)
    for frame in repaired:
        # 每轮恰好试修一个片段，且三种结局互斥；overflow=0 表示没被 max_patches 截断
        assert frame.payload["patched"] + frame.payload["rejected"] + frame.payload["failed"] == 1
        assert frame.payload["overflow"] == 0

    value = interrupt_event.payload["value"]
    assert value["frozen"] == [1, 2, 3]
    assert "（3 章待人工裁定）" in value["question"]
    assert "正文照常入库" in value["frozen_note"]


async def test_frozen_chapters_archive_text_but_no_facts() -> None:
    """冻结的语义：正文照走、事实与摘要作废、台账仍在——裁定闭环需要那行台账。

    链路不因一章被冻而中断：50 章的书不能因为第 7 章判不出来就整本报废，
    剩下的裁定在归档卡片和工作台上完成。
    """
    graph, store, canon = _build(model=_BlockerJudgeModel())
    runner = AgentRunner(timeout_seconds=30)
    config, _, _ = await _drive_to_interrupt(runner, graph, "novel-frozen-archive")

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    assert archived.payload["frozen"] == [1, 2, 3]
    # 冻结章的事实不许 commit：入库的只剩圣经基线那一条（它是动笔前的作者约定，
    # 不是这一章的未经裁定事实，所以不随章冻结）
    assert archived.payload["canon_inserted"] == archived.payload["seed_rows"] == 1
    assert archived.payload["summary_rows"] == 0, "摘要与断言同源，一并作废"
    assert archived.payload["arc_count"] == 0
    # 台账照旧：3 章 × (规则字数 major + 裁判 blocker)
    assert archived.payload["finding_rows"] == 6
    assert archived.payload["findings_failed"] == []
    assert [e.subject_key for e in canon._entries] == ["rule:offline"]
    assert canon._summaries == []
    assert sorted(row["code"] for row in canon._findings) == [
        "attribute_conflict",
        "attribute_conflict",
        "attribute_conflict",
        "length_out_of_band",
        "length_out_of_band",
        "length_out_of_band",
    ]
    books = await store.list_books()
    assert books[0].chapter_count == 3, "正文照常入库"
    reply = _text(resumed)
    assert "已归档入库" in reply and "第 1、2、3 章有未裁定的 blocker" in reply


async def test_exhausted_repairs_can_be_lowered_at_assembly() -> None:
    """max_repairs=1：一轮修补不成即冻结，闸门帧数与冻结章数都跟着变。

    这条预算是装配期给定的（N6 长测要调它），所以判据必须真的从参数走到策略，
    而不是写死在 policy 的默认值里。
    """
    graph, _, _ = _build(model=_BlockerJudgeModel(), max_repairs=1)
    runner = AgentRunner(timeout_seconds=30)
    _, _, events = await _drive_to_interrupt(runner, graph, "novel-one-repair")

    assert [f.payload["release"] for f in _gated(events)] == ["patch", "freeze"] * 3
    assert [e.payload["chapter"] for e in _repaired(events)] == [1, 2, 3]


async def test_judge_failure_freezes_without_any_repair() -> None:
    """裁判失败 = 不可判定：没有 blocker 可指就没有可执行的修补，直接冻到人工。

    「调用失败」绝不等于「无冲突」——若当成无冲突放行，一次网络抖动就能把一本
    没有审核的书送进正典。台账里只剩规则那一条，正典与摘要为空。
    """
    graph, store, canon = _build(model=_FailingJudgeModel())
    runner = AgentRunner(timeout_seconds=30)
    config, interrupt_event, events = await _drive_to_interrupt(
        runner, graph, "novel-judge-failed"
    )

    frames = _gated(events)
    assert [f.payload["chapter"] for f in frames] == [1, 2, 3]
    assert [f.payload["release"] for f in frames] == ["freeze"] * 3
    assert all(
        f.payload["judge_failed"] is True and f.payload["unreviewed"] is True for f in frames
    )
    assert all(f.payload["blockers"] == 0 and f.payload["judge"] == 0 for f in frames)
    assert all(f.payload["skipped"].get("judge_failed") == 1 for f in frames)
    assert _repaired(events) == [], "不可判定没有可执行的修补"
    assert interrupt_event.payload["value"]["frozen"] == [1, 2, 3]

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    archived = next(
        e for e in _of(resumed, EventType.THINKING) if e.payload.get("stage") == "archived"
    )
    assert archived.payload["canon_inserted"] == archived.payload["seed_rows"] == 1
    assert archived.payload["summary_rows"] == 0
    assert archived.payload["finding_rows"] == 3
    assert [row["code"] for row in canon._findings] == ["length_out_of_band"] * 3
    assert [e.subject_key for e in canon._entries] == ["rule:offline"]
    books = await store.list_books()
    assert books[0].chapter_count == 3


async def test_spanless_blocker_rewrites_the_chapter_then_passes() -> None:
    """整章级 blocker（空章）退化为一次整章重写，救回来下一章照走。

    两条路径共用一个 repair 节点、一个计轮点，所以这里断言的是「rewrite 只烧一轮」：
    重写后正文非空，字数越带降格为 major，闸门放行——没有第二次重写。
    """
    graph, store, canon = _build(model=_EmptyDraftModel())
    runner = AgentRunner(timeout_seconds=30)
    config, interrupt_event, events = await _drive_to_interrupt(
        runner, graph, "novel-rewrite-pass"
    )

    frames = _gated(events)
    assert [f.payload["chapter"] for f in frames] == [1, 1, 2, 2, 3, 3]
    assert [f.payload["release"] for f in frames] == ["rewrite", "pass"] * 3
    assert frames[0].payload["blockers"] == 1 and frames[0].payload["words"] == 0
    assert frames[1].payload["blockers"] == 0 and frames[1].payload["words"] > 0
    assert "整章重写（第 1 轮）" in frames[0].content

    repaired = _repaired(events)
    assert [e.payload["chapter"] for e in repaired] == [1, 2, 3]
    assert all(e.payload["action"] == "rewrite" and e.payload["patched"] == 1 for e in repaired)
    assert interrupt_event.payload["value"]["frozen"] == []

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    reply = _text(resumed)
    assert "已归档入库" in reply
    # 每章正文都带一次离线标记：三章都在，说明空章确实被整章重写救回来了
    assert reply.count("【离线模式】") == 3
    books = await store.list_books()
    assert books[0].chapter_count == 3
    # 正文非空后重抽的候选才进正典：空章那一轮的抽取结果是空集
    assert canon._entries


# ---------- 弧级摘要的切分 ----------


def _outline_of(arcs: list[str]) -> list[ChapterOutline]:
    return [
        ChapterOutline(title=f"第 {i + 1} 章", summary="占位概要", arc=name)
        for i, name in enumerate(arcs)
    ]


class TestArcSpans:
    """``_arc_spans`` 的三条口径：点名优先、空名延续、没点名才等分。

    只影响切分不影响落库（``save_arc_summary`` 没有弧名列），所以弧标题在这里
    是纯分组键——PRD §15.6 登记的偏差之一。
    """

    def test_named_arcs_split_by_name_not_by_span(self) -> None:
        # 跨度 10 也切不开作者点名的弧：把一段剧情劈成两半，进度线就是假信息
        assert _arc_spans(_outline_of(["起势", "起势", "暗流", "暗流"]), 4, 10) == [(1, 2), (3, 4)]
        # total 小于大纲长度时只看前 total 章（已定稿的章才有弧）
        assert _arc_spans(_outline_of(["起势", "起势", "暗流"]), 2, 10) == [(1, 2)]

    def test_unnamed_chapter_continues_the_current_arc(self) -> None:
        # 模型常常只在弧的第一章写名字：空名是「还在这一段里」，不是新的一弧
        assert _arc_spans(_outline_of(["起势", "", "", "暗流"]), 4, 10) == [(1, 3), (4, 4)]

    def test_unnamed_book_falls_back_to_equal_spans(self) -> None:
        # 整本都没点名时按跨度等分，长书才有分辨率
        assert _arc_spans(_outline_of(["", "", "", ""]), 4, 2) == [(1, 2), (3, 4)]

    def test_non_positive_guards_produce_no_arc(self) -> None:
        assert _arc_spans(_outline_of(["起势"]), 0, 10) == []
        assert _arc_spans(_outline_of(["起势"]), 1, 0) == []


class TestMergeGateRules:
    """``merge_gate_rules`` 的优先级：装配默认 ← 本轮圣经 ← 作者手改的文风契约。

    词表只能由人手收紧（§5.5），所以作者赢过圣经；字数带是「作者给了绝对带就整条
    换算」，不留比值与绝对值两套判据并存。
    """

    def test_bible_forbidden_is_used_when_contract_is_silent(self) -> None:
        bible = WorldBible(logline="送信少年发现收信人已死三年。", forbidden=["禁术"])
        rules = merge_gate_rules(GateRules(target_words=1500), bible, None)
        assert rules.forbidden_words == ("禁术",)
        # 没有字数带时目标照旧：圣经从不产出字数，别把它当成隐式覆盖
        assert rules.target_words == 1500

    def test_author_contract_replaces_the_bible_list(self) -> None:
        bible = WorldBible(logline="送信少年发现收信人已死三年。", forbidden=["禁术", "血祭"])
        contract = StyleContract(genre="玄幻", forbidden_words=("系统流",))
        rules = merge_gate_rules(GateRules(), bible, contract)
        # 整份替换而不是并集：作者点「保存」时面板里那份词表就是全部词表，
        # 并集会让作者刚删掉的词继续生效，等于面板不生效。
        assert rules.forbidden_words == ("系统流",)

    def test_absolute_word_band_is_converted_to_ratios(self) -> None:
        contract = StyleContract(
            genre="玄幻", chapter_words_min=2200, chapter_words_max=3200
        )
        rules = merge_gate_rules(GateRules(target_words=1200), None, contract)
        assert rules.target_words == 2700
        assert rules.min_ratio == pytest.approx(2200 / 2700)
        assert rules.max_ratio == pytest.approx(3200 / 2700)

    def test_half_band_keeps_derived_ratio(self) -> None:
        # 只给一个边界时不换算：中点会退化成那个边界本身，允许带变成 [1.0, 2.0]
        contract = StyleContract(genre="玄幻", chapter_words_min=2200)
        rules = merge_gate_rules(GateRules(target_words=1200), None, contract)
        assert (rules.target_words, rules.min_ratio, rules.max_ratio) == (1200, 0.6, 1.6)


# ---------- 续写（continue）+ 自动放行（auto）----------

_TAIL_TEXT = "灯下他终于看清那半枚虎符的裂纹。"


class _NoNewBookStore(MockNovelStore):
    """续写链路里「新建一本书」永远不该发生：闸门落下之后调用即失败。

    静默产出一本假书比报错严重得多——那本假书会带着这次的设定进书目，
    而作者以为自己在往原来那本书里补章。闸门由 `_seed_book` 在铺完数据后落下：
    seed 本身要建书，所以它不能是构造时就焊死的。
    """

    def __init__(self) -> None:
        super().__init__()
        self.locked = False

    async def save_book(self, draft: BookDraft) -> str:
        if self.locked:
            raise AssertionError("续写模式不得新建书目：save_book")
        return await super().save_book(draft)


async def _seed_book(
    store: MockNovelStore, canon: InMemoryCanonStore, chapters: int = 3
) -> tuple[str, list[str]]:
    """库里的一本旧书：N 章正文 + 每章 scene/chapter 摘要 + 第一段弧 + 一条已确立事实。

    四样都要 seed，因为它们各是续写链路的一处读源：正文供衔接尾段、章级摘要供大纲的
    「已写到哪」、弧摘要供 Tier-0 进度线（也是弧号偏移要避开的那一行）、事实供计划闸门的
    「这个实体登记过没有」。
    """
    book_id = await store.save_book(
        BookDraft(title="云海孤鸿", genre="玄幻", summary="少年偶得残卷，卷入两宗百年恩怨。")
    )
    ids = await store.save_chapters(
        book_id,
        [
            ChapterDraft(index=no, title=f"旧题{no}", content=f"第{no}章旧正文。{_TAIL_TEXT}")
            for no in range(1, chapters + 1)
        ],
    )
    for no, chapter_id in enumerate(ids, start=1):
        await canon.save_chapter_summaries(
            book_id,
            chapter_id,
            no,
            [SceneSummary(scene_no=1, content=f"第{no}章旧场景。")],
            digest=f"第{no}章旧摘要。",
        )
    await canon.save_arc_summary(book_id, 1, 1, chapters, "第一段弧：旧书前半。")
    await canon.append_assertions(
        book_id,
        chapters,
        ChapterExtraction(
            assertions=[
                AssertionCandidate(
                    kind="character",
                    subjectKey="char:hero",
                    predicate="eye_color",
                    objectText="墨绿色",
                    restatement="沈昭的瞳色是墨绿色。",
                    evidenceQuote=_TAIL_TEXT,
                )
            ]
        ),
        ExtractionSource(
            chapter_id=ids[-1],
            content_hash=f"seed-{chapters}",
            prompt_version="v1",
            model="m",
        ),
    )
    if isinstance(store, _NoNewBookStore):
        store.locked = True
    return book_id, ids


def _run_config(thread: str, context: dict[str, Any]) -> dict[str, Any]:
    """宿主注入运行控制键的形态：configurable.context（见 services/chat 的 Orchestrator）。"""
    return {"configurable": {"thread_id": thread, "context": context}}


async def test_continue_auto_writes_next_batch_without_any_interrupt() -> None:
    """一句话 + bookId + auto：两处人工口都不挂起，新章接在旧章之后，旧章一个字不动。"""
    store = _NoNewBookStore()
    graph, store, canon = _build(store=store)
    book_id, ids = await _seed_book(store, canon)
    runner = AgentRunner(timeout_seconds=30)

    events = await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="接着往下写三章，让师父在第 4 章复活")]},
        _run_config("novel-cont-auto", {"bookId": book_id, "tailChapterId": ids[-1], "auto": True}),
    )

    assert _interrupts(events) == [], "auto 模式不允许挂起等人"
    assert _of(events, EventType.RUN_FINISHED)
    resumed = _payloads(events, "resumed")[0]
    assert (resumed["book_id"], resumed["from_chapter"], resumed["existing_chapters"]) == (
        book_id,
        4,
        3,
    )
    assert resumed["auto"] is True and resumed["has_tail"] is True
    assert _stages(events).count("worldbuild_skipped") == 1, "已有书不重建世界圣经"
    assert [p["chapter"] for p in _payloads(events, "chapter_done")] == [4, 5, 6]

    archived = _payloads(events, "archived")[0]
    assert (archived["mode"], archived["from_chapter"], archived["to_chapter"]) == (
        "continue",
        4,
        6,
    )
    assert archived["book_id"] == book_id

    books = await store.list_books()
    assert [b.book_id for b in books] == [book_id]
    assert books[0].chapter_count == 6
    # 续写不重抽角色：整表覆盖会把首轮归档时那份角色档案换成「这几章里出现的人」
    assert books[0].character_count == 0

    # 旧章原样保留（load_book 按 id 点名，覆盖写会把这段变成新正文）
    snap = await store.load_book(book_id, chapter_id=ids[0])
    assert snap.chapter is not None and snap.chapter.content == f"第1章旧正文。{_TAIL_TEXT}"
    assert snap.chapter_count == 6

    reply = _text(events)
    assert "已续写入库" in reply and "新增第 4-6 章" in reply

    # 弧级是唯一会改写既有行的层：旧弧必须原样在，新弧从 2 起编
    arcs = await canon.load_summaries(book_id, upto_chapter=6, levels=("arc",), limit=10)
    assert {row.scene_no for row in arcs} == {1, 2}
    old_arc = next(row for row in arcs if row.scene_no == 1)
    assert (old_arc.content, old_arc.chapter_no) == ("第一段弧：旧书前半。", 1)
    new_arc = next(row for row in arcs if row.scene_no == 2)
    assert new_arc.chapter_no == 4


async def test_continue_without_auto_confirms_before_writing_anything() -> None:
    """auto=False 时续写仍然要拍板：确认之前库里一个字都不变。"""
    graph, store, canon = _build()
    book_id, ids = await _seed_book(store, canon)
    runner = AgentRunner(timeout_seconds=30)
    config = _run_config("novel-cont-ask", {"bookId": book_id, "auto": False})

    events = await _run(
        runner, graph, {"messages": [HumanMessage(content="续写三章")]}, config
    )
    interrupts = _interrupts(events)
    assert len(interrupts) == 1, f"续写只保留归档一处人工口：{_stages(events)}"
    payload = interrupts[0].payload["value"]
    assert (payload["mode"], payload["from_chapter"], payload["to_chapter"]) == (
        "continue",
        4,
        6,
    )
    assert "新增第 4-6 章" in payload["question"]
    assert (await store.load_book(book_id)).chapter_count == 3

    resumed = await _run(runner, graph, Command(resume="yes"), config)
    assert "已续写入库" in _text(resumed)
    assert (await store.load_book(book_id)).chapter_count == 6
    assert ids and (await store.load_book(book_id, chapter_id=ids[-1])).chapter is not None


async def test_continue_clamps_an_already_written_range_to_append_only() -> None:
    """作者要的第 2-3 章早就写完了：只往下追加，绝不回头覆盖已定稿章。"""
    store = _NoNewBookStore()
    graph, store, canon = _build(store=store)
    book_id, ids = await _seed_book(store, canon)
    runner = AgentRunner(timeout_seconds=30)

    events = await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="重写第 2 至第 3 章")]},
        _run_config(
            "novel-cont-clamp",
            {"bookId": book_id, "fromChapter": "2", "chapterCount": "2", "auto": True},
        ),
    )

    resumed = _payloads(events, "resumed")[0]
    assert resumed["requested_chapters"] == [2, 2]
    assert (resumed["from_chapter"], resumed["existing_chapters"]) == (4, 3)
    assert _interrupts(events) == []
    old = await store.load_book(book_id, chapter_id=ids[1])
    assert old.chapter is not None and old.chapter.index == 2
    assert old.chapter.content == "第2章旧正文。" + _TAIL_TEXT


async def test_continue_fills_the_blank_placeholder_the_author_left() -> None:
    """库里第 4 章是管理端排下的「待写占位」（标题与正文都空）：续写从它开始并填掉它。

    游标若按章节行数算会把这一章数进去，于是从第 5 章起写——第 4 章永久空着，而读者
    要的第 4 章从没生成过。行 id 也必须复用，正典断言按 chapter_id 溯源。
    """
    store = _NoNewBookStore()
    graph, store, canon = _build(store=store)
    book_id, ids = await _seed_book(store, canon)
    placeholder_id = (
        await store.save_chapters(book_id, [ChapterDraft(index=4, title="", content="")])
    )[0]
    assert (await store.load_book(book_id)).chapter_count == 3, "占位章不进游标"
    runner = AgentRunner(timeout_seconds=30)

    events = await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="接着往下写三章")]},
        _run_config(
            "novel-cont-placeholder",
            {"bookId": book_id, "tailChapterId": ids[-1], "auto": True},
        ),
    )

    resumed = _payloads(events, "resumed")[0]
    assert (resumed["from_chapter"], resumed["existing_chapters"]) == (4, 3)
    assert resumed["has_tail"] is True, "衔接尾段取第 3 章，不能取那行空的占位章"
    assert [p["chapter"] for p in _payloads(events, "chapter_done")] == [4, 5, 6]

    filled = await store.load_book(book_id, chapter_id=placeholder_id)
    assert filled.chapter is not None and filled.chapter.index == 4
    assert filled.chapter.content, "占位那一行被本轮正文填掉"
    assert (await store.list_books())[0].chapter_count == 6

    # 已定稿的旧章一个字不动
    old = await store.load_book(book_id, chapter_id=ids[0])
    assert old.chapter is not None and old.chapter.content == f"第1章旧正文。{_TAIL_TEXT}"


class _PromptSpyModel(OfflineNovelModel):
    """按 schema 分路记录提示词：续写要验「作者原话与已写章进没进三处提示词」。"""

    structured: dict[type, list[str]] = Field(default_factory=dict)
    prose: list[str] = Field(default_factory=list)

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        inner = super().with_structured_output(schema, **kwargs)

        async def run(prompt: str | list) -> Any:
            self.structured.setdefault(schema, []).append(str(prompt))
            return await inner.ainvoke(prompt)

        return RunnableLambda(func=run)  # type: ignore[arg-type]

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        self.prose.append(str(messages[-1].content))
        return await super()._agenerate(messages, stop, run_manager, **kwargs)


async def test_continue_threads_author_note_and_prior_state_into_every_prompt() -> None:
    """这一句从「开新书的想法」变成「对这本书的意见」：大纲、场景卡、正文三处都吃它。"""
    model = _PromptSpyModel()
    store = _NoNewBookStore()
    graph, store, canon = _build(model=model, store=store)
    book_id, ids = await _seed_book(store, canon)
    runner = AgentRunner(timeout_seconds=30)

    await _run(
        runner,
        graph,
        {"messages": [HumanMessage(content="让师父在第 4 章复活，别写雨夜宵禁")]},
        _run_config(
            "novel-cont-note",
            {"bookId": book_id, "tailChapterId": ids[-1], "auto": True},
        ),
    )

    note = "让师父在第 4 章复活，别写雨夜宵禁"
    outline_prompt = model.structured[Outline][0]
    assert note in outline_prompt
    assert "第 4 至" in outline_prompt
    # 已写章的章级摘要进大纲提示词：没有它，续排的大纲会从第 1 章的剧情重新开始
    assert "第 3 章：第3章旧摘要。" in outline_prompt

    card_prompt = model.structured[SceneCard][0]
    assert note in card_prompt
    prose_prompt = model.prose[0]
    assert note in prose_prompt
    # 衔接尾段走 L1 的 Tier-2（prior_tail），而不是被「已注入」的大段文本挡在门外
    assert _TAIL_TEXT in prose_prompt

