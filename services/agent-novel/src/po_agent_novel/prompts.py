"""小说创作提示词（全新编写，不搬移参考实现文本）。

统一结构：角色 / 目标 / 输入 / 工作要点 / 输出格式。
提示词为纯函数：入参领域数据，出参完整提示词字符串，
不引用运行时状态，便于单测与后续外置化管理。

调用方是 graph 中的子图节点，一节点一模板：
- conceive_prompt ← conceive 节点：一句话想法 → 书名/题材/梗概；
- outline_prompt ← outline 节点：全书章节大纲；
- write_chapter_prompt / revise_prompt ← generate 节点：初稿 / 按审稿意见修订；
- reflect_prompt ← reflect 节点：给当前章打分（回环判定的输入）；
- extract_characters_prompt ← archive 节点：归档前从全书正文抽角色档案。

模板末尾的「输出格式」节与 schemas 的 Field description 互为双保险：
前者是自然语言引导，后者是结构化输出（with_structured_output）的硬约束。
"""

from __future__ import annotations

from po_agent_novel.schemas import (
    BookIdea,
    ChapterDraft,
    ChapterOutline,
)


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
- 题材从常见类型中选定（玄幻/都市/悬疑/科幻/历史/武侠/言情等），可用复合类型；
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
- 章节标题风格统一、有画面感。

# 输出格式
按结构化约束返回 chapters：每项含 title（章节标题）与 summary（本章概要）。"""


def write_chapter_prompt(
    idea: BookIdea,
    chapters: list[ChapterOutline],
    index: int,
    prev_tail: str,
    chapter_words: int,
) -> str:
    """初稿提示词：index 为 0 基章节序号。

    generate 节点在无审稿意见（初稿路径）时调用。
    :param idea: 构思结果，给正文定基调
    :param chapters: 全书大纲，用于给本章定位并保持全书视角
    :param index: 当前章下标（0 基），仅用于编号展示与定位本章大纲
    :param prev_tail: 上一章定稿正文的末尾 200 字；开篇传空串
    :param chapter_words: 目标字数，写入「目标」节
    """
    outline_lines = "\n".join(
        f"{i + 1}. 《{c.title}》{c.summary}" for i, c in enumerate(chapters)
    )
    chapter = chapters[index]
    # 空串代表开篇（尚无已定稿章节）：切换为「铺开世界观」的要求，
    # 而非让模型面对一段空的「上一章结尾」。
    prev = f"上一章结尾（衔接参考）：\n{prev_tail}" if prev_tail else "（本章为开篇）"
    return f"""# 角色
你是小说作者，正在为《{idea.title}》撰写正文。

# 目标
写第 {index + 1}/{len(chapters)} 章《{chapter.title}》，约 {chapter_words} 字。

# 输入
题材与梗概：{idea.genre}——{idea.summary}
全书大纲：
{outline_lines}
{prev}

# 工作要点
- 剧情严格贴合本章大纲，可自然补充细节，不偏离主线；
- 开头承接上一章结尾；开篇则铺开世界观与主角处境；
- 叙事视角统一，对话与描写交替，结尾留钩子引出下一章。

# 输出格式
直接输出正文：不带章节标题、不带任何解释性文字。"""


def revise_prompt(
    idea: BookIdea,
    chapter: ChapterOutline,
    index: int,
    draft: str,
    feedback: str,
    chapter_words: int,
) -> str:
    """修订提示词：基于审稿意见重写当前章。

    generate 节点在回环路径（ns["feedback"] 非空）时调用。
    :param chapter: 本章大纲，确保修改不偏离既定剧情
    :param draft: 当前完整稿（不是片段）；提示词要求返回修改后的完整正文
    :param feedback: 审稿意见，来自 reflect 节点的 Reflection.comment
    :param chapter_words: 目标字数，与初稿保持一致
    """
    return f"""# 角色
你是小说作者，正在按审稿意见修改章节。

# 目标
修改《{idea.title}》第 {index + 1} 章《{chapter.title}》，约 {chapter_words} 字。

# 输入
本章大纲：{chapter.summary}
审稿意见：{feedback}
当前稿：
{draft}

# 工作要点
- 逐条落实审稿意见，未涉及的内容尽量保持稳定；
- 修改后剧情必须连贯，不引入与既有设定冲突的内容。

# 输出格式
直接输出修改后的完整正文（不是补丁），不带标题与解释。"""


def reflect_prompt(chapter: ChapterOutline, index: int, draft: str, target_score: float) -> str:
    """审稿提示词：给当前章打分并产出审稿意见（reflect 节点的唯一 LLM 调用）。

    :param chapter: 本章大纲，作为「剧情贴合度」的评分参照
    :param draft: 待评审的完整正文
    :param target_score: 定稿分数线；写进提示词只是让模型知道评分口径，
        是否回环重写仍由 reflect 节点的代码判定（阈值判定不交给 LLM）
    """
    return f"""# 角色
你是严格的小说审稿编辑。

# 目标
为第 {index + 1} 章《{chapter.title}》的正文评分并给出审稿意见。

# 输入
本章大纲：{chapter.summary}
正文：
{draft}

# 工作要点
- 从剧情贴合度、文字流畅度、人物生动性三个维度综合评分（0-10 整数）；
- {target_score} 分及以上视为可定稿；
- 低于 {target_score} 分时，意见必须具体可执行（指出哪一段、什么问题、怎么改）；
- 章节已达可用水平则不刻意挑剔，避免无意义的反复修改。

# 输出格式
按结构化约束返回：score（0-10 整数）、comment（审稿意见）。"""


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
