package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.goodzheng.po.novel.dto.AliasRequest;
import com.goodzheng.po.novel.dto.CanonRequest;
import com.goodzheng.po.novel.dto.CanonRetireRequest;
import com.goodzheng.po.novel.dto.ChapterImpactView;
import com.goodzheng.po.novel.dto.ChapterRevisionView;
import com.goodzheng.po.novel.dto.FindingAdjudicationRequest;
import com.goodzheng.po.novel.dto.FindingAdjudicationView;
import com.goodzheng.po.novel.dto.FindingView;
import com.goodzheng.po.novel.dto.ForeshadowRequest;
import com.goodzheng.po.novel.dto.NovelProgressView;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.ChapterRevision;
import com.goodzheng.po.novel.entity.Foreshadow;
import com.goodzheng.po.novel.entity.GenJob;
import com.goodzheng.po.novel.entity.ReviewFinding;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.ChapterRevisionMapper;
import com.goodzheng.po.novel.repository.ForeshadowMapper;
import com.goodzheng.po.novel.repository.GenJobMapper;
import com.goodzheng.po.novel.repository.ReviewFindingMapper;
import com.goodzheng.po.novel.service.NovelStudioService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * 工作台管理端读写面。
 *
 * <p>本类的每一条写路径都把 {@code authority} 写死成 {@code author} 且从不读入参：
 * 管理端 JWT 是 author 级唯一的入口（§10.5-②），而内部通道另有 {@link CanonTxWriter}。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NovelStudioServiceImpl implements NovelStudioService {

    private static final String AUTHORITY_AUTHOR = "author";
    private static final BigDecimal AUTHOR_CONFIDENCE = new BigDecimal("1.00");
    private static final Set<String> CANON_STATUS = Set.of("confirmed", "disputed", "todo", "rejected");
    private static final Set<String> FORESHADOW_STATUS = Set.of("opened", "paid", "abandoned");
    private static final Set<String> ACTIONS = Set.of("adopt", "reject", "waive", "rewrite");

    /** 章节状态：改写正文后退回草稿，重过闸门才准重新 commit（§10.5-③） */
    private static final String CHAPTER_DRAFT = "draft";

    private final CanonEntryMapper canonMapper;
    private final AliasMapper aliasMapper;
    private final ForeshadowMapper foreshadowMapper;
    private final ReviewFindingMapper findingMapper;
    private final GenJobMapper jobMapper;
    private final BookChapterMapper chapterMapper;
    private final ChapterRevisionMapper revisionMapper;
    // 与 CanonTxWriter 同因：Spring Boot 4 只自动装配 Jackson 3 的 ObjectMapper
    private final ObjectMapper objectMapper = new ObjectMapper();

    // ── 正典 ──────────────────────────────────────────────

    @Override
    @Transactional(readOnly = true)
    public Page<CanonEntry> canonPage(Long bookId, String subjectKey, String kind,
            String status, String authority, String keyword, Pageable pageable) {
        String kw = blankToNull(keyword);
        // 值侧转义交给检索面同一个口径：作者搜「100%」不该命中全书
        String like = NovelSearchServiceImpl.likeValue(orDefault(kw, ""));
        LambdaQueryWrapper<CanonEntry> wrapper = new LambdaQueryWrapper<CanonEntry>()
                .eq(CanonEntry::getBookId, bookId)
                .eq(blankToNull(subjectKey) != null, CanonEntry::getSubjectKey, blankToNull(subjectKey))
                .eq(blankToNull(kind) != null, CanonEntry::getKind, blankToNull(kind))
                .eq(blankToNull(status) != null, CanonEntry::getStatus, blankToNull(status))
                .eq(blankToNull(authority) != null, CanonEntry::getAuthority, blankToNull(authority))
                .and(kw != null, w -> w.like(CanonEntry::getSubjectKey, like)
                        .or().like(CanonEntry::getPredicate, like)
                        .or().like(CanonEntry::getObjectText, like)
                        .or().like(CanonEntry::getRestatement, like))
                // 按实体聚着排：作者扫的是「这个人/这个地方身上堆了什么」，同实体的断言散在两页
                // 就看不出冲突，而时间序在这里没有判据价值
                .orderByAsc(CanonEntry::getSubjectKey)
                .orderByDesc(CanonEntry::getId);
        var mpPage = MyBatisPages.<CanonEntry>toMpPage(pageable);
        canonMapper.selectPage(mpPage, wrapper);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional
    public CanonEntry createCanon(Long bookId, CanonRequest req, Long userId) {
        requireText(req.getKind(), "kind");
        requireText(req.getSubjectKey(), "subjectKey");
        requireText(req.getPredicate(), "predicate");
        requireText(req.getObjectText(), "objectText");

        Integer asOf = currentChapterIndex(bookId);
        CanonEntry entry = new CanonEntry();
        entry.setBookId(bookId);
        entry.setKind(clip(req.getKind(), 24));
        entry.setSubjectKey(clip(req.getSubjectKey(), 128));
        entry.setPredicate(clip(req.getPredicate(), 64));
        entry.setObjectText(clip(req.getObjectText(), 512));
        entry.setRestatement(clip(req.getRestatement(), 512));
        entry.setAuthority(AUTHORITY_AUTHOR);
        entry.setConfidence(AUTHOR_CONFIDENCE);
        // 作者在新书还没章时写的设定就是「开篇即有」：established 留 NULL、valid_from 落 0，
        // 与内部通道的第 1 章种子口径区分开——那条有 asOf 可挂，这条没有
        entry.setEstablishedChapter(req.getEstablishedChapter() == null ? asOf : req.getEstablishedChapter());
        entry.setValidFromChapter(req.getValidFromChapter() == null
                ? (asOf == null ? 0 : asOf) : req.getValidFromChapter());
        entry.setValidUntilChapter(req.getValidUntilChapter());
        entry.setStatus(canonStatus(req.getStatus()));
        entry.setDecidedBy(userId);
        entry.setDecidedAt(LocalDateTime.now());
        canonMapper.insert(entry);
        return entry;
    }

    @Override
    @Transactional
    public CanonEntry updateCanon(Long canonId, CanonRequest req, Long userId) {
        CanonEntry entry = canonOf(canonId);
        if (req.getKind() != null) {
            entry.setKind(clip(req.getKind(), 24));
        }
        if (req.getSubjectKey() != null) {
            entry.setSubjectKey(clip(req.getSubjectKey(), 128));
        }
        if (req.getPredicate() != null) {
            entry.setPredicate(clip(req.getPredicate(), 64));
        }
        if (req.getObjectText() != null) {
            entry.setObjectText(clip(req.getObjectText(), 512));
        }
        if (req.getRestatement() != null) {
            entry.setRestatement(clip(req.getRestatement(), 512));
        }
        if (req.getEstablishedChapter() != null) {
            entry.setEstablishedChapter(req.getEstablishedChapter());
        }
        if (req.getValidFromChapter() != null) {
            entry.setValidFromChapter(req.getValidFromChapter());
        }
        if (req.getValidUntilChapter() != null) {
            entry.setValidUntilChapter(req.getValidUntilChapter());
        }
        if (req.getStatus() != null) {
            entry.setStatus(canonStatus(req.getStatus()));
        }
        // 手改即裁定：作者动过内容的断言就升级为 author 级（§10.2）。一条 model 抽出来的
        // 「她的眼睛是蓝色的」被作者改成「灰蓝色」之后仍然是模型自证，那 §8-⑤ 的不可逆优先级
        // 就没有落点，下一轮抽取会把它按模型置信度再次覆盖。
        entry.setAuthority(AUTHORITY_AUTHOR);
        entry.setConfidence(AUTHOR_CONFIDENCE);
        entry.setDecidedBy(userId);
        entry.setDecidedAt(LocalDateTime.now());
        canonMapper.updateById(entry);
        return entry;
    }

    @Override
    @Transactional
    public CanonEntry retireCanon(Long canonId, CanonRetireRequest req, Long userId) {
        CanonEntry entry = canonOf(canonId);
        Integer until = req == null || req.getUntilChapter() == null
                ? currentChapterIndex(entry.getBookId()) : req.getUntilChapter();
        if (until == null) {
            until = 0;
        }
        if (entry.getValidUntilChapter() != null && entry.getValidUntilChapter() <= until) {
            // 已经闭到更早的章就别再改了：把区间往后推等于让一个已失效的事实复活
            log.info("断言 {} 已闭至第 {} 章，停用请求（第 {} 章）不生效", entry.getId(), entry.getValidUntilChapter(), until);
            return entry;
        }
        entry.setValidUntilChapter(until);
        entry.setDecidedBy(userId);
        entry.setDecidedAt(LocalDateTime.now());
        canonMapper.updateById(entry);
        log.info("断言 {} 由作者 {} 停用至第 {} 章（{}）", entry.getId(), userId, until,
                req == null || req.getReason() == null ? "无理由" : req.getReason());
        return entry;
    }

    @Override
    @Transactional(readOnly = true)
    public List<CanonEntry> previewConflicts(Long bookId, CanonRequest req, Integer asOfChapter) {
        if (blankToNull(req.getSubjectKey()) == null || blankToNull(req.getPredicate()) == null) {
            return List.of();
        }
        Integer asOf = asOfChapter == null ? currentChapterIndex(bookId) : asOfChapter;
        LambdaQueryWrapper<CanonEntry> wrapper = new LambdaQueryWrapper<CanonEntry>()
                .eq(CanonEntry::getBookId, bookId)
                .eq(CanonEntry::getSubjectKey, clip(req.getSubjectKey(), 128))
                .eq(CanonEntry::getPredicate, clip(req.getPredicate(), 64))
                .eq(CanonEntry::getStatus, "confirmed")
                .ne(blankToNull(req.getObjectText()) != null, CanonEntry::getObjectText,
                        clip(req.getObjectText(), 512));
        // as-of 只在看得到章号时才有意义；没有章号就退回「凡是没闭掉的」全列出来
        if (asOf != null) {
            wrapper.le(CanonEntry::getValidFromChapter, asOf)
                    .and(w -> w.isNull(CanonEntry::getValidUntilChapter).or().ge(CanonEntry::getValidUntilChapter, asOf));
        } else {
            wrapper.isNull(CanonEntry::getValidUntilChapter);
        }
        return canonMapper.selectList(wrapper.orderByAsc(CanonEntry::getId));
    }

    // ── 别名 ──────────────────────────────────────────────

    @Override
    @Transactional(readOnly = true)
    public List<Alias> listAliases(Long bookId) {
        return aliasMapper.selectList(new LambdaQueryWrapper<Alias>()
                .eq(Alias::getBookId, bookId)
                .orderByAsc(Alias::getEntityKey)
                .orderByAsc(Alias::getAliasText));
    }

    @Override
    @Transactional
    public Alias updateAlias(Long bookId, Long aliasId, AliasRequest req) {
        Alias alias = aliasMapper.selectById(aliasId);
        if (alias == null || !alias.getBookId().equals(bookId)) {
            throw new RuntimeException("别名不存在：" + aliasId);
        }
        if (blankToNull(req.getEntityKey()) != null) {
            // 改指向就是作者对 C3（一名多实）的裁定：库约束 (book_id, alias_text) 唯一，
            // 本方法不动 aliasText，所以不会撞唯一键，也不需要先删后插
            alias.setEntityKey(clip(req.getEntityKey(), 128));
        }
        if (req.getIsPrimary() != null) {
            alias.setIsPrimary(req.getIsPrimary());
        }
        aliasMapper.updateById(alias);
        return alias;
    }

    // ── 伏笔 ──────────────────────────────────────────────

    @Override
    @Transactional(readOnly = true)
    public List<Foreshadow> listForeshadows(Long bookId, String status) {
        return foreshadowMapper.selectList(new LambdaQueryWrapper<Foreshadow>()
                .eq(Foreshadow::getBookId, bookId)
                .eq(blankToNull(status) != null, Foreshadow::getStatus, blankToNull(status))
                .orderByAsc(Foreshadow::getPlantedChapter)
                .orderByAsc(Foreshadow::getId));
    }

    @Override
    @Transactional
    public Foreshadow createForeshadow(Long bookId, ForeshadowRequest req) {
        requireText(req.getContent(), "content");
        Foreshadow row = new Foreshadow();
        row.setBookId(bookId);
        Integer planted = req.getPlantedChapter() == null ? currentChapterIndex(bookId) : req.getPlantedChapter();
        row.setPlantedChapter(planted == null ? 1 : planted);
        row.setContent(clip(req.getContent(), 512));
        row.setDueByArc(req.getDueByArc());
        row.setPayoffChapter(req.getPayoffChapter());
        row.setStatus(foreshadowStatus(req.getStatus(), req.getPayoffChapter()));
        foreshadowMapper.insert(row);
        return row;
    }

    @Override
    @Transactional
    public Foreshadow updateForeshadow(Long bookId, Long foreshadowId, ForeshadowRequest req) {
        Foreshadow row = foreshadowMapper.selectById(foreshadowId);
        if (row == null || !row.getBookId().equals(bookId)) {
            throw new RuntimeException("伏笔不存在：" + foreshadowId);
        }
        if (req.getContent() != null) {
            row.setContent(clip(req.getContent(), 512));
        }
        if (req.getPlantedChapter() != null) {
            row.setPlantedChapter(req.getPlantedChapter());
        }
        if (req.getDueByArc() != null) {
            row.setDueByArc(req.getDueByArc());
        }
        if (req.getPayoffChapter() != null) {
            row.setPayoffChapter(req.getPayoffChapter());
        }
        row.setStatus(foreshadowStatus(req.getStatus(), row.getPayoffChapter()));
        foreshadowMapper.updateById(row);
        return row;
    }

    // ── 冲突台账 ──────────────────────────────────────────

    @Override
    @Transactional(readOnly = true)
    public Page<FindingView> findingPage(Long bookId, String severity, String status, String checker,
            String code, Pageable pageable) {
        LambdaQueryWrapper<ReviewFinding> wrapper = new LambdaQueryWrapper<ReviewFinding>()
                .eq(bookId != null, ReviewFinding::getBookId, bookId)
                .eq(blankToNull(severity) != null, ReviewFinding::getSeverity, blankToNull(severity))
                .eq(blankToNull(status) != null, ReviewFinding::getStatus, blankToNull(status))
                .eq(blankToNull(checker) != null, ReviewFinding::getChecker, blankToNull(checker))
                .eq(blankToNull(code) != null, ReviewFinding::getCode, blankToNull(code))
                // 新的在前：作者的处理队列是「刚刚闸门报了 gì」，而不是按章号复习一遍全书
                .orderByDesc(ReviewFinding::getId);
        var mpPage = MyBatisPages.<ReviewFinding>toMpPage(pageable);
        findingMapper.selectPage(mpPage, wrapper);
        Map<Long, BookChapter> chapters = loadChapters(mpPage.getRecords());
        List<FindingView> rows = mpPage.getRecords().stream()
                .map(finding -> toView(finding, chapters.get(finding.getChapterId())))
                .toList();
        return new PageImpl<>(rows, pageable, mpPage.getTotal());
    }

    /**
     * 裁定：adopt 是四步单事务（写 author 断言 + 闭旧区间 + 关 Finding + 记审计）。
     *
     * <p>半途成功会留下「作者说过但没有权威断言」的脏状态，正是本方案要消灭的那类不一致，
     * 所以这里不吞任何一步的异常，也不给「先写断言、下次再补台账」留路径（§15）。
     */
    @Override
    @Transactional
    public FindingAdjudicationView adjudicate(Long findingId, FindingAdjudicationRequest req, Long userId) {
        ReviewFinding finding = findingMapper.selectById(findingId);
        if (finding == null) {
            throw new RuntimeException("Finding 不存在：" + findingId);
        }
        if (!"open".equals(finding.getStatus())) {
            throw new RuntimeException("该条已裁定为 " + finding.getStatus() + "，不重复裁定");
        }
        String action = req.getAction() == null ? "" : req.getAction().trim().toLowerCase();
        if (!ACTIONS.contains(action)) {
            throw new RuntimeException("未知裁定动作：" + req.getAction());
        }
        if (("reject".equals(action) || "waive".equals(action)) && blankToNull(req.getBasis()) == null) {
            throw new RuntimeException("判误报与放行 blocker 必须写裁定依据");
        }

        FindingAdjudicationView view = new FindingAdjudicationView();
        view.setFindingId(findingId);

        if ("adopt".equals(action)) {
            adopt(finding, req, userId, view);
            finding.setStatus("adopted");
        } else if ("rewrite".equals(action)) {
            rewrite(finding, view);
            finding.setStatus("adopted");
        } else if ("reject".equals(action)) {
            finding.setStatus("rejected");
        } else {
            finding.setStatus("waived");
        }
        finding.setDecidedBy(userId);
        finding.setDecidedAt(LocalDateTime.now());
        finding.setBasis(clip(req.getBasis(), 512));
        view.setStatus(finding.getStatus());
        findingMapper.updateById(finding);
        return view;
    }

    private void adopt(ReviewFinding finding, FindingAdjudicationRequest req, Long userId,
            FindingAdjudicationView view) {
        CanonRequest assertion = req.getAssertion();
        if (assertion == null) {
            throw new RuntimeException("采纳裁定必须给出作者认定的事实（assertion）");
        }
        BookChapter chapter = chapterMapper.selectById(finding.getChapterId());
        // established/valid_from 取 Finding 所属章：作者是就着这一章说「事情是这样的」，
        // 拿当前最大章号会让裁定 retroactively 改掉更早章节的事实
        Integer at = chapter == null ? null : chapter.getChapterIndex();
        CanonEntry entry = new CanonEntry();
        entry.setBookId(finding.getBookId());
        entry.setKind(clip(orDefault(assertion.getKind(), "character"), 24));
        entry.setSubjectKey(clip(requireText(assertion.getSubjectKey(), "assertion.subjectKey"), 128));
        entry.setPredicate(clip(requireText(assertion.getPredicate(), "assertion.predicate"), 64));
        entry.setObjectText(clip(requireText(assertion.getObjectText(), "assertion.objectText"), 512));
        entry.setRestatement(clip(assertion.getRestatement(), 512));
        entry.setAuthority(AUTHORITY_AUTHOR);
        entry.setConfidence(AUTHOR_CONFIDENCE);
        entry.setEstablishedChapter(assertion.getEstablishedChapter() == null ? at : assertion.getEstablishedChapter());
        entry.setValidFromChapter(assertion.getValidFromChapter() == null
                ? (at == null ? 0 : at) : assertion.getValidFromChapter());
        entry.setValidUntilChapter(assertion.getValidUntilChapter());
        entry.setStatus(canonStatus(orDefault(assertion.getStatus(), "confirmed")));
        entry.setDecidedBy(userId);
        entry.setDecidedAt(LocalDateTime.now());

        List<Long> closeIds = closeTargets(finding, req);
        // 先全部校验再动手：闭到第 3 条时发现第 4 条不属于本书，事务回滚固然是兜底，
        // 但把「半途」压缩成「还没开始」更省事，也让单测能断言一次写库都没发生
        List<CanonEntry> toClose = new ArrayList<>();
        for (Long id : closeIds) {
            CanonEntry old = canonMapper.selectById(id);
            if (old == null) {
                throw new RuntimeException("被违反的断言不存在：" + id);
            }
            if (!old.getBookId().equals(finding.getBookId())) {
                throw new RuntimeException("断言 " + id + " 不属于本书，拒绝跨书闭区间");
            }
            if (old.getValidUntilChapter() == null && at != null) {
                toClose.add(old);
            }
        }
        for (CanonEntry old : toClose) {
            old.setValidUntilChapter(at);
            canonMapper.updateById(old);
            view.getClosedAssertionIds().add(old.getId());
        }
        if (toClose.size() == 1) {
            entry.setSupersedesId(toClose.get(0).getId());
        }
        canonMapper.insert(entry);
        view.setAssertionId(entry.getId());
    }

    private void rewrite(ReviewFinding finding, FindingAdjudicationView view) {
        BookChapter chapter = chapterMapper.selectById(finding.getChapterId());
        if (chapter == null) {
            throw new RuntimeException("章节不存在：" + finding.getChapterId());
        }
        if (!CHAPTER_DRAFT.equals(chapter.getStatus())) {
            chapter.setStatus(CHAPTER_DRAFT);
            chapterMapper.updateById(chapter);
            view.setChapterBackToDraft(true);
        }
        view.setFixInstruction(finding.getFixInstruction());
    }

    private List<Long> closeTargets(ReviewFinding finding, FindingAdjudicationRequest req) {
        if (req.getCloseAssertionIds() != null && !req.getCloseAssertionIds().isEmpty()) {
            return req.getCloseAssertionIds().stream().filter(java.util.Objects::nonNull).toList();
        }
        return parseIdArray(finding.getCanonRefs());
    }

    /** canon_refs 是闸门写入的 JSON 数组文本，元素可能是数字也可能是字符串 */
    private List<Long> parseIdArray(String json) {
        if (blankToNull(json) == null) {
            return List.of();
        }
        try {
            List<?> raw = objectMapper.readValue(json, List.class);
            List<Long> ids = new ArrayList<>();
            for (Object value : raw) {
                if (value instanceof Number number) {
                    ids.add(number.longValue());
                } else if (value instanceof String text && text.matches("\\d+")) {
                    ids.add(Long.parseLong(text));
                }
            }
            return ids;
        } catch (JsonProcessingException e) {
            log.warn("canon_refs 解析失败，本次裁定不闭任何旧区间：{}", json);
            return List.of();
        }
    }

    // ── 进度 ──────────────────────────────────────────────

    @Override
    @Transactional(readOnly = true)
    public NovelProgressView progress(Long bookId) {
        NovelProgressView view = new NovelProgressView();
        view.setBookId(bookId);
        view.setChapterCount(chapterMapper.selectCount(new LambdaQueryWrapper<BookChapter>()
                .eq(BookChapter::getBookId, bookId).isNull(BookChapter::getDeletedAt)));
        Object sum = chapterMapper.selectObjs(new QueryWrapper<BookChapter>()
                        .select("IFNULL(SUM(word_count), 0)")
                        .eq("book_id", bookId).isNull("deleted_at"))
                .stream().findFirst().orElse(0);
        view.setWordCount(((Number) sum).longValue());
        view.getChaptersByStatus().putAll(distribute(chapterMapper, "status", bookId, true));
        view.getCanonByStatus().putAll(distribute(canonMapper, "status", bookId, false));
        view.getCanonByAuthority().putAll(distribute(canonMapper, "authority", bookId, false));
        view.getFindingsByStatus().putAll(distribute(findingMapper, "status", bookId, false));
        Map<String, Long> openBySeverity = new LinkedHashMap<>();
        for (Map<String, Object> row : findingMapper.selectMaps(new QueryWrapper<ReviewFinding>()
                .select("severity AS k", "COUNT(*) AS c")
                .eq("book_id", bookId).eq("status", "open").groupBy("severity"))) {
            openBySeverity.put(String.valueOf(row.get("k")), asLong(row.get("c")));
        }
        view.setOpenFindingsBySeverity(openBySeverity);
        view.setOpenForeshadows(foreshadowMapper.selectCount(new LambdaQueryWrapper<Foreshadow>()
                .eq(Foreshadow::getBookId, bookId).eq(Foreshadow::getStatus, "opened")));
        view.getJobsByStage().putAll(distribute(jobMapper, "stage", bookId, false));
        return view;
    }

    /**
     * 按列分组计数。
     *
     * <p>{@code deletedAt} 只对章节表生效：正典层是 append-only，没有软删列，
     * 给它们拼 {@code isNull(deleted_at)} 会让 SQL 直接报错。
     */
    private <T> Map<String, Long> distribute(com.baomidou.mybatisplus.core.mapper.BaseMapper<T> mapper,
            String column, Long bookId, boolean softDeleted) {
        // 列名取自代码常量而非入参，拼进 SQL 无注入面；泛型只在这里出现一次，
        // 为的是六个不同的 Mapper 共用同一段 group by
        QueryWrapper<T> wrapper = new QueryWrapper<>();
        wrapper.select(column + " AS k", "COUNT(*) AS c").eq("book_id", bookId).groupBy(column);
        if (softDeleted) {
            wrapper.isNull("deleted_at");
        }
        Map<String, Long> out = new LinkedHashMap<>();
        for (Map<String, Object> row : mapper.selectMaps(wrapper)) {
            out.put(String.valueOf(row.get("k")), asLong(row.get("c")));
        }
        return out;
    }

    // ── 章节版本与改稿影响 ────────────────────────────────

    /**
     * 任一历史版本都能解析回原文：黄金集样本与断言出处按 {@code (chapterId, revision)} 引用，
     * 当前版本不在快照表里，这里拼成列表的第一项，前端按版本号取两条就能做 diff。
     */
    @Override
    @Transactional(readOnly = true)
    public List<ChapterRevisionView> chapterRevisions(Long bookId, Long chapterId) {
        BookChapter chapter = chapterOf(bookId, chapterId);
        List<ChapterRevisionView> out = new ArrayList<>();

        ChapterRevisionView live = new ChapterRevisionView();
        live.setChapterId(chapter.getId());
        live.setRevision(chapter.getRevision() == null ? 1 : chapter.getRevision());
        live.setContent(chapter.getContent());
        live.setContentHash(ChapterSourceRelocator.sha256Hex(orDefault(chapter.getContent(), "")));
        live.setCurrent(true);
        out.add(live);

        for (ChapterRevision row : revisionMapper.selectList(new QueryWrapper<ChapterRevision>()
                .eq("chapter_id", chapter.getId())
                .orderByDesc("revision"))) {
            ChapterRevisionView view = new ChapterRevisionView();
            view.setChapterId(row.getChapterId());
            view.setRevision(row.getRevision());
            view.setContent(row.getContent());
            view.setContentHash(row.getContentHash());
            view.setCreatedBy(row.getCreatedBy());
            view.setCreatedAt(row.getCreatedAt());
            out.add(view);
        }
        return out;
    }

    /**
     * 改这一章会波及谁（§10.5-③ 的第④件事）。
     *
     * <p>两处实时算而不是读快照表：出处失效按<b>当前</b>正文逐字重算，作者改完没保存也能看见风险；
     * 受影响后章按断言的双时态区间算，只列「仍会读到本章事实」的章，不把所有后章一锅端。
     */
    @Override
    @Transactional(readOnly = true)
    public ChapterImpactView chapterImpact(Long bookId, Long chapterId) {
        BookChapter chapter = chapterOf(bookId, chapterId);
        ChapterImpactView view = new ChapterImpactView();
        view.setChapterId(chapter.getId());
        view.setChapterIndex(chapter.getChapterIndex());
        view.setRevision(chapter.getRevision());
        view.setStatus(chapter.getStatus());

        String content = orDefault(chapter.getContent(), "");
        List<CanonEntry> sourced = canonMapper.selectList(new QueryWrapper<CanonEntry>()
                .eq("book_id", bookId)
                .eq("source_chapter_id", chapterId)
                .orderByAsc("id"));
        view.setOrphanedAssertions(orphanedAssertions(chapterId, content, sourced));
        view.setOrphanedFindings(findingMapper.selectCount(new QueryWrapper<ReviewFinding>()
                .eq("chapter_id", chapterId)
                .eq("status", "orphaned")));

        Integer index = chapter.getChapterIndex();
        if (index == null || sourced.isEmpty()) {
            return view;
        }
        for (BookChapter next : chapterMapper.selectList(new QueryWrapper<BookChapter>()
                .eq("book_id", bookId)
                .isNull("deleted_at")
                .gt("chapter_index", index)
                .orderByAsc("chapter_index"))) {
            List<CanonEntry> visible = sourced.stream()
                    .filter(entry -> visibleAt(entry, next.getChapterIndex()))
                    .toList();
            if (visible.isEmpty()) {
                continue;
            }
            ChapterImpactView.AffectedChapter affected = new ChapterImpactView.AffectedChapter();
            affected.setChapterId(next.getId());
            affected.setChapterIndex(next.getChapterIndex());
            affected.setTitle(next.getTitle());
            affected.setStatus(next.getStatus());
            affected.setCanonIds(visible.stream().map(CanonEntry::getId).toList());
            affected.setBrief(briefOf(visible));
            view.getAffectedChapters().add(affected);
        }
        return view;
    }

    /** 引文已不在当前正文里的断言，配上台账里那条未裁定的 source_orphaned */
    private List<ChapterImpactView.OrphanedAssertion> orphanedAssertions(Long chapterId, String content,
            List<CanonEntry> sourced) {
        Map<Long, Long> findingByCanon = new LinkedHashMap<>();
        for (ReviewFinding row : findingMapper.selectList(new QueryWrapper<ReviewFinding>()
                .eq("chapter_id", chapterId)
                .eq("code", ChapterSourceRelocator.CODE_SOURCE_ORPHANED)
                .eq("status", "open"))) {
            for (Long canonId : parseIdArray(row.getCanonRefs())) {
                findingByCanon.putIfAbsent(canonId, row.getId());
            }
        }
        List<ChapterImpactView.OrphanedAssertion> out = new ArrayList<>();
        for (CanonEntry entry : sourced) {
            if (blankToNull(entry.getEvidenceQuote()) == null
                    || ChapterSourceRelocator.locate(content, entry.getEvidenceQuote(), entry.getSourceStart()) != null) {
                continue;
            }
            ChapterImpactView.OrphanedAssertion orphan = new ChapterImpactView.OrphanedAssertion();
            orphan.setCanonId(entry.getId());
            orphan.setSubjectKey(entry.getSubjectKey());
            orphan.setPredicate(entry.getPredicate());
            orphan.setObjectText(entry.getObjectText());
            orphan.setEvidenceQuote(entry.getEvidenceQuote());
            orphan.setFindingId(findingByCanon.get(entry.getId()));
            out.add(orphan);
        }
        return out;
    }

    /** 断言在第 idx 章是否还成立：区间起于生效章，止于被关闭的章（闭区间，含端点） */
    private static boolean visibleAt(CanonEntry entry, Integer idx) {
        if (idx == null) {
            return false;
        }
        int from = entry.getValidFromChapter() != null ? entry.getValidFromChapter()
                : (entry.getEstablishedChapter() != null ? entry.getEstablishedChapter() : 1);
        int until = entry.getValidUntilChapter() != null ? entry.getValidUntilChapter() : Integer.MAX_VALUE;
        return idx >= from && idx <= until;
    }

    /** 只列前两条主-谓，够了——这是一句提示，不是断言清单 */
    private static String briefOf(List<CanonEntry> visible) {
        String head = visible.stream().limit(2)
                .map(entry -> entry.getSubjectKey() + "·" + entry.getPredicate())
                .collect(Collectors.joining("、"));
        return visible.size() > 2 ? head + " 等 " + visible.size() + " 条" : head;
    }

    private BookChapter chapterOf(Long bookId, Long chapterId) {
        BookChapter chapter = chapterMapper.selectById(chapterId);
        if (chapter == null || !Objects.equals(chapter.getBookId(), bookId) || chapter.getDeletedAt() != null) {
            throw new RuntimeException("章节不存在：" + chapterId);
        }
        return chapter;
    }

    // ── 工具 ──────────────────────────────────────────────

    private static FindingView toView(ReviewFinding finding, BookChapter chapter) {
        FindingView view = new FindingView();
        BeanUtils.copyProperties(finding, view);
        if (chapter != null) {
            view.setChapterIndex(chapter.getChapterIndex());
            view.setChapterTitle(chapter.getTitle());
            view.setChapterWords(chapter.getWordCount());
            view.setChapterStatus(chapter.getStatus());
        }
        return view;
    }

    /** 一页台账里同一章会反复出现，逐条 selectById 就是 N+1，按 id 批量取一次 */
    private Map<Long, BookChapter> loadChapters(List<ReviewFinding> rows) {
        Set<Long> ids = rows.stream().map(ReviewFinding::getChapterId).filter(Objects::nonNull).collect(Collectors.toSet());
        if (ids.isEmpty()) {
            return Map.of();
        }
        return chapterMapper.selectByIds(ids).stream()
                .collect(Collectors.toMap(BookChapter::getId, chapter -> chapter));
    }

    private CanonEntry canonOf(Long canonId) {
        CanonEntry entry = canonMapper.selectById(canonId);
        if (entry == null) {
            throw new RuntimeException("断言不存在：" + canonId);
        }
        return entry;
    }

    /**
     * 该书当前最大章号，作为「现在」的坐标。
     *
     * <p>用 QueryWrapper 的列名字符串而不是 LambdaQueryWrapper 的 {@code .select(方法引用)}：
     * 后者在构建阶段就要查 MyBatis-Plus 的 lambda 列缓存，纯单测里没有 mapper 注册就没有这份缓存，
     * 一个取章号的小工具不该因此变成必须起容器才测得动。
     */
    @Override
    public Integer currentChapterIndex(Long bookId) {
        return chapterMapper.selectObjs(new QueryWrapper<BookChapter>()
                        .select("IFNULL(MAX(chapter_index), 0)")
                        .eq("book_id", bookId)
                        .isNull("deleted_at"))
                .stream().findFirst()
                .map(o -> ((Number) o).intValue())
                .filter(index -> index > 0)
                .orElse(null);
    }

    private static String canonStatus(String raw) {
        String status = raw == null ? "confirmed" : raw.trim().toLowerCase();
        if (!CANON_STATUS.contains(status)) {
            throw new RuntimeException("非法的断言状态：" + raw);
        }
        return status;
    }

    private static String foreshadowStatus(String raw, Integer payoffChapter) {
        if (blankToNull(raw) != null) {
            String status = raw.trim().toLowerCase();
            if (!FORESHADOW_STATUS.contains(status)) {
                throw new RuntimeException("非法的伏笔状态：" + raw);
            }
            return status;
        }
        return payoffChapter == null ? "opened" : "paid";
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

    private static long asLong(Object value) {
        return value instanceof Number number ? number.longValue() : 0L;
    }

    private static String clip(String value, int limit) {
        if (value == null) {
            return null;
        }
        return value.length() <= limit ? value : value.substring(0, limit);
    }
}
