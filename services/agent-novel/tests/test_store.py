"""MockNovelStore 单测：锁定 NovelStore 协议的语义（未来 HTTP 实现须保持一致）。"""

from __future__ import annotations

import pytest

from po_agent_novel.schemas import BookDraft, ChapterDraft, CharacterProfile
from po_agent_novel.store import MockNovelStore


def _draft() -> BookDraft:
    return BookDraft(title="云海孤鸿", genre="玄幻", summary="少年偶得上古残卷。")


async def test_save_and_list_roundtrip() -> None:
    store = MockNovelStore()
    book_id = await store.save_book(_draft())
    assert book_id.startswith("book-")

    await store.save_chapters(
        book_id,
        [
            ChapterDraft(index=1, title="启程", content="夜色压得很低。"),
            ChapterDraft(index=2, title="暗流", content="看似平静。"),
        ],
    )
    await store.save_characters(
        book_id, [CharacterProfile(name="林晚", role="主角", description="少年")]
    )

    books = await store.list_books()
    assert len(books) == 1
    book = books[0]
    assert book.book_id == book_id
    assert book.title == "云海孤鸿"
    assert book.chapter_count == 2
    assert book.character_count == 1


async def test_unknown_book_id_raises() -> None:
    store = MockNovelStore()
    with pytest.raises(KeyError):
        await store.save_chapters("book-missing", [])


async def test_books_are_isolated_per_id() -> None:
    store = MockNovelStore()
    first = await store.save_book(_draft())
    second = await store.save_book(_draft())
    await store.save_chapters(first, [ChapterDraft(index=1, title="启程", content="一")])
    await store.save_chapters(second, [])
    books = {b.book_id: b for b in await store.list_books()}
    assert books[first].chapter_count == 1
    assert books[second].chapter_count == 0
