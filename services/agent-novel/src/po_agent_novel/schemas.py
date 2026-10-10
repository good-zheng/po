"""小说领域结构化输出 schema（Layer3：structured_output 决策）。

字段 description 即对 LLM 的输出约束，与 prompts 的「输出格式」节
配合使用；长度/范围约束保证领域数据进入 artifacts 前已收敛。

长度约束分两道：``Field(max_length=...)`` 随 json schema 下发给模型作为
参照（只有 OpenAI 的 strict 模式会由服务端强制），本地再用
:func:`_clip_text` 截断兜底——DeepSeek / DashScope 的兼容端点走 tool 调用，
不认长度约束，模型写超了会让 Pydantic 直接抛 ValidationError 终止整轮运行。

本模块含两类模型，消费方不同：
- Pydantic 模型（BookIdea / ChapterOutline / Outline / WorldBible / CharacterProfile /
  CharacterList / SceneCard / ChapterExtraction / ChapterDigest / ArcDigest /
  Finding / FindingList）：结构化输出与闸门产物的目标类型。其中 Finding 有两种来源——
  规则引擎（gates.py，逐条构造）与语义裁判（judge.py 的 structured_output，
  目标是 FindingList），两条来源进同一个验收口 ``gates.validate_findings``；
- frozen dataclass（BookDraft / ChapterDraft / ArchivedBook）：不是 LLM 输出，
  而是 NovelStore 协议的载荷与回执类型，用不可变值对象保证异步写入期间
  数据不被意外改写。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Annotated, Any, Literal

from pydantic import BaseModel, BeforeValidator, Field


def _clip_text(limit: int) -> BeforeValidator:
    """生成「超长即截断」的前置校验器，配合 ``Field(max_length=limit)`` 使用。

    前置（Before）语义保证截断发生在长度校验之前，因此只会把越界输出收敛为
    ``limit`` 个字符，不会触发 ValidationError；``min_length`` 等下限仍照常生效。
    """

    def clip(value: Any) -> Any:
        return value[:limit] if isinstance(value, str) and len(value) > limit else value

    return BeforeValidator(clip)


def _clip_list(limit: int) -> BeforeValidator:
    """生成「列表超长即截断」的前置校验器，配合 ``Field(max_length=limit)`` 使用。

    与 :func:`_clip_text` 同一条取舍：模型多返回几条不该让整轮运行终止。
    """

    def clip(value: Any) -> Any:
        return value[:limit] if isinstance(value, list) and len(value) > limit else value

    return BeforeValidator(clip)


class BookIdea(BaseModel):
    """构思结果：书名 / 题材 / 核心梗概。

    conceive 节点产出（with_structured_output(BookIdea)），写入
    artifacts["novel"]["idea"]，被 outline / generate / archive 复用。
    """

    # min_length=1 是防呆下限：空字段一旦落进 artifacts，后续节点会拼出无意义提示词；
    # max_length 用于把模型输出约束在「一句话」量级（越界由 _clip_text 截断，
    # 见模块 docstring），避免梗概被写成一章正文。
    title: Annotated[str, _clip_text(50)] = Field(
        min_length=1, max_length=50, description="书名，简洁有记忆点"
    )
    genre: Annotated[str, _clip_text(20)] = Field(
        min_length=1,
        max_length=20,
        description="题材，取自类型字典（玄幻/武侠/科幻/言情/悬疑/历史/都市/游戏/恐怖/其他），"
        "复合写法把中心词放最后，如「都市科幻」",
    )
    summary: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="核心梗概：主角、核心冲突与最大看点"
    )


class ChapterOutline(BaseModel):
    """单章大纲（不含正文字段，正文由 write 节点产出）。

    注意：无「章节序号」字段——序号由在 Outline.chapters 中的位置隐含，
    这样模型无需维护自增序号，也不会出现序号错乱。

    ``arc`` 是弧级摘要的分组依据：连续同名即一段弧。刻意允许为空——
    短篇（3 章）没有「弧」的概念，强给一个标题会把三章切成三段伪弧。
    """

    title: Annotated[str, _clip_text(50)] = Field(
        min_length=1, max_length=50, description="章节标题"
    )
    summary: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="本章剧情概要与关键场景"
    )
    arc: Annotated[str, _clip_text(30)] = Field(
        default="", max_length=30, description="所属剧情弧名称，同一弧内各章写法一致；可不填"
    )


class Outline(BaseModel):
    """全书大纲；outline 节点产出，plan_scene / write 节点按章取用。"""

    chapters: list[ChapterOutline] = Field(
        min_length=1, max_length=20, description="章节列表，按叙事顺序排列"
    )


# ---------- 书级圣经（worldbuild 节点产出：机制①的「先定义再动笔」） ----------


class WorldRuleEntry(BaseModel):
    """一条世界级设定，直接作为正典种子行入库。

    字段形状对齐 :class:`AssertionCandidate`（落库载荷），但**没有 ``evidenceQuote``**：
    圣经是动笔前的作者约定，此刻还没有正文可引。种子入库时以 ``restatement`` 充当证据，
    出处则靠 ``established_chapter=1`` 与「种子不是抽取产物」这一事实来交代——
    机制②的「正文里必须找得到」约束的是**抽取**，不许反过来要求设定自证出处。
    """

    kind: Annotated[str, _clip_text(24)] = Field(
        default="world_rule",
        max_length=24,
        description="world_rule/location/item/theme/style，人物与关系另有专表",
    )
    subjectKey: Annotated[str, _clip_text(128)] = Field(
        min_length=1, max_length=128, description="实体键，如 rule:moonlight_burns / loc:old_city"
    )
    predicate: Annotated[str, _clip_text(64)] = Field(
        min_length=1, max_length=64, description="机器可比谓词，小写下划线，如 harms / exists_at"
    )
    objectText: Annotated[str, _clip_text(512)] = Field(
        min_length=1, max_length=512, description="值本体，用于一致性比对"
    )
    restatement: Annotated[str, _clip_text(512)] = Field(
        min_length=1, max_length=512, description="给提示词与作者读的一句自然语言"
    )
    status: Annotated[str, _clip_text(16)] = Field(
        default="confirmed", max_length=16, description="confirmed 或 todo（作者还没定的缺口）"
    )


class WorldCharacterEntry(BaseModel):
    """开篇前就定好的人物：实体键、身份与不可漂移的锚点。

    ``key`` 必须是 ``char:`` 前缀的归一键：后续 plan_scene 的在场名单、extract 的别名
    归一、gate 的「未登记实体」判定全按这个键比对，键形不一致就等于每个人都是新人。
    """

    key: Annotated[str, _clip_text(128)] = Field(
        min_length=1, max_length=128, description="实体键，形如 char:linwan（全小写拼音或英文名）"
    )
    name: Annotated[str, _clip_text(30)] = Field(min_length=1, max_length=30, description="正文里用的中文名")
    role: Annotated[str, _clip_text(50)] = Field(
        min_length=1, max_length=50, description="定位，如：主角、反派、导师"
    )
    anchor: Annotated[str, _clip_text(200)] = Field(
        min_length=1,
        max_length=200,
        description="不可违背的特征与动机（含外貌、能力边界、说话方式），一句到两句",
    )
    alive: bool = Field(default=True, description="开篇时是否活着（写死的人物后续不许开口说话）")


class WorldRelationEntry(BaseModel):
    """人物关系：关系是「谁」的断言，所以主语键必须是已登记人物的 ``key``。"""

    fromKey: Annotated[str, _clip_text(128)] = Field(min_length=1, max_length=128, description="关系主语实体键")
    toKey: Annotated[str, _clip_text(128)] = Field(min_length=1, max_length=128, description="关系宾语实体键")
    relation: Annotated[str, _clip_text(64)] = Field(
        min_length=1, max_length=64, description="关系名，如：师徒、宿敌、暗恋"
    )
    restatement: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="一句话说明这段关系及其当前的张力"
    )


class WorldBible(BaseModel):
    """书级圣经：世界规则 + 人物 + 关系 + 文风契约 + 禁用词 + 未决缺口。

    一份产出而不是多次调用：这些维度互相引用（关系要指向人物键、禁用词来自文风），
    拆开就会得到「人物表里没有、关系里却出现了」的自相矛盾输入。

    ``openQuestions`` 不进正典，只进作者可见的缺口清单（机制③）——
    模型「还想知道什么」不是这本书「已经成立的事实」。
    """

    logline: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="一句话故事内核：谁、想要什么、被什么拦住"
    )
    rules: Annotated[list[WorldRuleEntry], _clip_list(24)] = Field(
        default_factory=list, max_length=24, description="世界级规则与设定，最多 24 条"
    )
    characters: Annotated[list[WorldCharacterEntry], _clip_list(12)] = Field(
        default_factory=list, max_length=12, description="开篇人物，按重要度排序，最多 12 人"
    )
    relations: Annotated[list[WorldRelationEntry], _clip_list(24)] = Field(
        default_factory=list, max_length=24, description="人物关系，最多 24 条"
    )
    # 文风契约两字段落到 context.StyleContract，并作为 style_drift 的比对基准。
    pov: Annotated[str, _clip_text(32)] = Field(
        default="第三人称限知", max_length=32, description="人称与视角，如：第一人称、第三人称限知"
    )
    tense: Annotated[str, _clip_text(32)] = Field(
        default="过去时", max_length=32, description="时态，如：过去时、现在时"
    )
    forbidden: Annotated[list[Annotated[str, _clip_text(32)]], _clip_list(20)] = Field(
        default_factory=list, max_length=20, description="禁用词（题材不该出现的词），最多 20 个"
    )
    openQuestions: Annotated[list[Annotated[str, _clip_text(120)]], _clip_list(12)] = Field(
        default_factory=list, max_length=12, description="还没定但会影响一致性的问题，最多 12 条"
    )


class CharacterProfile(BaseModel):
    """角色档案（归档时提取）。"""

    name: Annotated[str, _clip_text(30)] = Field(min_length=1, max_length=30, description="角色姓名")
    role: Annotated[str, _clip_text(50)] = Field(
        min_length=1, max_length=50, description="身份定位，如：主角、女主、反派、导师"
    )
    description: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="身份、性格与关键特征"
    )


class CharacterList(BaseModel):
    """角色列表；archive 节点在归档前提取，随后交给 store.save_characters。"""

    # max_length=10 与 extract_characters_prompt 的「最多 10 个」一致：
    # 提示词是引导，这里是硬约束，超出的角色会被校验拦下。
    characters: list[CharacterProfile] = Field(
        default_factory=list, max_length=10, description="出场角色，按重要度排序"
    )


# ---------- 场景计划（plan_scene 节点产出，gate_plan 的输入） ----------


class PlannedScene(BaseModel):
    """章内单个场景的计划。

    ``present`` 用实体键而不是人名：闸门要按 ``is_alive`` 查在场人物是否已死，
    按人名比对会把「林晚」「林晚姐」当成两个人。
    """

    goal: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="这个场景要推进什么（不可与上一章同义复述）"
    )
    locationKey: Annotated[str | None, _clip_text(128)] = Field(
        default=None, description="场景地点实体键，如 loc:old_city；可不填"
    )
    present: Annotated[list[Annotated[str, _clip_text(128)]], _clip_list(8)] = Field(
        default_factory=list, max_length=8, description="在场实体键（含旁听者），最多 8 个"
    )
    beats: Annotated[list[Annotated[str, _clip_text(160)]], _clip_list(8)] = Field(
        default_factory=list, max_length=8, description="场景内按顺序发生的情节点，最多 8 条"
    )


class SceneCard(BaseModel):
    """一章的场景卡：写正文之前必须先交出的计划。

    计划本身不是出处（§机制①的边界）——它只约束「这一章打算怎么写」，
    绝不进正典。因此 ``newEntities`` 自造的人物**只出现在待补清单里**，
    不写 alias 表、不写断言表：否则「计划里有」会在下一章变成「书里已经成立」，
    那是比漏写更糟的污染（它带着正典的权威）。

    ``entities`` 只允许从注入的已登记键清单里挑；挑不出来的进 ``newEntities``。
    ``payoffs`` 用 L1 注入的 ``[fsh#N]`` 编号，未收清单里没有的编号即 C6。
    """

    entities: Annotated[list[Annotated[str, _clip_text(128)]], _clip_list(12)] = Field(
        default_factory=list, max_length=12, description="本章用到的已登记实体键，必须逐字取自给定清单"
    )
    newEntities: Annotated[list[Annotated[str, _clip_text(128)]], _clip_list(8)] = Field(
        default_factory=list, max_length=8, description="清单外必须新增的实体键（待作者补登记）"
    )
    scenes: Annotated[list[PlannedScene], _clip_list(5)] = Field(
        default_factory=list, max_length=5, description="按叙事顺序，最多 5 个场景"
    )
    mustChange: Annotated[list[Annotated[str, _clip_text(200)]], _clip_list(6)] = Field(
        default_factory=list, max_length=6, description="本章结束时必须与开始时不同的状态"
    )
    payoffs: Annotated[list[int], _clip_list(6)] = Field(
        default_factory=list, max_length=6, description="本章要收的伏笔编号（[fsh#N] 的 N）"
    )
    wordsLow: int = Field(default=800, ge=100, le=8000, description="本章字数下限")
    wordsHigh: int = Field(default=1500, ge=100, le=8000, description="本章字数上限")
    hook: Annotated[str, _clip_text(200)] = Field(
        default="", max_length=200, description="章末钩子：让读者非读下一章不可的那一句"
    )


# ---------- 正典抽取（extract 节点的结构化输出，字段名对齐 Java DTO 的 camelCase） ----------


class AssertionCandidate(BaseModel):
    """一条候选正典断言。

    字段名直接用 Java 侧 ``InternalAssertionAppendRequest.AssertionItem`` 的 camelCase：
    这条链路是「模型输出 → 落库载荷」，中间加一层 snake_case 映射只会多一个会漂移的翻译表。
    """

    kind: Annotated[str, _clip_text(24)] = Field(
        min_length=1,
        max_length=24,
        description="world_rule/character/relation/location/item/theme/style 之一",
    )
    subjectKey: Annotated[str, _clip_text(128)] = Field(
        min_length=1, max_length=128, description="别名归一后的实体键，如 char:shenqing"
    )
    predicate: Annotated[str, _clip_text(64)] = Field(
        min_length=1,
        max_length=64,
        description="机器可比谓词，小写下划线，如 eye_color / is_alive / cannot_use",
    )
    objectText: Annotated[str, _clip_text(512)] = Field(
        min_length=1, max_length=512, description="值本体，用于一致性比对"
    )
    restatement: Annotated[str, _clip_text(512)] = Field(
        min_length=1, max_length=512, description="给提示词读的一句自然语言"
    )
    # 证据逐字摘自本章正文：extract 节点用「原文里找不到就丢弃」来落实机制②，
    # 没有这条字段就无法区分「正文里写了」与「模型觉得应该如此」。
    evidenceQuote: Annotated[str, _clip_text(512)] = Field(
        min_length=2, max_length=512, description="必须逐字摘自本章正文的证据片段"
    )
    confidence: float = Field(default=1.0, ge=0, le=1, description="抽取置信度")
    # todo 即机制③的「未知即缺口」：正文引用了未定义设定时登记待补，而不是编一个答案
    status: Annotated[str, _clip_text(16)] = Field(
        default="confirmed", max_length=16, description="confirmed 或 todo（缺口）"
    )


class StateChangeCandidate(BaseModel):
    """本章结束时的人物状态，落 character_state 快照。"""

    charKey: Annotated[str, _clip_text(128)] = Field(min_length=1, max_length=128)
    isAlive: bool | None = None
    locationKey: Annotated[str | None, _clip_text(128)] = None
    knows: list[Annotated[str, _clip_text(128)]] = Field(default_factory=list, max_length=20)
    holds: list[Annotated[str, _clip_text(128)]] = Field(default_factory=list, max_length=20)
    mood: Annotated[str | None, _clip_text(64)] = None


class AliasCandidate(BaseModel):
    """本章出现的称谓；落 alias 表，一个称谓在一书内只能指向一个实体。"""

    entityKey: Annotated[str, _clip_text(128)] = Field(min_length=1, max_length=128)
    aliasText: Annotated[str, _clip_text(128)] = Field(min_length=1, max_length=128)
    isPrimary: bool = False


class ForeshadowPlantCandidate(BaseModel):
    """本章埋下的伏笔。

    只有「埋」没有「收」：收束要按 id 关闭既有伏笔，而 id 来自 L1 注入的未收清单
    （N3），抽取节点此刻手里没有可引用的一手信息，硬让它猜 id 就是新的幻觉源。
    """

    content: Annotated[str, _clip_text(512)] = Field(min_length=1, max_length=512)
    dueByArc: int | None = None


class ChapterExtraction(BaseModel):
    """extract 节点的产出：一章正文对应的候选正典增量。

    ``assertions`` 的预算不是「一章能抽出多少条」，而是两个调用方里较大的那个：
    :func:`bible_extraction` 把书级圣经摊平成同一份载荷，最坏情形是
    24 规则 + 12 人物锚点 + 12 条 ``is_alive`` + 24 关系 = 72 条。按 20 卡它会让
    一本设定扎实的书写到 worldbuild 就整轮崩掉（实测翻车过一次）。
    四个字段都配 ``_clip_list``：模型多返回几条不该让整轮运行终止。
    """

    assertions: Annotated[list[AssertionCandidate], _clip_list(80)] = Field(
        default_factory=list, max_length=80
    )
    stateChanges: Annotated[list[StateChangeCandidate], _clip_list(20)] = Field(
        default_factory=list, max_length=20
    )
    aliases: Annotated[list[AliasCandidate], _clip_list(30)] = Field(
        default_factory=list, max_length=30
    )
    foreshadows: Annotated[list[ForeshadowPlantCandidate], _clip_list(10)] = Field(
        default_factory=list, max_length=10
    )


class SceneDigest(BaseModel):
    """单个场景的摘要条目。"""

    sceneNo: int = Field(ge=1, le=8, description="场景在本章内的序号，1 基")
    content: Annotated[str, _clip_text(300)] = Field(
        min_length=2, max_length=300, description="该场景发生了什么：人物、地点、状态变化，各一句"
    )


class ChapterDigest(BaseModel):
    """summarize 节点的产出：一章的场景级摘要 + 一段章级摘要。

    两者一起产出而不是两次调用：正文此刻已在上下文里，分两次就是同一章付两遍
    token，而且第二遍的输入换成第一遍的输出就成了「摘要的摘要」（§6-4 明令禁止）。
    """

    scenes: list[SceneDigest] = Field(
        default_factory=list, max_length=5, description="按叙事顺序切分，最多 5 段"
    )
    digest: Annotated[str, _clip_text(300)] = Field(
        min_length=2, max_length=300, description="整章一段话：谁做了什么、留下了什么未决"
    )


class ArcDigest(BaseModel):
    """弧级摘要：只从章级摘要合成，输入里没有正文。"""

    content: Annotated[str, _clip_text(400)] = Field(
        min_length=2,
        max_length=400,
        description="这一段剧情弧的推进与未收线，只允许使用给定的各章摘要",
    )


# ---------- 闸门产物（§9.2 双闸门的统一输出，字段名对齐 Java FindingItem） ----------

FindingCode = Literal[
    "attribute_conflict",  # C1 实体属性漂移
    "death_speaks",  # C2 已死角色发言
    "resurrection",  # C2 已死角色复活（无交代）
    "knowledge_leak",  # C2 knows 集合越界
    "alias_drift",  # C3 一个称谓指向多个实体
    "unregistered_entity",  # C3 白名单外新实体
    "timeline_break",  # C4 时间区间越界
    "world_rule_break",  # C5 世界规则违反
    "foreshadow_missing",  # C6 引用的伏笔编号不存在
    "unknown_ref",  # C6 正文引用了未注入的 [canon#N]
    "motivation_break",  # C6 情节与动机矛盾
    "style_drift",  # C6 人称/视角违反文风契约
    "length_out_of_band",  # C6 章节字数越带
    "forbidden_word",  # C6 命中禁用词
]
FindingSeverity = Literal["blocker", "major", "minor"]
FindingChecker = Literal["rule", "judge"]


class Finding(BaseModel):
    """一条冲突记录（闸门产物 → ``review_finding`` 行）。

    字段名沿用 Java 侧 ``InternalFindingRequest.FindingItem`` 的 camelCase，与
    :class:`AssertionCandidate` 同因：Finding 是「模型输出 / 规则命中 → 落库载荷」
    的一条直链，中间加一层 snake_case 映射只会多一个会漂移的翻译表。

    长度上限与 Java 的 ``clip(...)`` 逐字段对齐（code 32 / severity 16 /
    checker 16 / 三段文本 512）：**Python 侧先收敛，服务端才不会静默截断**——
    ``evidenceQuote`` 一旦被服务端裁短，它就跟 ``text_span`` 的原文不再逐字相等，
    机制②的落库产物自己过不了自己定的闸门。

    ``textStart`` / ``textEnd`` 可空：整章级规则（字数越带）没有可指向的片段，
    Java 的 ``review_finding.text_start`` 允许 NULL 并在服务层按「NULL 也算重复」
    显式查重，所以重放不会写双份。

    ``checker`` 给默认值而不是必填：提示词让裁判一律填 ``judge``，而 DeepSeek 会把这种
    「恒定值」字段省略掉，实测一次 7 条 missing 让整份 FindingList 作废，闸门只能报
    「裁判未完成」——一张查出了 7 条冲突的干净结果被整体丢掉。裁判侧本来就在
    ``judge.prepare_findings`` 里强制归位 checker，要求模型自报换不来任何约束。
    """

    code: Annotated[str, _clip_text(32)] = Field(
        min_length=1, max_length=32, description="冲突编码，见 FindingCode"
    )
    severity: FindingSeverity = Field(
        default="major", description="blocker 不 commit / major 进台账 / minor 仅记录"
    )
    checker: FindingChecker = Field(
        default="judge",
        description="rule 规则引擎 / judge 语义裁判；语义裁判可省略，默认 judge",
    )
    # L1 注入编号（[canon#N] / [fsh#N]），不是库主键：作者在工作台看到的编号必须
    # 与模型当时看到的那一份对得上，否则裁定无法复核。
    canonRefs: list[int] = Field(default_factory=list, max_length=12)
    textStart: int | None = Field(default=None, ge=0, description="正文片段起点（含）")
    textEnd: int | None = Field(default=None, ge=0, description="正文片段终点（不含）")
    evidenceQuote: Annotated[str, _clip_text(512)] = Field(
        default="", description="必须逐字等于 text[textStart:textEnd]"
    )
    explanation: Annotated[str, _clip_text(512)] = Field(default="", description="冲突是什么")
    fixInstruction: Annotated[str, _clip_text(512)] = Field(
        default="", description="只针对该片段的定向修补指令"
    )


class FindingList(BaseModel):
    """语义裁判（§9.2）的结构化产出：一章的 Finding 集合。

    只包一层列表、不带「通过/不通过」结论：判定权在闸门与放行策略（§9.3），
    裁判只负责给出可指认的冲突。让模型自己宣布 pass 就是 §8-⑨ 禁的自评通过。

    列表越界由 ``_clip_list`` 截断而非报错——理由与 ``_clip_text`` 同：一次裁判
    违约会让整轮运行终止，而截断只是少几条记录，且 ``GateReport`` 那边有计数。
    上限取 10：§9.2 要求「不给全库」以防裁判被淹，同理台账也不该被一次调用刷满。
    """

    findings: Annotated[list[Finding], _clip_list(10)] = Field(
        default_factory=list, max_length=10, description="本章查出的冲突，没有则空列表"
    )


class ProposalCandidate(BaseModel):
    """一张设定提议卡（§10.3 约定 1 的「主-谓-宾 / 生效区间 / 依据」前两行）。

    字段名对齐 Java 的 ``ProposalRequest``，前端拿到帧即可原样转发，不需要翻译表。

    刻意**没有**的两个字段：
    - ``validFromChapter``：生效起点由出卡时的参照章决定（graph 侧填），模型自报章号
      等于让它猜一个库里的位置——猜错就是「作者采纳了一条区间写错的设定」；
    - ``authority``：提议卡连一条断言都还不是，权威级只在作者点采纳之后由服务端判定
      （§10.5-②）。若这里能自报 author，聊天窗就成了提权入口。
    """

    kind: Annotated[str, _clip_text(24)] = Field(
        min_length=1,
        max_length=24,
        description="world_rule/character/relation/location/item/theme/style 之一",
    )
    subjectKey: Annotated[str, _clip_text(128)] = Field(
        min_length=1,
        max_length=128,
        description="实体键，人物用 char:xxx、地点 place:xxx、规则 rule:xxx；与已登记的同名同键",
    )
    predicate: Annotated[str, _clip_text(64)] = Field(
        min_length=1,
        max_length=64,
        description="机器可比谓词，小写下划线，如 eye_color / cannot_use",
    )
    objectText: Annotated[str, _clip_text(512)] = Field(
        min_length=1, max_length=512, description="值本体，一句话，不要写成剧情"
    )
    basisQuote: Annotated[str, _clip_text(512)] = Field(
        min_length=2,
        max_length=512,
        description="依据：本轮讨论里的那句原话，必须逐字出自那段答复（出卡前按此校验，对不上就不出卡）",
    )


class ProposalList(BaseModel):
    """提议抽取节点的产出：本轮讨论里值得写进正典的结论。

    与 :class:`FindingList` 同构——只包一层列表、不自报「已确认」：确认权在作者。
    没有结论时返回空列表，这是正常结果而不是失败。
    上限 5：一次对话谈成的设定就那么几条，多出来的多半是把同一个结论换了三种说法。
    """

    proposals: Annotated[list[ProposalCandidate], _clip_list(5)] = Field(
        default_factory=list, max_length=5, description="本轮讨论出的设定结论，没有则空列表"
    )


# ---------- 持久化记录（非 LLM 输出，store 协议的载荷类型） ----------


#: 题材字典：value 是入库串，label 是给模型与人看的中文。
#:
#: 真源在 Java 侧 ``NovelGenres.java``（书架筛选按 value 查，前端做 value→label 展示映射），
#: 这里是一份必须与它逐条对齐的镜像——``tests/test_genre_contract.py`` 会现读那个 java
#: 文件比对，漂了就让测试红，免得又靠一次线上 400 才发现。
GENRES: tuple[tuple[str, str], ...] = (
    ("fantasy", "玄幻"),
    ("wuxia", "武侠"),
    ("scifi", "科幻"),
    ("romance", "言情"),
    ("mystery", "悬疑"),
    ("history", "历史"),
    ("urban", "都市"),
    ("game", "游戏"),
    ("horror", "恐怖"),
    ("other", "其他"),
)

_VALUE_TO_LABEL = dict(GENRES)
_LABEL_TO_VALUE = {label: value for value, label in GENRES}
#: 括号里的补充说明（“都市科幻（都市异能+赛博救世）”的后半段）不参与取词。
_PARENTHETICAL = re.compile(r"[（(][^）)]*[）)]?")


def normalize_genre(raw: str) -> str:
    """把模型给的中文题材收敛成 ``GENRES`` 的 value。

    构思提示词允许复合类型（“都市科幻”），而服务端只认那十个固定串，宽容匹配会把脏值
    留在库里继续漂（``BookGenreContractTest`` 钉死了这个口径）。所以归一只发生在写边界：
    复合串取**最后一个**命中的词——中文偏正结构里中心词在后，“都市科幻”是科幻；
    一个都对不上时落 ``other`` 而不是丢空：书架上“其他”是个能筛的真实分类，
    而 ``genre`` 为空的书在任何类型筛选下都查不到，等于凭空少一本。
    """
    text = _PARENTHETICAL.sub("", raw or "").strip()
    if text in _VALUE_TO_LABEL:
        return text
    hits = [(text.find(label), label) for label in _LABEL_TO_VALUE if label in text]
    if not hits:
        return "other"
    return _LABEL_TO_VALUE[max(hits)[1]]


def genre_label(value: str) -> str:
    """把库里的 value 翻回中文 label，供提示词与事件流展示。

    认不出来的原样返回：``MockNovelStore`` 里存的本来就是中文，历史脏行也不该被这条
    函数改写成「其他」——读侧的展示映射没有资格改数据。
    """
    return _VALUE_TO_LABEL.get(value, value)


@dataclass(frozen=True, slots=True)
class BookDraft:
    """待归档的书稿元数据；NovelStore.save_book 的入参。

    ``genre`` 在这里仍是构思节点产出的中文原话（它同时要进注入块与成稿标题行）；
    译成 value 是 HTTP 数据层的事，见 :func:`normalize_genre`。
    """

    title: str
    genre: str
    summary: str


@dataclass(frozen=True, slots=True)
class ChapterDraft:
    """待归档的章节正文；NovelStore.save_chapters 的载荷元素。"""

    index: int  # 从 1 开始
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class ArchivedBook:
    """归档结果摘要；NovelStore.list_books 的返回项。

    只带聚合计数（章节数 / 角色数）而非正文：列表页用它渲染书目卡片，
    正文按需另取，避免一次查询拉回整本书。
    """

    book_id: str
    title: str
    genre: str
    summary: str
    chapter_count: int
    character_count: int
