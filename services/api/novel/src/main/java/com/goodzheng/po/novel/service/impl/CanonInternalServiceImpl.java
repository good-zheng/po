package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.novel.dto.InternalAssertionAppendRequest;
import com.goodzheng.po.novel.dto.InternalAssertionCloseRequest;
import com.goodzheng.po.novel.dto.InternalFindingRequest;
import com.goodzheng.po.novel.dto.InternalSummaryRequest;
import com.goodzheng.po.novel.dto.InternalSummaryView;
import com.goodzheng.po.novel.dto.InternalWriteResult;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.ChapterSummary;
import com.goodzheng.po.novel.entity.Foreshadow;
import com.goodzheng.po.novel.repository.CanonEntryMapper;
import com.goodzheng.po.novel.repository.ChapterSummaryMapper;
import com.goodzheng.po.novel.repository.ForeshadowMapper;
import com.goodzheng.po.novel.service.CanonInternalService;
import com.goodzheng.po.novel.service.impl.IdempotencyGuard.Claim;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Set;

/**
 * 内部通道的编排：认领幂等键 → 单事务写入 → 收尾记终态。
 *
 * <p>本类<b>刻意不加</b> {@code @Transactional}：一加分段提交就退化成一个大事务，
 * 写入失败会连带回滚认领记录，重放时被视为全新请求，「重放不重复入库」这条退出条件当场失守。
 *
 * <p>只有 append 走 gen_job：findings 与 summaries 各自有唯一键
 * （chapter_id+revision+code+checker+text_start / book+chapter+level+scene_no），
 * 重放被库层挡住建不了重复行，无需再叠一层任务状态。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CanonInternalServiceImpl implements CanonInternalService {

    /** 摘要层级合法值：与 chapter_summary.level 的注释同一套口径 */
    private static final Set<String> SUMMARY_LEVELS = Set.of("scene", "chapter", "arc");

    /** 缺省只取 scene,chapter：arc 是按弧批量预生成的粗粒度摘要，编译器要它得点名 */
    private static final List<String> DEFAULT_SUMMARY_LEVELS = List.of("scene", "chapter");

    private static final int DEFAULT_SUMMARY_LIMIT = 24;

    /** 硬上限：编译器一次注入上百条摘要必然是预算算错了，宁可挡回去 */
    private static final int MAX_SUMMARY_LIMIT = 200;

    private final IdempotencyGuard guard;
    private final CanonTxWriter writer;
    private final CanonEntryMapper canonMapper;
    private final ForeshadowMapper foreshadowMapper;
    private final ChapterSummaryMapper summaryMapper;

    @Override
    public InternalWriteResult append(InternalAssertionAppendRequest request) {
        if (request.getBookId() == null) {
            throw new RuntimeException("bookId 必填");
        }
        if (request.getAsOfChapter() == null) {
            throw new RuntimeException("asOfChapter 必填：断言没有生效起点就无法参与 as-of 过滤");
        }
        if (isBlank(request.getIdempotencyKey())) {
            throw new RuntimeException("idempotencyKey 必填");
        }
        Claim claim = guard.claim(request.getIdempotencyKey(), request.getBookId(), request.getAsOfChapter());
        if (claim == Claim.REPLAY) {
            log.info("幂等键 {} 已入库，跳过重放", request.getIdempotencyKey());
            return InternalWriteResult.replayed();
        }
        try {
            InternalWriteResult result = writer.persistAppend(request);
            guard.markCommitted(request.getIdempotencyKey());
            return result;
        } catch (RuntimeException e) {
            guard.markFailed(request.getIdempotencyKey(), describe(e));
            throw e;
        }
    }

    @Override
    public InternalWriteResult close(InternalAssertionCloseRequest request) {
        return writer.persistClose(request);
    }

    @Override
    public InternalWriteResult saveFindings(InternalFindingRequest request) {
        if (request.getChapterId() == null) {
            throw new RuntimeException("chapterId 必填");
        }
        return writer.persistFindings(request);
    }

    @Override
    public InternalWriteResult saveSummaries(InternalSummaryRequest request) {
        // 只有 arc 级不挂章节：其余两级没有 chapterId 就推不出区间端点与来源版本
        if (!CanonTxWriter.LEVEL_ARC.equals(CanonTxWriter.summaryLevel(request.getLevel()))
                && request.getChapterId() == null) {
            throw new RuntimeException("chapterId 必填");
        }
        return writer.persistSummaries(request);
    }

    @Override
    @Transactional(readOnly = true)
    public List<CanonEntry> snapshot(Long bookId, Integer asOf, List<String> entities, List<String> kinds) {
        if (bookId == null || asOf == null) {
            throw new RuntimeException("bookId 与 asOf 必填：不带章号的正典读取等于把后文剧透给正在写第 N 章的模型");
        }
        return canonMapper.selectList(new LambdaQueryWrapper<CanonEntry>()
                .eq(CanonEntry::getBookId, bookId)
                .eq(CanonEntry::getStatus, "confirmed")
                .le(CanonEntry::getValidFromChapter, asOf)
                .and(w -> w.isNull(CanonEntry::getValidUntilChapter).or().ge(CanonEntry::getValidUntilChapter, asOf))
                .in(entities != null && !entities.isEmpty(), CanonEntry::getSubjectKey, safe(entities))
                .in(kinds != null && !kinds.isEmpty(), CanonEntry::getKind, safe(kinds))
                .orderByAsc(CanonEntry::getEstablishedChapter)
                .orderByAsc(CanonEntry::getId));
    }

    @Override
    @Transactional(readOnly = true)
    public List<Foreshadow> openForeshadows(Long bookId, Integer asOf) {
        if (bookId == null || asOf == null) {
            throw new RuntimeException("bookId 与 asOf 必填");
        }
        return foreshadowMapper.selectList(new LambdaQueryWrapper<Foreshadow>()
                .eq(Foreshadow::getBookId, bookId)
                .eq(Foreshadow::getStatus, "opened")
                // 只看已埋下的：未来章节才埋的伏笔不该在此刻提醒模型去收
                .le(Foreshadow::getPlantedChapter, asOf)
                .orderByAsc(Foreshadow::getPlantedChapter));
    }

    @Override
    @Transactional(readOnly = true)
    public List<InternalSummaryView> summaries(Long bookId, Integer upto, List<String> levels, Integer limit) {
        if (bookId == null || upto == null) {
            throw new RuntimeException("bookId 与 upto 必填：不声明站在第几章，就无法判断一段摘要是否含后文");
        }
        List<String> wanted = levels == null || levels.isEmpty() ? DEFAULT_SUMMARY_LEVELS : levels;
        for (String level : wanted) {
            if (!SUMMARY_LEVELS.contains(level)) {
                throw new RuntimeException("未知摘要层级：" + level);
            }
        }
        if (limit != null && limit < 1) {
            throw new RuntimeException("limit 需为正整数");
        }
        int size = Math.min(limit == null ? DEFAULT_SUMMARY_LIMIT : limit, MAX_SUMMARY_LIMIT);

        // 与 snapshot 的相交判定刻意相反：摘要是有损总结，区间与 upto 相交就意味着它写了
        // upto 之后发生的事，注入进去就是剧透（见接口方法注释）。from_chapter 为 NULL 的
        // 历史行同样查不出来——起点未知即无法证明不含后文。
        // chapter_summary 没有软删列（正典层只追加/就地 upsert），故此处无需 isNull(deletedAt)
        List<ChapterSummary> rows = summaryMapper.selectList(new LambdaQueryWrapper<ChapterSummary>()
                .eq(ChapterSummary::getBookId, bookId)
                .in(ChapterSummary::getLevel, wanted)
                .le(ChapterSummary::getFromChapter, upto)
                .and(w -> w.isNull(ChapterSummary::getToChapter).or().le(ChapterSummary::getToChapter, upto))
                .orderByDesc(ChapterSummary::getFromChapter)
                .orderByAsc(ChapterSummary::getSceneNo)
                // size 是本地 int 且已夹在 [1,200]，拼进 LIMIT 无注入面
                .last("LIMIT " + size));
        return rows.stream().map(CanonInternalServiceImpl::toSummaryView).toList();
    }

    private static InternalSummaryView toSummaryView(ChapterSummary row) {
        InternalSummaryView view = new InternalSummaryView();
        view.setId(row.getId());
        view.setLevel(row.getLevel());
        view.setChapterNo(row.getFromChapter());
        view.setSceneNo(row.getSceneNo());
        view.setContent(row.getContent());
        view.setTokens(row.getTokens());
        return view;
    }

    private static List<String> safe(List<String> values) {
        return values == null ? List.of() : values.stream().filter(v -> v != null && !v.isBlank()).toList();
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private static String describe(RuntimeException e) {
        return e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
    }
}
