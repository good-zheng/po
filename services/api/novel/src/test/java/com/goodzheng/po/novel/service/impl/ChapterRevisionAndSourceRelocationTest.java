package com.goodzheng.po.novel.service.impl;

import com.goodzheng.po.novel.dto.ChapterRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.ChapterRevision;
import com.goodzheng.po.novel.entity.ReviewFinding;
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
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * §12.4 的 {@code test_edit_chapter_relocates_sources} 与 {@code test_chapter_revision_keeps_golden}
 * 在 Java 侧的落点（§10.5-③ 的四件事）。
 *
 * <p>纯 Mockito、不起容器：验的是顺序与副作用——旧文进快照、引用它的断言 span 被搬走或进台账、
 * 已定稿的章退回待复核、没改正文就一次额外写入都不许有。
 * 两个协作者手工 {@code new} 而不是 {@code @InjectMocks}，因为要验的正是「重算挂在唯一的正文写路径上」，
 * 服务必须拿到<b>真的</b> relocator。本类与被测同包，是因为 {@code locate}/{@code sha256Hex} 是包内工具，
 * 它们不该为了测试暴露成正 API。
 */
@ExtendWith(MockitoExtension.class)
class ChapterRevisionAndSourceRelocationTest {

    private static final Long BOOK_ID = 1L;
    private static final Long CHAPTER_ID = 10L;

    /** 出处句「眼睛是灰蓝色的」在第 20-27 字 */
    private static final String OLD_CONTENT = "渡口的风把灯笼吹得倾斜。\n她站在石阶上，眼睛是灰蓝色的。";
    private static final String QUOTE = "眼睛是灰蓝色的";

    @Mock
    private ChapterRevisionMapper revisionMapper;
    @Mock
    private CanonEntryMapper canonMapper;
    @Mock
    private ReviewFindingMapper findingMapper;
    @Mock
    private BookChapterMapper chapterMapper;
    @Mock
    private BookMapper bookMapper;

    private BookChapterServiceImpl chapterService;

    @BeforeEach
    void setUp() {
        chapterService = new BookChapterServiceImpl(chapterMapper, bookMapper,
                new ChapterSourceRelocator(revisionMapper, canonMapper, findingMapper));
    }

    // ── ① 旧文不覆盖 ──────────────────────────────────────

    @Test
    void editingAChapterSnapshotsTheOutgoingRevision() {
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));
        when(canonMapper.selectList(any())).thenReturn(List.of());
        when(findingMapper.selectList(any())).thenReturn(List.of());

        String newContent = OLD_CONTENT + "\n她把灯挪到了栏杆内侧。";
        BookChapter saved = chapterService.update(BOOK_ID, CHAPTER_ID, request(newContent), 42L);

        ArgumentCaptor<ChapterRevision> snapshot = ArgumentCaptor.forClass(ChapterRevision.class);
        verify(revisionMapper).insert(snapshot.capture());
        assertEquals(CHAPTER_ID, snapshot.getValue().getChapterId());
        assertEquals(1, snapshot.getValue().getRevision().intValue());
        // 快照存的是让位出去的那一版，不是刚写进去的新版
        assertEquals(OLD_CONTENT, snapshot.getValue().getContent());
        assertEquals(42L, snapshot.getValue().getCreatedBy().longValue());
        assertEquals(2, saved.getRevision().intValue());
    }

    /** 空串的 sha256 是跨语言固定向量，对上了才说明 Java 快照与 Python 幂等键算的是同一把哈希 */
    @Test
    void contentHashMatchesTheCrossLanguageVector() {
        assertEquals("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                ChapterSourceRelocator.sha256Hex(""));
    }

    /** 没改正文就一次连带写入都不许有：改个标题加一版会让台账对上从未存在过的内容 */
    @Test
    void titleOnlySaveAddsNoRevisionAndTouchesNothing() {
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));

        BookChapter saved = chapterService.update(BOOK_ID, CHAPTER_ID, request(OLD_CONTENT), 42L);

        assertEquals(1, saved.getRevision().intValue());
        assertEquals("committed", saved.getStatus());
        verify(revisionMapper, never()).insert(any(ChapterRevision.class));
        verify(canonMapper, never()).selectList(any());
        verify(canonMapper, never()).updateById(any(CanonEntry.class));
    }

    // ── ② 出处重定位 ──────────────────────────────────────

    @Test
    void aQuoteThatSurvivedGetsMovedNotRetired() {
        String newContent = "夜色压下来。" + OLD_CONTENT;
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));
        when(canonMapper.selectList(any())).thenReturn(List.of(assertion(9L, QUOTE, 20, 27)));
        when(findingMapper.selectList(any())).thenReturn(List.of());

        chapterService.update(BOOK_ID, CHAPTER_ID, request(newContent), 42L);

        ArgumentCaptor<CanonEntry> moved = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).updateById(moved.capture());
        assertEquals(newContent.indexOf(QUOTE), moved.getValue().getSourceStart().intValue());
        assertEquals(newContent.indexOf(QUOTE) + QUOTE.length(), moved.getValue().getSourceEnd().intValue());
        // 引文还在，就不该有台账行：断言与它的出处仍然对得上
        verify(findingMapper, never()).insert(any(ReviewFinding.class));
    }

    /** 找不回来的引文：断言一个字都不动，只把「暂时没有可核对的原文」摆进台账 */
    @Test
    void aLostQuoteGoesToTheLedgerAndLeavesTheAssertionAlone() {
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));
        when(canonMapper.selectList(any())).thenReturn(List.of(assertion(9L, QUOTE, 20, 27)));
        when(findingMapper.selectList(any())).thenReturn(List.of());
        when(findingMapper.selectCount(any())).thenReturn(0L);

        chapterService.update(BOOK_ID, CHAPTER_ID, request("她把眼睛的颜色忘了。"), 42L);

        verify(canonMapper, never()).updateById(any(CanonEntry.class));
        ArgumentCaptor<ReviewFinding> row = ArgumentCaptor.forClass(ReviewFinding.class);
        verify(findingMapper).insert(row.capture());
        ReviewFinding finding = row.getValue();
        assertEquals(ChapterSourceRelocator.CODE_SOURCE_ORPHANED, finding.getCode());
        assertEquals("major", finding.getSeverity());
        assertEquals("rule", finding.getChecker());
        assertEquals("open", finding.getStatus());
        assertEquals("[9]", finding.getCanonRefs());
        assertEquals(QUOTE, finding.getEvidenceQuote());
        assertNull(finding.getTextStart(), "新版本里没有这段位置，填旧坐标等于指着一行不存在的字");
    }

    /** 反复改稿不该把台账刷成一串重复行 */
    @Test
    void anAlreadyOpenOrphanRowIsNotDuplicated() {
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));
        when(canonMapper.selectList(any())).thenReturn(List.of(assertion(9L, QUOTE, 20, 27)));
        when(findingMapper.selectList(any())).thenReturn(List.of());
        when(findingMapper.selectCount(any())).thenReturn(1L);

        chapterService.update(BOOK_ID, CHAPTER_ID, request("她把眼睛的颜色忘了。"), 42L);

        verify(findingMapper, never()).insert(any(ReviewFinding.class));
    }

    /** 本章未裁定的冲突，证据被改掉才转 orphaned；不删行，否则黄金集再也复现不出当时报了什么 */
    @Test
    void staleEvidenceFindingsAreMarkedOrphanedInPlace() {
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));
        when(canonMapper.selectList(any())).thenReturn(List.of());
        ReviewFinding surviving = evidence("灯笼吹得倾斜");
        ReviewFinding vanished = evidence("她提着一盏白灯");
        when(findingMapper.selectList(any())).thenReturn(List.of(surviving, vanished));

        chapterService.update(BOOK_ID, CHAPTER_ID, request(OLD_CONTENT + "\n后来灯灭了。"), 42L);

        // 只转状态、不删行：黄金集样本按 (chapter_id, revision) 引用，删掉就再也复现不出当时报了什么
        ArgumentCaptor<ReviewFinding> flipped = ArgumentCaptor.forClass(ReviewFinding.class);
        verify(findingMapper).updateById(flipped.capture());
        assertEquals(vanished.getId(), flipped.getValue().getId());
        assertEquals("orphaned", flipped.getValue().getStatus());
        assertEquals("open", surviving.getStatus());
    }

    // ── ③ 改过的章要重过闸门 ──────────────────────────────

    @Test
    void aCommittedChapterGoesBackToPendingReview() {
        givenChapter(chapter(OLD_CONTENT, 1, "committed"));
        when(canonMapper.selectList(any())).thenReturn(List.of());
        when(findingMapper.selectList(any())).thenReturn(List.of());

        BookChapter saved = chapterService.update(BOOK_ID, CHAPTER_ID,
                request(OLD_CONTENT + "灯影里有人应答。"), 42L);

        assertEquals("pending_review", saved.getStatus());
    }

    @Test
    void aDraftChapterStaysDraft() {
        givenChapter(chapter(OLD_CONTENT, 4, "draft"));
        when(canonMapper.selectList(any())).thenReturn(List.of());
        when(findingMapper.selectList(any())).thenReturn(List.of());

        BookChapter saved = chapterService.update(BOOK_ID, CHAPTER_ID,
                request(OLD_CONTENT + "灯影里有人应答。"), 42L);

        assertEquals("draft", saved.getStatus());
        assertEquals(5, saved.getRevision().intValue());
    }

    // ── 定位口径 ──────────────────────────────────────────

    /** 同一句重现多处时取离旧起点最近的一处：按第一个匹配搬 span 会把出处指到错误的段落 */
    @Test
    void repeatedQuoteResolvesToTheNearestOccurrence() {
        String text = "她说她死了。\n旁人说她死了。\n只有她自己知道她死了。";
        int first = text.indexOf("她死了");
        int last = text.lastIndexOf("她死了");

        assertEquals(first, ChapterSourceRelocator.locate(text, "她死了", first).start());
        assertEquals(last, ChapterSourceRelocator.locate(text, "她死了", last).start());
    }

    /** 全角空格必须算空白，否则与 Python 的 re.sub(r"\s+", "") 判定相反 */
    @Test
    void fullWidthSpaceIsGapJustLikePython() {
        String text = "她　的　眼　睛是灰蓝色";
        ChapterSourceRelocator.Span span = ChapterSourceRelocator.locate(text, "她的眼睛", null);

        assertNotNull(span);
        assertEquals(0, span.start());
        assertEquals(text.indexOf("睛") + 1, span.end());
    }

    @Test
    void blankOrMissingQuoteIsNeverLocated() {
        assertNull(ChapterSourceRelocator.locate(OLD_CONTENT, "   ", 0));
        assertNull(ChapterSourceRelocator.locate(null, QUOTE, 0));
        assertNull(ChapterSourceRelocator.locate(OLD_CONTENT, null, 0));
        assertNotNull(ChapterSourceRelocator.locate(OLD_CONTENT, QUOTE, 0));
    }

    // ── 章数读回（内网对话装配） ────────────────────────────

    @Test
    void chapterCountIsAQueryNotAListLoad() {
        when(bookMapper.selectById(BOOK_ID)).thenReturn(new Book());
        when(chapterMapper.selectCount(any())).thenReturn(7L);

        // 装配只要一个数字：走 list() 会把整本书的正文读进内存
        assertEquals(7, chapterService.countByBook(BOOK_ID));
        verify(chapterMapper, never()).selectList(any());
    }

    @Test
    void chapterCountOfMissingBookIsRejectedBeforeCounting() {
        when(bookMapper.selectById(BOOK_ID)).thenReturn(null);

        RuntimeException error = assertThrows(RuntimeException.class,
                () -> chapterService.countByBook(BOOK_ID));
        assertEquals("书籍不存在", error.getMessage());
        verify(chapterMapper, never()).selectCount(any());
    }

    // ── 夹具 ──────────────────────────────────────────────

    private void givenChapter(BookChapter chapter) {
        when(bookMapper.selectById(BOOK_ID)).thenReturn(new Book());
        when(chapterMapper.selectOne(any())).thenReturn(chapter);
    }

    private static ChapterRequest request(String content) {
        ChapterRequest req = new ChapterRequest();
        req.setTitle("渡口");
        req.setContent(content);
        return req;
    }

    private static BookChapter chapter(String content, int revision, String status) {
        BookChapter chapter = new BookChapter();
        chapter.setId(CHAPTER_ID);
        chapter.setBookId(BOOK_ID);
        chapter.setChapterIndex(5);
        chapter.setTitle("渡口");
        chapter.setContent(content);
        chapter.setRevision(revision);
        chapter.setStatus(status);
        return chapter;
    }

    private static CanonEntry assertion(Long id, String evidenceQuote, Integer start, Integer end) {
        CanonEntry entry = new CanonEntry();
        entry.setId(id);
        entry.setBookId(BOOK_ID);
        entry.setSubjectKey("char:shen");
        entry.setPredicate("eye_color");
        entry.setObjectText("灰蓝色");
        entry.setAuthority("author");
        entry.setSourceChapterId(CHAPTER_ID);
        entry.setEvidenceQuote(evidenceQuote);
        entry.setSourceStart(start);
        entry.setSourceEnd(end);
        return entry;
    }

    private static ReviewFinding evidence(String quote) {
        ReviewFinding finding = new ReviewFinding();
        finding.setId(quote.equals("灯笼吹得倾斜") ? 101L : 102L);
        finding.setBookId(BOOK_ID);
        finding.setChapterId(CHAPTER_ID);
        finding.setRevision(1);
        finding.setCode("attribute_conflict");
        finding.setSeverity("blocker");
        finding.setChecker("rule");
        finding.setEvidenceQuote(quote);
        finding.setStatus("open");
        return finding;
    }
}
