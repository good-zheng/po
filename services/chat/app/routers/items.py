from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas import Item, ItemCreate, ItemUpdate
from app.store import ItemStore, get_store

router = APIRouter(prefix="/items", tags=["items"])

StoreDep = Annotated[ItemStore, Depends(get_store)]


@router.get("", response_model=list[Item])
async def list_items(
    store: StoreDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    q: Annotated[str | None, Query(max_length=100)] = None,
) -> list[Item]:
    return store.list(skip=skip, limit=limit, q=q)


@router.post("", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(store: StoreDep, payload: ItemCreate) -> Item:
    return store.create(payload)


@router.get("/{item_id}", response_model=Item)
async def get_item(store: StoreDep, item_id: int) -> Item:
    item = store.get(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return item


@router.put("/{item_id}", response_model=Item)
async def replace_item(store: StoreDep, item_id: int, payload: ItemCreate) -> Item:
    existing = store.get(item_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return store.update(item_id, ItemUpdate(**payload.model_dump()))


@router.patch("/{item_id}", response_model=Item)
async def update_item(store: StoreDep, item_id: int, payload: ItemUpdate) -> Item:
    item = store.update(item_id, payload)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(store: StoreDep, item_id: int) -> None:
    if not store.delete(item_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="item not found")
