package com.goodzheng.po.novel.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.goodzheng.po.novel.entity.GenJob;
import com.goodzheng.po.novel.repository.GenJobMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * 幂等认领：用 gen_job 的唯一索引把「同一份抽取结果重复入库」挡在库层。
 *
 * <p>三个方法各自成事务、且调用方不在事务内，因此认领、写入、收尾是三段独立提交：
 * 若合进一个事务，写入回滚会连带撤销认领记录，重放时又当成新请求跑一遍，幂等形同虚设。
 * 反过来讲，认领成功但写入失败会留下 failed 行——这正是「写库失败必须有终态」要求的产物。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class IdempotencyGuard {

    public enum Claim {
        /** 首次认领，可以写 */
        FRESH,
        /** 键已 committed：interrupt 重放，直接跳过 */
        REPLAY,
        /** 上次失败，本次重试 */
        RETRY
    }

    private static final String STAGE_WRITING = "writing";
    private static final String STAGE_COMMITTED = "committed";
    private static final String STAGE_FAILED = "failed";

    private final GenJobMapper genJobMapper;

    @Transactional
    public Claim claim(String idempotencyKey, Long bookId, Integer chapterIndex) {
        GenJob job = new GenJob();
        job.setBookId(bookId);
        job.setChapterIndex(chapterIndex);
        job.setIdempotencyKey(idempotencyKey);
        job.setStage(STAGE_WRITING);
        job.setRetryCount(0);
        try {
            genJobMapper.insert(job);
            return Claim.FRESH;
        } catch (DuplicateKeyException e) {
            GenJob existing = findByKey(idempotencyKey);
            if (existing == null) {
                // 唯一键冲突却查不到行只可能是并发刚删完，按重放处理最安全
                return Claim.REPLAY;
            }
            if (STAGE_COMMITTED.equals(existing.getStage())) {
                return Claim.REPLAY;
            }
            if (STAGE_FAILED.equals(existing.getStage())) {
                genJobMapper.update(null, new LambdaUpdateWrapper<GenJob>()
                        .eq(GenJob::getIdempotencyKey, idempotencyKey)
                        .set(GenJob::getStage, STAGE_WRITING)
                        .set(GenJob::getUpdatedAt, LocalDateTime.now())
                        .set(GenJob::getRetryCount, (existing.getRetryCount() == null ? 0 : existing.getRetryCount()) + 1));
                return Claim.RETRY;
            }
            // writing 状态说明有一次同样的写入正在飞行中；宁可让作者事后重驱，
            // 也不做「抢锁重写」——那会把断言写成双份。
            log.warn("幂等键 {} 处于 {} 状态，本次不重复入库", idempotencyKey, existing.getStage());
            return Claim.REPLAY;
        }
    }

    @Transactional
    public void markCommitted(String idempotencyKey) {
        genJobMapper.update(null, new LambdaUpdateWrapper<GenJob>()
                .eq(GenJob::getIdempotencyKey, idempotencyKey)
                .set(GenJob::getStage, STAGE_COMMITTED)
                .set(GenJob::getUpdatedAt, LocalDateTime.now())
                .set(GenJob::getLastError, null));
    }

    @Transactional
    public void markFailed(String idempotencyKey, String error) {
        genJobMapper.update(null, new LambdaUpdateWrapper<GenJob>()
                .eq(GenJob::getIdempotencyKey, idempotencyKey)
                .set(GenJob::getStage, STAGE_FAILED)
                .set(GenJob::getUpdatedAt, LocalDateTime.now())
                .set(GenJob::getLastError, clip(error, 512)));
    }

    private GenJob findByKey(String idempotencyKey) {
        return genJobMapper.selectOne(new LambdaQueryWrapper<GenJob>()
                .eq(GenJob::getIdempotencyKey, idempotencyKey)
                .last("LIMIT 1"));
    }

    private static String clip(String value, int limit) {
        if (value == null) {
            return null;
        }
        return value.length() <= limit ? value : value.substring(0, limit);
    }
}
