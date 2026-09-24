"""菜谱数据层：领域模型 + 数据源协议 + HTTP 实现。

分层意图与 agent-core 的记忆模块一致——工具只依赖 :class:`RecipeStore`
协议，真实实现走 Java API，测试与离线演示注入 :class:`MockRecipeStore`。
这样「Agent 逻辑」与「数据从哪来」解耦：换数据源不用动图与提示词。

领域模型刻意只取 Agent 用得到的字段（而非 Java 实体全量），
字段名与后端 JSON 契约（camelCase）保持一致，省掉一层映射；
模型只声明字段而不做业务校验，多余字段由 pydantic 默认忽略。
"""

from __future__ import annotations

from typing import Any, Protocol

import httpx
from pydantic import BaseModel, Field

from po_agent_cooking.config import CookingSettings


class RecipeStoreError(RuntimeError):
    """菜谱数据源不可用（网络失败、后端报错、返回结构异常）。"""


class RecipeBrief(BaseModel):
    """列表场景的菜谱摘要（搜索结果的元素，也是移动端卡片的渲染源）。"""

    id: int
    title: str = ""
    description: str = ""
    coverImageUrl: str = ""
    prepTime: int | None = None
    cookTime: int | None = None
    totalTime: int | None = None
    # 1=简单 2=中等 3=困难（与 Java 侧 Integer 列一致）
    difficulty: int | None = None
    servings: int | None = None
    category: str = ""
    tags: str = ""
    likesCount: int | None = None


class RecipeIngredient(BaseModel):
    """一道菜的用料。"""

    id: int | None = None
    name: str = ""
    amount: str = ""
    unit: str = ""
    isEssential: bool | None = None


class RecipeStep(BaseModel):
    """一个做菜步骤。"""

    id: int | None = None
    stepNumber: int | None = None
    content: str = ""
    duration: int | None = None


class RecipeDetail(RecipeBrief):
    """详情：摘要 + 用料 + 步骤 + 小贴士。"""

    tips: str = ""
    ingredients: list[RecipeIngredient] = Field(default_factory=list)
    steps: list[RecipeStep] = Field(default_factory=list)


class RecipeCategory(BaseModel):
    """菜谱分类（把用户口语里的「川菜」映射到后端认可的类别名）。"""

    id: int
    name: str = ""
    description: str = ""


class RecipeStore(Protocol):
    """菜谱数据源协议（结构化子类型，无需显式继承）。

    刻意不引入缓存 / 连接池等优化：工具调用频率低，真正的性能问题
    该由后端分页与索引解决。
    """

    async def search_briefs(
        self,
        keyword: str = "",
        *,
        category: str = "",
        difficulty: int | None = None,
        limit: int = 5,
    ) -> list[RecipeBrief]: ...

    async def get_detail(self, recipe_id: int) -> RecipeDetail | None: ...

    async def list_categories(self) -> list[RecipeCategory]: ...


def _as_list(payload: Any) -> list[Any]:
    """兼容后端两种分页形状：``{"content": [...]}`` 与裸数组。

    MyBatis-Plus 的分页对象序列化后是前者；部分接口（如分类）直接返回数组。
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("content", "records"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


class HttpRecipeStore:
    """经 HTTP 调用 Java 菜谱接口的数据源。

    每次调用自建 ``AsyncClient``：工具调用频率低，复用连接池的收益抵不过
    「client 实例绑定创建时的事件循环、跨 loop 复用会报错」的风险。
    """

    def __init__(
        self,
        settings: CookingSettings | None = None,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings = settings or CookingSettings()
        # 传输层可替换：测试用 httpx.MockTransport 打桩，避免为了可测性
        # 把 _get 拆成「可覆写的钩子 + 真实实现」两份逻辑
        self._transport = transport

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET 一个 ``Result<T>`` 响应并解出 data。

        异常统一在这里收口成 :class:`RecipeStoreError`，工具层就只需处理
        一种失败，不必把 httpx 的十几种异常泄漏进提示词。
        """
        url = f"{self.settings.api_base_url.rstrip('/')}{path}"
        try:
            async with httpx.AsyncClient(
                timeout=self.settings.request_timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.get(url, params=params or {})
                response.raise_for_status()
                body = response.json()
        except httpx.HTTPError as exc:
            raise RecipeStoreError(f"菜谱服务请求失败：{exc}") from exc
        except ValueError as exc:  # 非 JSON 响应（如网关返回 HTML 错误页）
            raise RecipeStoreError("菜谱服务返回了非 JSON 响应") from exc

        if not isinstance(body, dict):
            raise RecipeStoreError("菜谱服务返回结构异常：顶层不是对象")
        if not body.get("success", False):
            message = body.get("message") or "未知错误"
            raise RecipeStoreError(f"菜谱服务返回业务错误：{message}")
        return body.get("data")

    async def search_briefs(
        self,
        keyword: str = "",
        *,
        category: str = "",
        difficulty: int | None = None,
        limit: int = 5,
    ) -> list[RecipeBrief]:
        """按关键词 / 分类 / 难度检索菜谱。

        参数仍然收**类别名**（模型可以把用户口语里的「川菜」原样传进来），
        但在发给后端前要换成数字 ID：Java 侧 ``categoryIdStr`` 是
        「逗号分隔的分类 ID」，按 ``Long::parseLong`` 解析后查库换成名字
        再过滤，直接传中文名会抛 NumberFormatException（接口 500）。
        """
        # page 从 0 起（Spring 的 PageRequest 语义），传 1 会跳过第一页；
        # sort 只认 recommend / likes / newest，这里取 likes：稳定按热度排，
        # 不随「时间衰减」项让同一问题每次拿到不同的第一页
        params: dict[str, Any] = {"page": 0, "size": max(1, limit), "sort": "likes"}
        if keyword.strip():
            params["keyword"] = keyword.strip()
        if category.strip():
            category_ids = await self._resolve_category_ids(category)
            if not category_ids:
                # 库里没有这个分类：返回空结果交给工具的 hint 引导换词，
                # 比丢掉筛选条件、端回一堆无关菜谱要诚实
                return []
            params["categoryIdStr"] = ",".join(str(item) for item in category_ids)
        if difficulty is not None:
            params["difficulty"] = difficulty
        data = await self._get("/recipes", params)
        return [RecipeBrief.model_validate(item) for item in _as_list(data)]

    async def _resolve_category_ids(self, category: str) -> list[int]:
        """把分类名解析成后端要的分类 ID。

        先精确匹配；未命中再退回包含匹配（「家常」→「家常菜」这样的
        口语简称），命中多个就都发过去——后端按 ``category IN (...)``
        做 or 过滤，多给几个候选好过猜错一个。
        """
        wanted = category.strip()
        categories = await self.list_categories()
        exact = [item.id for item in categories if item.name == wanted]
        if exact:
            return exact
        return [
            item.id
            for item in categories
            if item.name and (wanted in item.name or item.name in wanted)
        ]

    async def get_detail(self, recipe_id: int) -> RecipeDetail | None:
        """取菜谱详情（含用料与步骤）。不存在时返回 None 而非抛错。"""
        data = await self._get(f"/recipes/{recipe_id}")
        if not isinstance(data, dict):
            return None
        return RecipeDetail.model_validate(data)

    async def list_categories(self) -> list[RecipeCategory]:
        data = await self._get("/recipe-categories")
        return [RecipeCategory.model_validate(item) for item in _as_list(data)]


class MockRecipeStore:
    """内存数据源：离线演示与测试用，也可在后端不可用时兜底。

    数据刻意少而典型，够覆盖「按关键词搜」「按分类搜」「查详情」三条路径。
    """

    def __init__(self) -> None:
        self._recipes: list[RecipeDetail] = [
            RecipeDetail(
                id=1,
                title="番茄炒蛋",
                description="家常快手菜，酸甜下饭",
                difficulty=1,
                totalTime=15,
                prepTime=5,
                cookTime=10,
                servings=2,
                category="家常菜",
                tags="快手,家常",
                tips="番茄先用少许糖炒出沙，味道更浓",
                ingredients=[
                    RecipeIngredient(name="番茄", amount="2", unit="个"),
                    RecipeIngredient(name="鸡蛋", amount="3", unit="个"),
                ],
                steps=[
                    RecipeStep(stepNumber=1, content="鸡蛋打散加少许盐", duration=2),
                    RecipeStep(stepNumber=2, content="番茄切块下锅炒出汁", duration=5),
                    RecipeStep(stepNumber=3, content="倒入蛋液翻炒均匀即可", duration=3),
                ],
            ),
            RecipeDetail(
                id=2,
                title="宫保鸡丁",
                description="经典川菜，微辣带甜",
                difficulty=2,
                totalTime=30,
                prepTime=15,
                cookTime=15,
                servings=3,
                category="川菜",
                tags="川菜,下饭",
                ingredients=[
                    RecipeIngredient(name="鸡腿肉", amount="300", unit="克"),
                    RecipeIngredient(name="花生米", amount="50", unit="克"),
                ],
                steps=[
                    RecipeStep(stepNumber=1, content="鸡肉切丁用料酒生抽腌制", duration=10),
                    RecipeStep(stepNumber=2, content="调好宫保汁备用", duration=3),
                    RecipeStep(
                        stepNumber=3, content="爆香干辣椒与花椒后下鸡丁翻炒", duration=5
                    ),
                ],
            ),
            RecipeDetail(
                id=3,
                title="清炒时蔬",
                description="清爽少油，适合减脂",
                difficulty=1,
                totalTime=10,
                prepTime=5,
                cookTime=5,
                servings=2,
                category="素菜",
                tags="低脂,快手",
                ingredients=[
                    RecipeIngredient(name="时令青菜", amount="400", unit="克")
                ],
                steps=[RecipeStep(stepNumber=1, content="大火快炒，出锅前加盐", duration=5)],
            ),
        ]

    async def search_briefs(
        self,
        keyword: str = "",
        *,
        category: str = "",
        difficulty: int | None = None,
        limit: int = 5,
    ) -> list[RecipeBrief]:
        keyword = keyword.strip()
        hits = [
            recipe
            for recipe in self._recipes
            if (not keyword or keyword in recipe.title or keyword in recipe.tags)
            and (not category or category == recipe.category)
            and (difficulty is None or difficulty == recipe.difficulty)
        ]
        return [
            RecipeBrief.model_validate(recipe.model_dump()) for recipe in hits[:limit]
        ]

    async def get_detail(self, recipe_id: int) -> RecipeDetail | None:
        for recipe in self._recipes:
            if recipe.id == recipe_id:
                return recipe
        return None

    async def list_categories(self) -> list[RecipeCategory]:
        names = sorted({recipe.category for recipe in self._recipes if recipe.category})
        return [RecipeCategory(id=index + 1, name=name) for index, name in enumerate(names)]
