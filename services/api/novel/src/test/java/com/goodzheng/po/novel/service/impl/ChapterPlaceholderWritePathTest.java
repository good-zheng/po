package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.ChapterRevision;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.ChapterRevisionMapper;
import com.goodzheng.po.novel.repository.ReviewFindingMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * 「留空的新建章节 = 待写占位」在库侧的三条约束。
 *
 * <p>作者在管理端留空标题与正文排下一章，这一行必须满足：不进续写游标（否则它被跳过、
 * 永久空着）、标题自动落成一个可显示的值（{@code book_chapter.title} 是 NOT NULL）、
 * 生成链路按章号写回来时填的是<b>它这一行</b>而不是新插一行——行 id 是正典断言的溯源键。
 * 同号那行已有正文时报错，是这一组里唯一的拒绝路径：静默覆盖会把整本书的事实指向一份
 * 不再存在的正文，比这一轮红着结束严重得多。
 *
 * <p>纯 Mockito、不起容器：与 {@code ChapterRevisionAndSourceRelocationTest} 同一理由，
 * 本类与被测同包才能用它的包内行为做断言。
 */
@ExtendWith(MockitoExtension.class)
class ChapterPlaceholderWritePathTest {

    private static final Long BOOK_ID = 1L;
    private static final Long PLACEHOLDER_ID = 40L;

    @Mock
    private BookChapterMapper chapterMapper;
    @Mock
    private BookMapper bookMapper;
    @Mock
    private ChapterRevisionMapper revisionMapper;
    @Mock
    private CanonEntryMapper canonMapper;
    @Mock
    private ReviewFindingMapper findingMapper;

    private BookChapterServiceImpl chapterService;

    @BeforeEach
    void setUp() {
        chapterService = new BookChapterServiceImpl(chapterMapper, bookMapper,
                new ChapterSourceRelocator(revisionMapper, canonMapper, findingMapper));
        when(bookMapper.selectById(BOOK_ID)).thenReturn(new Book());
    }

    // ── 留空标题 ──────────────────────────────────────────

    @Test
    void aBlankTitleIsNamedAfterItsChapterNumber() {
        BookChapter saved = chapterService.create(BOOK_ID, request("", null, 4));

        ArgumentCaptor<BookChapter> row = ArgumentCaptor.forClass(BookChapter.class);
        verify(chapterMapper).insert(row.capture());
        assertEquals("第 4 章", saved.getTitle());
        assertEquals("第 4 章", row.getValue().getTitle());
        assertEquals(0, row.getValue().getWordCount().intValue());
    }

    @Test
    void clearingTheTitleOnEditRestoresTheAutoName() {
        givenRow(chapter(PLACEHOLDER_ID, 4, "第 4 章", "旧正文", 3));

        BookChapter saved = chapterService.update(BOOK_ID, PLACEHOLDER_ID,
                request("  ", "旧正文", null), null);

        assertEquals("第 4 章", saved.getTitle());
    }

    /** 没给章号就排到最后面：管理端新建章节的默认值走的就是这一条 */
    @Test
    void aChapterWithoutAnIndexTakesTheNextFreeNumber() {
        when(chapterMapper.selectObjs(any())).thenReturn(List.of(2, 3));

        BookChapter saved = chapterService.create(BOOK_ID, request("渡口", "正文", null));

        assertEquals(4, saved.getChapterIndex().intValue());
    }

    // ── 游标只数有正文的章 ────────────────────────────────

    @Test
    void writtenCountExcludesRowsWithoutContent() {
        when(chapterMapper.selectCount(any())).thenReturn(3L);

        assertEquals(3, chapterService.countWrittenByBook(BOOK_ID));

        ArgumentCaptor<QueryWrapper<BookChapter>> query = ArgumentCaptor.forClass(QueryWrapper.class);
        verify(chapterMapper).selectCount(query.capture());
        // word_count 是正文的派生列，所以「字数 > 0」就是「有正文」；这一条条件是
        // countWrittenByBook 与 countByBook 唯一的差别，必须能在 SQL 段里看见
        assertTrue(query.getValue().getSqlSegment().toLowerCase().contains("word_count"),
                "游标条件没落到 SQL 上：" + query.getValue().getSqlSegment());
    }

    @Test
    void rowCountStillCountsPlaceholderRows() {
        when(chapterMapper.selectCount(any())).thenReturn(4L);

        assertEquals(4, chapterService.countByBook(BOOK_ID));

        ArgumentCaptor<QueryWrapper<BookChapter>> query = ArgumentCaptor.forClass(QueryWrapper.class);
        verify(chapterMapper).selectCount(query.capture());
        assertFalse(query.getValue().getSqlSegment().toLowerCase().contains("word_count"),
                "台账口径不该跟着游标一起收窄：" + query.getValue().getSqlSegment());
    }

    // ── 生成链路按章号落位 ────────────────────────────────

    @Test
    void anEmptyChapterNumberIsFilledByTheGeneratedChapter() {
        // 库里只有那一行空白占位（第 4 章），本轮生成的正文按同一个章号写回来
        givenRow(chapter(PLACEHOLDER_ID, 4, "第 4 章", null, 0));

        BookChapter saved = chapterService.putByIndex(BOOK_ID, request("风雪夜", "生成的正文。", 4), 7L);

        assertEquals(PLACEHOLDER_ID, saved.getId(), "占位行要被填掉，不是另起一行");
        assertEquals("生成的正文。", saved.getContent());
        assertEquals(2, saved.getRevision().intValue(), "填正文是一次真实的正文写入，要走连带重算");
        verify(chapterMapper, never()).insert(any(BookChapter.class));
        // 走 update 意味着改稿的连带后果都在：旧版进快照、引用重定位
        verify(revisionMapper).insert(any(ChapterRevision.class));
    }

    /** 章号没人占着就照常插一行：新建一本书的那几章走的就是这条路 */
    @Test
    void aFreeChapterNumberStillInserts() {
        BookChapter saved = chapterService.putByIndex(BOOK_ID, request("风雪夜", "生成的正文。", 5), null);

        assertEquals(5, saved.getChapterIndex().intValue());
        verify(chapterMapper).insert(any(BookChapter.class));
        verify(chapterMapper, never()).updateById(any(BookChapter.class));
    }

    /** 撞上有正文的章号：停下来报错，而不是把已定稿的正文换掉 */
    @Test
    void aChapterThatAlreadyHasContentIsNeverOverwritten() {
        givenRow(chapter(30L, 3, "旧题", "已经写过的正文", 1500));

        RuntimeException error = assertThrows(RuntimeException.class,
                () -> chapterService.putByIndex(BOOK_ID, request("新题", "想覆盖它", 3), null));

        assertTrue(error.getMessage().contains("第 3 章已有正文"), error.getMessage());
        verify(chapterMapper, never()).insert(any(BookChapter.class));
        verify(chapterMapper, never()).updateById(any(BookChapter.class));
    }

    // ── 夹具 ──────────────────────────────────────────────

    private void givenRow(BookChapter row) {
        when(chapterMapper.selectOne(any())).thenReturn(row);
    }

    private static BookChapter chapter(Long id, int index, String title, String content, int wordCount) {
        BookChapter row = new BookChapter();
        row.setId(id);
        row.setBookId(BOOK_ID);
        row.setChapterIndex(index);
        row.setTitle(title);
        row.setContent(content);
        row.setWordCount(wordCount);
        row.setRevision(1);
        row.setStatus("draft");
        return row;
    }

    private static ChapterRequest request(String title, String content, Integer index) {
        ChapterRequest req = new ChapterRequest();
        req.setTitle(title);
        req.setContent(content);
        req.setChapterIndex(index);
        return req;
    }
}
