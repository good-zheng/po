"""OfflineNovelModel 单测：确定性占位 + 与真实模型的结构化行为同构。"""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from po_agent_novel.offline import OfflineNovelModel
from po_agent_novel.schemas import (
    BookIdea,
    CharacterList,
    Outline,
    Reflection,
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


async def test_reflection_score_always_passes(model: OfflineNovelModel) -> None:
    reflection = await model.with_structured_output(Reflection).ainvoke("审稿")
    assert isinstance(reflection, Reflection)
    assert reflection.score >= 9  # 恒达标：离线链路不进修订循环


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
