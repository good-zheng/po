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
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import RunnableLambda

from po_agent_novel.schemas import (
    BookIdea,
    CharacterList,
    CharacterProfile,
    ChapterOutline,
    Outline,
    Reflection,
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
    if schema is Reflection:
        # 占位评分恒达标：离线链路不进入修订循环，一次走到归档
        # （9 分高于默认装配的 target_score=8.0，故 reflect 判定直接定稿）。
        return Reflection(score=9, comment="离线占位评分：正文为占位内容，直接放行定稿。")
    if schema is CharacterList:
        return CharacterList(
            characters=[
                CharacterProfile(
                    name="占位主角", role="主角", description="离线模式下的占位角色档案。"
                )
            ]
        )
    raise ValueError(f"OfflineNovelModel 不支持的 schema：{schema!r}")


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

        :param schema: 目标结构化模型（仅支持 schemas 中的四个领域类型）
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
