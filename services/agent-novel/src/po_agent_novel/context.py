"""L1 记忆装配：把正典、层级摘要与原文尾段组装成注入块（PRD §6）。

存在的唯一理由：注入预算必须与书长无关。第 3 章和第 300 章拿到的上下文规模
应当一致——靠「把前文都塞进去」写长篇小说，成本随章数线性增长，而模型对中段
信息的利用率随长度衰减（§1.2），最后既是钱的问题也是连贯性问题。

四条装配规则（对应 §6 的四条）：
1. 先抽实体再检索：``entities`` 由调用方给定（N4 的 plan_scene 产出场景卡实体清单）。
   本模块**不**从大纲正文里猜实体——猜出来的实体键会让 Tier-1 命中一堆无关断言，
   比空命中更难发现。``entities=None`` 表示「本轮没有实体清单」，退化为全量 as-of 快照。
2. 注入即编号：每条事实前缀 ``[canon#N]``，``CompiledContext.refs`` 保存 N → 断言 id，
   这是机制②「证据强制」能落地的前提（正文引用必须能落回这些编号）。
3. Tier-2 必留原文尾段：只喂摘要会让文风趋同（摘要腔是真实退化模式），
   因此预算超支时的裁剪顺序里，原文尾段排在最后才被动。
4. 检索命中为空是信号不是错误：由调用方按「未知即缺口」处理（§8-③），本模块只如实
   返回空 Tier-1 并在 ``counts`` 里记账。
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from po_agent_novel.schemas import BookIdea, ChapterDraft, ChapterOutline
from po_agent_novel.store import (
    CanonAssertion,
    CanonStore,
    ChapterSnapshot,
    StyleProfileRecord,
    SummaryRecord,
)

# 契约行里每类词表最多列出几项（裁剪是按行做的，一条超长行会让整行落不进预算）
_STYLE_WORDS_MAX = 12

# CJK 区间：中日韩统一表意文字 + 扩展 A + 兼容表意 + 全角标点。
# 估算器按「1 汉字 ≈ 1 token」计，DeepSeek / OpenAI 的中文实测在 0.6~1.5 之间，
# 取 1 是刻意偏保守（宁可早裁剪，也不让注入悄悄越过预算）。
_CJK_RANGES = (
    (0x3000, 0x303F),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
    (0xFF00, 0xFFEF),
)


def approx_tokens(text: str) -> int:
    """无依赖的 token 估算：CJK 按字计，其余按 4 字符 1 token。

    不用 tiktoken：它的 BPE 文件要从 openaipublic blob 存储现拉，本项目的出网
    环境不通（见项目记忆 `project-network-mirrors`），一旦网络受限，
    「预算核算」就会变成「运行时崩溃」。预算是防御性度量，够用且确定性优先。
    """
    cjk = sum(1 for ch in text if any(lo <= ord(ch) <= hi for lo, hi in _CJK_RANGES))
    other = len(text) - cjk
    return cjk + math.ceil(other / 4)


@dataclass(frozen=True, slots=True)
class Budgets:
    """四层注入预算（token，估算口径见 :func:`approx_tokens`）。

    默认值即 PRD §6 表的四行，总和 4000——「P95 注入 ≤ 4k」这条退出条件是
    由裁剪保证的硬上限，不是统计期望：装配结果超限就当场砍。
    """

    tier0: int = 800
    tier1: int = 1500
    tier2: int = 1000
    task: int = 700

    @property
    def total(self) -> int:
        return self.tier0 + self.tier1 + self.tier2 + self.task


@dataclass(frozen=True, slots=True)
class CanonRef:
    """一条被编号注入的事实：``number`` 是提示词里的 ``[canon#N]`` 或 ``[fsh#N]``。"""

    number: int
    kind: str  # canon（断言）/ foreshadow（未收伏笔）
    source_id: str
    text: str


@dataclass(frozen=True, slots=True)
class StyleContract:
    """文风契约（Tier-0 的一行）。

    载体是 ``style_profile`` 表：作者手改的契约经内部通道读回后覆盖派生值
    （:meth:`with_profile`），没定过的书仍用装配侧从本轮构思派生的默认契约，
    所以 Tier-0 永不为空。
    """

    genre: str
    pov: str = "第三人称限知"
    tense: str = "过去时"
    forbidden_words: tuple[str, ...] = ()
    tics: tuple[str, ...] = ()
    taboo: tuple[str, ...] = ()
    chapter_words_min: int | None = None
    chapter_words_max: int | None = None
    sentence_len_min: int | None = None
    sentence_len_max: int | None = None

    def with_profile(self, record: StyleProfileRecord | None) -> StyleContract:
        """把作者定的契约盖到派生契约上。

        只盖作者真表了态的字段（``None`` = 没表态）：作者一次只收紧「人称 + 字数带」
        是常态，把没填的项当空值覆盖会把派生值抹平。词表按「给了就整份替换」处理——
        管理端 PUT 的空数组就是作者明确的「这一项清空」。
        """
        if record is None:
            return self
        return replace(
            self,
            pov=record.person or self.pov,
            tense=record.tense or self.tense,
            forbidden_words=record.forbidden_words or self.forbidden_words,
            tics=record.tics or self.tics,
            taboo=record.taboo or self.taboo,
            chapter_words_min=record.chapter_words_min or self.chapter_words_min,
            chapter_words_max=record.chapter_words_max or self.chapter_words_max,
            sentence_len_min=record.sentence_len_min or self.sentence_len_min,
            sentence_len_max=record.sentence_len_max or self.sentence_len_max,
        )

    def as_line(self) -> str:
        """Tier-0 的契约行。

        词表只列前 ``_STYLE_WORDS_MAX`` 项：这一层是按行裁剪的，一条 30 个禁用词的长行
        会先把自己挤出预算，结果不是「少看几个词」而是整条文风契约都不注入。
        """
        parts = [f"文风契约：{self.genre}｜{self.pov}｜{self.tense}"]
        if self.chapter_words_min or self.chapter_words_max:
            parts.append(
                f"单章 {self.chapter_words_min or '不限'}-"
                f"{self.chapter_words_max or '不限'} 字"
            )
        if self.sentence_len_min or self.sentence_len_max:
            parts.append(
                f"句长 {self.sentence_len_min or '不限'}-"
                f"{self.sentence_len_max or '不限'} 字"
            )
        for label, words in (("禁用词", self.forbidden_words), ("口头禅", self.tics)):
            if words:
                shown = "、".join(words[:_STYLE_WORDS_MAX])
                more = f"（共 {len(words)} 项）" if len(words) > _STYLE_WORDS_MAX else ""
                parts.append(f"{label}：{shown}{more}")
        if self.taboo:
            shown = "、".join(self.taboo[:_STYLE_WORDS_MAX])
            more = f"（共 {len(self.taboo)} 项）" if len(self.taboo) > _STYLE_WORDS_MAX else ""
            parts.append(f"禁项：{shown}{more}")
        return "；".join(parts) + "。"


@dataclass(slots=True)
class CompiledContext:
    """L1 装配产物。

    ``refs`` / ``snapshot`` / ``style`` 三个字段是给规则闸门（gates.GateInput）的：
    闸门必须用**这一次装配**的行集与编号，而不是自己再去读一遍库——自读会得到一份
    更宽（或更窄）的视图，于是「闸门报的冲突模型压根没看见」与「模型用的设定闸门查不到」
    两种错都无从归因。
    ``snapshot`` 与 ``refs`` 里的 canon 行 1:1（含本轮 overlay，按 ``pending:`` 键编号，
    并以 ``world`` 里的圣经行打头——它们同样受实体与 as-of 之外的全书级约束），
    且都在预算裁剪**之前**取全：被裁掉的行模型没读到，但仍是合法引用对象。
    对闸门同理——正文与设定冲突是写在章里的事实，不因为那条设定没进注入块就变成对的；
    它同时也是一条 L1 信号（该进 Tier-1 的实体没进），代价是可能报出模型无从避免的冲突，
    所以 N4b 只记账不拦截。
    """

    block: str
    refs: list[CanonRef] = field(default_factory=list)
    snapshot: list[CanonAssertion] = field(default_factory=list)
    style: StyleContract | None = None
    tokens: int = 0
    counts: dict[str, int] = field(default_factory=dict)


def _fit(lines: list[str], budget: int) -> tuple[list[str], int]:
    """按预算从尾部裁剪，返回（保留行, 丢弃条数）。

    从尾部丢而不是从头丢：列表头部即检索器认为最相关的条目（as-of 快照按
    established 升序，越靠后越旧/越边缘），头部被丢会让模型看不到本章直接实体的状态。
    """
    kept: list[str] = []
    used = 0
    dropped = 0
    for line in lines:
        cost = approx_tokens(line)
        if used + cost > budget:
            dropped += 1
            continue
        kept.append(line)
        used += cost
    return kept, dropped


def _assertion_line(ref_number: int, subject_key: str, predicate: str, object_text: str) -> str:
    return f"[canon#{ref_number}] {subject_key} · {predicate} = {object_text}"


def _with_framing(budgets: Budgets, reserve: int = 10) -> Budgets:
    """给每段留出标题行与空行的开销。

    「P95 注入 ≤ 4k」按注入块的总 token 计，而各层预算只管内容行；不留这一份，
    四个段落标题就会在预算之外再叠 30~40 token，上限变成一句没人核验的话。
    """
    return Budgets(
        tier0=max(0, budgets.tier0 - reserve),
        tier1=max(0, budgets.tier1 - reserve),
        tier2=max(0, budgets.tier2 - reserve),
        task=max(0, budgets.task - reserve),
    )


async def compile_context(
    canon_store: CanonStore,
    *,
    book_id: str | None,
    idea: BookIdea,
    outline: Sequence[ChapterOutline],
    index: int,
    chapters: Sequence[ChapterDraft],
    task_chapter: ChapterSnapshot | None = None,
    entities: list[str] | None = None,
    world: Sequence[CanonAssertion] = (),
    overlay: Sequence[CanonAssertion] = (),
    digests: Sequence[SummaryRecord] = (),
    style: StyleContract | None = None,
    prior_tail: str = "",
    budgets: Budgets = Budgets(),
    recent_chapters: int = 3,
    tail_chars: int = 300,
    summary_limit: int = 24,
) -> CompiledContext:
    """装配「当前章」的注入块。

    :param book_id: 书 id；``None`` 或空串表示尚未落库（本轮从零开始写），此时 Tier-1/2
        没有任何可读的东西，直接跳过读取而不是拿假 id 去打后端
    :param index: 正在写章的 0 基下标；**as-of = index**，即「截至已定稿的那一章」。
        这个换算是不泄漏后文的唯一支点：写第 index+1 章时绝不读取第 index+1 章之后
        的事实，回溯重写第 12 章时也不会看到第 30 章
    :param entities: 场景卡实体清单（§6-1）。缺省 ``None`` = 无清单，Tier-1 退化为
        全量 as-of 快照（不猜实体，见模块 docstring）
    :param world: 书级圣经的设定行（worldbuild 产出，形态同 overlay 的 ``CanonAssertion``）。
        它们进 **Tier-0** 而不是 Tier-1，且不受 ``entities`` 与 ``as_of >= 1`` 约束，两个理由：
        ① 它们是全书背景（世界规则、人物锚点），「本章没提到这个实体」不等于可以不遵守；
        ② 第 1 章的 as_of 是 0，Tier-1 整段不跑——若圣经只走 Tier-1，开篇那一章恰恰
        看不见全书唯一的设定，而它正是最容易把世界观写歪的一章。
        编号与 Tier-1 共用一条序列，因此正文与规则闸门能照样引 ``[canon#N]``
    :param overlay: 本轮已抽但**尚未入库**的候选断言（CanonAssertion 形态）。
        正典写入刻意留在归档确认之后（resume 重放会把入库写成双份），于是连续写
        多章时第 2 章读不到第 1 章的事实——overlay 就是补这一段的本轮内存视图。
        它按同样的 as-of 与实体条件过滤，编号与库内断言共用一条序列，
        ``refs.source_id`` 以 ``pending:`` 前缀标明「还没落地」
    :param digests: 本轮已产但尚未入库的层级摘要行（``SummaryRecord`` 形态），
        与 overlay 同理——摘要也是在归档之后才落库，连续写多章时前几章的场景摘要
        只能从本轮状态里取。同 (level, 章号, 场景号) 以本轮为准
    :param recent_chapters: Tier-2 取前几章的场景摘要（PRD：前 3 章）
    :param tail_chars: Tier-2 上一章末尾原文字数（PRD：300）
    :param prior_tail: 本轮 ``chapters`` 为空时的「上一章结尾原文」（续写模式的第一章）。
        续写时上一批章的正文在库里而不在本轮状态里，``chapters[-1]`` 取不到，
        不传它就会让本轮第一章什么衔接都不带——那是最容易被忽略也最贵的一种漏注入：
        正文照写，衔接全靠模型猜。已有本轮定稿章时 ``chapters[-1]`` 优先，
        因为它更新（前一轮的库内尾段此刻已经是「上上一章」）。
    :param task_chapter: 对话侧的「当前参照章」（§10.3 左栏：把任意章设为参照章）。
        设置后它同时改写两处：任务区不再出大纲而是「当前参照章」，近因的原文尾段
        取这一章的末尾。之所以由一个参数同时管两件事——分开传就会出现「任务区说第 5 章、
        尾段来自第 8 章」这种没人会报错的错配。生成链路永不传它。
        **必须满足 ``task_chapter.index <= index``**：as-of 仍是唯一支点，参照章的正文
        若晚于 as-of，未定稿的后文就会从近因漏进上下文，所以这里直接拒绝而不是过滤。
    """
    as_of = index
    if task_chapter is not None and task_chapter.index > as_of:
        raise ValueError(
            f"参照章第 {task_chapter.index} 章晚于 as-of 第 {as_of} 章，注入会漏后文"
        )
    budgets = _with_framing(budgets)
    # 空串与 None 同义：ns["book_id"] 在归档前是空串，此时库里根本没有这本书，
    # 拿它去打后端只会得到「book 不存在」的 400（HTTP 实现的 _as_int 也会直接拒绝）。
    book_id = book_id or None
    counts: dict[str, int] = {
        "tier1": 0,
        "tier2": 0,
        "dropped": 0,
        "openForeshadows": 0,
        "world": 0,
    }
    # 编号序列从 Tier-0 就开始分配（圣经行也要能被正文与闸门引用），所以 refs 提到最前。
    # 它与 snapshot 同源于「这一次装配」，闸门必须用这一份而不是自己再读一遍库。
    refs: list[CanonRef] = []

    # ---------- Tier-0 常驻：与书长无关的一屏背景 ----------
    tier0: list[str] = [f"世界观与主线：{idea.summary}"]
    contract = style or StyleContract(genre=idea.genre)
    progress_line: str | None = None
    if book_id is not None:
        # 作者手改的契约盖在本轮派生值之上（§5.5）：闸门用的词表取自 compiled.style，
        # 所以装配与闸门读的是同一份，不会分裂成「计划里没禁、正文里被禁」。
        contract = contract.with_profile(await canon_store.load_style_profile(book_id))
        # 进度线用最新 arc 摘要：arc 是「截至某章已知」的最高层压缩，
        # 用它代替「把前面所有章节标题列一遍」，预算才不会随章数增长。
        # 读端按「整段区间都 ≤ as-of」过滤，所以拿到的 arc 必然不含后文。
        arcs = await canon_store.load_summaries(
            book_id, upto_chapter=as_of, levels=("arc",), limit=1
        )
        if arcs:
            progress_line = f"主线进度（自第 {arcs[0].chapter_no} 章的弧）：{arcs[0].content}"
    tier0.append(contract.as_line())
    if progress_line:
        tier0.append(progress_line)
    # 圣经行排在最后：_fit 从尾部丢弃，超限时的牺牲顺序是 关系 → 人物 → 世界规则 →
    # 进度线，把「不可违背的规则」留到最后才被动。
    world_rows = [row for row in world if row.status == "confirmed"]
    for row in world_rows:
        number = len(refs) + 1
        tier0.append(_assertion_line(number, row.subject_key, row.predicate, row.object_text))
        refs.append(
            CanonRef(
                number=number,
                kind="canon",
                source_id=row.id or f"pending:{row.subject_key}:{row.predicate}",
                text=f"{row.subject_key} · {row.predicate} = {row.object_text}",
            )
        )
    counts["world"] = len(world_rows)
    tier0_kept, tier0_dropped = _fit(tier0, budgets.tier0)
    counts["dropped"] += tier0_dropped

    # ---------- Tier-1 检索：本章涉及的实体截至 as-of 的断言 + 相关 open 伏笔 ----------
    tier1: list[str] = []
    # (断言, 是否本轮候选)：候选没有库主键，编号引用时要带 pending: 前缀标明「还没落地」
    assertion_rows: list[tuple[CanonAssertion, bool]] = []
    if as_of >= 1:
        if book_id is not None:
            snapshot = await canon_store.load_snapshot(
                book_id, as_of_chapter=as_of, entities=entities
            )
            assertion_rows.extend((fact, False) for fact in snapshot)
        seen = {(fact.subject_key, fact.predicate) for fact, _ in assertion_rows}
        for extra in overlay:
            # overlay 走与库读同一套过滤条件，否则「本轮视图」会比库内视图更宽松，
            # 后文事实就会从这里绕过 as-of 这道支点漏进上下文
            if extra.status != "confirmed":
                continue
            if extra.valid_from_chapter > as_of:
                continue
            if extra.valid_until_chapter is not None and extra.valid_until_chapter < as_of:
                continue
            if entities and extra.subject_key not in set(entities):
                continue
            if (extra.subject_key, extra.predicate) in seen:
                continue
            seen.add((extra.subject_key, extra.predicate))
            assertion_rows.append((extra, True))
        for entry, pending in assertion_rows:
            number = len(refs) + 1
            text = _assertion_line(number, entry.subject_key, entry.predicate, entry.object_text)
            tier1.append(text)
            refs.append(
                CanonRef(
                    number=number,
                    kind="canon",
                    source_id=(
                        f"pending:{entry.subject_key}:{entry.predicate}"
                        if pending
                        else entry.id
                    ),
                    text=f"{entry.subject_key} · {entry.predicate} = {entry.object_text}",
                )
            )
        counts["tier1"] = len(assertion_rows)
        if book_id is not None:
            foreshadows = await canon_store.load_open_foreshadows(book_id, as_of_chapter=as_of)
            for record in foreshadows:
                due = f"，应于第 {record.due_by_arc} 弧内收" if record.due_by_arc else ""
                number = len(refs) + 1
                # 编号与断言共用一条序列（前缀区分类型）：正文若要收某条伏笔，
                # 也靠这个编号回指，不必让模型去复述数据库主键。
                tier1.append(
                    f"[fsh#{number}] 未收伏笔（埋于第 {record.planted_chapter} 章{due}）："
                    f"{record.content}"
                )
                refs.append(
                    CanonRef(
                        number=number,
                        kind="foreshadow",
                        source_id=record.id,
                        text=record.content,
                    )
                )
            counts["openForeshadows"] = len(foreshadows)
    tier1_kept, tier1_dropped = _fit(tier1, budgets.tier1)
    counts["dropped"] += tier1_dropped

    # ---------- Tier-2 近因：前 N 章场景摘要 + 上一章末尾原文 ----------
    tier2: list[str] = []
    if as_of >= 1:
        allowed = set(range(max(1, as_of - recent_chapters + 1), as_of + 1))
        summary_rows: list[SummaryRecord] = []
        if book_id is not None:
            stored = await canon_store.load_summaries(
                book_id,
                upto_chapter=as_of,
                levels=("scene", "chapter"),
                limit=summary_limit,
            )
            # chapter_no 为 NULL 的加列前历史行落不进任何窗口，因此自然被排除
            summary_rows = [record for record in stored if record.chapter_no in allowed]
        summary_rows.extend(record for record in digests if record.chapter_no in allowed)
        # 同键去重：后写的本轮摘要覆盖库内旧行（本章刚定稿时库里还是上一版正文的摘要）
        merged = {
            (record.level, record.chapter_no, record.scene_no or 0): record
            for record in summary_rows
        }
        # 新章在前：_fit 从尾部丢弃，被牺牲的必须是最久的那几章
        ordered = sorted(
            merged.values(), key=lambda record: (-(record.chapter_no or 0), record.scene_no or 0)
        )
        # 同一章只进一层：有场景拆解就用场景，没有才退到章级摘要。
        # 两级同注等于把同一章说两遍，白吃掉近因预算的大半。
        has_scene = {record.chapter_no for record in ordered if record.level == "scene"}
        for record in ordered:
            if record.level == "chapter" and record.chapter_no in has_scene:
                continue
            at = (
                f"·场景 {record.scene_no}"
                if record.level == "scene" and record.scene_no
                else ""
            )
            tier2.append(f"第 {record.chapter_no} 章{at}摘要：{record.content}")
            counts["tier2"] += 1
    # 原文尾段进的是 Tier-2 预算，但裁剪发生在摘要之后（规则 3）。
    tail_source = (
        task_chapter.content
        if task_chapter is not None
        else (chapters[-1].content if chapters else prior_tail)
    )
    tail = tail_source[-tail_chars:]
    # 尾段归属要说对：对话带进来的参照章就是「当前这一章」，标成「上一章」会让模型
    # 把正在讨论的那一章当成过去式来谈。
    tail_label = "上一章结尾原文：" if task_chapter is None else "当前参照章结尾原文："

    # ---------- 任务区：本章大纲（生成）/ 当前参照章（对话） ----------
    task: list[str] = []
    if task_chapter is not None:
        task.append(
            f"当前参照章：《{task_chapter.title}》（第 {task_chapter.index} 章，已定稿）"
        )
    else:
        chapter = outline[index] if index < len(outline) else None
        if chapter is not None:
            task.append(f"本章大纲：《{chapter.title}》——{chapter.summary}")
    task.append(
        "只使用上面编号过的设定；正文没写到的设定不要自行补全，"
        "需要它就先把它当作缺口（后续章节再登记），不要编。"
    )
    task_kept, task_dropped = _fit(task, budgets.task)
    counts["dropped"] += task_dropped

    # Tier-2 的裁剪单独算：摘要先让位，原文尾段最后才被动。
    tier2_budget_used = sum(approx_tokens(line) for line in tier2)
    tail_cost = approx_tokens(f"{tail_label}{tail}") if tail else 0
    if tier2_budget_used + tail_cost > budgets.tier2:
        room = max(0, budgets.tier2 - tail_cost)
        tier2_kept, tier2_dropped = _fit(tier2, room)
        counts["dropped"] += tier2_dropped
    else:
        tier2_kept = tier2

    sections = [f"# 世界与进度\n{chr(10).join(tier0_kept)}"]
    tier1_text = "\n".join(tier1_kept) or "（无登记）"
    sections.append(f"# 已成立的事实（截至第 {as_of} 章）\n{tier1_text}")
    # 空段不进块：连着两个「（无登记）」比缺一段更 distracting，而且白占预算
    if tier2_kept or tail:
        recent = "\n".join(tier2_kept)
        tail_line = f"{tail_label}{tail}" if tail else ""
        sections.append("# 近因\n" + "\n".join(part for part in (recent, tail_line) if part))
    sections.append(f"# 本章任务\n{chr(10).join(task_kept)}")
    block = "\n\n".join(sections)
    counts["refs"] = len(refs)
    return CompiledContext(
        block=block,
        refs=refs,
        snapshot=[*world_rows, *(fact for fact, _ in assertion_rows)],
        style=contract,
        tokens=approx_tokens(block),
        counts=counts,
    )


__all__ = [
    "Budgets",
    "CanonRef",
    "CompiledContext",
    "StyleContract",
    "approx_tokens",
    "compile_context",
]
