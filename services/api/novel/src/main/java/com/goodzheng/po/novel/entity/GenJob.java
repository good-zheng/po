package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 生成任务与幂等键。
 *
 * <p>{@code idempotencyKey} 上有唯一索引，是「重放不重复入库」的库层兜底；
 * 写库失败必须把 {@code stage} 落到 failed 并留 {@code lastError}，
 * 只记日志返回布尔值会让半途失败变成查无实据的鬼故事。
 */
@Data
@TableName("gen_job")
public class GenJob {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    private Integer chapterIndex;

    /** queued/writing/gating/awaiting_review/committed/failed */
    private String stage;

    /** chapterId + contentHash + promptVersion + model */
    private String idempotencyKey;

    private Integer retryCount;

    private String lastError;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;

    /** 时间戳由 IdempotencyGuard 显式写入：LambdaUpdateWrapper 的 set 形态不走 MetaObjectHandler */
    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime updatedAt;
}
