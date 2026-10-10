"""resume 之后的命名空间复原：检查点把 pydantic 模型存成 LangChain constructor 信封。

真机（checkpointer=redis）在第 1 章计划闸门确认后就报 ``'dict' object has no attribute
'wordsLow'``——信封没被还原。这里钉住三件事：

- 信封能拆回模型实例，且**嵌套**信封逐层拆（SceneCard 里的每个 PlannedScene 各带一份）；
- 值本来就是实例时是空操作（未挂起的常规运行不受影响，冻结 dataclass 原样回来）；
- ``None`` 与形状不对的值不许被强行捏成模型。
"""

from __future__ import annotations

from typing import Any

from po_agent_novel.context import StyleContract
from po_agent_novel.graph import NOVEL_KEY, _ns
from po_agent_novel.schemas import (
    AssertionCandidate,
    ChapterDraft,
    ChapterExtraction,
    ChapterOutline,
    PlannedScene,
    SceneCard,
    WorldBible,
)

MODULE_PATH = ["po_agent_novel", "schemas"]


def _envelope(cls: type[Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    """LangChain 序列化信封的样子（真机取回时就是这个 dict）。"""
    return {"lc": 2, "type": "constructor", "id": [*MODULE_PATH, cls.__name__], "kwargs": kwargs}


def _state(**namespace: Any) -> dict[str, Any]:
    return {"artifacts": {NOVEL_KEY: namespace}}


def test_plain_card_survives_untouched() -> None:
    """没挂起过的运行：值已是实例，复原必须是空操作而不是重建。"""
    card = SceneCard(entities=["char:a"], scenes=[], wordsLow=900, wordsHigh=1500, hook="钩子")
    ns = _ns(_state(plan=card, style=StyleContract(genre="都市")))
    assert ns["plan"] is card
    assert isinstance(ns["style"], StyleContract)


def test_enveloped_card_is_rebuilt_with_nested_scenes() -> None:
    """嵌套信封也要拆：只拆最外层会让 PlannedScene 揣着 lc/type/id 进校验。"""
    ns = _ns(
        _state(
            plan=_envelope(
                SceneCard,
                {
                    "entities": ["char:a"],
                    "scenes": [
                        _envelope(PlannedScene, {"goal": "主角发现裂隙", "present": ["char:a"]}),
                        _envelope(PlannedScene, {"goal": "第一次尝试改写"}),
                    ],
                    "wordsLow": 900,
                    "wordsHigh": 1500,
                    "hook": "钩子",
                },
            )
        )
    )
    card = ns["plan"]
    assert isinstance(card, SceneCard)
    assert (card.wordsLow, card.wordsHigh) == (900, 1500)
    assert [type(scene) for scene in card.scenes] == [PlannedScene, PlannedScene]
    assert card.scenes[0].goal == "主角发现裂隙"
    # 信封的键不许漏进模型
    assert "lc" not in card.model_dump()


def test_outline_list_and_bible_are_rebuilt() -> None:
    ns = _ns(
        _state(
            outline=[
                _envelope(ChapterOutline, {"title": "裂隙", "goal": "发现", "summary": "第一章梗概"}),
                _envelope(ChapterOutline, {"title": "重写", "goal": "尝试", "summary": "第二章梗概"}),
            ],
            bible=_envelope(WorldBible, {"logline": "一句话内核", "rules": [], "characters": [], "relations": []}),
        )
    )
    assert [type(item) for item in ns["outline"]] == [ChapterOutline, ChapterOutline]
    assert ns["outline"][0].title == "裂隙"
    assert isinstance(ns["bible"], WorldBible)
    assert ns["bible"].logline == "一句话内核"


def test_extraction_inside_entry_dict_is_rebuilt_but_none_stays_none() -> None:
    """extract 条目是 dict，模型藏在它的 ``extraction`` 字段里；失败章的那条必须是 None。"""
    entry = {
        "chapter": 1,
        "content_hash": "abc",
        "dropped": 0,
        "extraction": _envelope(
            ChapterExtraction,
            {
                "assertions": [
                    _envelope(
                        AssertionCandidate,
                        {
                            "kind": "character",
                            "subjectKey": "char:a",
                            "predicate": "eye_color",
                            "objectText": "黑色",
                            "restatement": "a 是黑眼睛",
                            "evidenceQuote": "a 是黑眼睛",
                        },
                    )
                ]
            },
        ),
    }
    ns = _ns(_state(extractions=[entry, {**entry, "extraction": None}]))
    assert isinstance(ns["extractions"][0]["extraction"], ChapterExtraction)
    assert ns["extractions"][0]["extraction"].assertions[0].predicate == "eye_color"
    assert ns["extractions"][1]["extraction"] is None


def test_chapters_of_dataclass_shape_are_left_alone() -> None:
    """冻结 dataclass 过检查点是原样回来的，复原层不许多事去重建它。"""
    draft = ChapterDraft(index=1, title="裂隙", content="正文")
    ns = _ns(_state(chapters=[draft]))
    assert ns["chapters"] == [draft]


def test_unknown_and_malformed_values_pass_through() -> None:
    """不在表里的键、以及形状不对的值都原样留着：复原层不该成为新的崩溃源。"""
    ns = _ns(_state(plan="还不是卡", entity_keys=["char:a"], index=0))
    assert ns["plan"] == "还不是卡"
    assert ns["index"] == 0


def test_empty_namespace_is_empty() -> None:
    assert _ns({}) == {}
    assert _ns({"artifacts": {"other": {"plan": 1}}}) == {}
