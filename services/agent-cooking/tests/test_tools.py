"""工具层测试：输出结构、错误翻译、参数归一化。

工具是「模型」与「App」共用的唯一数据通路，输出结构一旦变化，
移动端卡片与提示词都会同时失效，所以这里断言得细一些。
"""

from __future__ import annotations

import json

from conftest import run

from po_agent_cooking.config import CookingSettings
from po_agent_cooking.recipes import MockRecipeStore, RecipeStoreError
from po_agent_cooking.tools import build_recipe_tools


def _tools(store=None):  # type: ignore[no-untyped-def]
    settings = CookingSettings(_env_file=None, search_limit=3)
    return {item.name: item for item in build_recipe_tools(store or MockRecipeStore(), settings)}


def test_tool_names_are_stable() -> None:
    """工具名是移动端与提示词的公共契约，改名会静默破坏前端解析。"""
    assert set(_tools()) == {"search_recipes", "get_recipe_detail", "list_categories"}


def test_search_returns_json_with_recipe_fields() -> None:
    payload = json.loads(run(_tools()["search_recipes"].ainvoke({"keyword": "番茄"})))

    assert payload["count"] == 1
    recipe = payload["recipes"][0]
    # 移动端卡片渲染依赖这几个字段，缺一个就会显示成空白
    for field in ("id", "title", "coverImageUrl", "difficulty", "totalTime"):
        assert field in recipe
    # difficultyLabel 让模型不必自己把 1/2/3 翻译成中文
    assert recipe["difficultyLabel"] == "简单"


def test_search_translates_difficulty_words() -> None:
    """难度支持中文/英文/数字三种说法，统一归一化为 1/2/3。"""
    tools = _tools()

    assert json.loads(run(tools["search_recipes"].ainvoke({"difficulty": "简单"})))["count"] == 2
    assert json.loads(run(tools["search_recipes"].ainvoke({"difficulty": "easy"})))["count"] == 2
    assert json.loads(run(tools["search_recipes"].ainvoke({"difficulty": "2"})))["count"] == 1
    # 无法识别的说法按「不筛选」处理，而不是让对话失败
    assert json.loads(run(tools["search_recipes"].ainvoke({"difficulty": "随便"})))["count"] == 3


def test_search_empty_result_carries_hint() -> None:
    """空结果要附带回退建议，否则模型容易原地反复重试。"""
    payload = json.loads(run(_tools()["search_recipes"].ainvoke({"keyword": "不存在的菜"})))

    assert payload["count"] == 0
    assert payload["recipes"] == []
    assert payload["hint"]


def test_search_respects_limit() -> None:
    tools = _tools()
    payload = json.loads(run(tools["search_recipes"].ainvoke({})))

    assert payload["count"] == 3  # CookingSettings.search_limit=3，MockRecipeStore 有 3 条


def test_detail_sorted_by_step_number() -> None:
    """后端返回的步骤集合无序，工具必须排序后再交给模型。"""
    payload = json.loads(run(_tools()["get_recipe_detail"].ainvoke({"recipe_id": 1})))

    assert payload["found"] is True
    recipe = payload["recipe"]
    numbers = [step["stepNumber"] for step in recipe["steps"]]
    assert numbers == sorted(numbers)
    assert recipe["ingredients"][0]["amount"] == "2"
    assert recipe["tips"]


def test_detail_missing_recipe_is_not_an_error() -> None:
    payload = json.loads(run(_tools()["get_recipe_detail"].ainvoke({"recipe_id": 999})))

    assert payload["found"] is False
    assert "error" not in payload


def test_categories_returns_names() -> None:
    payload = json.loads(run(_tools()["list_categories"].ainvoke({})))

    assert payload["count"] == len(payload["categories"])
    assert "川菜" in payload["categories"]


class _BrokenStore(MockRecipeStore):
    """数据源全部失败：验证工具把异常转成 error 字段而非向外抛。"""

    async def search_briefs(self, keyword: str = "", **kwargs):  # type: ignore[no-untyped-def]
        raise RecipeStoreError("连接被拒绝")

    async def get_detail(self, recipe_id: int):  # type: ignore[no-untyped-def]
        raise RecipeStoreError("连接被拒绝")

    async def list_categories(self):  # type: ignore[no-untyped-def]
        raise RecipeStoreError("连接被拒绝")


def test_store_failure_becomes_readable_error() -> None:
    """工具永不抛异常：失败必须转成 {"error": ...}，否则整轮对话以 RUN_ERROR 收场。"""
    tools = _tools(_BrokenStore())

    for name, args in (
        ("search_recipes", {"keyword": "番茄"}),
        ("get_recipe_detail", {"recipe_id": 1}),
        ("list_categories", {}),
    ):
        payload = json.loads(run(tools[name].ainvoke(args)))
        assert "连接被拒绝" in payload["error"]
