"""items 示例 CRUD 的进程内存储：线程安全，但进程重启即丢。

定位说明：这是为演示 REST 链路（校验 → 存储 → 序列化）而存在的内存实现，
不是生产持久层——没有落盘、没有多进程共享，多 worker 部署时各 worker 各持
一份数据。真实业务接入时应替换 :func:`get_store` 的实现（路由层只依赖
``ItemStore`` 的这组方法签名，替换不影响端点代码）。

被调用方：:mod:`app.routers.items` 通过 FastAPI 依赖 ``Depends(get_store)``
注入；``get_store`` 之所以做成函数而非直接暴露实例，是为了让测试能用
``app.dependency_overrides`` 换成隔离的存储。
"""

import itertools
import threading
from datetime import datetime

from app.schemas import Item, ItemCreate, ItemUpdate


class ItemStore:
    """线程安全的 items 内存存储。

    虽然 FastAPI 端点通常跑在事件循环里，但 ``threading.Lock`` 仍然是必要的：
    部分测试/工具会以多线程方式并发访问同一实例，且锁的成本在此可忽略。
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # 单调递增的 id 源：删除后不会复用编号，避免客户端缓存了旧 id 后
        # 误命中新对象（``count`` 比 ``max(id)+1`` 更省事也天然不复用）。
        self._counter = itertools.count(1)
        self._items: dict[int, Item] = {}

    def list(self, skip: int = 0, limit: int = 100, q: str | None = None) -> list[Item]:
        """按 id 升序返回分页列表，``q`` 为名称的包含式（大小写不敏感）过滤。"""
        with self._lock:
            items = sorted(self._items.values(), key=lambda item: item.id)
        # 排序在锁内、过滤与切片在锁外：锁只保护快照生成这一小段，
        # 后续只读操作基于已复制的列表，不会与写入互相阻塞。
        if q:
            items = [item for item in items if q.lower() in item.name.lower()]
        return items[skip : skip + limit]

    def create(self, payload: ItemCreate) -> Item:
        """用已校验的入参生成带服务端字段的新资源。"""
        now = datetime.now()
        with self._lock:
            # 展开 payload 而不是逐字段赋值：ItemCreate 的字段是 Item 的子集，
            # 新增字段时此处无需同步修改。
            item = Item(id=next(self._counter), created_at=now, updated_at=now, **payload.model_dump())
            self._items[item.id] = item
            return item

    def get(self, item_id: int) -> Item | None:
        """读取单条；不存在返回 ``None``（由路由层翻译成 404）。

        返回的是存储内的同一实例（Pydantic 模型默认可变），调用方只应读取，
        任何修改都要走 :meth:`update` 才能保持 ``updated_at`` 与锁语义一致。
        """
        with self._lock:
            return self._items.get(item_id)

    def update(self, item_id: int, payload: ItemUpdate) -> Item | None:
        """局部更新；不存在返回 ``None``。

        ``exclude_unset=True`` 是关键：只把请求里真正出现过的字段并入，
        因此 PATCH 传 ``{"price": 1}`` 不会把 ``description`` 清空，
        而显式传 ``null`` 才会覆盖为空值。
        ``model_copy`` 产生新实例而非就地修改，保证读取方拿到的对象不会被
        后台更新突然改写。
        """
        with self._lock:
            existing = self._items.get(item_id)
            if existing is None:
                return None
            updated = existing.model_copy(update={**payload.model_dump(exclude_unset=True), "updated_at": datetime.now()})
            self._items[item_id] = updated
            return updated

    def delete(self, item_id: int) -> bool:
        """删除并返回是否存在过：``pop`` 的哨兵默认值把 404 判断留在路由层。"""
        with self._lock:
            return self._items.pop(item_id, None) is not None


_store = ItemStore()


def get_store() -> ItemStore:
    """FastAPI 依赖：返回进程级单例存储。"""
    return _store
