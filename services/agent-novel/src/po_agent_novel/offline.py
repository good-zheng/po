"""离线降级模型：LLM 未配置时保证小说链路可完整走通。

- 输出为确定性占位内容（按提示词哈希从固定池选取），同一输入恒同输出；
- 所有面向用户的文本显式标注「离线模式」，绝不冒充真实生成；
- ``with_structured_output`` 按目标 schema 直接构造占位实例，
  与真实模型的 Layer3 结构化决策行为保持同构。

调用方是装配层 ``agent.build_novel_agent``：``create_chat_model`` 因缺 API Key
抛 AgentCoreError 时以本模型兜底。离线降级是设计内铁律而非临时方案——
没有它，未配置 key 的环境连服务都起不来、全链路也无从验证。
继承 BaseChatModel 是为了与真实模型接口同构（含 with_structured_output），
这样子图节点无需任何「当前是不是离线」的分支。
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda

from po_agent_novel.schemas import (
    ArcDigest,
    AssertionCandidate,
    BookIdea,
    ChapterDigest,
    ChapterExtraction,
    ChapterOutline,
    CharacterList,
    CharacterProfile,
    FindingList,
    Outline,
    PlannedScene,
    ProposalList,
    SceneCard,
    SceneDigest,
    WorldBible,
    WorldCharacterEntry,
    WorldRuleEntry,
)

# 占位标识：所有面向用户的正文都以此开头，是「绝不冒充真实生成」这条铁律的落点，
# 用户与前端据此一眼区分离线占位内容与真实生成内容。
_OFFLINE_TAG = "【离线模式】"

# 占位素材池：书名 / 题材 / 梗概 / 章节标题与概要 / 正文片段。
# 配合哈希种子取用，同一提示词恒得同一份占位内容，便于回归测试与人工复核。
_TITLES = ["云海孤鸿", "雾隐长街", "星屑拾遗", "残卷与灯", "山北有客", "潮汐来信"]
_GENRES = ["玄幻", "都市悬疑", "科幻", "武侠", "历史"]
_SUMMARIES = [
    "少年偶得上古残卷，被迫卷入两大宗门的百年恩怨。",
    "深夜便利店店员发现，凌晨到访的客人都来自一条消失的街。",
    "修复师接手一台旧收音机，从此每晚收到三十年前的求救电波。",
    "边关小吏在例行巡查中捡到半枚虎符，摸到了一场兵变的引线。",
    "退休天文台守夜人目睹星图错位，而官方记录里那颗星从未存在。",
]
_CHAPTERS = [
    ("启程", "主角离开熟悉的环境，冲突的第一丝线索浮现。"),
    ("暗流", "看似平静的日常下，各方势力开始试探交锋。"),
    ("裂隙", "真相撕开一角，主角被迫做出第一次抉择。"),
]
_PROSE = [
    "夜色压得很低，风里裹着一点铁锈味，像谁在很远的地方磨刀。",
    "他数到第七块砖的时候停了下来——缝隙里的光，比昨天亮了一分。",
    "「你确定要走这条路？」对面的声音很轻，轻得像是不希望被听见。",
    "远处的灯一盏一盏灭下去，整条街只剩下他们两人之间的沉默。",
    "他没有回头。有些话一旦说出口，就再也装不回去了。",
    "天亮之前还有三个时辰，够他把最后一步棋走完。",
]


def _seed(prompt: str) -> int:
    """提示词 → 稳定种子（sha256 摘要首字节）。"""
    # 取首字节（0-255）即可打散；不用随机数是为了保证「同输入恒同输出」，
    # 使离线链路的结果可复现（回归测试与人工复核都依赖这一点）。
    return hashlib.sha256(prompt.encode("utf-8")).digest()[0]


def _pick(pool: tuple[str, ...] | list[str], seed: int) -> str:
    """按种子从素材池取一项（模运算，越界自然回绕）。"""
    return pool[seed % len(pool)]


def _prompt_text(prompt: str | list[AnyMessage]) -> str:
    """把提示词（字符串或消息列表）归一化为纯文本，供哈希与取样使用。"""
    # 只取人类/助手消息的文本内容：工具消息、系统消息与非 str 内容（多模态块）
    # 一律忽略。用 type(...) is AIMessage 精确匹配（而非 isinstance）可把
    # AIMessageChunk 等子类排除在外，保证只有完整消息参与取样。
    if isinstance(prompt, str):
        return prompt
    parts = [
        message.content
        for message in prompt
        if isinstance(message, HumanMessage) or type(message) is AIMessage
    ]
    texts = [p for p in parts if isinstance(p, str)]
    return "\n".join(texts)


def _offline_prose(prompt: str) -> str:
    """生成占位正文：连续取 4 句素材拼接，并显式标注离线模式。"""
    seed = _seed(prompt)
    # seed + i 连续取句：同一提示词下取到的句子组合固定，且 4 句之间不会重复。
    body = "".join(_pick(_PROSE, seed + i) for i in range(4))
    return f"{_OFFLINE_TAG}未配置 LLM，以下为占位正文。\n{body}"


def _offline_structured(schema: type, prompt: str) -> Any:
    """按目标 schema 构造占位结构化结果。"""
    # 用类型恒等（is）而非 isinstance 分派：目标类型就是下列几个具体 schema；
    # 未知 schema 直接抛错，避免静默返回结构不符的对象给子图。
    seed = _seed(prompt)
    if schema is BookIdea:
        return BookIdea(
            # 书名带「（占位）」后缀：与 _OFFLINE_TAG 一样，属于显式标注的一部分。
            title=f"{_pick(_TITLES, seed)}（占位）",
            genre=_pick(_GENRES, seed + 1),
            summary=_pick(_SUMMARIES, seed + 2),
        )
    if schema is Outline:
        return Outline(
            chapters=[ChapterOutline(title=title, summary=summary) for title, summary in _CHAPTERS]
        )
    if schema is WorldBible:
        return _offline_bible()
    if schema is SceneCard:
        return _offline_plan(prompt)
    if schema is CharacterList:
        return CharacterList(
            characters=[
                CharacterProfile(
                    name="占位主角", role="主角", description="离线模式下的占位角色档案。"
                )
            ]
        )
    if schema is ChapterExtraction:
        return _offline_extraction(prompt)
    if schema is ChapterDigest:
        # 占位摘要各产一行（scene 1 + 章级）：让层级摘要树在离线链路里也有真实读写，
        # 但内容一律带离线标记，不会被当成真剧情读进后续注入。
        return ChapterDigest(
            scenes=[
                SceneDigest(
                    sceneNo=1,
                    content=f"{_OFFLINE_TAG}离线占位场景：本章正文为占位内容，无真实剧情可压缩。",
                )
            ],
            digest=f"{_OFFLINE_TAG}离线占位章级摘要：未做真实压缩，配置模型后请重算。",
        )
    if schema is ArcDigest:
        return ArcDigest(
            content=f"{_OFFLINE_TAG}离线占位弧级摘要：仅由占位章摘要合成，不含真实剧情。"
        )
    if schema is FindingList:
        # 离线裁判恒空集，且这是**如实**而非「审查通过」：占位正文里没有真实剧情，
        # 编一条冲突与编一条「没问题」同样是无据判定。消费方（gate_text 事件与 N4c 的
        # 放行策略）必须按 model_tag == "offline-novel-model" 标注「未经真实审查」，
        # 不许把空列表当绿灯——§8-⑨ 禁的就是这种假通过。
        return FindingList()
    raise ValueError(f"OfflineNovelModel 不支持的 schema：{schema!r}")


# extract_prompt 的「正文：」段——占位抽取从这里取逐字证据。
# 与提示词模板的耦合是刻意取舍：不这么做的替代方案是「离线时不抽任何事实」，
# 那会让未配 key 的环境失去唯一一条能验证正典写入链路的通路。
_EXTRACT_BODY = re.compile(r"正文：\n(.*?)\n\n# 工作要点", re.S)
_SENTENCE_END = re.compile(r"(?<=[。！？；])")


def _offline_extraction(prompt: str) -> ChapterExtraction:
    """占位抽取：产出一条 ``status="todo"`` 的缺口，不产任何「事实」。

    为什么是 todo 而非 confirmed：读侧只注入 confirmed（见 store.CanonStore.load_snapshot），
    所以占位内容既走完了整条写入链路，又绝不会反过来污染后续章节的上下文——
    「离线冒充真实生成」这条铁律在正典层同样成立。
    """
    match = _EXTRACT_BODY.search(prompt)
    if not match:
        # 拿不到正文段就没有可逐字引用的证据，此时如实返回空结果（该章不入库新事实）。
        return ChapterExtraction()
    body = match.group(1)
    evidence = next(
        (s for s in (p.strip() for p in _SENTENCE_END.split(body)) if len(s) >= 2), ""
    )
    if not evidence:
        return ChapterExtraction()
    return ChapterExtraction(
        assertions=[
            AssertionCandidate(
                kind="theme",
                subjectKey="char:offline",
                predicate="offline_placeholder",
                objectText="离线模式未做真实抽取",
                restatement=(
                    f"{_OFFLINE_TAG}未配置 LLM，本章未做真实正典抽取；"
                    "配置模型后请对该章重跑抽取。"
                ),
                evidenceQuote=evidence,
                confidence=0.0,
                status="todo",
            )
        ]
    )


# plan_scene 的两段可解析文本：已登记实体清单与目标字数。
# 与提示词模板耦合是刻意取舍（理由同 _EXTRACT_BODY）：离线卡若自带一个自拟实体，
# 计划闸门就会把它报成「未登记实体」，于是离线链路每章都要烧一轮重规划——
# 占位模型不该有这种破坏性。照抄提示词给出的清单才是最诚实的「我没做计划」。
_PLAN_REGISTERED = re.compile(r"已登记实体键（只能从这些里挑）：(.+)")
_PLAN_TARGET_WORDS = re.compile(r"本章目标字数：(\d+)")
_PLAN_NONE = "（本章无可挑实体，entities 请留空）"


def _offline_bible() -> WorldBible:
    """占位圣经：一条 ``status="todo"`` 的缺口，不产任何「已确立设定」。

    与占位抽取同一个理由：读侧只注入 ``confirmed``，所以 todo 行既走完了圣经的写入
    链路，又不会反过来变成后续章节的依据。**离线模型不能替作者定世界**——
    它给出的规则一旦标成 confirmed，整本书都会按一条编造的设定被闸门校正。
    """
    return WorldBible(
        logline=f"{_OFFLINE_TAG}未配置 LLM，本条圣经不是真实设定。",
        rules=[
            WorldRuleEntry(
                kind="style",
                subjectKey="rule:offline",
                predicate="offline_placeholder",
                objectText="离线模式未做真实世界构建",
                restatement=f"{_OFFLINE_TAG}未配置 LLM，本条为占位缺口，配置模型后请重跑 worldbuild。",
                status="todo",
            )
        ],
        characters=[],
        relations=[],
        openQuestions=[f"{_OFFLINE_TAG}本书的世界规则、人物与关系均未真实定义"],
    )


def _offline_plan(prompt: str) -> SceneCard:
    """占位场景卡：entities 恒空，让 L1 退回「全量 as-of 快照」而不是猜实体。

    空清单是 §6-1「不猜实体」的合法表达，也是 PRD 给「无清单」留的退化分支；
    字数带按提示词目标字数的 ±带宽取，避免占位卡自己触发 length_out_of_band。
    """
    registered = _PLAN_REGISTERED.search(prompt)
    new_entities: list[str] = []
    if registered and registered.group(1).strip() != _PLAN_NONE:
        # 清单里有东西却仍然留空 entities：这是「离线没做规划」，把原清单转成可见的
        # 待办（newEntities 只上浮给作者看，永不进正典），比静默丢弃更如实。
        new_entities = [key for key in registered.group(1).split("、") if key][:3]
    match = _PLAN_TARGET_WORDS.search(prompt)
    target = int(match.group(1)) if match else 1200
    return SceneCard(
        entities=[],
        newEntities=new_entities,
        scenes=[
            PlannedScene(
                goal=f"{_OFFLINE_TAG}未做真实场景规划，本章正文为占位内容。",
                present=[],
                beats=[],
            )
        ],
        mustChange=[],
        payoffs=[],
        wordsLow=max(100, int(target * 0.6)),
        wordsHigh=max(200, int(target * 1.6)),
        hook="",
    )


class OfflineNovelModel(BaseChatModel):
    """确定性离线模型：普通调用出占位正文，结构化调用出占位实例。

    继承 BaseChatModel 使子图对「模型来自真实 provider 还是离线兜底」无感知
    （与 create_chat_model 的产物同接口）；``_llm_type`` 会出现在日志与追踪里，
    作为「当前运行在离线模式」的标识。
    """

    @property
    def _llm_type(self) -> str:
        return "offline-novel-model"

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        """返回直接构造占位实例的异步 Runnable，与真实模型的绑定接口对齐。

        :param schema: 目标结构化模型（仅支持 schemas 中的九个领域类型；FindingList
            恒空集，理由见 ``_offline_structured``）
        """

        async def run(prompt: str | list[AnyMessage]) -> Any:
            return _offline_structured(schema, _prompt_text(prompt))

        # 忽略 **kwargs（真实实现用的 model=/method= 等）：占位实现直接构造实例，
        # 无需模型侧绑定。节点统一以 ainvoke 调用，故只提供异步路径即可。
        return RunnableLambda(func=run)  # type: ignore[arg-type]

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        """BaseChatModel 的同步生成入口：按提示词产出确定性占位正文。"""
        prompt = _prompt_text([m for m in messages])
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=_offline_prose(prompt)))]
        )

    async def _agenerate(
        self, messages, stop=None, run_manager=None, **kwargs
    ) -> ChatResult:
        # 无 IO、纯内存构造，直接复用同步实现，避免两份逻辑各自漂移。
        return self._generate(messages, stop, run_manager, **kwargs)


class OfflineNovelChatModel(BaseChatModel):
    """对话面板的离线降级模型：只说明「没配模型」，不产出讨论内容。

    刻意不复用 :class:`OfflineNovelModel`：那占位的是一段**小说正文**，而 §10.3 约定 3
    禁止对话面板产出正文——离线模式也不能例外，否则右栏会出现一段看起来像稿子的东西，
    作者可能以为生成链路已经产出了它。
    """

    @property
    def _llm_type(self) -> str:
        return "offline-novel-chat-model"

    def with_structured_output(self, schema: type, **kwargs: Any) -> RunnableLambda:
        """提议抽取的离线降级：恒空列表。

        与 ``FindingList`` 恒空同一个理由：占位模型给不出「已定论的设定」，编一张卡等于
        让作者在工作台点采纳一条模型自证的设定——那正是 §10.3 约定 1 要挡住的路径。
        """
        if schema is not ProposalList:
            raise ValueError(f"OfflineNovelChatModel 不支持的 schema：{schema!r}")

        async def run(prompt: str | list[AnyMessage]) -> ProposalList:
            return ProposalList()

        return RunnableLambda(func=run)  # type: ignore[arg-type]

    @staticmethod
    def _notice(messages: list[Any]) -> str:
        """把「没配模型」说清楚，并回显本轮问的是什么，便于离线联调时对齐链路。"""
        question = next(
            (
                m.content
                for m in reversed(messages)
                if isinstance(m, HumanMessage) and isinstance(m.content, str)
            ),
            "",
        )
        return (
            f"{_OFFLINE_TAG}未配置 LLM，对话面板不做真实讨论，也不产出设定结论。\n"
            f"已收到的问题：{question[:120] or '（空）'}\n"
            "配置 AGENT_CORE_LLM_API_KEY 后重试；已登记的正典可在左栏直接查看。"
        )

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self._notice(list(messages))))]
        )

    async def _agenerate(
        self, messages, stop=None, run_manager=None, **kwargs
    ) -> ChatResult:
        return self._generate(messages, stop, run_manager, **kwargs)
