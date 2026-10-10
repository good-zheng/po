package com.goodzheng.po.novel.service.impl;

import com.goodzheng.po.novel.dto.BookRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.BookCharacterMapper;
import com.goodzheng.po.novel.repository.BookMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * genre 写的是 {@code NovelGenres} 的 value，不是 label。
 *
 * <p>这条契约原本没人管：写「玄幻」照样入库，列表页靠 label 兜底显示看着完全正常，
 * 只有在书架按类型筛选时才凭空少掉一本——本地 3 本 smoke 书就是这么脏的。校验收在这条写路径上，
 * 测试要钉住的是「拒得干净」：错值既不能落库，也不能连带把已有字段刷成新值。
 */
@ExtendWith(MockitoExtension.class)
class BookGenreContractTest {

    private static final Long BOOK_ID = 1L;

    @Mock
    private BookMapper bookMapper;
    @Mock
    private BookChapterMapper chapterMapper;
    @Mock
    private BookCharacterMapper characterMapper;

    private BookServiceImpl bookService;

    @BeforeEach
    void setUp() {
        bookService = new BookServiceImpl(bookMapper, chapterMapper, characterMapper);
    }

    @Test
    void createStoresTheGenreValueNotTheLabel() {
        Book saved = bookService.create(request("fantasy"), 42L);

        ArgumentCaptor<Book> inserted = ArgumentCaptor.forClass(Book.class);
        verify(bookMapper).insert(inserted.capture());
        assertEquals("fantasy", inserted.getValue().getGenre());
        assertEquals("fantasy", saved.getGenre());
    }

    /** label 是展示串，落库就等于这本书从类型筛选里消失 */
    @Test
    void createRejectsTheLabel() {
        RuntimeException error = assertThrows(RuntimeException.class,
                () -> bookService.create(request("玄幻"), 42L));

        assertEquals("无效的小说类型", error.getMessage());
        verify(bookMapper, never()).insert(any(Book.class));
    }

    /** 字典就是那十个固定串，不做大小写归一：宽容匹配只是把脏值留在库里继续漂 */
    @Test
    void createRejectsACaseVariant() {
        assertThrows(RuntimeException.class, () -> bookService.create(request("Fantasy"), 42L));

        verify(bookMapper, never()).insert(any(Book.class));
    }

    /** 新书常常还没定类型：留空必须仍然合法，否则这条校验会把建书本身堵死 */
    @Test
    void createAcceptsAnAbsentGenre() {
        bookService.create(request(null), 42L);

        ArgumentCaptor<Book> inserted = ArgumentCaptor.forClass(Book.class);
        verify(bookMapper).insert(inserted.capture());
        assertNull(inserted.getValue().getGenre());
    }

    @Test
    void updateRejectsTheLabelAndWritesNothing() {
        when(bookMapper.selectById(BOOK_ID)).thenReturn(existingBook());

        RuntimeException error = assertThrows(RuntimeException.class,
                () -> bookService.update(BOOK_ID, request("玄幻")));

        assertEquals("无效的小说类型", error.getMessage());
        verify(bookMapper, never()).updateById(any(Book.class));
    }

    @Test
    void updateAcceptsAKnownGenreValue() {
        when(bookMapper.selectById(BOOK_ID)).thenReturn(existingBook());

        Book saved = bookService.update(BOOK_ID, request("scifi"));

        assertEquals("scifi", saved.getGenre());
        verify(bookMapper).updateById(saved);
    }

    // ── 夹具 ──────────────────────────────────────────────

    private static BookRequest request(String genre) {
        BookRequest req = new BookRequest();
        req.setTitle("檐下三年");
        req.setGenre(genre);
        return req;
    }

    private static Book existingBook() {
        Book book = new Book();
        book.setId(BOOK_ID);
        book.setTitle("檐下三年");
        book.setGenre("fantasy");
        book.setSummary("世界观摘要 + 主线进度");
        return book;
    }
}
