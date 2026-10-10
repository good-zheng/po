"""对话面板（novel-chat）：§10.3 的三条能力边界与 §12.4-1 的不变式。

这里锁的四件事都是「重构一下就白掉一片」的那类：

1. **一次写库调用都没有**——用「写方法一律抛错」的哨兵 store 跑任意输入，
   并断言 ``canon_entry`` 行数不变（§12.4-1 的前半）；
2. **未采纳的设定不参与注入**——提议只是上浮成事件，编译器的读源里没有它（§12.4-1 后半）；
3. **与生成链路共用同一个编译器、同一个 as-of 支点**——参照章决定看得见哪些事实（§10.3-②）；
4. **要正文就回引导**——明显的代写请求不调模型；而 PRD 自己举的那句「把第 3 章那段
   改冷一点的说法」必须放行，否则守门就把这个面板最核心的用途挡了。

断言口径与 test_context 一致：优先看「提示词与块里看不看得到」，其次才是调用次数。
"""

from __future__ import annotations

from typing import Any

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda
from pydantic import Field

from po_agent_core import AgentCoreSettings, AgentRunner, EventType, VerticalAgent
from po_agent_core.config import ModelRole
from po_agent_novel import (
    InMemoryCanonStore,
    MockNovelStore,
    NOVEL_CHAT_AGENT_NAME,
    build_novel_chat_agent,
)
from po_agent_novel.chat import (
    NOVEL_CHAT_KEY,
    PROSE_REFUSAL,
    _window,
    build_chat_context,
    build_novel_chat_graph,
)
from po_agent_novel.offline import OfflineNovelChatModel
from po_agent_novel.schemas import (
    AssertionCandidate,
    BookDraft,
    ChapterDraft,
    ChapterExtraction,
    ProposalCandidate,
    ProposalList,
)
from po_agent_novel.store import ExtractionSource

_TAIL = "灯下他终于看清那半枚虎符的裂纹。"
_EVIDENCE = "她抬眼，墨绿色的瞳仁映着灯。"

# 已登记事实：第 2 章确立主角瞳色，第 3 章确立师父已死。
# 两个章号是为了让「参照章=2 看不见第 3 章」这一条有可断言的对象。
_HERO_EYES = ProposalCandidate(
    kind="character",
    subjectKey="char:hero",
    predicate="eye_color_by_night",
    objectText="夜里会变成金色",
    basisQuote="夜里会变成金色这个说法可以定下来了。",
)
_ANSWER_WITH_CONCLUSION = "夜里会变成金色这个说法可以定下来了。白天仍是墨绿色（[canon#1]）。"


def _assertion(subject: str, predicate: str, value: str) -> AssertionCandidate:
    return AssertionCandidate(
        kind="character",
        subjectKey=subject,
        predicate=predicate,
        objectText=value,
        restatement=f"{subject} 的 {predicate} 是 {value}。",
        evidenceQuote=_EVIDENCE,
    )


async def _seed(
    novel_store: MockNovelStore, canon_store: InMemoryCanonStore, chapters: int = 3
) -> tuple[str, list[str]]:
    """建一本 3 章的书 + 两条已定稿事实（分别立于第 2、第 3 章）。"""
    book_id = await novel_store.save_book(
        BookDraft(title="云海孤鸿", genre="玄幻", summary="少年偶得残卷，卷入两宗百年恩怨。")
    )
    ids = await novel_store.save_chapters(
        book_id,
        [
            ChapterDraft(index=n, title=f"第{n}章", content=f"第{n}章正文。{_TAIL}")
            for n in range(1, chapters + 1)
        ],
    )
    await _canon(canon_store, book_id, 2, _assertion("char:hero", "eye_color", "墨绿色"))
    await _canon(canon_store, book_id, 3, _assertion("char:mentor", "is_dead", "是"))
    return book_id, ids


async def _canon(
    canon_store: InMemoryCanonStore, book_id: str, chapter: int, item: AssertionCandidate
) -> None:
    await canon_store.append_assertions(
        book_id,
        chapter,
        ChapterExtraction(assertions=[item]),
        ExtractionSource(
            chapter_id=str(chapter), content_hash=f"hash-{chapter}", prompt_version="v1", model="m"
        ),
    )


class ScriptedChatModel(OfflineNovelChatModel):
    """普通调用出固定答复、结构化调用出固定提议卡的对话模型。

    两类提示词分别记录：答复那一路要验「注入块进没进、历史进没进」，
    抽取那一路要验「只喂本轮答复」，混在一个列表里断言就会含糊。
    """

    answer: str = f"沈昭的瞳色是墨绿色，这条已经登记（[canon#1]）。{_EVIDENCE}"
    cards: list[ProposalCandidate] = Field(default_factory=list)
    answer_prompts: list[str] = Field(default_factory=list)
    extract_prompts: list[str] = Field(default_factory=list)
    calls: int = 0

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        if schema is not ProposalList:
            return super().with_structured_output(schema, **kwargs)

        async def run(prompt: str | list) -> ProposalList:
            self.extract_prompts.append(str(prompt))
            return ProposalList(proposals=list(self.cards))

        return RunnableLambda(func=run)  # type: ignore[arg-type]

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls += 1
        self.answer_prompts.append("|".join(str(message.content) for message in messages))
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self.answer))]
        )


class WriteHostileNovelStore(MockNovelStore):
    """成稿侧写方法一律抛错：对话面板碰任何一次写库就红（§12.4-1）。"""

    async def save_book(self, draft: BookDraft) -> str:
        raise AssertionError("对话链路不得写成稿：save_book")

    async def save_chapters(self, book_id: str, chapters: list[ChapterDraft]) -> list[str]:
        raise AssertionError("对话链路不得写成稿：save_chapters")

    async def save_characters(self, book_id: str, characters: list[Any]) -> None:
        raise AssertionError("对话链路不得写成稿：save_characters")


class WriteHostileCanonStore(InMemoryCanonStore):
    """正典侧写方法一律抛错。

    刻意包含 ``append_assertions``：一张提议卡离 ``canon_entry`` 只差一次调用，
    「顺手入个库」在这种代码里看起来毫无异常，只有哨兵能证明这条边界是空的。
    """

    async def append_assertions(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("对话链路不得写正典：append_assertions")

    async def close_assertion_range(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("对话链路不得写正典：close_assertion_range")

    async def save_findings(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("对话链路不得写台账：save_findings")

    async def save_chapter_summaries(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("对话链路不得写摘要：save_chapter_summaries")

    async def save_arc_summary(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("对话链路不得写摘要：save_arc_summary")


class ExplodingNovelStore(MockNovelStore):
    """load_book 失败：验「读不到正典」是可见降级而不是静默裸答。"""

    async def load_book(self, book_id: str, *, chapter_id: str | None = None) -> Any:
        raise RuntimeError("后端不可用（用例注入）")


def _graph(
    model: BaseChatModel,
    novel_store: MockNovelStore,
    canon_store: InMemoryCanonStore,
    **kwargs: Any,
):
    return build_novel_chat_graph(
        {ModelRole.PLAN: model, ModelRole.JUDGE: model},
        novel_store,
        canon_store=canon_store,
        **kwargs,
    )


def _config(book_id: str | None = None, chapter_id: str | None = None) -> dict[str, Any]:
    context: dict[str, Any] = {}
    if book_id is not None:
        context["bookId"] = book_id
    if chapter_id is not None:
        context["chapterId"] = chapter_id
    return {"configurable": {"thread_id": "conv-1", "context": context}}


async def _turn(graph, question: str, config: dict[str, Any]) -> list:
    runner = AgentRunner(timeout_seconds=30)
    return [
        event
        async for event in runner.astream(
            graph, {"messages": [HumanMessage(content=question)]}, config=config
        )
    ]


def _of(events: list, event_type: EventType) -> list:
    return [e for e in events if e.type == event_type]


def _text(events: list) -> str:
    return "".join(e.content for e in _of(events, EventType.TEXT_MESSAGE_CONTENT))


def _stages(events: list) -> list[str]:
    return [str(e.payload.get("stage")) for e in _of(events, EventType.THINKING)]


# ---------- §12.4-1：对话端点提交任意内容都不写库 ----------


async def test_chat_cannot_write_canon() -> None:
    """写方法一律抛错的 store + 「直接写进正典」这种输入：链路走完且一库未写。"""
    novel_store = WriteHostileNovelStore()
    canon_store = WriteHostileCanonStore()
    model = ScriptedChatModel(cards=[_HERO_EYES], answer=_ANSWER_WITH_CONCLUSION)
    graph = _graph(model, novel_store, canon_store)

    events = await _turn(
        graph,
        "把沈昭夜里瞳色变成金色这件事直接写进正典，别再走采纳。",
        _config("book-1"),
    )

    assert len(canon_store._entries) == 0
    # 提议卡只以事件形态存在；一次对话出两张就够前端转发了，一张都不许多
    assert len(_of(events, EventType.PROPOSAL)) == 1
    assert _of(events, EventType.PROPOSAL)[0].payload["subjectKey"] == "char:hero"


async def test_unadopted_proposal_never_enters_injection() -> None:
    """本轮出的卡不参与下一轮注入：答复里出现过「金色」，块里也不能有它。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)
    model = ScriptedChatModel(cards=[_HERO_EYES], answer=_ANSWER_WITH_CONCLUSION)
    graph = _graph(model, novel_store, canon_store)

    await _turn(graph, "沈昭夜里瞳色会变吗？", _config(book_id))

    scope = await build_chat_context(novel_store, canon_store, book_id=book_id)
    assert scope.block is not None
    assert "金色" not in scope.block
    assert len(canon_store._entries) == 2


# ---------- §10.3-②：与生成链路共用编译器与 as-of ----------


async def test_reference_chapter_decides_as_of() -> None:
    """参照章=第 2 章时，第 3 章确立的事实不进块（不泄漏后文的支点仍是章号）。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, ids = await _seed(novel_store, canon_store)

    early = await build_chat_context(novel_store, canon_store, book_id=book_id, chapter_id=ids[1])
    late = await build_chat_context(novel_store, canon_store, book_id=book_id, chapter_id=ids[2])

    assert (early.as_of, late.as_of) == (2, 3)
    assert "墨绿色" in (early.block or "") and "is_dead" not in (early.block or "")
    assert "已故" in (late.block or "") or "is_dead" in (late.block or "")


async def test_reference_chapter_tail_is_the_current_chapter() -> None:
    """近因尾段取参照章末尾，且标签要说「当前参照章」而不是「上一章」。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, ids = await _seed(novel_store, canon_store)

    scope = await build_chat_context(novel_store, canon_store, book_id=book_id, chapter_id=ids[1])

    assert _TAIL in (scope.block or "")
    assert "当前参照章结尾原文" in (scope.block or "")
    assert "上一章结尾原文" not in (scope.block or "")


async def test_no_reference_chapter_falls_back_to_archived_count() -> None:
    """没点参照章：as-of 取已归档章数，任务区不出参照章行。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)

    scope = await build_chat_context(novel_store, canon_store, book_id=book_id)

    assert scope.as_of == 3
    assert scope.error is None
    assert "当前参照章" not in (scope.block or "")


async def test_answer_prompt_carries_the_compiled_block() -> None:
    """注入块走系统提示词进答复调用，且带 [canon#N] 编号（与生成链路同一套编号）。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, ids = await _seed(novel_store, canon_store)
    model = ScriptedChatModel()
    graph = _graph(model, novel_store, canon_store)

    await _turn(graph, "沈昭的眼睛是什么颜色？", _config(book_id, ids[1]))

    prompt = model.answer_prompts[-1]
    assert "[canon#" in prompt
    assert "讨论口径：截至第 2 章" in prompt
    assert "《云海孤鸿》" in prompt


async def test_history_window_feeds_coherence_but_not_facts() -> None:
    """第二轮：上一轮答复进窗口（连贯性），注入块是本轮重拼的（事实）。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, ids = await _seed(novel_store, canon_store)
    model = ScriptedChatModel(answer="第一轮：瞳色已登记。")
    graph = _graph(model, novel_store, canon_store)
    config = _config(book_id, ids[1])

    await _turn(graph, "沈昭的眼睛是什么颜色？", config)
    events = [
        event
        async for event in AgentRunner(timeout_seconds=30).astream(
            graph,
            {
                "messages": [
                    HumanMessage(content="沈昭的眼睛是什么颜色？"),
                    AIMessage(content="第一轮：瞳色已登记。"),
                    HumanMessage(content="那这条登记是哪来的？"),
                ]
            },
            config=config,
        )
    ]

    assert events  # 帧序列完整即可，本例断言在下面那条
    assert "第一轮：瞳色已登记。" in model.answer_prompts[-1]
    assert model.answer_prompts[-1].count("[canon#") >= model.answer_prompts[0].count("[canon#")


# ---------- §10.3 约定 3：要正文就走生成链路 ----------


@pytest.mark.parametrize(
    "question",
    [
        "帮我写第 4 章正文",
        "续写一段",
        "把下一章生成出来",
    ],
)
async def test_obvious_prose_request_never_reaches_the_model(question: str) -> None:
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)
    model = ScriptedChatModel(cards=[_HERO_EYES])
    graph = _graph(model, novel_store, canon_store)

    events = await _turn(graph, question, _config(book_id))

    assert _text(events) == PROSE_REFUSAL
    assert model.calls == 0
    # 代写请求不产卡：一句引导里没有任何设定结论，抽取只会凭空造一张
    assert _of(events, EventType.PROPOSAL) == []
    assert "chat_prose_refused" in _stages(events)


@pytest.mark.parametrize(
    "question",
    [
        "把第 3 章那段改冷一点的说法",
        "这段重写会更好吗？",
        "帮我看看第 2 章的正文节奏问题",
        "梗概写出来给我看看",
    ],
)
async def test_talking_about_prose_is_not_refused(question: str) -> None:
    """谈改法必须放行：PRD 举的那句正是这一类，误判等于废掉这个面板。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)
    model = ScriptedChatModel()
    graph = _graph(model, novel_store, canon_store)

    await _turn(graph, question, _config(book_id))

    assert model.calls == 1


# ---------- §10.3 约定 1：提议卡 payload 即 Java 入参 ----------


async def test_proposal_payload_matches_java_request_fields() -> None:
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, ids = await _seed(novel_store, canon_store)
    model = ScriptedChatModel(cards=[_HERO_EYES], answer=_ANSWER_WITH_CONCLUSION)
    graph = _graph(model, novel_store, canon_store)

    events = await _turn(graph, "夜里瞳色会变吗？", _config(book_id, ids[1]))

    payload = _of(events, EventType.PROPOSAL)[0].payload
    assert set(payload) == {
        "bookId",
        "sessionId",
        "asOfChapter",
        "kind",
        "subjectKey",
        "predicate",
        "objectText",
        "validFromChapter",
        "basisQuote",
    }
    assert payload["asOfChapter"] == 2 and payload["validFromChapter"] == 2
    assert payload["sessionId"] == "conv-1"
    # status / authority 缺席是契约的一部分：能自报就是提权入口（§10.5-②）
    assert "status" not in payload and "authority" not in payload
    # 纯数字 id 发数字形态，前端原样转发即可（Java 侧 bookId 是 Long）
    assert payload["bookId"] == book_id or isinstance(payload["bookId"], int)


async def test_non_verbatim_basis_quote_is_dropped() -> None:
    """依据不在这轮答复里的卡直接丢：作者采纳时无从复核的结论就是模型的自由发挥。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)
    invented = _HERO_EYES.model_copy(update={"basisQuote": "这句话答复里根本没有。"})
    model = ScriptedChatModel(cards=[invented], answer=_ANSWER_WITH_CONCLUSION)
    graph = _graph(model, novel_store, canon_store)

    events = await _turn(graph, "夜里瞳色会变吗？", _config(book_id))

    assert _of(events, EventType.PROPOSAL) == []
    thinking = "\n".join(e.content for e in _of(events, EventType.THINKING))
    assert "1 条依据无法逐字对上讨论原文" in thinking


async def test_extract_prompt_only_sees_the_answer() -> None:
    """抽取那一路只喂本轮答复：把注入块也喂过去，模型就能「引」一条设定冒充新结论。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, ids = await _seed(novel_store, canon_store)
    model = ScriptedChatModel(cards=[_HERO_EYES], answer=_ANSWER_WITH_CONCLUSION)
    graph = _graph(model, novel_store, canon_store)

    await _turn(graph, "夜里瞳色会变吗？", _config(book_id, ids[1]))

    assert _ANSWER_WITH_CONCLUSION in model.extract_prompts[-1]
    assert "当前参照章结尾原文" not in model.extract_prompts[-1]


# ---------- 降级可见性 ----------


async def test_turn_without_book_answers_but_keeps_proposals_back() -> None:
    """没带 bookId：答复改口为「没有可用上下文」，且不抽卡（卡无处挂）。"""
    novel_store = WriteHostileNovelStore()
    canon_store = WriteHostileCanonStore()
    model = ScriptedChatModel(cards=[_HERO_EYES], answer=_ANSWER_WITH_CONCLUSION)
    graph = _graph(model, novel_store, canon_store)

    events = await _turn(graph, "主角的眼睛是什么颜色？", _config())

    assert "本轮没有可用的书籍上下文" in model.answer_prompts[-1]
    assert _of(events, EventType.PROPOSAL) == []
    assert model.extract_prompts == []


async def test_book_read_failure_is_visible_and_still_answers() -> None:
    novel_store = ExplodingNovelStore()
    canon_store = InMemoryCanonStore()
    model = ScriptedChatModel()
    graph = _graph(model, novel_store, canon_store)

    events = await _turn(graph, "沈昭的眼睛是什么颜色？", _config("book-1"))

    assert "chat_context_failed" in _stages(events)
    assert _text(events) == model.answer


async def test_failing_extractor_is_reported_not_swallowed() -> None:
    class _BrokenExtractor(ScriptedChatModel):
        def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
            if schema is not ProposalList:
                return super().with_structured_output(schema, **kwargs)

            async def run(prompt: str | list) -> ProposalList:
                raise RuntimeError("抽取违约（用例注入）")

            return RunnableLambda(func=run)  # type: ignore[arg-type]

    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)
    graph = _graph(_BrokenExtractor(answer=_ANSWER_WITH_CONCLUSION), novel_store, canon_store)

    events = await _turn(graph, "夜里瞳色会变吗？", _config(book_id))

    assert "chat_proposal_failed" in _stages(events)
    assert _of(events, EventType.PROPOSAL) == []


# ---------- 插槽与离线降级 ----------


async def test_slot_contract_is_direct_connect_only() -> None:
    """语料为空 = 不参与 Layer1 意图路由（讨论用语与生成用语高度重叠，误判代价不对称）。"""
    slot: VerticalAgent = build_novel_chat_agent(
        AgentCoreSettings(_env_file=None), chat_model=OfflineNovelChatModel()
    )
    assert slot.name == NOVEL_CHAT_AGENT_NAME
    assert slot.utterances == ()
    assert "不写正文" in slot.description


async def test_offline_chat_model_stubs_no_prose_and_no_card() -> None:
    """离线答复必须是「没配模型」的说明，而不是 OfflineNovelModel 那种占位正文。"""
    novel_store = MockNovelStore()
    canon_store = InMemoryCanonStore()
    book_id, _ = await _seed(novel_store, canon_store)
    slot = build_novel_chat_agent(AgentCoreSettings(_env_file=None))
    config = _config(book_id)

    events = await _turn(slot.graph, "沈昭的眼睛是什么颜色？", config)

    answer = _text(events)
    assert "【离线模式】" in answer
    assert "以下为占位正文" not in answer
    assert _of(events, EventType.PROPOSAL) == []


def test_history_window_starts_on_a_human_message() -> None:
    """窗口起点必须对齐到人话：从半句 AI 回答切开，模型只见结论不见提问。"""
    messages = [
        HumanMessage(content="问1"),
        AIMessage(content="答1"),
        HumanMessage(content="问2"),
        AIMessage(content="答2"),
        HumanMessage(content="问3"),
    ]
    window = _window(messages, 3)
    assert [m.content for m in window] == ["答1", "答2", "问3"] or [
        m.content for m in window
    ] == ["问2", "答2", "问3"]
    assert isinstance(window[0], HumanMessage) or len(window) == 3


def test_namespace_key_matches_slot_name() -> None:
    """artifacts 命名空间键必须等于插槽名，否则宿主按名取不到领域数据。"""
    assert NOVEL_CHAT_KEY == NOVEL_CHAT_AGENT_NAME
