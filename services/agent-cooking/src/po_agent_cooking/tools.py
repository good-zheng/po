"""Agent 可调用的菜谱工具。

三个工具覆盖「找菜 → 看细节 → 报分类」的完整检索链路：

- ``search_recipes``：按关键词/分类/难度搜菜谱，返回摘要列表；
- ``get_recipe_detail``：按 id 取用料与步骤；
- ``list_categories``：列出可选分类。

两条贯穿始终的设计约束：

1. **工具永不抛异常**。数据源失败会被转成 ``{"error": "..."}`` 文本回给
   模型——模型看到错误可以换个说法重试或如实告知用户；若任异常穿过
   ToolNode，整轮对话会以 RUN_ERROR 终止，用户只看到一句「运行出错」。
2. **返回值是 JSON 字符串**。它既是模型读的上下文，也是移动端渲染菜谱
   卡片的唯一数据源（经 TOOL_CALL_RESULT 帧原样下发），所以字段名必须
   与 ``RecipeBrief`` 契约一致，不能改成给模型看的自然语言。
"""

from __future__ import annotations

import json
import logging
from typing import Any

from langchain_core.tools import BaseTool, tool

from po_agent_cooking.config import CookingSettings
from po_agent_cooking.recipes import RecipeStore, RecipeStoreError

logger = logging.getLogger(__name__)

# 难度取值：Java 侧是 1/2/3 的整型列，这里用词表把用户口语转成该枚举，
# 转换放在工具内而非提示词里，模型只需照抄中文说法。
DIFFICULTY_LABELS: dict[int, str] = {1: "简单", 2: "中等", 3: "困难"}

DIFFICULTY_ALIASES: dict[str, int] = {
    "简单": 1,
    "容易": 1,
    "新手": 1,
    "easy": 1,
    "中等": 2,
    "一般": 2,
    "普通": 2,
    "medium": 2,
    "困难": 3,
    "难": 3,
    "高手": 3,
    "hard": 3,
    # 整型字面量也认，方便模型直接传 1/2/3
    "1": 1,
    "2": 2,
    "3": 3,
}


def _dump(payload: dict[str, Any]) -> str:
    """序列化工具结果：中文不转义，避免模型与前端看到 \\uXXXX。"""
    return json.dumps(payload, ensure_ascii=False)


def _resolve_difficulty(raw: str | int | None) -> int | None:
    """把难度说法（中文 / 英文 / 数字）归一化为 1/2/3；无法识别则返回 None。

    容忍无法识别的输入而不是报错：用户可能说「随便」，模型也可能传空串，
    此时按「不筛选」处理比中断对话更符合预期。
    """
    if raw is None:
        return None
    if isinstance(raw, int):
        return raw if raw in DIFFICULTY_LABELS else None
    text = raw.strip().lower()
    if not text:
        return None
    return DIFFICULTY_ALIASES.get(text)


def _brief_payload(recipe: Any) -> dict[str, Any]:
    """搜索结果里单条菜谱的字段：够模型描述、也够移动端渲染卡片。"""
    return {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "coverImageUrl": recipe.coverImageUrl,
        "prepTime": recipe.prepTime,
        "cookTime": recipe.cookTime,
        "totalTime": recipe.totalTime,
        "difficulty": recipe.difficulty,
        "difficultyLabel": DIFFICULTY_LABELS.get(recipe.difficulty or 0, ""),
        "servings": recipe.servings,
        "category": recipe.category,
        "tags": recipe.tags,
    }


def build_recipe_tools(
    store: RecipeStore,
    settings: CookingSettings | None = None,
) -> list[BaseTool]:
    """按数据源装配工具集（闭包注入 store，工具函数本身保持无状态）。"""
    settings = settings or CookingSettings()
    default_limit = settings.search_limit

    @tool
    async def search_recipes(
        keyword: str = "",
        category: str = "",
        difficulty: str = "",
    ) -> str:
        """搜索菜谱，返回匹配的菜谱摘要列表。

        用户想吃某道菜、某个类别、或某难度时都用它。找到菜谱后，
        结合返回的 title/description/totalTime/difficultyLabel 用自然语言
        介绍，一次通常推荐 2-3 道。

        Args:
            keyword: 关键词，匹配菜名、描述或标签，如「番茄」「红烧」「低脂」。
            category: 菜系或类别名，如「川菜」「家常菜」「素菜」。
            difficulty: 难度，可选「简单」「中等」「困难」。
        """
        try:
            recipes = await store.search_briefs(
                keyword,
                category=category,
                difficulty=_resolve_difficulty(difficulty),
                limit=default_limit,
            )
        except RecipeStoreError as exc:
            logger.warning("菜谱检索失败：%s", exc)
            return _dump({"error": f"菜谱检索失败：{exc}"})
        payload: dict[str, Any] = {
            "count": len(recipes),
            "recipes": [_brief_payload(recipe) for recipe in recipes],
        }
        if not recipes:
            # 明确给出「下一步怎么说」，否则模型容易在同一条件下反复重试
            payload["hint"] = "没有匹配的菜谱，可换更宽泛的关键词，或去掉分类/难度限制再试"
        return _dump(payload)

    @tool
    async def get_recipe_detail(recipe_id: int) -> str:
        """查询一道菜谱的完整用料与做法步骤。

        当用户问到「怎么做」「需要什么材料」「要多久」时使用。
        recipe_id 必须取自 search_recipes 的返回结果。

        Args:
            recipe_id: 菜谱 ID（search_recipes 结果里的 id）。
        """
        try:
            detail = await store.get_detail(recipe_id)
        except RecipeStoreError as exc:
            logger.warning("菜谱详情查询失败：%s", exc)
            return _dump({"error": f"菜谱详情查询失败：{exc}"})
        if detail is None:
            return _dump({"found": False, "hint": "菜谱不存在，可用 search_recipes 重新检索"})
        return _dump(
            {
                "found": True,
                "recipe": {
                    **_brief_payload(detail),
                    "tips": detail.tips,
                    "ingredients": [
                        {
                            "name": item.name,
                            "amount": item.amount,
                            "unit": item.unit,
                            "isEssential": item.isEssential,
                        }
                        for item in detail.ingredients
                    ],
                    # 后端返回集合无序，按步骤号排序后再交给模型，
                    # 否则提示词里的步骤顺序是随机的
                    "steps": [
                        {
                            "stepNumber": step.stepNumber,
                            "content": step.content,
                            "duration": step.duration,
                        }
                        for step in sorted(
                            detail.steps, key=lambda item: item.stepNumber or 0
                        )
                    ],
                },
            }
        )

    @tool
    async def list_categories() -> str:
        """列出菜谱库里全部可用的分类名。

        不确定用户说的菜系对应哪个 category 时先调它，再带分类名去搜索。
        """
        try:
            categories = await store.list_categories()
        except RecipeStoreError as exc:
            logger.warning("分类列表查询失败：%s", exc)
            return _dump({"error": f"分类列表查询失败：{exc}"})
        return _dump(
            {
                "count": len(categories),
                "categories": [item.name for item in categories if item.name],
            }
        )

    return [search_recipes, get_recipe_detail, list_categories]
