"""items 示例 CRUD 端点（完整路径 ``/api/items``）。

定位：作为 REST 链路的样例与后续业务的模板——展示「Pydantic 校验 →
依赖注入存储 → 统一 404 语义」这套约定；本身不涉及聊天编排。

依赖方向：上游是 HTTP 客户端；下游是 :class:`app.store.ItemStore` 的内存字典。
本模块不直接实例化存储，全部经 ``Depends(get_store)`` 注入，测试可用
``app.dependency_overrides`` 替换。

错误约定：路径参数命中不存在的 id 统一 404 ``item not found``；
请求体不合法则由 FastAPI 自动返回 422。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas import Item, ItemCreate, ItemUpdate
from app.store import ItemStore, get_store

router = APIRouter(prefix="/items", tags=["items"])

# 把「依赖类型」收成一个别名：端点签名只写 StoreDep 即可，
# 避免每个函数重复 Depends(get_store) 并在多处维护同一依赖关系。
StoreDep = Annotated[ItemStore, Depends(get_store)]


@router.get("", response_model=list[Item])
async def list_items(
    store: StoreDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
) -> list[Item]:
    """分页查询列表；``limit`` 上限 200，防止一次拉全表。"""
    return store.list(skip=skip, limit=limit, q=q)


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(store: StoreDep, payload: ItemCreate) -> Item:
    """创建资源：id 与时间戳由存储层生成，返回 201 + 完整资源体。"""
    return store.create(payload)


@router.get("/{item_id}", response_model=Item)
async def get_item(store: StoreDep, item_id: int) -> Item:
    """按 id 读取单条，不存在返回 404。"""
    item = store.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return item


@router.put("/{item_id}", response_model=Item)
async def replace_item(store: StoreDep, item_id: int, payload: ItemCreate) -> Item:
    """整体替换：请求体用 ``ItemCreate``，未提供的可选字段被重置为默认值。

    先 ``get`` 判存在再更新，是为了把「新建还是替换」的选择权留在客户端：
    这里不实现 upsert，路径 id 不存在直接 404。
    入参转成 ``ItemUpdate`` 才能复用 ``store.update``；转换后所有字段都处于
    「已设置」状态，因此存储层不会把它当成局部补丁（与 PATCH 的关键差别）。
    """
    existing = store.get(item_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return store.update(item_id, ItemUpdate(**payload.model_dump()))


@router.patch("/{item_id}", response_model=Item)
async def update_item(store: StoreDep, item_id: int, payload: ItemUpdate) -> Item:
    """局部更新：只覆盖请求体中出现过的字段，其余保持原值。"""
    item = store.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(store: StoreDep, item_id: int) -> None:
    """删除资源，成功返回 204（无响应体），不存在返回 404。

    删除幂等性由调用方决定：这里对不存在的 id 返回 404，因此重复删除
    第二次会失败，客户端需自行忽略该状态码。
    """
    if not store.delete(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
