"""In-memory item store with thread-safe CRUD operations."""

import itertools
import threading
from datetime import datetime

from app.schemas import Item, ItemCreate, ItemUpdate


class ItemStore:
    """Thread-safe in-memory storage for items."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counter = itertools.count(1)
        self._items: dict[int, Item] = {}

    def list(self, skip: int = 0, limit: int = 100, q: str | None = None) -> list[Item]:
        with self._lock:
            items = sorted(self._items.values(), key=lambda item: item.id)
        if q:
            items = [item for item in items if q.lower() in item.name.lower()]
        return items[skip : skip + limit]

    def create(self, payload: ItemCreate) -> Item:
        now = datetime.now()
        with self._lock:
            item = Item(id=next(self._counter), created_at=now, updated_at=now, **payload.model_dump())
            self._items[item.id] = item
            return item

    def get(self, item_id: int) -> Item | None:
        with self._lock:
            return self._items.get(item_id)

    def update(self, item_id: int, payload: ItemUpdate) -> Item | None:
        with self._lock:
            existing = self._items.get(item_id)
            if existing is None:
                return None
            updated = existing.model_copy(update={**payload.model_dump(exclude_unset=True), "updated_at": datetime.now()})
            self._items[item_id] = updated
            return updated

    def delete(self, item_id: int) -> bool:
        with self._lock:
            return self._items.pop(item_id, None) is not None


_store = ItemStore()


def get_store() -> ItemStore:
    return _store
