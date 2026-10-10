"""OfflineNovelModel 单测：确定性占位 + 与真实模型的结构化行为同构。"""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from po_agent_novel.offline import OfflineNovelModel
from po_agent_novel.schemas import (
    BookIdea,
    CharacterList,
    Outline,
    SceneCard,
    WorldBible,
)


@pytest.fixture
def model() -> OfflineNovelModel:
    return OfflineNovelModel()


async def test_book_idea_output_is_deterministic(model: OfflineNovelModel) -> None:
    conceiver = model.with_structured_output(BookIdea)
    first = await conceiver.ainvoke("写一本关于少年修行的小说")
    second = await conceiver.ainvoke("写一本关于少年修行的小说")
    assert isinstance(first, BookIdea)
    assert first == second
    assert "占位" in first.title
    assert first.genre and first.summary


async def test_outline_has_fixed_three_chapters(model: OfflineNovelModel) -> None:
    outline = await model.with_structured_output(Outline).ainvoke("大纲")
    assert isinstance(outline, Outline)
    assert [c.title for c in outline.chapters] == ["启程", "暗流", "裂隙"]


async def test_world_bible_keeps_everything_as_a_gap(model: OfflineNovelModel) -> None:
    """离线模型不能替作者定世界：圣经只产 todo 缺口，读侧（恒读 confirmed）看不见它。

    占位规则若标成 confirmed，整本书会按一条编造的设定被闸门校正——那正是
    「离线冒充真实生成」在设定层的形式。
    """
    bible = await model.with_structured_output(WorldBible).ainvoke("构建世界观")
    assert isinstance(bible, WorldBible)
    assert bible.rules and all(rule.status == "todo" for rule in bible.rules)
    assert bible.characters == [] and bible.relations == [] and bible.forbidden == []
    assert bible.openQuestions  # 缺口必须可见，静默的「没想过」等于漏写


async def test_scene_card_picks_no_entities_but_surfaces_the_pool(
    model: OfflineNovelModel,
) -> None:
    """没做规划不能变成「挑了别人」：entities 恒空，可挑清单转为待办而非丢弃。"""
    card = await model.with_structured_output(SceneCard).ainvoke(
        "已登记实体键（只能从这些里挑）：char:a、char:b\n本章目标字数：900"
    )
    assert isinstance(card, SceneCard)
    assert card.entities == []
    assert card.newEntities == ["char:a", "char:b"]
    assert (card.wordsLow, card.wordsHigh) == (540, 1440)  # 带宽跟着提示词的目标字数


async def test_scene_card_band_spans_the_default_target(model: OfflineNovelModel) -> None:
    """提示词既无实体清单也无目标字数时的兜底：占位卡不许自己触发字数带规则。"""
    card = await model.with_structured_output(SceneCard).ainvoke("出一张场景卡")
    assert card.newEntities == []  # 无从可挑，就不硬造待办
    assert card.wordsLow <= 1200 <= card.wordsHigh


async def test_character_list_single_placeholder(model: OfflineNovelModel) -> None:
    extracted = await model.with_structured_output(CharacterList).ainvoke("提取角色")
    assert isinstance(extracted, CharacterList)
    assert len(extracted.characters) == 1
    assert extracted.characters[0].role == "主角"


async def test_unknown_schema_raises(model: OfflineNovelModel) -> None:
    runnable = model.with_structured_output(int)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        await runnable.ainvoke("任意")


def test_prose_is_explicitly_tagged_offline(model: OfflineNovelModel) -> None:
    response = model.invoke([HumanMessage(content="写第一章")])
    assert isinstance(response, AIMessage)
    assert "【离线模式】" in response.content
