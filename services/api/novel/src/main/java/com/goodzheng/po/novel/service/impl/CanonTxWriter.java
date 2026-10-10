package com.goodzheng.po.novel.service.impl;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.novel.dto.InternalAssertionAppendRequest;
import com.goodzheng.po.novel.dto.InternalAssertionCloseRequest;
import com.goodzheng.po.novel.dto.InternalFindingRequest;
import com.goodzheng.po.novel.dto.InternalSummaryRequest;
import com.goodzheng.po.novel.dto.InternalWriteResult;
import com.goodzheng.po.novel.entity.Alias;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.ChapterSummary;
import com.goodzheng.po.novel.entity.CharacterState;
import com.goodzheng.po.novel.entity.Foreshadow;
import com.goodzheng.po.novel.entity.ReviewFinding;
import com.goodzheng.po.novel.entity.BookChapter;
import com.goodzheng.po.novel.repository.AliasMapper;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.ChapterSummaryMapper;
import com.goodzheng.po.novel.repository.CharacterStateMapper;
import com.goodzheng.po.novel.repository.ForeshadowMapper;
import com.goodzheng.po.novel.repository.ReviewFindingMapper;
import com.goodzheng.po.novel.repository.BookChapterMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

/**
 * 正典层的单事务写入器。
 *
 * <p>与 {@link IdempotencyGuard} 分开放：幂等状态要独立提交，业务写入要整体回滚，
 * 两者的边界不同，合在一个类里就会互相迁就。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CanonTxWriter {

    /** 本通道唯一允许的权威级：模型自证不能把自己写成作者设定 */
    private static final String AUTHORITY_MODEL = "model";
    private static final BigDecimal DEFAULT_CONFIDENCE = new BigDecimal("1.00");

    // 摘要层级：chapter_summary.level 的全部合法值。对同包的 CanonInternalServiceImpl 可见，
    // 它要在写侧判层级决定 chapterId 是否必填
    static final String LEVEL_SCENE = "scene";
    static final String LEVEL_CHAPTER = "chapter";
    static final String LEVEL_ARC = "arc";

    private final CanonEntryMapper canonMapper;
    private final ForeshadowMapper foreshadowMapper;
    private final AliasMapper aliasMapper;
    private final CharacterStateMapper stateMapper;
    private final ReviewFindingMapper findingMapper;
    private final ChapterSummaryMapper summaryMapper;
    private final BookChapterMapper chapterMapper;
    // 自己 new 而不是注入：Spring Boot 4 只自动装配 Jackson 3 的
    // tools.jackson.databind.ObjectMapper，注入 Jackson 2 的会让应用启动即失败
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Transactional
    public InternalWriteResult persistAppend(InternalAssertionAppendRequest req) {
        InternalWriteResult result = new InternalWriteResult();
        result.setApplied(true);
        Integer asOf = req.getAsOfChapter();

        for (InternalAssertionAppendRequest.AssertionItem item : req.getAssertions()) {
            canonMapper.insert(toEntry(req.getBookId(), asOf, req.getChapterId(), item));
            result.setAssertionsInserted(result.getAssertionsInserted() + 1);
        }
        for (InternalAssertionAppendRequest.ForeshadowOpItem op : req.getForeshadows()) {
            applyForeshadow(req.getBookId(), asOf, op, result);
        }
        for (InternalAssertionAppendRequest.AliasItem item : req.getAliases()) {
            applyAlias(req.getBookId(), item, result);
        }
        for (InternalAssertionAppendRequest.StateChangeItem item : req.getStateChanges()) {
            applyState(req.getBookId(), asOf, item);
        }
        return result;
    }

    @Transactional
    public InternalWriteResult persistClose(InternalAssertionCloseRequest req) {
        if (req.getAssertionId() == null || req.getUntilChapter() == null) {
            throw new RuntimeException("assertionId 与 untilChapter 必填");
        }
        CanonEntry entry = canonMapper.selectById(req.getAssertionId());
        if (entry == null) {
            throw new RuntimeException("断言不存在：" + req.getAssertionId());
        }
        // 闭区间而非删除：旧事实留在库里，as-of 查询才答得出「第 N 章时已知什么」
        entry.setValidUntilChapter(req.getUntilChapter());
        canonMapper.updateById(entry);
        log.info("断言 {} 有效期关闭至第 {} 章（{}）", entry.getId(), req.getUntilChapter(), req.getReason());

        InternalWriteResult result = new InternalWriteResult();
        result.setApplied(true);
        return result;
    }

    @Transactional
    public InternalWriteResult persistFindings(InternalFindingRequest req) {
        BookChapter chapter = chapterMapper.selectById(req.getChapterId());
        if (chapter == null || chapter.getDeletedAt() != null) {
            throw new RuntimeException("章节不存在：" + req.getChapterId());
        }
        InternalWriteResult result = new InternalWriteResult();
        result.setApplied(true);
        for (InternalFindingRequest.FindingItem item : req.getFindings()) {
            if (isBlank(item.getCode()) || isBlank(item.getChecker())) {
                throw new RuntimeException("Finding 缺少 code 或 checker");
            }
            // 台账的唯一键含 revision：先查重再插，避免异常把事务标记成回滚
            Long existing = findingMapper.selectCount(new LambdaQueryWrapper<ReviewFinding>()
                    .eq(ReviewFinding::getChapterId, chapter.getId())
                    .eq(ReviewFinding::getRevision, chapter.getRevision())
                    .eq(ReviewFinding::getCode, clip(item.getCode(), 32))
                    .eq(ReviewFinding::getChecker, clip(item.getChecker(), 16))
                    .eq(item.getTextStart() != null, ReviewFinding::getTextStart, item.getTextStart())
                    .isNull(item.getTextStart() == null, ReviewFinding::getTextStart));
            if (existing != null && existing > 0) {
                result.setSkipped(result.getSkipped() + 1);
                continue;
            }
            findingMapper.insert(toFinding(chapter, item));
        }
        return result;
    }

    @Transactional
    public InternalWriteResult persistSummaries(InternalSummaryRequest req) {
        String level = summaryLevel(req.getLevel());
        InternalWriteResult result = new InternalWriteResult();
        result.setApplied(true);

        if (LEVEL_ARC.equals(level)) {
            persistArcSummary(req, result);
            return result;
        }

        BookChapter chapter = chapterMapper.selectById(req.getChapterId());
        if (chapter == null || chapter.getDeletedAt() != null) {
            throw new RuntimeException("章节不存在：" + req.getChapterId());
        }
        for (InternalSummaryRequest.SceneItem item : req.getScenes()) {
            if (isBlank(item.getContent())) {
                throw new RuntimeException("摘要缺少 content");
            }
            // chapter 级 scene_no 固定 0 而不是 NULL：uk_summary_level 里 NULL 与 NULL 不算重复
            // （MySQL 唯一索引不比较 NULL），写 NULL 等于把「同章只有一条章节摘要」这条约束
            // 从库层让给代码层，重放就会插出并行；scene 级序号从 1 起，0 不会与它撞键
            Integer sceneNo = LEVEL_CHAPTER.equals(level) ? 0 : item.getSceneNo();
            if (sceneNo == null) {
                throw new RuntimeException("场景摘要缺少 sceneNo");
            }
            ChapterSummary summary = summaryMapper.selectOne(new LambdaQueryWrapper<ChapterSummary>()
                    .eq(ChapterSummary::getBookId, chapter.getBookId())
                    .eq(ChapterSummary::getChapterId, chapter.getId())
                    .eq(ChapterSummary::getLevel, level)
                    .eq(ChapterSummary::getSceneNo, sceneNo)
                    .last("LIMIT 1"));
            boolean isNew = summary == null;
            if (isNew) {
                summary = new ChapterSummary();
                summary.setBookId(chapter.getBookId());
                summary.setChapterId(chapter.getId());
                summary.setLevel(level);
                summary.setSceneNo(sceneNo);
            }
            summary.setContent(item.getContent());
            summary.setTokens(item.getTokens() == null ? item.getContent().length() : item.getTokens());
            // 区间端点服务端推导（同 sourceVersion 取章节 revision 的口径）：scene/chapter 级
            // 的覆盖范围就是它自己那一章，调用方无从置入
            summary.setFromChapter(chapter.getChapterIndex());
            summary.setToChapter(chapter.getChapterIndex());
            // 版本跟着章节走：正文一改 revision 就变，旧摘要据此被判过期重算
            summary.setSourceVersion(chapter.getRevision());
            if (isNew) {
                summaryMapper.insert(summary);
            } else {
                summaryMapper.updateById(summary);
            }
            result.setSummariesWritten(result.getSummariesWritten() + 1);
        }
        return result;
    }

    /**
     * arc 级：整段跨章区间压成一行。
     *
     * <p>没有 sourceVersion 可对取——弧摘要不对应某一章正文，故写 NULL，
     * 它由编译器按「成员章节摘要是否重算过」自行判新旧。
     */
    private void persistArcSummary(InternalSummaryRequest req, InternalWriteResult result) {
        if (req.getArcNo() == null) {
            throw new RuntimeException("arc 级摘要缺少 arcNo");
        }
        Integer from = req.getFromChapter();
        Integer to = req.getToChapter();
        if (from == null || to == null) {
            throw new RuntimeException("arc 级摘要缺少 fromChapter/toChapter");
        }
        if (from < 1 || from > to) {
            throw new RuntimeException("arc 级摘要区间非法：" + from + ".." + to + "（需 1 <= fromChapter <= toChapter）");
        }
        Long bookId = req.getBookId();
        if (bookId == null) {
            BookChapter chapter = req.getChapterId() == null ? null : chapterMapper.selectById(req.getChapterId());
            if (chapter == null) {
                throw new RuntimeException("arc 级摘要必须给 bookId（chapterId 只用于反查所属书籍）");
            }
            bookId = chapter.getBookId();
        }
        // arc 级不参与 uk_summary_level 的去重：那条唯一键含 chapter_id，而 arc 行该列为 NULL，
        // MySQL 不判 NULL 相等，键形同不存在——所以同弧重复写只能在这里按 (book_id, arc, arcNo) 挡
        ChapterSummary summary = summaryMapper.selectOne(new LambdaQueryWrapper<ChapterSummary>()
                .eq(ChapterSummary::getBookId, bookId)
                .eq(ChapterSummary::getLevel, LEVEL_ARC)
                .eq(ChapterSummary::getSceneNo, req.getArcNo())
                .last("LIMIT 1"));
        boolean isNew = summary == null;
        if (isNew) {
            summary = new ChapterSummary();
            summary.setBookId(bookId);
            summary.setLevel(LEVEL_ARC);
            summary.setSceneNo(req.getArcNo());
        }
        summary.setChapterId(req.getChapterId());
        summary.setFromChapter(from);
        summary.setToChapter(to);
        summary.setSourceVersion(null);
        List<InternalSummaryRequest.SceneItem> items = req.getScenes();
        if (items == null || items.isEmpty() || isBlank(items.get(0).getContent())) {
            throw new RuntimeException("arc 级摘要缺少 content");
        }
        if (items.size() > 1) {
            log.warn("arc 级摘要一份载荷只落一行，收到 {} 条 scenes，取首条", items.size());
        }
        InternalSummaryRequest.SceneItem item = items.get(0);
        summary.setContent(item.getContent());
        summary.setTokens(item.getTokens() == null ? item.getContent().length() : item.getTokens());
        if (isNew) {
            summaryMapper.insert(summary);
        } else {
            summaryMapper.updateById(summary);
        }
        result.setSummariesWritten(result.getSummariesWritten() + 1);
    }

    /** 载荷里缺省/空的层级一律按 scene：Python 侧旧载荷不带 level，扩三级不能变成破坏性变更 */
    static String summaryLevel(String raw) {
        if (raw == null || raw.isBlank()) {
            return LEVEL_SCENE;
        }
        String level = raw.trim().toLowerCase(java.util.Locale.ROOT);
        if (!LEVEL_SCENE.equals(level) && !LEVEL_CHAPTER.equals(level) && !LEVEL_ARC.equals(level)) {
            throw new RuntimeException("未知摘要层级：" + raw);
        }
        return level;
    }

    private CanonEntry toEntry(Long bookId, Integer asOf, Long defaultChapterId,
            InternalAssertionAppendRequest.AssertionItem item) {
        if (isBlank(item.getKind()) || isBlank(item.getSubjectKey())
                || isBlank(item.getPredicate()) || isBlank(item.getObjectText())) {
            throw new RuntimeException("断言缺少 kind/subjectKey/predicate/objectText");
        }
        CanonEntry entry = new CanonEntry();
        entry.setBookId(bookId);
        entry.setKind(clip(item.getKind(), 24));
        entry.setSubjectKey(clip(item.getSubjectKey(), 128));
        entry.setPredicate(clip(item.getPredicate(), 64));
        entry.setObjectText(clip(item.getObjectText(), 512));
        entry.setRestatement(clip(item.getRestatement(), 512));
        // 服务端写死，不读入参：见 InternalAssertionAppendRequest 的类注释
        entry.setAuthority(AUTHORITY_MODEL);
        entry.setConfidence(item.getConfidence() == null ? DEFAULT_CONFIDENCE : item.getConfidence());
        entry.setEstablishedChapter(item.getEstablishedChapter() == null ? asOf : item.getEstablishedChapter());
        entry.setValidFromChapter(item.getValidFromChapter() == null ? asOf : item.getValidFromChapter());
        entry.setValidUntilChapter(item.getValidUntilChapter());
        entry.setSupersedesId(item.getSupersedesId());
        entry.setStatus("todo".equals(item.getStatus()) ? "todo" : "confirmed");
        entry.setSourceChapterId(item.getSourceChapterId() == null ? defaultChapterId : item.getSourceChapterId());
        entry.setSourceStart(item.getSourceStart());
        entry.setSourceEnd(item.getSourceEnd());
        entry.setEvidenceQuote(clip(item.getEvidenceQuote(), 512));
        entry.setPromptVersion(clip(item.getPromptVersion(), 32));
        entry.setModel(clip(item.getModel(), 64));
        return entry;
    }

    private void applyForeshadow(Long bookId, Integer asOf,
            InternalAssertionAppendRequest.ForeshadowOpItem op, InternalWriteResult result) {
        if ("pay".equals(op.getOp()) || "abandon".equals(op.getOp())) {
            Foreshadow open = op.getForeshadowId() == null ? null : foreshadowMapper.selectById(op.getForeshadowId());
            if (open == null) {
                result.setSkipped(result.getSkipped() + 1);
                return;
            }
            open.setStatus("pay".equals(op.getOp()) ? "paid" : "abandoned");
            if ("pay".equals(op.getOp())) {
                open.setPayoffChapter(asOf);
            }
            foreshadowMapper.updateById(open);
        } else {
            if (isBlank(op.getContent())) {
                throw new RuntimeException("埋设伏笔必须给 content");
            }
            Foreshadow created = new Foreshadow();
            created.setBookId(bookId);
            created.setPlantedChapter(op.getPlantedChapter() == null ? asOf : op.getPlantedChapter());
            created.setContent(clip(op.getContent(), 512));
            created.setDueByArc(op.getDueByArc());
            created.setStatus("opened");
            foreshadowMapper.insert(created);
        }
        result.setForeshadowsWritten(result.getForeshadowsWritten() + 1);
    }

    private void applyAlias(Long bookId, InternalAssertionAppendRequest.AliasItem item,
            InternalWriteResult result) {
        if (isBlank(item.getAliasText()) || isBlank(item.getEntityKey())) {
            throw new RuntimeException("别名必须给 aliasText 与 entityKey");
        }
        Alias existing = aliasMapper.selectOne(new LambdaQueryWrapper<Alias>()
                .eq(Alias::getBookId, bookId)
                .eq(Alias::getAliasText, clip(item.getAliasText(), 128))
                .last("LIMIT 1"));
        if (existing == null) {
            Alias alias = new Alias();
            alias.setBookId(bookId);
            alias.setEntityKey(clip(item.getEntityKey(), 128));
            alias.setAliasText(clip(item.getAliasText(), 128));
            alias.setFirstSeenChapter(item.getFirstSeenChapter());
            alias.setIsPrimary(Boolean.TRUE.equals(item.getIsPrimary()));
            aliasMapper.insert(alias);
            result.setAliasesWritten(result.getAliasesWritten() + 1);
            return;
        }
        if (existing.getEntityKey().equals(item.getEntityKey())) {
            // 同一实体同一称谓：重放或重复抽取，跳过即可
            result.setSkipped(result.getSkipped() + 1);
            return;
        }
        // 一个称谓指向两个实体属于 C3 冲突，裁定权在作者（N5b 台账），
        // 内部通道无权改判，因此保留原映射只记账。
        log.warn("别名冲突：书 {} 的「{}」已指向 {}，本次抽取想指向 {}",
                bookId, existing.getAliasText(), existing.getEntityKey(), item.getEntityKey());
        result.setSkipped(result.getSkipped() + 1);
    }

    private void applyState(Long bookId, Integer asOf,
            InternalAssertionAppendRequest.StateChangeItem item) {
        if (isBlank(item.getCharKey())) {
            throw new RuntimeException("状态变迁缺少 charKey");
        }
        Integer chapter = item.getAsOfChapter() == null ? asOf : item.getAsOfChapter();
        CharacterState state = stateMapper.selectOne(new LambdaQueryWrapper<CharacterState>()
                .eq(CharacterState::getBookId, bookId)
                .eq(CharacterState::getCharKey, clip(item.getCharKey(), 128))
                .eq(CharacterState::getAsOfChapter, chapter)
                .last("LIMIT 1"));
        boolean isNew = state == null;
        if (isNew) {
            state = new CharacterState();
            state.setBookId(bookId);
            state.setCharKey(clip(item.getCharKey(), 128));
            state.setAsOfChapter(chapter);
        }
        if (item.getIsAlive() != null) {
            state.setIsAlive(item.getIsAlive());
        } else if (isNew) {
            state.setIsAlive(Boolean.TRUE);
        }
        state.setLocationKey(clip(item.getLocationKey(), 128));
        state.setKnows(toJsonArray(item.getKnows()));
        state.setHolds(toJsonArray(item.getHolds()));
        state.setMood(clip(item.getMood(), 64));
        state.setLastSeenChapter(item.getLastSeenChapter());
        if (isNew) {
            stateMapper.insert(state);
        } else {
            stateMapper.updateById(state);
        }
    }

    private ReviewFinding toFinding(BookChapter chapter, InternalFindingRequest.FindingItem item) {
        ReviewFinding finding = new ReviewFinding();
        finding.setBookId(chapter.getBookId());
        finding.setChapterId(chapter.getId());
        finding.setRevision(chapter.getRevision());
        finding.setCode(clip(item.getCode(), 32));
        finding.setSeverity(isBlank(item.getSeverity()) ? "major" : clip(item.getSeverity(), 16));
        finding.setChecker(clip(item.getChecker(), 16));
        finding.setCanonRefs(toJsonArray(item.getCanonRefs() == null ? null
                : item.getCanonRefs().stream().map(String::valueOf).toList()));
        finding.setTextStart(item.getTextStart());
        finding.setTextEnd(item.getTextEnd());
        finding.setEvidenceQuote(clip(item.getEvidenceQuote(), 512));
        finding.setExplanation(clip(item.getExplanation(), 512));
        finding.setFixInstruction(clip(item.getFixInstruction(), 512));
        finding.setStatus("open");
        return finding;
    }

    private String toJsonArray(List<String> values) {
        if (values == null) {
            return null;
        }
        try {
            return objectMapper.writeValueAsString(values);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("JSON 列序列化失败：" + e.getMessage(), e);
        }
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    /** 列宽截断：模型输出超长属于常态，截断入库比让整章写入失败更可接受 */
    private static String clip(String value, int limit) {
        if (value == null) {
            return null;
        }
        return value.length() <= limit ? value : value.substring(0, limit);
    }
}
