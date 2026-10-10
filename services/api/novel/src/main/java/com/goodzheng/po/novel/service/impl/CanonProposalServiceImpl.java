package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.goodzheng.po.novel.dto.CanonRequest;
import com.goodzheng.po.novel.dto.ProposalDecisionRequest;
import com.goodzheng.po.novel.dto.ProposalDecisionView;
import com.goodzheng.po.novel.dto.ProposalRequest;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.CanonProposal;
import com.goodzheng.po.novel.repository.BookMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.CanonProposalMapper;
import com.goodzheng.po.novel.service.CanonProposalService;
import com.goodzheng.po.novel.service.NovelStudioService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 提议卡队列与采纳事务。
 *
 * <p>与 Finding 裁定共用 {@link NovelStudioService#previewConflicts} 而不是自带一份冲突查询：
 * 「同主同谓、已确认、as-of 可见、值不同」这一条口径若分叉，作者在工作台上看到的冲突预览
 * 和采纳时实际被覆盖的断言就不是同一批，二次确认当场失去意义。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CanonProposalServiceImpl implements CanonProposalService {

    private static final String PENDING = "pending";
    private static final String ADOPTED = "adopted";
    private static final String DISMISSED = "dismissed";

    private static final BigDecimal AUTHOR_CONFIDENCE = new BigDecimal("1.00");

    private final CanonProposalMapper proposalMapper;
    private final CanonEntryMapper canonMapper;
    private final BookMapper bookMapper;
    private final NovelStudioService studioService;

    @Override
    @Transactional(readOnly = true)
    public Page<CanonProposal> page(Long bookId, String status, Pageable pageable) {
        String wanted = blankToNull(status);
        if (wanted != null && !Set.of(PENDING, ADOPTED, DISMISSED, "expired").contains(wanted)) {
            throw new RuntimeException("非法的提议卡状态：" + status);
        }
        QueryWrapper<CanonProposal> wrapper = new QueryWrapper<CanonProposal>()
                .eq(bookId != null, "book_id", bookId)
                .eq(wanted != null, "status", wanted)
                // 新卡在最上面。不按 status 排：库里 pending/adopted/dismissed 的字典序
                // 是 adopted→dismissed→pending，待办的反而沉底；面板默认就带 status=pending
                .orderByDesc("id");
        var mpPage = MyBatisPages.<CanonProposal>toMpPage(pageable);
        proposalMapper.selectPage(mpPage, wrapper);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional
    public CanonProposal create(ProposalRequest req) {
        if (req.getBookId() == null) {
            throw new RuntimeException("缺少必填字段：bookId");
        }
        if (bookMapper.selectById(req.getBookId()) == null) {
            // bookId 来自请求体而不是路径，不验就会造出一张挂在不存在的书上的卡，
            // 它永远不会被任何工作台面读到
            throw new RuntimeException("书籍不存在：" + req.getBookId());
        }
        requireText(req.getKind(), "kind");
        requireText(req.getSubjectKey(), "subjectKey");
        requireText(req.getPredicate(), "predicate");
        requireText(req.getObjectText(), "objectText");

        CanonProposal row = new CanonProposal();
        row.setBookId(req.getBookId());
        row.setSessionId(clip(req.getSessionId(), 64));
        row.setAsOfChapter(req.getAsOfChapter());
        row.setKind(clip(req.getKind(), 24));
        row.setSubjectKey(clip(req.getSubjectKey(), 128));
        row.setPredicate(clip(req.getPredicate(), 64));
        row.setObjectText(clip(req.getObjectText(), 512));
        row.setValidFromChapter(req.getValidFromChapter());
        row.setBasisQuote(clip(req.getBasisQuote(), 512));
        row.setStatus(PENDING);
        proposalMapper.insert(row);
        return row;
    }

    @Override
    @Transactional
    public ProposalDecisionView adopt(Long proposalId, ProposalDecisionRequest req, Long userId) {
        CanonProposal proposal = pendingOf(proposalId);
        ProposalDecisionView view = new ProposalDecisionView();
        view.setProposalId(proposalId);

        Integer asOf = proposal.getAsOfChapter() != null
                ? proposal.getAsOfChapter() : proposal.getValidFromChapter();
        List<CanonEntry> conflicts = conflictsOf(proposal, asOf);
        Set<Long> conflictIds = conflicts.stream().map(CanonEntry::getId).collect(Collectors.toSet());
        view.setConflictIds(conflicts.stream().map(CanonEntry::getId).toList());

        List<Long> requested = req == null || req.getCloseAssertionIds() == null
                ? List.of()
                : req.getCloseAssertionIds().stream().filter(Objects::nonNull).toList();
        if (!conflicts.isEmpty() && requested.isEmpty()) {
            throw new RuntimeException("这张卡与 " + conflicts.size() + " 条既有断言冲突（"
                    + view.getConflictIds() + "），采纳必须显式指定要覆盖哪几条");
        }

        Integer from = proposal.getValidFromChapter() != null ? proposal.getValidFromChapter()
                : (asOf != null ? asOf : studioService.currentChapterIndex(proposal.getBookId()));
        if (!requested.isEmpty() && from == null) {
            // 没有章坐标就闭不了区间：此刻落库会留下两条互相矛盾且都「至今有效」的 author 断言，
            // 而那正是这张卡想解决的东西
            throw new RuntimeException("本书还没有任何章，提议卡必须带 asOfChapter 或 validFromChapter 才能覆盖旧断言");
        }

        List<CanonEntry> toClose = new ArrayList<>();
        for (Long id : requested) {
            if (!conflictIds.contains(id)) {
                throw new RuntimeException("断言 " + id + " 不是这张卡的冲突项，提议卡无权关闭它");
            }
            CanonEntry old = canonMapper.selectById(id);
            if (old == null) {
                throw new RuntimeException("要闭区间的断言不存在：" + id);
            }
            if (!old.getBookId().equals(proposal.getBookId())) {
                throw new RuntimeException("断言 " + id + " 不属于本书，拒绝跨书闭区间");
            }
            if (old.getValidUntilChapter() == null) {
                toClose.add(old);
            }
        }

        for (CanonEntry old : toClose) {
            old.setValidUntilChapter(from);
            canonMapper.updateById(old);
            view.getClosedAssertionIds().add(old.getId());
        }
        CanonEntry entry = toEntry(proposal, req, userId, from);
        if (toClose.size() == 1) {
            entry.setSupersedesId(toClose.get(0).getId());
        }
        canonMapper.insert(entry);
        view.setEntryId(entry.getId());

        proposal.setStatus(ADOPTED);
        proposal.setAdoptedEntryId(entry.getId());
        proposal.setDecidedBy(userId);
        proposal.setDecidedAt(LocalDateTime.now());
        proposal.setDecidedBasis(clip(req == null ? null : req.getBasis(), 512));
        proposalMapper.updateById(proposal);
        view.setStatus(ADOPTED);
        log.info("提议卡 {} 由作者 {} 采纳为断言 {}（覆盖 {} 条）",
                proposalId, userId, entry.getId(), view.getClosedAssertionIds());
        return view;
    }

    @Override
    @Transactional
    public ProposalDecisionView dismiss(Long proposalId, ProposalDecisionRequest req, Long userId) {
        CanonProposal proposal = pendingOf(proposalId);
        String basis = blankToNull(req == null ? null : req.getBasis());
        if (basis == null) {
            throw new RuntimeException("驳回提议卡必须写依据");
        }
        ProposalDecisionView view = new ProposalDecisionView();
        view.setProposalId(proposalId);
        view.setStatus(DISMISSED);
        proposal.setStatus(DISMISSED);
        proposal.setDecidedBy(userId);
        proposal.setDecidedAt(LocalDateTime.now());
        proposal.setDecidedBasis(clip(basis, 512));
        proposalMapper.updateById(proposal);
        return view;
    }

    /**
     * 撞车预览：与既有断言同主同谓、{@code confirmed}、as-of 可见而值不同。
     *
     * <p>复用 Finding 裁定那条冲突口径（{@link NovelStudioService#previewConflicts}），
     * 纯比对、不调模型。
     */
    private List<CanonEntry> conflictsOf(CanonProposal proposal, Integer asOf) {
        CanonRequest probe = new CanonRequest();
        probe.setSubjectKey(proposal.getSubjectKey());
        probe.setPredicate(proposal.getPredicate());
        probe.setObjectText(proposal.getObjectText());
        return studioService.previewConflicts(proposal.getBookId(), probe, asOf);
    }

    private CanonEntry toEntry(CanonProposal proposal, ProposalDecisionRequest req, Long userId, Integer from) {
        CanonEntry entry = new CanonEntry();
        entry.setBookId(proposal.getBookId());
        entry.setKind(proposal.getKind());
        entry.setSubjectKey(proposal.getSubjectKey());
        entry.setPredicate(proposal.getPredicate());
        entry.setObjectText(proposal.getObjectText());
        entry.setRestatement(clip(orDefault(req == null ? null : req.getRestatement(), proposal.getObjectText()), 512));
        // 采纳即裁定：这一条的权威级是 author，且置信度钉死 1.00（§10.5-②）
        entry.setAuthority("author");
        entry.setConfidence(AUTHOR_CONFIDENCE);
        entry.setEstablishedChapter(from);
        entry.setValidFromChapter(from == null ? 0 : from);
        entry.setStatus("confirmed");
        entry.setDecidedBy(userId);
        entry.setDecidedAt(LocalDateTime.now());
        return entry;
    }

    private CanonProposal pendingOf(Long proposalId) {
        CanonProposal proposal = proposalMapper.selectById(proposalId);
        if (proposal == null) {
            throw new RuntimeException("提议卡不存在：" + proposalId);
        }
        if (!PENDING.equals(proposal.getStatus())) {
            throw new RuntimeException("这张卡已处理为 " + proposal.getStatus() + "，不重复裁定");
        }
        return proposal;
    }

    private static String requireText(String value, String field) {
        if (value == null || value.isBlank()) {
            throw new RuntimeException("缺少必填字段：" + field);
        }
        return value;
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }

    private static String orDefault(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private static String clip(String value, int limit) {
        if (value == null) {
            return null;
        }
        return value.length() <= limit ? value : value.substring(0, limit);
    }
}
