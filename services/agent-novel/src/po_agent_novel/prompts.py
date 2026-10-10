"""小说创作提示词（全新编写，不搬移参考实现文本）。

统一结构：角色 / 目标 / 输入 / 工作要点 / 输出格式。
提示词为纯函数：入参领域数据，出参完整提示词字符串，
不引用运行时状态，便于单测与后续外置化管理。

调用方是 graph 中的子图节点，一节点一模板：
- conceive_prompt ← conceive 节点：一句话想法 → 书名/题材/梗概；
- worldbuild_prompt ← worldbuild 节点：动笔之前的书级圣经（规则/人物/关系/文风契约）；
- outline_prompt ← outline 节点：全书章节大纲；
- plan_scene_prompt ← plan_scene 节点：本章场景卡（用哪些实体、谁在场、要收哪条伏笔）；
- write_chapter_prompt / revise_prompt ← write 与 revise 节点：初稿 / 整章重写；
- patch_prompt ← revise 节点：只重写闸门点出的一个片段；
- judge_prompt ← 正文语义裁判（judge.run_judge）：查规则覆盖不到的 C5/C6，产 FindingList；
- plan_judge_prompt ← 计划语义裁判（judge.run_plan_judge）：审**场景卡**而不是正文；
- extract_prompt ← extract 节点：从定稿正文抽取候选正典（断言/状态/称谓/伏笔）；
- summarize_chapter_prompt / summarize_arc_prompt ← 摘要步骤：章正文 → 场景/章级摘要，
  章级摘要 → 弧级摘要（层级摘要树，见 context.compile_context 的 Tier-2 与 Tier-0）；
- extract_characters_prompt ← archive 节点：归档前从全书正文抽角色档案；
- novel_chat_prompt / proposal_extract_prompt ← novel-chat 插槽：创作工作台右栏的
  对话与「把讨论里的定论升为提议卡」的结构化抽取（见 chat.py，对话不写正典也不写正文）。

没有「审稿打分」模板：自评式回环（旧 reflect 节点）已在 §8-⑨ 与 N4 退出条件里废除，
一章能不能定稿只由 gate_text 的闸门产物与放行策略（§9.3）决定。

模板末尾的「输出格式」节与 schemas 的 Field description 互为双保险：
前者是自然语言引导，后者是结构化输出（with_structured_output）的硬约束。
"""

from __future__ import annotations

from po_agent_novel.schemas import (
    BookIdea,
    ChapterDraft,
    ChapterOutline,
    SceneCard,
)
from po_agent_novel.store import BookSnapshot

# 抽取契约版本：进入幂等键（见 store.ExtractionSource）。改 extract_prompt 的
# 字段语义或判定口径时必须 +1，否则同一章的新旧抽取在库侧被视为同一次而互相屏蔽。
#
# judge_prompt 不在这条键上：`review_finding` 没有 prompt_version/model 列，Finding 的
# 去重靠 (chapter_id, revision, code, checker)。所以改裁判提示词不会让库里的旧
# Finding 失效，重放同一版正文只会覆盖同编码的行——需要按提示词版本统计误报率时，
# 得先给 review_finding 补列（PRD §15.3 偏差 #1）。
PROMPT_VERSION = "v1"


def conceive_prompt(brief: str) -> str:
    """构思提示词：把一句话想法扩展为书名/题材/梗概。

    :param brief: 本轮用户输入原文（可能只有一句话），来自父图最近一条 HumanMessage
    """
    return f"""# 角色
你是资深网文主编，擅长把一句话想法打磨成有读者缘的作品构思。

# 目标
基于用户想法确定书名、题材类型与核心梗概。

# 输入
用户想法：{brief}

# 工作要点
- 书名要有记忆点、贴合题材气质，不与知名作品雷同；
- 题材只能用类型字典里的词：玄幻 / 武侠 / 科幻 / 言情 / 悬疑 / 历史 / 都市 / 游戏 / 恐怖 / 其他。
  可以复合（如「都市科幻」），但**中心词必须放在最后**——入库时按最后一个字典词归架，
  「都市科幻」进科幻架，「科幻都市」进都市架；括号里的补充说明不参与归架；
- 核心梗概一两句话，必须包含主角、核心冲突与最大看点。

# 输出格式
按结构化约束返回：title（书名）、genre（题材）、summary（核心梗概）。"""


def outline_prompt(idea: BookIdea, chapter_count: int) -> str:
    """大纲提示词：为已确定的构思规划全书章节。

    :param idea: 构思结果（书名/题材/梗概），提供主题与基调
    :param chapter_count: 目标章数，由装配参数给出；需与 Outline.chapters 的
        max_length=20 相容（schema 才是最终硬约束，提示词只是引导）
    """
    return f"""# 角色
你是小说结构师，擅长用章节大纲撑起完整的叙事骨架。

# 目标
为《{idea.title}》（{idea.genre}）规划 {chapter_count} 章大纲。

# 输入
核心梗概：{idea.summary}

# 工作要点
- 每章有明确的剧情推进与至少一个关键场景；
- 章节间形成因果链：铺垫→发展→高潮→收束；
- 章节标题风格统一、有画面感；
- arc 用「一段剧情弧的名字」把章节分组（连续几章写同一个 arc），只有确实换了一段
  剧情才起新名字；全书不足三段剧情时 arc 一律留空。

# 输出格式
按结构化约束返回 chapters：每项含 title（章节标题）、summary（本章概要）、arc（所属剧情弧，可空）。"""


def worldbuild_prompt(idea: BookIdea) -> str:
    """书级圣经提示词：动笔之前先把世界钉死（§机制①「先定义再动笔」）。

    这一份产出决定了后面每一章「能引的事实」，因此要求全部落在可判定形态上：
    规则要能当成比对对象（一条一个谓词），人物要有稳定 key（后面按 key 认人），
    想不清楚的必须进 openQuestions 而不是编一个答案。
    """
    return f"""# 角色
你是设定管理员，负责在一本书动笔之前把它的世界钉死。

# 目标
为《{idea.title}》（{idea.genre}）建立书级圣经：世界规则、开篇人物、人物关系、文风契约、禁用词与未决缺口。

# 输入
核心梗概：{idea.summary}

# 工作要点
- 规则要「可判定」：写「月光会灼伤沈青的皮肤」这种能拿去比对的句子，不写「月光很重要」；
  一条规则一个谓词，predicate 用小写下划线（如 harms / cannot_use / exists_at）；
- subjectKey 用「类型:归一名拼音」形式（rule:、loc:、item:、char:），全小写、整本书唯一；
- characters 的 key 必须是 char: 前缀，后续所有章节都按这个 key 认人；外貌、能力边界、
  说话方式写进 anchor，只写不可违背的部分；
- 开篇就已经死掉的人物 alive=false——正文此后不许让他们直接开口；
- relations 的 fromKey/toKey 只能用上面 characters 里出现过的 key，不许发明新人物；
- pov 与 tense 是整本书的硬契约（例：第三人称限知 / 过去时），定了就不许中途换；
- forbidden 只放题材与平台红线词（这个世界里不该存在、或写了就会被拦的），宁少勿多，没有就留空；
- 想不清楚、但会影响后面一致性的问题一律进 openQuestions，**不要**在 rules 里替作者编一个答案。

# 输出格式
按结构化约束返回：logline、rules（kind/subjectKey/predicate/objectText/restatement/status）、
characters（key/name/role/anchor/alive）、relations（fromKey/toKey/relation/restatement）、
pov、tense、forbidden、openQuestions。某一类没有就返回空列表。"""


def plan_scene_prompt(
    idea: BookIdea,
    chapter: ChapterOutline,
    index: int,
    *,
    total: int,
    registered: list[str],
    foreshadows: list[str],
    chapter_words: int,
    pov: str = "",
    prev_tail: str = "",
    instruction: str = "",
) -> str:
    """场景卡提示词：写正文之前先交出「这一章打算怎么写」。

    存在的理由：正文一旦写出来，实体、在场人物、要收的伏笔就都被既成事实绑住了。
    计划阶段把这些挑出来，闸门才能在**几行文本**上判掉「让已死的人出场」这类冲突，
    而不是等 1200 字写完再烧一轮修补；计划里的实体清单同时是 L1 的 Tier-1 检索条件
    （PRD §6-1「先抽实体再检索」）。

    :param registered: 已登记实体键全集（只能从中挑选，挑不出的进 newEntities）；
        空列表时提示词明说「本章无可选实体」，避免模型以为漏传而自己编一套
    :param foreshadows: 未收伏笔的编号行（``[fsh#N] …``），``payoffs`` 只能引这里的编号
    :param instruction: 计划闸门上一轮的退回意见（replan 回环时非空）
    """
    entities = (
        f"已登记实体键（只能从这些里挑）：{'、'.join(registered)}"
        if registered
        else "已登记实体键（只能从这些里挑）：（本章无可挑实体，entities 请留空）"
    )
    payoff_lines = "\n".join(foreshadows) if foreshadows else "（当前没有未收的伏笔，payoffs 请留空）"
    tail = f"上一章结尾（衔接参考）：\n{prev_tail}\n" if prev_tail else ""
    rework = f"\n上一版计划的退回意见（必须逐条改掉）：\n{instruction}\n" if instruction else ""
    style = f"文风契约：{pov}\n" if pov else ""
    return f"""# 角色
你是这本小说的责任编辑，负责在作者动笔之前把本章要用的设定与场景排清楚。

# 目标
为《{idea.title}》第 {index + 1}/{total} 章《{chapter.title}》出一张场景卡。

# 输入
本章大纲：{chapter.summary}
{style}{entities}
未收伏笔（要收就引这里的编号）：
{payoff_lines}
{tail}{rework}
# 工作要点
- entities 只能逐字从上面「已登记实体键」里挑本章真正要用到的（出场、被提及、被对话的都算）；
  大纲里出现了清单之外的人物，写进 newEntities，**不要**替它编设定，也不要把它的名字混进 entities；
- 每个场景的 present 是在场人物（含旁听者），只能写 entities 里有的 key：
  不在场的人不许有台词，已登记为死亡的人不许出现在 present 里；
- mustChange 写「本章结束时必须与开始时不同」的状态（谁知道了什么、谁丢了什么、谁死了），
  一章没有任何变化的场景就是水字数；
- wordsLow/wordsHigh 围绕目标字数给一个能接受的带，别宽到失去约束意义；
- 这一张卡只是计划，不会进设定库：不要在 restatement 之外的地方宣布新事实。

# 输出格式
按结构化约束返回：entities、newEntities、scenes（goal/locationKey/present/beats）、
mustChange、payoffs（整数编号）、wordsLow、wordsHigh、hook。
本章目标字数：{chapter_words}"""


def scene_card_text(card: SceneCard, chapter: ChapterOutline | None = None) -> str:
    """场景卡 → 稳定文本。

    两个用途：① 写正文时作为任务区（比 summary 更可执行）；② 计划闸门的 **span 坐标系**
    ——裁判要在计划文本上指出「就是这一行有问题」，因此这里必须是无歧义的纯文本，
    且同一张卡每次都渲染成同一个字符串（否则重放时坐标漂移，台账里的片段指向别处）。
    """
    lines: list[str] = []
    heading = f"第 {card.wordsLow}-{card.wordsHigh} 字"
    if chapter is not None:
        heading = f"《{chapter.title}》场景计划（{heading}）"
    lines.append(heading)
    lines.append("本章实体：" + ("、".join(card.entities) if card.entities else "（无）"))
    if card.newEntities:
        lines.append("待登记新实体：" + "、".join(card.newEntities))
    for scene_no, scene in enumerate(card.scenes, start=1):
        present = "、".join(scene.present) if scene.present else "（无）"
        where = scene.locationKey or "（未定地点）"
        lines.append(f"场景 {scene_no}｜{where}｜在场：{present}｜目标：{scene.goal}")
        for beat in scene.beats:
            lines.append(f"  · {beat}")
    if card.mustChange:
        lines.append("必须改变：" + "；".join(card.mustChange))
    if card.payoffs:
        lines.append("要收的伏笔：" + "、".join(f"[fsh#{no}]" for no in card.payoffs))
    if card.hook:
        lines.append(f"章末钩子：{card.hook}")
    return "\n".join(lines)


def write_chapter_prompt(
    idea: BookIdea,
    chapters: list[ChapterOutline],
    index: int,
    prev_tail: str,
    chapter_words: int,
    context: str | None = None,
    card: SceneCard | None = None,
) -> str:
    """初稿提示词：index 为 0 基章节序号。

    write 节点调用（正文只有一条产出路径：整章重写归 revise 节点）。
    :param idea: 构思结果，给正文定基调
    :param chapters: 全书大纲，用于给本章定位并保持全书视角
    :param index: 当前章下标（0 基），仅用于编号展示与定位本章大纲
    :param prev_tail: 上一章定稿正文的末尾 200 字；开篇传空串
    :param chapter_words: 目标字数，写入「目标」节
    :param context: L1 装配产物（见 context.compile_context）。**非空时它已经包含
        「上一章结尾原文」与本章任务区**，此时 prev_tail 被忽略——两处各贴一份
        上章结尾会把注入预算白烧一倍，而且两份不一致时模型会挑错的那份跟
    :param card: 本章场景卡（plan_scene 产出、gate_plan 放行后才走到这里）。
        它是**必须执行的任务单**而不是参考意见：在场名单与伏笔回收编号都已被闸门
        校验过，正文脱离它写就是「计划白做」——计划闸门拦不住的那种漂移
    """
    outline_lines = "\n".join(
        f"{i + 1}. 《{c.title}》{c.summary}" for i, c in enumerate(chapters)
    )
    chapter = chapters[index]
    task = f"\n\n本章场景计划（按它执行）：\n{scene_card_text(card, chapter)}" if card else ""
    if context:
        # 有 L1 注入时不再贴「全书大纲全文」：那是随书长增长的文本，正是 §6
        # 要把预算与书长解耦的第一号对象；本章大纲已在 context 的任务区里。
        prev = context + task
    else:
        # 空串代表开篇（尚无已定稿章节）：切换为「铺开世界观」的要求，
        # 而非让模型面对一段空的「上一章结尾」。
        prev = f"上一章结尾（衔接参考）：\n{prev_tail}" if prev_tail else "（本章为开篇）"
        prev = (
            f"题材与梗概：{idea.genre}——{idea.summary}\n"
            f"全书大纲：\n{outline_lines}\n{prev}"
        )
        prev += task
    return f"""# 角色
你是小说作者，正在为《{idea.title}》撰写正文。

# 目标
写第 {index + 1}/{len(chapters)} 章《{chapter.title}》，约 {chapter_words} 字。

# 输入
{prev}

# 工作要点
- 剧情严格贴合上面的场景计划：在场名单之外的人物不要有台词与行动，
  计划点名的伏笔要在本章正面回收，不要顺手新增设定；
- 开头承接上一章结尾；开篇则铺开世界观与主角处境；
- 叙述视角与时态严守文风契约，对话与描写交替，结尾按计划留钩子引出下一章。

# 输出格式
直接输出正文：不带章节标题、不带任何解释性文字。"""


def revise_prompt(
    idea: BookIdea,
    chapter: ChapterOutline,
    index: int,
    draft: str,
    feedback: str,
    chapter_words: int,
    context: str | None = None,
) -> str:
    """整章重写提示词：按闸门意见重写当前章（revise 节点的 rewrite 分支）。

    :param chapter: 本章大纲，确保修改不偏离既定剧情
    :param draft: 当前完整稿（不是片段）；提示词要求返回修改后的完整正文
    :param feedback: 审稿意见，来自 :func:`policy.rewrite_feedback`（整章级 blocker 清单）
    :param chapter_words: 目标字数，与初稿保持一致
    :param context: L1 注入块。修订同样要看得见正典——否则「改一处引入一处新冲突」，
        下一轮闸门才发现，修补预算就这么烧掉了
    """
    setting = f"{context}\n" if context else f"题材与梗概：{idea.genre}——{idea.summary}\n"
    return f"""# 角色
你是小说作者，正在按闸门指出的冲突重写整章。

# 目标
修改《{idea.title}》第 {index + 1} 章《{chapter.title}》，约 {chapter_words} 字。

# 输入
{setting}本章大纲：{chapter.summary}
必须解决的问题：
{feedback}
当前稿：
{draft}

# 工作要点
- 逐条落实上面的问题，未被点出的内容尽量保持稳定；
- 修改后剧情必须连贯，不引入与既有设定冲突的内容；
- 不要顺手回收计划外的伏笔，也不要新增人物与设定。

# 输出格式
直接输出修改后的完整正文（不是补丁），不带标题与解释。"""


def patch_prompt(
    idea: BookIdea,
    chapter: ChapterOutline,
    index: int,
    *,
    before: str,
    target: str,
    after: str,
    instruction: str,
    canon_lines: list[str],
) -> str:
    """定向修补提示词：只重写被闸门点出的那一个片段（§9.3「不整章重写」）。

    repair 节点按片段逐个调用，返回值由 :func:`policy.splice_patch` 原位回拼，
    因此这里要的**不是**整章：喂的上下文越窄，改出来的句子越不会牵动别处，
    §12 黄金集统计的「那一处改掉没有」才有可归因的对象。

    :param before: 片段前文（``patch_context_chars`` 个字），只用于接语气与指代
    :param target: 待替换片段原文——模型必须知道要换掉的就是这一串
    :param after: 片段后文
    :param instruction: Finding.fixInstruction；空则退回 explanation
    :param canon_lines: 该冲突引用的设定行（``[canon#N] …``），修补不许引入新冲突
    """
    canon = "\n".join(canon_lines) if canon_lines else "（本条冲突没有引用设定行）"
    return f"""# 角色
你是小说作者，正在按闸门指出的冲突修改**一个片段**。

# 目标
《{idea.title}》第 {index + 1} 章《{chapter.title}》中，下面这段与既有设定相抵：
冲突：{instruction}

# 输入
需要遵守的设定：
{canon}

前文：…{before}
【待替换片段】{target}
后文：{after}…

# 工作要点
- 只改【待替换片段】，前后文一个字都不要动、不要复述；
- 改完的片段必须能直接接在「前文」之后、接上「后文」，不重写语气；
- 长度与片段相当（可略长略短），不要扩写成一段新剧情；
- 严格遵守上面的设定，不引入新的冲突。

# 输出格式
直接输出替换后的片段本身，不带引号、不带说明、不带前后文。"""


def judge_prompt(
    chapter_no: int,
    text: str,
    canon_lines: list[str],
    *,
    chapter: ChapterOutline | None = None,
    style_pov: str | None = None,
    rule_codes: list[str] | None = None,
) -> str:
    """语义裁判提示词（PRD §9.2）：只查确定性规则覆盖不到的 C5/C6。

    与 :func:`plan_judge_prompt` 的分工：那一份审**计划**（几行文本，还没花掉写正文的
    token），这一份审**正文**（已经写完的稿子）。两者都只产 Finding 不产分数——
    「这章好不好看」没有任何一处由模型宣布（§8-⑨ 废的就是这种自评通过）。

    :param canon_lines: L1 注入的编号清单（``[canon#N] …`` / ``[fsh#N] …``）。
        **只给这一份，不给全库**：裁判也会被淹，且它引出的编号必须在工作台里
        与作者看到的那一份对得上
    :param rule_codes: 规则引擎已命中的编码，要求裁判不重复报——同一处冲突
        两条来源会挤占台账名额（``per_code_limit`` 只按编码取舍，不分来源）
    """
    outline = f"本章大纲：{chapter.summary}\n" if chapter else ""
    style = f"文风契约（视角）：{style_pov}\n" if style_pov else ""
    known = (
        "已由确定性规则查出、**不要再重复报**的编码：" + "、".join(rule_codes) + "\n"
        if rule_codes
        else ""
    )
    canon = "\n".join(canon_lines) if canon_lines else "（本章无相关已登记设定）"
    return f"""# 角色
你是与作者不同源的一致性审查编辑。你的价值不在于挑出多问题，而在于**每个问题都能指回正文的一处**。

# 目标
检查《第 {chapter_no} 章》正文，输出它与下列设定之间可指认的冲突。

# 输入
{style}{outline}已登记设定（编号即引用凭据）：
{canon}
{known}正文：
{text}

# 工作要点
- 只报规则引擎查不出的语义问题，四类编码：
  world_rule_break（世界观里确立过的限制被无代价地违反）、
  motivation_break（人物行为与其既有动机/性格矛盾，且正文没给理由）、
  timeline_break（本章内或与前文的先后、时长明显矛盾）、
  style_drift（叙述腔调、时态与契约不符，且非角色口吻所致）；
- **每条都必须能在上面「已登记设定」里引到至少一个编号**（canonRefs），
  引不出的判定等于你的猜测，系统会整条丢弃；
- evidenceQuote 必须是从正文**逐字连续**抄下来的片段（不改字、不加省略号、不用句号截半），
  它是冲突的落点；textStart/textEnd 给该片段在正文中的 0 基字符区间（左闭右开），
  不确定就留空，系统会按证据自行定位；
- 严重度：blocker 只留给「不改掉就不能定稿」的事实级冲突；需要作者裁定谁对的取 major；
  文风、节奏一类取 minor；
- 拿不准就不报。误报会让作者不信任整套闸门，这是这套系统失败的主要方式之一；
- 不评价文笔好坏、不复述剧情、不补全正文没写的信息（那是 §8-③ 禁的填空）。

# 输出格式
按结构化约束返回 findings：每项含 code、severity、canonRefs、textStart、textEnd、
evidenceQuote、explanation（冲突是什么，≤200 字）、fixInstruction（只针对该片段的改法）。
checker 一律填 "judge"。没有冲突就返回空列表，不要为了交差编造。"""


def plan_judge_prompt(
    chapter_no: int,
    card_text: str,
    canon_lines: list[str],
    *,
    chapter: ChapterOutline | None = None,
    style_pov: str | None = None,
    rule_codes: list[str] | None = None,
) -> str:
    """计划裁判提示词：审**场景卡**而不是正文。

    与正文裁判的差别只在被检对象与严重度口径：计划只有十几行，改它不要烧整章重写的
    token，所以这里宁可严一点——按这个计划写**必然**出事的一律 blocker/major，
    「写得出来但不好看」一类不属于本裁判的职责（那归读者与 §12 的评测）。

    :param card_text: :func:`scene_card_text` 的稳定渲染，**也是本次判定的 span 坐标系**；
        裁判引的片段必须落在这段文本里，不许引正文、不许引大纲
    """
    outline = f"本章大纲：{chapter.summary}\n" if chapter else ""
    style = f"文风契约（视角）：{style_pov}\n" if style_pov else ""
    known = (
        "已由确定性规则查出、**不要再重复报**的编码：" + "、".join(rule_codes) + "\n"
        if rule_codes
        else ""
    )
    canon = "\n".join(canon_lines) if canon_lines else "（本书暂无已登记设定）"
    return f"""# 角色
你是与计划者不同源的责任编辑，检查的是**这一章的计划**，正文还没开始写。

# 目标
指出下面这张场景卡里会导致正文必然与既有设定相抵的设计缺陷。

# 输入
{style}{outline}已登记设定与未收伏笔（编号即引用凭据）：
{canon}
{known}场景卡（你唯一的被检对象）：
{card_text}

# 工作要点
- 只报四类编码：
  world_rule_break（照这个计划写必然违反上面已确立的规则）、
  motivation_break（某人物按计划在做什么，但他没有做这件事的动机依据，计划里也没交代）、
  timeline_break（同一场景要求一个人同时在两地，或先后次序互相矛盾）、
  knowledge_leak（计划让某人物说出/利用他按既有事实不可能知道的信息）；
- **每条都必须引一个上面的编号**（canonRefs），引不出的就是猜测，系统会整条丢弃；
- evidenceQuote 必须从「场景卡」里**逐字连续**抄一行（或一行中的一段），它是冲突的落点；
  textStart/textEnd 给该片段在场景卡文本中的 0 基字符区间（左闭右开），不确定就留空；
- 严重度：照计划写出来一定报废的取 blocker；需要作者取舍的取 major；
  只是「这一章可能平淡」一类**不要报**；
- 不评价剧情好坏、不替作者补设定、不建议增加新人物（那是 newEntities 与 openQuestions 的事）；
- 拿不准就不报。计划闸门误报一次，作者就会开始绕过闸门。

# 输出格式
按结构化约束返回 findings：每项含 code、severity、canonRefs、textStart、textEnd、
evidenceQuote、explanation（≤200 字）、fixInstruction（只针对这一行的改法）。
checker 一律填 "judge"。没有冲突就返回空列表。"""


def extract_characters_prompt(title: str, drafts: list[ChapterDraft]) -> str:
    """角色提取提示词：归档前从全书正文抽取主要角色档案。

    :param title: 书名；仅用于提示词中的作品指代
    :param drafts: 全部定稿章节（含正文），是角色信息的唯一来源
    """
    # 全书正文整体喂入：角色跨章出现，只看单章会漏掉只在后文活跃的人物。
    chapters_text = "\n\n".join(
        f"【第 {d.index} 章 {d.title}】\n{d.content}" for d in drafts
    )
    return f"""# 角色
你是小说资料编辑，负责整理作品角色档案。

# 目标
从《{title}》全部正文中提取主要角色。

# 输入
{chapters_text}

# 工作要点
- 只提取有名字或明确代称、对剧情有作用的角色，最多 10 个，按重要度排序；
- role 用「主角/女主/反派/导师/配角」等定位词；
- description 概括身份、性格与关键特征，不复述剧情。

# 输出格式
按结构化约束返回 characters：每项含 name、role、description。"""


def extract_prompt(
    idea: BookIdea,
    chapter: ChapterOutline,
    index: int,
    content: str,
    known_entities: list[str] | None = None,
) -> str:
    """正典抽取提示词：从一章定稿正文里抽出可入库的增量事实。

    extract 节点（PLAN 角色、温度 0）调用，产物交给内部通道落库。
    :param known_entities: 已登记的实体键，用于压制「同一人物第二个 key」；
        为空表示尚无登记（开篇章节），此时要求模型自拟并保持一致
    """
    entities = (
        "已登记实体键（必须复用，不要另造同义 key）：\n" + "、".join(known_entities)
        if known_entities
        else "当前没有已登记实体：请自拟稳定 key（如 char:姓名拼音），全章保持一致。"
    )
    return f"""# 角色
你是设定管理员，负责把小说正文里已经发生的事实登记进设定库（正典）。

# 目标
从《{idea.title}》第 {index + 1} 章《{chapter.title}》的正文中抽取新增事实、状态变迁、
新称谓与本章埋下的伏笔。

# 输入
题材与梗概：{idea.genre}——{idea.summary}
本章大纲：{chapter.summary}
{entities}
正文：
{content}

# 工作要点
- 只登记正文里**写明白**的事实。正文没写的，一律不要补全：世界观留白是作者的权限，
  你替它填空就等于把幻觉写进设定库，之后每一章都会以它为依据；
- 遇到正文引用了尚未定义的设定（例如提到「门规」但没有任何条目），
  把这条以 status="todo" 登记为缺口，而不是自行编造其内容；
- evidenceQuote 必须是从正文逐字抄下来的连续片段（不改字、不加省略号），
  否则该条会被系统丢弃；一条断言只对应一句证据；
- subjectKey/entityKey 用「类型:归一名」形式（char:、place:、item:），
  称谓（如「沈师兄」「青衫客」）登记进 aliases 并指向同一个实体键，不要把称谓当成新人物；
- 状态变迁只写「本章结束时」的状态：死亡、位移、得知某事、取得/失去某物；
- 不抽取审美判断（文笔好、节奏紧凑）与情节复述（他去了某地又做了某事）——
  那些不是可比对的事实。

# 输出格式
按结构化约束返回：assertions（kind/subjectKey/predicate/objectText/restatement/evidenceQuote/confidence/status）、
stateChanges（charKey/isAlive/locationKey/knows/holds/mood）、
aliases（entityKey/aliasText/isPrimary）、
foreshadows（content/dueByArc）。
某一类没有就返回空列表，不要为了凑数编造。"""


def summarize_chapter_prompt(
    idea: BookIdea, chapter: ChapterOutline, index: int, content: str, max_scenes: int = 3
) -> str:
    """章级摘要提示词：把一章正文切成场景摘要并给出一段章级摘要。

    summarize 步骤（PLAN 角色）调用，产物经 ``CanonStore.save_chapter_summaries``
    落 chapter_summary，供下一章的 Tier-2 近因注入。
    """
    return f"""# 角色
你是小说资料编辑，负责把定稿章节整理成可复用的剧情摘要。

# 目标
为《{idea.title}》第 {index + 1} 章《{chapter.title}》产出场景级摘要与章级摘要。

# 输入
正文：
{content}

# 工作要点
- 按叙事顺序切分，最多 {max_scenes} 个场景，每个场景一段，sceneNo 从 1 起连续；
- 每条只写正文里发生了的：谁、在哪里、做了什么、状态有什么变化；
- digest 用一段话概括整章，并在末尾点明本章结束时仍未解决的问题（为后文的伏笔登记提供线索）；
- 不复述原句、不做评价（文笔、节奏之类一律不要），不推断正文没写的动机。

# 输出格式
按结构化约束返回：scenes（sceneNo/content）、digest。"""


def summarize_arc_prompt(idea: BookIdea, digests: list[tuple[int, str]], arc_no: int) -> str:
    """弧级摘要提示词：**输入只有各章的章级摘要，没有正文**。

    §6-4 禁止「摘要的摘要再摘要」的套娃，但 arc 级按定义就是从章级摘要合成——
    这里的合规性在于「只升一层」：arc 的输入是章摘要（章摘要的输入是正文），
    不存在 arc 吃 arc 的路径，因此提示词必须明说「不许引用未在给定摘要中出现的内容」。
    """
    lines = "\n".join(f"第 {no} 章：{digest}" for no, digest in digests)
    return f"""# 角色
你是小说资料编辑，负责把若干章的剧情合并成一段弧级摘要。

# 目标
为《{idea.title}》第 {arc_no} 段剧情弧（共 {len(digests)} 章）写一段弧级摘要。

# 输入（这是你唯一可用的信息，逐章摘要）
{lines}

# 工作要点
- 只允许使用上面出现过的事实，不要补全任何细节；
- 写清弧内推进了什么、ending 时还有什么没收；
- 不复述各章摘要的原句，不做评价。

# 输出格式
按结构化约束返回：content。"""


def novel_chat_prompt(book: BookSnapshot | None, context: str | None, as_of: int | None) -> str:
    """对话面板（创作工作台右栏）的系统提示词（§10.3 约定 1/2/3）。

    :param book: 本轮读回的书目快照；``None`` = 这一轮没带 bookId（从通用聊天窗进来
        问了一句小说问题），此时提示词必须改口为「没有可依据的正典」而不是留一段
        空的注入块——模型面对空注入最容易做的事就是照着用户的措辞编
    :param context: L1 注入块（``compile_context`` 的产物）。对话与生成共用同一份，
        所以这里的编号与生成链路一致（§10.3 约定 2「不允许聊天窗知道得比生成链路多」）
    :param as_of: 参照章号；``None`` 时不提「截至第几章」
    """
    if book is None:
        # 「没选书」与「选了书但读回失败」共用这一支：两种情况下模型手里都没有可引的事实。
        # 不在这里复述失败原因——模型分不清是哪种，写死「请先选书」会对一个已经选了书
        # 的作者说错话；原因由对话侧的 THINKING 帧直接告诉作者。
        head = (
            "# 输入\n"
            "本轮没有可用的书籍上下文（未选定书籍，或书目读回失败）。\n"
            "因此：不要假设书名、人物与设定；要讨论某本已建档的书时，"
            "请提示作者确认左栏的书籍与参照章。"
        )
        tail = ""
    else:
        head = (
            f"# 输入\n书目：《{book.title}》｜{book.genre}——{book.summary}"
            f"（已归档 {book.chapter_count} 章）\n"
        )
        if as_of is not None:
            head += f"讨论口径：截至第 {as_of} 章的已定稿事实。\n"
        tail = (
            context
            if context
            else "（本轮正典读取失败，下面没有任何已登记事实可引用。）"
        )
    return f"""# 角色
你是《{(book.title if book else '（未选书）')}》的责任编辑，与作者讨论，不写正文。

# 目标
回答人物动机、桥段推演、已成立设定与写法建议；把讨论中真正需要进正典的结论讲清楚。

{head}{tail}

# 工作要点
- 只依据上面注入的事实回答。注入里没有的就是**尚未登记**，直说是缺口，不要替作者补全；
- 引用已登记设定时带上 [canon#N] 编号，作者要能点回出处；
- **不产出小说正文**。被要求「写一章」「续写」「把这段写出来」时，回一句「正文由生成链路产出，请在中栏查看」；
  可以给思路、节拍、因果关系与可参照的已定稿句子，但不给成段正文；
- **不改动正典**。你的结论只是讨论内容，是否写入正典由作者在工作台裁定；
- 晚于参照章的情节你看不到：作者提到后文时说明「按当前参照章看不到这部分」，不要猜。

# 输出格式
自然语言，200 字以内，分点不超过 4 条。不要输出 JSON，不要复述上面的注入块。"""


def proposal_extract_prompt(book: BookSnapshot | None, answer: str) -> str:
    """提议抽取提示词：把一轮讨论里已经定论的设定升为提议卡候选（§10.3 约定 1）。

    单独一次结构化调用而不是让回答模型顺手输出 JSON：回答那一路要求「不要输出 JSON」
    （混着机器块的用户文本既难读又要从流式 token 里抠），拆开之后每张卡都有独立的
    校验口，解析失败只是少一张卡，不会把一段残缺 JSON 当答案推给作者。

    :param answer: 本轮回答原文（``AIMessage`` 的内容），是这次抽取唯一的证据来源
    """
    title = book.title if book else "（未选书）"
    return f"""# 角色
你是设定记录员，从《{title}》的一轮讨论里挑出**已经定论**的设定结论。

# 目标
把需要写进正典的结论整理为提议卡候选；没有就返回空列表。

# 输入（本轮讨论内容，这是你唯一可用的信息）
{answer}

# 工作要点
- 只抽「已经定论」的表述：讨论、推测、举例、反问、「可以考虑」都不算，宁缺毋滥；
- subjectKey 用前缀键：人物 ``char:``、地点 ``place:``、规则 ``rule:``、道具 ``item:``；
  拿不准实体键的写法就不要抽这一条；
- predicate 用小写下划线的机器可比谓词（如 eye_color、cannot_use），objectText 一句话；
- basisQuote 必须逐字摘自上面这段讨论，不能改写、不能拼接；
- 一次最多 5 条；同一结论换说法只留一条。

# 输出格式
按结构化约束返回：proposals（数组，可为空）。"""
