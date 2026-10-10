package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.goodzheng.po.novel.dto.SearchResultsView;
import com.goodzheng.po.novel.dto.StyleProfileRequest;
import com.goodzheng.po.novel.dto.StyleProfileView;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.StyleProfile;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.StyleProfileMapper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageRequest;

import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

/**
 * 左栏统一检索与文风契约读写（N5c-2）。
 *
 * <p>两侧都刻意不起容器：检索要验的是「查询词进 SQL 前被怎么对待」，契约要验的是
 * 「没填」与「填了空」的区别，两者都是纯赋值与纯字符串逻辑，容器只会把它们埋进噪音里。
 */
@ExtendWith(MockitoExtension.class)
class StyleProfileAndSearchTest {

    private static final Long BOOK_ID = 1L;
    private static final String CONTENT = "渡口的风把灯笼吹得倾斜。\n她站在石阶上，眼睛是灰蓝色的。";

    @Mock
    private BookChapterMapper chapterMapper;
    @Mock
    private CanonEntryMapper canonMapper;
    @Mock
    private AliasMapper aliasMapper;
    @Mock
    private StyleProfileMapper styleMapper;

    @InjectMocks
    private NovelSearchServiceImpl searchService;
    @InjectMocks
    private StyleProfileServiceImpl styleService;

    // ── 检索 ──────────────────────────────────────────────

    /** 空词不查：LIKE '%%' 会把全书章节连正文一起捞出来，那不是检索而是拖库 */
    @Test
    void blankQueryNeverTouchesTheDatabase() {
        SearchResultsView view = searchService.search(BOOK_ID, "   ", null, PageRequest.of(0, 20));

        assertTrue(view.getChapters().isEmpty());
        assertTrue(view.getCanon().isEmpty());
        assertTrue(view.getAliases().isEmpty());
        verifyNoInteractions(chapterMapper, canonMapper, aliasMapper);
    }

    /** 非法 scope 忽略而不是报错：勾选框多出一个旧前端不认识的值时，检索不该整块挂掉 */
    @Test
    void unknownScopesAreIgnored() {
        givenChapters();
        SearchResultsView view = searchService.search(BOOK_ID, "渡口", List.of("es", "chapter", "CANON?" , " "),
                PageRequest.of(0, 20));

        assertEquals(List.of("chapter"), view.getScopes());
        verifyNoInteractions(canonMapper, aliasMapper);
    }

    @Test
    void chapterHitCarriesAnExcerptAroundTheMatch() {
        givenChapters();
        SearchResultsView view = searchService.search(BOOK_ID, "眼睛", List.of("chapter"), PageRequest.of(0, 20));

        assertEquals(1, view.getChapters().size());
        SearchResultsView.ChapterHit hit = view.getChapters().get(0);
        assertEquals(5, hit.getChapterIndex().intValue());
        assertEquals(7L, hit.getChapterId().longValue());
        assertTrue(hit.getExcerpt().contains("眼睛"), hit.getExcerpt());
        // 摘出来是贴着一行显示的，正文里的换行必须被压掉
        assertFalse(hit.getExcerpt().contains("\n"), hit.getExcerpt());
        assertEquals(7, view.getChapterTotal());
    }

    /**
     * 别名展开：查到称谓后按实体键再捞一遍 subject_key。
     *
     * <p>命中的那条断言四列文本里并没有查询词，所以 {@code matchedViaAlias} 必须为真——
     * 否则作者会以为「阿青」这个词写在设定里，而它其实只在正文被叫过。
     */
    @Test
    void aliasQueryExpandsIntoEntityKeys() {
        when(aliasMapper.selectList(any())).thenReturn(List.of(alias("阿青", "char:qing")));
        when(aliasMapper.selectPage(any(), any())).thenAnswer(invocation -> {
            Page<Alias> page = invocation.getArgument(0);
            page.setRecords(List.of(alias("阿青", "char:qing")));
            page.setTotal(1);
            return page;
        });
        when(canonMapper.selectPage(any(), any())).thenAnswer(invocation -> {
            Page<CanonEntry> page = invocation.getArgument(0);
            page.setRecords(List.of(assertion(900L, "char:qing", "is_alive", "已死于第 4 章")));
            page.setTotal(1);
            return page;
        });

        SearchResultsView view = searchService.search(BOOK_ID, "阿青", List.of("canon", "alias"),
                PageRequest.of(0, 20));

        assertEquals(List.of("char:qing"), view.getExpandedEntityKeys());
        assertEquals(1, view.getCanon().size());
        assertTrue(view.getCanon().get(0).isMatchedViaAlias());
        assertEquals(1, view.getAliases().size());
        verifyNoInteractions(chapterMapper);
    }

    @Test
    void textHitIsNotMarkedAsAliasMatched() {
        when(aliasMapper.selectList(any())).thenReturn(List.of());
        when(canonMapper.selectPage(any(), any())).thenAnswer(invocation -> {
            Page<CanonEntry> page = invocation.getArgument(0);
            page.setRecords(List.of(assertion(901L, "char:shen", "eye_color", "灰蓝色")));
            page.setTotal(1);
            return page;
        });

        SearchResultsView view = searchService.search(BOOK_ID, "灰蓝色", List.of("canon"), PageRequest.of(0, 20));

        assertFalse(view.getCanon().get(0).isMatchedViaAlias());
    }

    @Test
    void wildcardCharactersInTheQueryAreNotWildcards() {
        assertEquals("100\\%\\_a\\\\b", NovelSearchServiceImpl.likeValue("100%_a\\b"));
        assertEquals("渡口", NovelSearchServiceImpl.likeValue("渡口"));
    }

    @Test
    void excerptFallsBackToTheHeadWhenJavaCannotFindTheMatch() {
        // 库层的 LIKE 会折叠全半角与空白，正文里是「渡　口」（中间一个全角空格）也算命中；
        // Java 侧找不到时不能假装知道命中位置，退回段首并标明是节选
        String excerpt = NovelSearchServiceImpl.excerpt("渡　口的风把灯笼吹得倾斜，她站在石阶上等一条船回来。", "渡口");

        assertTrue(excerpt.startsWith("渡"), excerpt);
        assertTrue(excerpt.endsWith("…"), excerpt);
    }

    // ── 文风契约 ──────────────────────────────────────────

    /** 没定过契约的书读出 null，而不是错误也不是空契约：装配侧据此才该退回派生默认值 */
    @Test
    void absentContractReadsAsNull() {
        when(styleMapper.selectOne(any())).thenReturn(null);
        assertNull(styleService.get(BOOK_ID));
    }

    @Test
    void firstContractIsInserted() {
        when(styleMapper.selectOne(any())).thenReturn(null);
        StyleProfileRequest req = new StyleProfileRequest();
        req.setPerson("第三人称限知");
        req.setChapterWordsMin(2200);
        req.setChapterWordsMax(3200);
        req.setForbiddenWords(List.of("破折号", "  ", "突然", "破折号"));

        StyleProfileView view = styleService.update(BOOK_ID, req);

        ArgumentCaptor<StyleProfile> captor = ArgumentCaptor.forClass(StyleProfile.class);
        verify(styleMapper).insert(captor.capture());
        verify(styleMapper, never()).updateById(any(StyleProfile.class));
        // 去空白、去重后落成合法 JSON 文本，非法输入进不了 MySQL
        assertEquals("[\"破折号\",\"突然\"]", captor.getValue().getForbiddenWords());
        assertEquals(2200, view.getChapterWordsMin().intValue());
        assertEquals(List.of("破折号", "突然"), view.getForbiddenWords());
    }

    /** 「这次没提」保留原值，「提了空数组」才清空——否则收紧一项契约会顺手抹掉其余几项 */
    @Test
    void omittedFieldsAreKeptAndEmptyListClears() {
        givenRow();
        StyleProfileRequest req = new StyleProfileRequest();
        req.setTense("过去完成时");
        req.setForbiddenWords(List.of());

        StyleProfileView view = styleService.update(BOOK_ID, req);

        ArgumentCaptor<StyleProfile> captor = ArgumentCaptor.forClass(StyleProfile.class);
        verify(styleMapper).updateById(captor.capture());
        StyleProfile row = captor.getValue();
        assertEquals("第三人称限知", row.getPerson());
        assertEquals("过去完成时", row.getTense());
        assertEquals(2200, row.getChapterWordsMin().intValue());
        assertEquals("[]", row.getForbiddenWords());
        assertTrue(view.getForbiddenWords().isEmpty());
    }

    @Test
    void reversedBandIsRejectedBeforeAnyWrite() {
        StyleProfileRequest req = new StyleProfileRequest();
        req.setChapterWordsMin(3200);
        req.setChapterWordsMax(2200);

        RuntimeException error = assertThrows(RuntimeException.class, () -> styleService.update(BOOK_ID, req));

        assertTrue(error.getMessage().contains("下限不能大于上限"), error.getMessage());
        verifyNoInteractions(styleMapper);
    }

    /** 库里已有非法词表时不炸整条读路径：契约的其余字段仍然有效，缺的那项按无词表处理 */
    @Test
    void corruptWordListDegradesToEmpty() {
        StyleProfile row = new StyleProfile();
        row.setBookId(BOOK_ID);
        row.setPerson("第三人称限知");
        row.setForbiddenWords("{\"a\":1}");
        when(styleMapper.selectOne(any())).thenReturn(row);

        StyleProfileView view = styleService.get(BOOK_ID);

        assertEquals("第三人称限知", view.getPerson());
        assertTrue(view.getForbiddenWords().isEmpty());
        assertTrue(view.getTics().isEmpty());
    }

    // ── 夹具 ──────────────────────────────────────────────

    private void givenChapters() {
        when(chapterMapper.selectPage(any(), any())).thenAnswer(invocation -> {
            Page<BookChapter> page = invocation.getArgument(0);
            BookChapter chapter = new BookChapter();
            chapter.setId(7L);
            chapter.setBookId(BOOK_ID);
            chapter.setChapterIndex(5);
            chapter.setTitle("渡口");
            chapter.setContent(CONTENT);
            chapter.setStatus("committed");
            chapter.setRevision(2);
            page.setRecords(List.of(chapter));
            page.setTotal(7);
            return page;
        });
    }

    private void givenRow() {
        StyleProfile row = new StyleProfile();
        row.setId(3L);
        row.setBookId(BOOK_ID);
        row.setPerson("第三人称限知");
        row.setTense("过去时");
        row.setChapterWordsMin(2200);
        row.setChapterWordsMax(3200);
        row.setForbiddenWords("[\"突然\"]");
        when(styleMapper.selectOne(any())).thenReturn(row);
    }

    private static Alias alias(String text, String entityKey) {
        Alias row = new Alias();
        row.setId(11L);
        row.setBookId(BOOK_ID);
        row.setAliasText(text);
        row.setEntityKey(entityKey);
        row.setIsPrimary(false);
        return row;
    }

    private static CanonEntry assertion(Long id, String subjectKey, String predicate, String objectText) {
        CanonEntry entry = new CanonEntry();
        entry.setId(id);
        entry.setBookId(BOOK_ID);
        entry.setKind("character");
        entry.setSubjectKey(subjectKey);
        entry.setPredicate(predicate);
        entry.setObjectText(objectText);
        entry.setAuthority("author");
        entry.setStatus("confirmed");
        entry.setValidFromChapter(4);
        return entry;
    }
}
