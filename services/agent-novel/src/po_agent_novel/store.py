"""小说数据层：NovelStore 协议 + 进程内 mock 实现。

NovelStore 是垂直 Agent 与持久层之间的接缝——本迭代用
MockNovelStore（数据层先 mock 的既定决策），后续接入 Java
novel 模块（services/api/novel 的 Book/BookChapter/BookCharacter
REST CRUD）时，只需提供同一协议的 HTTP 实现，子图零改动。

唯一调用方是 ``graph.archive_node``（用户确认归档之后），
因此协议只覆盖「写入归档 + 列出书目」，不含更新/删除——
成稿一经归档即视为定本，修订发生在归档之前的 reflect 回环里。

协议是结构性子类型（typing.Protocol）：实现方无需继承，只要方法签名
匹配即可被子图使用；方法声明为 async 是为了让未来的 HTTP 实现
（aiohttp/httpx）与 mock 在调用侧完全同形。
"""

from __future__ import annotations

from typing import Protocol
from uuid import uuid4

from po_agent_novel.schemas import ArchivedBook, BookDraft, ChapterDraft, CharacterProfile


class NovelStore(Protocol):
    """小说持久层协议（归档写入 + 书目查询）。

    方法粒度对齐 Java novel 模块的资源划分
    （book / chapter / character），未来逐方法替换为 HTTP 调用。

    book_id 是三种资源之间的唯一关联键：save_book 先建书目并返回 id，
    章节与角色再按该 id 写入（调用顺序见 graph.archive_node）。
    """

    async def save_book(self, draft: BookDraft) -> str:
        """保存书稿元数据，返回 book_id。"""
        ...

    async def save_chapters(self, book_id: str, chapters: list[ChapterDraft]) -> None:
        """批量保存章节正文。

        语义为「整体写入」而非增量追加：一次归档即写入全书章节
        （与 NovelStore 只服务归档场景相称）。
        """
        ...

    async def save_characters(
        self, book_id: str, characters: list[CharacterProfile]
    ) -> None:
        """保存角色档案（整体写入，来源为归档前的角色提取结果）。"""
        ...

    async def list_books(self) -> list[ArchivedBook]:
        """列出已归档书目（未来回溯续写的数据入口）。"""
        ...


class MockNovelStore:
    """进程内 mock：uuid 主键、列表保存、重启即失。

    仅用于开发与测试——数据不落盘，进程重启即清空；
    换真实实现时按 NovelStore 协议提供 HTTP 版本即可，本类无需保留。
    """

    def __init__(self) -> None:
        # 三张表按 book_id 关联，对应协议里的三类资源。
        self._meta: dict[str, BookDraft] = {}
        self._chapters: dict[str, list[ChapterDraft]] = {}
        self._characters: dict[str, list[CharacterProfile]] = {}

    async def save_book(self, draft: BookDraft) -> str:
        # 短主键（12 位十六进制）足够避免碰撞，且便于在日志与用户回执中辨识。
        book_id = f"book-{uuid4().hex[:12]}"
        self._meta[book_id] = draft
        # 先把章节/角色表初始化为空列表，list_books 的聚合计数无需再判 None。
        self._chapters[book_id] = []
        self._characters[book_id] = []
        return book_id

    async def save_chapters(self, book_id: str, chapters: list[ChapterDraft]) -> None:
        self._require(book_id)
        # 复制一份入参列表：调用方后续若改动自己的列表，不影响已归档数据。
        self._chapters[book_id] = list(chapters)

    async def save_characters(
        self, book_id: str, characters: list[CharacterProfile]
    ) -> None:
        self._require(book_id)
        self._characters[book_id] = list(characters)

    async def list_books(self) -> list[ArchivedBook]:
        # 以书目表为基准遍历，章节/角色计数缺失时按 0 处理（防御式取默认值）。
        return [
            ArchivedBook(
                book_id=book_id,
                title=draft.title,
                genre=draft.genre,
                summary=draft.summary,
                chapter_count=len(self._chapters.get(book_id, [])),
                character_count=len(self._characters.get(book_id, [])),
            )
            for book_id, draft in self._meta.items()
        ]

    def _require(self, book_id: str) -> None:
        """校验 book_id 已存在：把真实数据层的外键约束在 mock 里显式化。"""
        if book_id not in self._meta:
            raise KeyError(f"book 不存在：{book_id}")
