package com.goodzheng.po.novel.service.impl;

import com.goodzheng.po.novel.dto.ProposalDecisionRequest;
import com.goodzheng.po.novel.dto.ProposalDecisionView;
import com.goodzheng.po.novel.dto.ProposalRequest;
import com.goodzheng.po.novel.entity.Book;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.CanonProposal;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.CanonProposalMapper;
import com.goodzheng.po.novel.service.NovelStudioService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.beans.BeanUtils;
import org.springframework.data.domain.PageRequest;

import java.beans.PropertyDescriptor;
import java.math.BigDecimal;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.isNull;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * §10.3 约定 1/3 与 §10.5-④ 的 Java 侧落点：提议卡唯一能变成的东西是一条 author 断言，
 * 而变成之前必须让作者看见它撞了谁。
 *
 * <p>这里用纯 Mockito：要验的是「撞车时不显式指定覆盖项就一次写库都不发生」，
 * 这是赋值次序与校验前件的问题，起容器只会把它稀释成「集成测试没报错」。
 */
@ExtendWith(MockitoExtension.class)
class CanonProposalAdoptionTest {

    private static final Long BOOK_ID = 1L;
    private static final Long PROPOSAL_ID = 77L;
    private static final Long USER_ID = 42L;

    @Mock
    private CanonProposalMapper proposalMapper;
    @Mock
    private CanonEntryMapper canonMapper;
    @Mock
    private BookMapper bookMapper;
    @Mock
    private NovelStudioService studioService;

    @InjectMocks
    private CanonProposalServiceImpl proposalService;

    // ── 入库 ──────────────────────────────────────────────

    /**
     * 入参 DTO 必须<b>没有</b> status 与 authority：卡片能变成的只有断言，而断言的权威级
     * 由服务端判定（§10.5-②）。字段不存在比「传了会被忽略」更硬。
     */
    @Test
    void proposalRequestCarriesNeitherStatusNorAuthority() {
        Set<String> props = writableProps(ProposalRequest.class);
        assertTrue(!props.contains("status"), "提议卡入参不得接受 status：初始状态由服务端写死");
        assertTrue(!props.contains("authority"), "提议卡连一条断言都还不是，不该能带权威级");
    }

    @Test
    void newCardIsForcedToPending() {
        when(bookMapper.selectById(BOOK_ID)).thenReturn(new Book());
        proposalService.create(request("她的眼睛是灰蓝色"));

        ArgumentCaptor<CanonProposal> captor = ArgumentCaptor.forClass(CanonProposal.class);
        verify(proposalMapper).insert(captor.capture());
        CanonProposal row = captor.getValue();
        assertEquals("pending", row.getStatus());
        assertEquals(BOOK_ID, row.getBookId());
        assertEquals("char:shen", row.getSubjectKey());
        assertEquals("她的眼睛是灰蓝色", row.getObjectText());
    }

    /** bookId 这次来自请求体而不是路径，不验就会造出一张任何工作台都读不到的卡 */
    @Test
    void cardForUnknownBookIsRejected() {
        when(bookMapper.selectById(999L)).thenReturn(null);
        ProposalRequest req = request("她的眼睛是灰蓝色");
        req.setBookId(999L);

        assertThrows(RuntimeException.class, () -> proposalService.create(req));
        verify(proposalMapper, never()).insert(any(CanonProposal.class));
    }

    @Test
    void illegalStatusFilterIsRejectedBeforeAnyQuery() {
        assertThrows(RuntimeException.class,
                () -> proposalService.page(BOOK_ID, "adopted?", PageRequest.of(0, 20)));
        verify(proposalMapper, never()).selectPage(any(), any());
    }

    // ── 采纳 ──────────────────────────────────────────────

    @Test
    void adoptWritesAnAuthorAssertionAndClosesTheCollidingOne() {
        givenCard(card(3, 3));
        CanonEntry old = existing(500L, "她的眼睛是蓝色");
        givenConflicts(old);
        when(canonMapper.selectById(500L)).thenReturn(old);

        ProposalDecisionView view = proposalService.adopt(PROPOSAL_ID, close(List.of(500L)), USER_ID);

        ArgumentCaptor<CanonEntry> inserted = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).insert(inserted.capture());
        CanonEntry entry = inserted.getValue();
        assertEquals("author", entry.getAuthority());
        assertEquals(0, new BigDecimal("1.00").compareTo(entry.getConfidence()));
        assertEquals("confirmed", entry.getStatus());
        // 章号坐标取卡片自带的 valid_from：作者是就着第 3 章说「事情是这样的」
        assertEquals(3, entry.getValidFromChapter().intValue());
        assertEquals(3, entry.getEstablishedChapter().intValue());
        assertEquals(500L, entry.getSupersedesId().longValue());
        assertEquals(USER_ID, entry.getDecidedBy());
        assertEquals("她的眼睛是灰蓝色", entry.getRestatement());

        ArgumentCaptor<CanonEntry> closed = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).updateById(closed.capture());
        assertEquals(3, closed.getValue().getValidUntilChapter().intValue());

        ArgumentCaptor<CanonProposal> decided = ArgumentCaptor.forClass(CanonProposal.class);
        verify(proposalMapper).updateById(decided.capture());
        assertEquals("adopted", decided.getValue().getStatus());
        assertEquals(USER_ID, decided.getValue().getDecidedBy());

        assertEquals(List.of(500L), view.getConflictIds());
        assertEquals(List.of(500L), view.getClosedAssertionIds());
        assertEquals("adopted", view.getStatus());
    }

    /** 撞车而不指定覆盖项就不许落库：「作者已确认」不能靠前端自觉（§10.6） */
    @Test
    void adoptWithoutExplicitOverrideWritesNothing() {
        givenCard(card(3, 3));
        givenConflicts(existing(500L, "她的眼睛是蓝色"));

        RuntimeException error = assertThrows(RuntimeException.class,
                () -> proposalService.adopt(PROPOSAL_ID, close(List.of()), USER_ID));

        assertTrue(error.getMessage().contains("冲突"), error.getMessage());
        assertNoCanonWrite();
        verify(proposalMapper, never()).updateById(any(CanonProposal.class));
    }

    /** 一张卡不该有权闭掉与它无关的断言，否则采纳动作变成了任意删除入口 */
    @Test
    void adoptRefusesToCloseAnAssertionThatDidNotCollide() {
        givenCard(card(3, 3));
        givenConflicts(existing(500L, "她的眼睛是蓝色"));

        RuntimeException error = assertThrows(RuntimeException.class,
                () -> proposalService.adopt(PROPOSAL_ID, close(List.of(611L)), USER_ID));

        assertTrue(error.getMessage().contains("冲突项"), error.getMessage());
        assertNoCanonWrite();
    }

    @Test
    void closingWithoutAChapterCoordinateIsRefused() {
        givenCard(card(null, null));
        when(studioService.currentChapterIndex(BOOK_ID)).thenReturn(null);
        givenConflicts(existing(500L, "她的眼睛是蓝色"));

        RuntimeException error = assertThrows(RuntimeException.class,
                () -> proposalService.adopt(PROPOSAL_ID, close(List.of(500L)), USER_ID));

        assertTrue(error.getMessage().contains("还没有任何章"), error.getMessage());
        assertNoCanonWrite();
    }

    /** 没撞车的卡直接落库：不让作者多点一次确认（与 N5b 的冲突预览同一取舍） */
    @Test
    void cleanCardAdoptsWithoutConfirmation() {
        givenCard(card(null, 5));
        givenConflicts();

        ProposalDecisionView view = proposalService.adopt(PROPOSAL_ID, close(List.of()), USER_ID);

        ArgumentCaptor<CanonEntry> inserted = ArgumentCaptor.forClass(CanonEntry.class);
        verify(canonMapper).insert(inserted.capture());
        assertEquals(5, inserted.getValue().getValidFromChapter().intValue());
        assertNull(inserted.getValue().getSupersedesId());
        assertTrue(view.getConflictIds().isEmpty());
        verify(canonMapper, never()).updateById(any(CanonEntry.class));
    }

    @Test
    void handledCardIsNotReadjudicated() {
        CanonProposal done = card(3, 3);
        done.setStatus("adopted");
        givenCard(done);

        assertThrows(RuntimeException.class,
                () -> proposalService.adopt(PROPOSAL_ID, close(List.of()), USER_ID));
        assertThrows(RuntimeException.class,
                () -> proposalService.dismiss(PROPOSAL_ID, close(List.of()), USER_ID));
        assertNoCanonWrite();
    }

    // ── 驳回 ──────────────────────────────────────────────

    /** 驳回必须留依据：卡片内容还留着，「为什么不要它」不写就没有下一次 */
    @Test
    void dismissRequiresABasis() {
        givenCard(card(3, 3));

        ProposalDecisionRequest req = new ProposalDecisionRequest();
        assertThrows(RuntimeException.class, () -> proposalService.dismiss(PROPOSAL_ID, req, USER_ID));
        assertThrows(RuntimeException.class, () -> proposalService.dismiss(PROPOSAL_ID, null, USER_ID));
        verify(proposalMapper, never()).updateById(any(CanonProposal.class));
    }

    @Test
    void dismissKeepsTheReasonAndTouchesNoCanon() {
        givenCard(card(3, 3));
        ProposalDecisionRequest req = new ProposalDecisionRequest();
        req.setBasis("这条与第 1 章的开场矛盾，不改开场");

        ProposalDecisionView view = proposalService.dismiss(PROPOSAL_ID, req, USER_ID);

        ArgumentCaptor<CanonProposal> captor = ArgumentCaptor.forClass(CanonProposal.class);
        verify(proposalMapper).updateById(captor.capture());
        assertEquals("dismissed", captor.getValue().getStatus());
        assertEquals("这条与第 1 章的开场矛盾，不改开场", captor.getValue().getDecidedBasis());
        assertEquals("dismissed", view.getStatus());
        assertNoCanonWrite();
    }

    // ── 文风契约见 StyleProfileAndSearchTest ───────────────

    private static Set<String> writableProps(Class<?> type) {
        return java.util.Arrays.stream(BeanUtils.getPropertyDescriptors(type))
                .filter(pd -> pd.getWriteMethod() != null)
                .map(PropertyDescriptor::getName)
                .collect(Collectors.toSet());
    }

    private void givenCard(CanonProposal proposal) {
        when(proposalMapper.selectById(PROPOSAL_ID)).thenReturn(proposal);
    }

    private void givenConflicts(CanonEntry... conflicts) {
        // 提议卡不是既有断言，冲突口径里必须不带 excludeId——带了就等于允许它排除掉一条撞车
        when(studioService.previewConflicts(eq(BOOK_ID), any(), any(), isNull()))
                .thenReturn(List.of(conflicts));
    }

    private void assertNoCanonWrite() {
        verify(canonMapper, never()).insert(any(CanonEntry.class));
        verify(canonMapper, never()).updateById(any(CanonEntry.class));
    }

    private static ProposalRequest request(String objectText) {
        ProposalRequest req = new ProposalRequest();
        req.setBookId(BOOK_ID);
        req.setSessionId("conv-9");
        req.setAsOfChapter(3);
        req.setKind("character");
        req.setSubjectKey("char:shen");
        req.setPredicate("eye_color");
        req.setObjectText(objectText);
        req.setBasisQuote("她抬眼，灰蓝色在灯下亮了一下");
        return req;
    }

    private static ProposalDecisionRequest close(List<Long> ids) {
        ProposalDecisionRequest req = new ProposalDecisionRequest();
        req.setCloseAssertionIds(ids);
        return req;
    }

    private static CanonProposal card(Integer asOf, Integer validFrom) {
        CanonProposal row = new CanonProposal();
        row.setId(PROPOSAL_ID);
        row.setBookId(BOOK_ID);
        row.setStatus("pending");
        row.setAsOfChapter(asOf);
        row.setValidFromChapter(validFrom);
        row.setKind("character");
        row.setSubjectKey("char:shen");
        row.setPredicate("eye_color");
        row.setObjectText("她的眼睛是灰蓝色");
        return row;
    }

    private static CanonEntry existing(Long id, String objectText) {
        CanonEntry entry = new CanonEntry();
        entry.setId(id);
        entry.setBookId(BOOK_ID);
        entry.setSubjectKey("char:shen");
        entry.setPredicate("eye_color");
        entry.setObjectText(objectText);
        entry.setAuthority("text");
        entry.setStatus("confirmed");
        return entry;
    }
}
