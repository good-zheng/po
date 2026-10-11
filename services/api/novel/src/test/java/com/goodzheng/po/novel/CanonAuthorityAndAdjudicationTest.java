package com.goodzheng.po.novel;

import com.goodzheng.po.novel.dto.CanonRequest;
import com.goodzheng.po.novel.dto.FindingAdjudicationRequest;
import com.goodzheng.po.novel.dto.InternalAssertionAppendRequest;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.ReviewFinding;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.CharacterStateMapper;
import com.goodzheng.po.novel.repository.ChapterSummaryMapper;
import com.goodzheng.po.novel.repository.ForeshadowMapper;
import com.goodzheng.po.novel.repository.GenJobMapper;
import com.goodzheng.po.novel.repository.ReviewFindingMapper;
import com.goodzheng.po.novel.service.impl.CanonTxWriter;
import com.goodzheng.po.novel.service.impl.NovelStudioServiceImpl;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.BeanUtils;

import java.beans.PropertyDescriptor;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * §12.4 的 {@code test_authority_is_server_decided} 与裁定事务的 Java 侧落点。
 *
 * <p>这里用纯 Mockito 而不是起容器：要验的是「authority 在契约层就不可能被调用方设定」，
 * 这件事全部发生在 DTO 字段与 Service 赋值里，起一次 Spring 上下文反而把断言稀释成
 * 「集成测试没报错」。真实的回滚由 {@code @Transactional} 保证，本测试退一步验它的前件：
 * 校验不过时一次写库都不许发生。
 */
@ExtendWith(MockitoExtension.class)
class CanonAuthorityAndAdjudicationTest {

    @Mock
    private CanonEntryMapper canonMapper;
    @Mock
    private AliasMapper aliasMapper;
    @Mock
    private ForeshadowMapper foreshadowMapper;
    @Mock
    private ReviewFindingMapper findingMapper;
    @Mock
    private GenJobMapper jobMapper;
    @Mock
    private BookChapterMapper chapterMapper;
    @Mock
    private CharacterStateMapper stateMapper;
    @Mock
    private ChapterSummaryMapper summaryMapper;

    @InjectMocks
    private NovelStudioServiceImpl studioService;

    @InjectMocks
    private CanonTxWriter txWriter;

    // ── authority 由服务端判定 ────────────────────────────

    /**
     * 两个入参 DTO 都必须<b>没有</b> authority 属性：字段不存在比「传了会被忽略」更硬，
     * 后者只要有人手滑加个 setter 就整条防线消失（§10.5-②）。
     */
    @Test
    void requestDtosHaveNoAuthorityField() {
        Set<String> canonProps = writableProps(CanonRequest.class);
        assertTrue(!canonProps.contains("authority"), "管理端正典入参不得接受 authority");

        Set<String> internalProps = writableProps(InternalAssertionAppendRequest.AssertionItem.class);
        assertTrue(!internalProps.contains("authority"), "内部通道入参不得接受 authority");
    }

    @Test
    void manualCanonCreationIsWrittenAsAuthorAuthority() {
        when(chapterMapper.selectObjs(any())).thenReturn(List.of(7));

        CanonEntry saved = studioService.createCanon(1L, canonRequest("她的眼睛是灰蓝色"), 42L);

        ArgumentCaptor<CanonEntry> captor = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).insert(captor.capture());
        assertEquals("author", captor.getValue().getAuthority());
        assertEquals("1.00", captor.getValue().getConfidence().toPlainString());
        assertEquals(7, captor.getValue().getEstablishedChapter().intValue());
        assertEquals(7, captor.getValue().getValidFromChapter().intValue());
        assertEquals(42L, captor.getValue().getDecidedBy().longValue());
        assertEquals("author", saved.getAuthority());
    }

    /** 手改即裁定：作者动过的模型断言升级为 author，否则下一轮抽取会按模型置信度再覆盖一次 */
    @Test
    void editingAModelAssertionPromotesItToAuthor() {
        CanonEntry existing = modelEntry(9L);
        when(canonMapper.selectById(9L)).thenReturn(existing);

        studioService.updateCanon(9L, canonRequest("她的眼睛是灰蓝色"), 42L);

        ArgumentCaptor<CanonEntry> captor = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).updateById(captor.capture());
        assertEquals("author", captor.getValue().getAuthority());
        assertEquals(42L, captor.getValue().getDecidedBy().longValue());
        assertEquals("她的眼睛是灰蓝色", captor.getValue().getObjectText());
    }

    /** 同一条断言走内部通道仍然是 model：两条写路径不共用方法，也就不可能共用权威级 */
    @Test
    void internalChannelStillWritesModelAuthority() {
        InternalAssertionAppendRequest req = new InternalAssertionAppendRequest();
        req.setBookId(1L);
        req.setAsOfChapter(3);
        InternalAssertionAppendRequest.AssertionItem item = new InternalAssertionAppendRequest.AssertionItem();
        item.setKind("character");
        item.setSubjectKey("char:shen");
        item.setPredicate("eye_color");
        item.setObjectText("蓝色");
        req.getAssertions().add(item);

        txWriter.persistAppend(req);

        ArgumentCaptor<CanonEntry> captor = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).insert(captor.capture());
        assertEquals("model", captor.getValue().getAuthority());
    }

    // ── 裁定事务 ──────────────────────────────────────────

    @Test
    void adoptWritesAuthorAssertionClosesOldRangeAndClosesFinding() {
        ReviewFinding finding = openFinding(100L, "[9]");
        when(findingMapper.selectById(100L)).thenReturn(finding);
        when(chapterMapper.selectById(10L)).thenReturn(chapter(10L, 5));
        CanonEntry violated = modelEntry(9L);
        when(canonMapper.selectById(9L)).thenReturn(violated);

        FindingAdjudicationRequest req = new FindingAdjudicationRequest();
        req.setAction("adopt");
        req.setBasis("作者设定：瞳色为灰蓝");
        req.setAssertion(canonRequest("她的眼睛是灰蓝色"));

        var view = studioService.adjudicate(100L, req, 42L);

        ArgumentCaptor<CanonEntry> inserted = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).insert(inserted.capture());
        assertEquals("author", inserted.getValue().getAuthority());
        assertEquals(5, inserted.getValue().getEstablishedChapter().intValue());
        assertEquals(9L, inserted.getValue().getSupersedesId().longValue());
        assertEquals(5, violated.getValidUntilChapter().intValue());
        assertEquals(List.of(9L), view.getClosedAssertionIds());

        ArgumentCaptor<ReviewFinding> decided = ArgumentCaptor.forClass(ReviewFinding.class);
        verify(findingMapper).updateById(decided.capture());
        assertEquals("adopted", decided.getValue().getStatus());
        assertEquals(42L, decided.getValue().getDecidedBy());
        assertEquals("作者设定：瞳色为灰蓝", decided.getValue().getBasis());
    }

    /** 被违反的断言查不到时，一次写库都不许发生（事务回滚的前件） */
    @Test
    void adoptWithMissingAssertionWritesNothing() {
        ReviewFinding finding = openFinding(100L, "[9]");
        when(findingMapper.selectById(100L)).thenReturn(finding);
        when(chapterMapper.selectById(10L)).thenReturn(chapter(10L, 5));
        when(canonMapper.selectById(9L)).thenReturn(null);

        FindingAdjudicationRequest req = new FindingAdjudicationRequest();
        req.setAction("adopt");
        req.setAssertion(canonRequest("她的眼睛是灰蓝色"));

        assertThrows(RuntimeException.class, () -> studioService.adjudicate(100L, req, 42L));
        verify(canonMapper, never()).insert(any(CanonEntry.class));
        verify(canonMapper, never()).updateById(any(CanonEntry.class));
        verify(findingMapper, never()).updateById(any(ReviewFinding.class));
    }

    @Test
    void alreadyAdjudicatedFindingCannotBeRuledAgain() {
        ReviewFinding finding = openFinding(100L, null);
        finding.setStatus("waived");
        when(findingMapper.selectById(100L)).thenReturn(finding);

        FindingAdjudicationRequest req = new FindingAdjudicationRequest();
        req.setAction("reject");
        req.setBasis("误报");

        assertThrows(RuntimeException.class, () -> studioService.adjudicate(100L, req, 42L));
        verify(findingMapper, never()).updateById(any(ReviewFinding.class));
    }

    /** 判误报与放行 blocker 不写依据就是给误判盖章，必须在 Service 层就拒掉 */
    @Test
    void rejectAndWaiveRequireABasis() {
        ReviewFinding finding = openFinding(100L, null);
        when(findingMapper.selectById(100L)).thenReturn(finding);

        for (String action : List.of("reject", "waive")) {
            FindingAdjudicationRequest req = new FindingAdjudicationRequest();
            req.setAction(action);
            assertThrows(RuntimeException.class, () -> studioService.adjudicate(100L, req, 42L), action);
        }
        verify(findingMapper, never()).updateById(any(ReviewFinding.class));
    }

    /** 改写正文：Finding 记 adopted，章节退回 draft，修补指令原样回带给生成链路 */
    @Test
    void rewriteSendsChapterBackToDraft() {
        ReviewFinding finding = openFinding(100L, null);
        finding.setFixInstruction("把渡口一段改冷，保留时间锚点");
        when(findingMapper.selectById(100L)).thenReturn(finding);
        when(chapterMapper.selectById(10L)).thenReturn(chapter(10L, 5));

        FindingAdjudicationRequest req = new FindingAdjudicationRequest();
        req.setAction("rewrite");

        var view = studioService.adjudicate(100L, req, 42L);

        assertTrue(view.isChapterBackToDraft());
        assertEquals("把渡口一段改冷，保留时间锚点", view.getFixInstruction());
        ArgumentCaptor<BookChapter> captor = ArgumentCaptor.forClass(BookChapter.class);
        verify(chapterMapper).updateById(captor.capture());
        assertEquals("draft", captor.getValue().getStatus());
        verify(canonMapper, never()).insert(any(CanonEntry.class));
    }

    // ── 单条读取与撞车预览 ────────────────────────────────

    /** 中栏按 id 取「被点中的那一条」：查不到要报出是哪个 id，作者才知道是台账里的旧引用 */
    @Test
    void canonLookupFailureNamesTheId() {
        when(canonMapper.selectById(9L)).thenReturn(null);

        RuntimeException error = assertThrows(RuntimeException.class, () -> studioService.canonById(9L));
        assertTrue(error.getMessage().contains("断言不存在：9"), error.getMessage());
    }

    /** 实体键或谓词没填就没有「同主同谓」可判，一次查询都不该发出去：发了等于把全书设定报成撞车 */
    @Test
    void previewWithoutSubjectOrPredicateSkipsTheQuery() {
        CanonRequest noSubject = canonRequest("灰蓝色");
        noSubject.setSubjectKey(" ");
        assertTrue(studioService.previewConflicts(1L, noSubject, 3, null).isEmpty());

        CanonRequest noPredicate = canonRequest("灰蓝色");
        noPredicate.setPredicate(null);
        assertTrue(studioService.previewConflicts(1L, noPredicate, 3, 9L).isEmpty());

        verify(canonMapper, never()).selectList(any());
    }

    // ── 夹具 ──────────────────────────────────────────────

    private static Set<String> writableProps(Class<?> type) {
        return java.util.Arrays.stream(BeanUtils.getPropertyDescriptors(type))
                .filter(pd -> pd.getWriteMethod() != null)
                .map(PropertyDescriptor::getName)
                .collect(Collectors.toSet());
    }

    private static CanonRequest canonRequest(String objectText) {
        CanonRequest req = new CanonRequest();
        req.setKind("character");
        req.setSubjectKey("char:shen");
        req.setPredicate("eye_color");
        req.setObjectText(objectText);
        return req;
    }

    private static CanonEntry modelEntry(Long id) {
        CanonEntry entry = new CanonEntry();
        entry.setId(id);
        entry.setBookId(1L);
        entry.setKind("character");
        entry.setSubjectKey("char:shen");
        entry.setPredicate("eye_color");
        entry.setObjectText("蓝色");
        entry.setAuthority("model");
        entry.setStatus("confirmed");
        entry.setValidFromChapter(2);
        return entry;
    }

    private static ReviewFinding openFinding(Long id, String canonRefs) {
        ReviewFinding finding = new ReviewFinding();
        finding.setId(id);
        finding.setBookId(1L);
        finding.setChapterId(10L);
        finding.setRevision(1);
        finding.setCode("C1_state_conflict");
        finding.setSeverity("blocker");
        finding.setChecker("rule");
        finding.setCanonRefs(canonRefs);
        finding.setStatus("open");
        return finding;
    }

    private static BookChapter chapter(Long id, Integer index) {
        BookChapter chapter = new BookChapter();
        chapter.setId(id);
        chapter.setBookId(1L);
        chapter.setChapterIndex(index);
        chapter.setStatus("committed");
        chapter.setRevision(1);
        return chapter;
    }
}
