"""菜谱数据层测试：HTTP 解析、错误收口、内存数据源行为。"""

from __future__ import annotations

import httpx
import pytest
from conftest import run

from po_agent_cooking.config import CookingSettings
from po_agent_cooking.recipes import (
    HttpRecipeStore,
    MockRecipeStore,
    RecipeDetail,
    RecipeStoreError,
)

_LIST_ITEM = {
    "id": 7,
    "title": "麻婆豆腐",
    "description": "麻辣鲜香",
    "coverImageUrl": "/api/covers/7.jpg",
    "prepTime": 10,
    "cookTime": 15,
    "totalTime": 25,
    "difficulty": 2,
    "servings": 2,
    "category": "川菜",
    "tags": "川菜,下饭",
    "likesCount": 12,
}


def _store(handler) -> HttpRecipeStore:  # type: ignore[no-untyped-def]
    """构造走假 transport 的 store：不发真实网络，但完整经过 _get 的真实逻辑。"""
    settings = CookingSettings(_env_file=None, api_base_url="http://api.test/api")
    return HttpRecipeStore(settings, transport=httpx.MockTransport(handler))


def _catalog_handler(captured: dict[str, str], categories: list[dict[str, object]]):
    """分类接口 + 列表接口的双端点假后端，把各自收到的 URL 记进 captured。"""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/recipe-categories"):
            captured["categories_url"] = str(request.url)
            return httpx.Response(200, json={"success": True, "data": categories})
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={"success": True, "code": 1, "data": {"content": [_LIST_ITEM]}},
        )

    return handler


def test_search_parses_paged_content() -> None:
    """后端分页对象 {"content": [...]} 能被正确解包为摘要列表。"""
    captured: dict[str, str] = {}
    handler = _catalog_handler(
        captured, categories=[{"id": 3, "name": "川菜"}]
    )

    results = run(_store(handler).search_briefs("豆腐", category="川菜", difficulty=2, limit=5))

    assert [item.title for item in results] == ["麻婆豆腐"]
    assert results[0].difficulty == 2
    assert results[0].coverImageUrl == "/api/covers/7.jpg"
    url = captured["url"]
    assert "keyword=" in url and "difficulty=2" in url
    # 分类必须换成数字 ID：后端按 Long::parseLong 解析，传中文名会 500
    assert "categoryIdStr=3" in url
    # Spring 分页从 0 起，sort 只认枚举里的 recommend/likes/newest
    assert "page=0" in url and "sort=likes" in url


def test_search_maps_partial_category_name() -> None:
    """口语简称（「家常」）解析不到精确名时退回包含匹配，命中多个就都带上。"""
    captured: dict[str, str] = {}
    handler = _catalog_handler(
        captured,
        categories=[{"id": 1, "name": "家常菜"}, {"id": 2, "name": "家常汤羹"}],
    )

    run(_store(handler).search_briefs("", category="家常"))

    assert "categoryIdStr=1%2C2" in captured["url"]


def test_search_unknown_category_skips_list_call() -> None:
    """分类名在库里不存在时直接空手而归，不再打列表接口。"""
    captured: dict[str, str] = {}
    handler = _catalog_handler(captured, categories=[{"id": 1, "name": "川菜"}])

    results = run(_store(handler).search_briefs("", category="粤菜"))

    assert results == []
    assert "url" not in captured


def test_search_omits_empty_filters() -> None:
    """空关键词/分类不该出现在查询串里，否则会拼出空条件。"""
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(200, json={"success": True, "data": {"content": []}})

    run(_store(handler).search_briefs("", difficulty=None, limit=3))

    assert "keyword" not in captured["url"]
    assert "categoryIdStr" not in captured["url"]
    assert "difficulty" not in captured["url"]


def test_accepts_bare_array() -> None:
    """分类等接口直接返回数组，也要能解析。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": True, "data": [{"id": 1, "name": "家常菜"}]})

    categories = run(_store(handler).list_categories())

    assert [item.name for item in categories] == ["家常菜"]


def test_business_error_raises_store_error() -> None:
    """success=false 必须转成 RecipeStoreError，交由工具层翻译成可读文本。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": False, "code": 0, "message": "服务内部错误"})

    with pytest.raises(RecipeStoreError, match="服务内部错误"):
        run(_store(handler).search_briefs("任意"))


def test_http_failure_raises_store_error() -> None:
    """网络层失败同样收敛为 RecipeStoreError，不泄漏 httpx 异常类型。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="upstream down")

    with pytest.raises(RecipeStoreError):
        run(_store(handler).search_briefs("任意"))


def test_non_json_response_raises_store_error() -> None:
    """网关返回 HTML 错误页时给可读错误，而不是 JSONDecodeError。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>502 Bad Gateway</html>")

    with pytest.raises(RecipeStoreError, match="非 JSON"):
        run(_store(handler).search_briefs("任意"))


def test_missing_recipe_returns_none() -> None:
    """详情接口返回空数据时给 None，而不是抛错。"""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"success": True, "data": None})

    assert run(_store(handler).get_detail(999)) is None


def test_mock_store_filters() -> None:
    """内存数据源按关键词、分类、难度组合筛选。"""
    store = MockRecipeStore()

    assert [item.title for item in run(store.search_briefs("番茄"))] == ["番茄炒蛋"]
    assert [item.title for item in run(store.search_briefs("", category="川菜"))] == ["宫保鸡丁"]
    assert len(run(store.search_briefs("", difficulty=1))) == 2
    assert run(store.search_briefs("不存在的菜")) == []


def test_mock_store_detail_has_steps_and_ingredients() -> None:
    """详情用例数据要含步骤与用料，否则工具与提示词测试无从断言。"""
    detail = run(MockRecipeStore().get_detail(1))

    assert isinstance(detail, RecipeDetail)
    assert detail.ingredients and detail.steps
    assert detail.steps[0].content
