"""小说领域结构化输出 schema（Layer3：structured_output 决策）。

字段 description 即对 LLM 的输出约束，与 prompts 的「输出格式」节
配合使用；长度/范围约束保证领域数据进入 artifacts 前已收敛。

长度约束分两道：``Field(max_length=...)`` 随 json schema 下发给模型作为
参照（只有 OpenAI 的 strict 模式会由服务端强制），本地再用
:func:`_clip_text` 截断兜底——DeepSeek / DashScope 的兼容端点走 tool 调用，
不认长度约束，模型写超了会让 Pydantic 直接抛 ValidationError 终止整轮运行。

本模块含两类模型，消费方不同：
- Pydantic 模型（BookIdea / ChapterOutline / Outline / Reflection /
  CharacterProfile / CharacterList）：LLM 结构化输出的目标类型，
  经 ``with_structured_output`` 绑定后由 graph 各节点调用；
- frozen dataclass（BookDraft / ChapterDraft / ArchivedBook）：不是 LLM 输出，
  而是 NovelStore 协议的载荷与回执类型，用不可变值对象保证异步写入期间
  数据不被意外改写。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, Field


def _clip_text(limit: int) -> BeforeValidator:
    """生成「超长即截断」的前置校验器，配合 ``Field(max_length=limit)`` 使用。

    前置（Before）语义保证截断发生在长度校验之前，因此只会把越界输出收敛为
    ``limit`` 个字符，不会触发 ValidationError；``min_length`` 等下限仍照常生效。
    """

    def clip(value: Any) -> Any:
        return value[:limit] if isinstance(value, str) and len(value) > limit else value

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
        min_length=1, max_length=20, description="题材类型，如：玄幻、都市、悬疑"
    )
    summary: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="核心梗概：主角、核心冲突与最大看点"
    )


class ChapterOutline(BaseModel):
    """单章大纲（不含正文字段，正文由 generate 节点产出）。

    注意：无「章节序号」字段——序号由在 Outline.chapters 中的位置隐含，
    这样模型无需维护自增序号，也不会出现序号错乱。
    """

    title: Annotated[str, _clip_text(50)] = Field(
        min_length=1, max_length=50, description="章节标题"
    )
    summary: Annotated[str, _clip_text(200)] = Field(
        min_length=1, max_length=200, description="本章剧情概要与关键场景"
    )


class Outline(BaseModel):
    """全书大纲；outline 节点产出，generate 节点按章取用。"""

    chapters: list[ChapterOutline] = Field(
        min_length=1, max_length=20, description="章节列表，按叙事顺序排列"
    )


class Reflection(BaseModel):
    """反思评分：generate→reflect 循环的终止判定依据。

    只承载「模型判断」，循环与否的比较在 reflect 节点代码里完成
    （见 graph.reflect_node）：score 决定是否达标，comment 决定下一轮改什么。
    """

    score: int = Field(ge=0, le=10, description="正文质量评分（0-10 整数）")
    comment: Annotated[str, _clip_text(500)] = Field(
        min_length=1, max_length=500, description="修改意见：低分时须具体可执行，达标时给出定稿理由"
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


# ---------- 持久化记录（非 LLM 输出，store 协议的载荷类型） ----------


@dataclass(frozen=True, slots=True)
class BookDraft:
    """待归档的书稿元数据；NovelStore.save_book 的入参。"""

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
