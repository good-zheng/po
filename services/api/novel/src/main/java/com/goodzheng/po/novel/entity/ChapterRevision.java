package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 章节历史版本（§10.5-③ 的第①件事：旧文不覆盖）。
 *
 * <p>存的是**让位出去**的那一版正文：当前版本永远只在 {@code book_chapter.content} 上，
 * 于是 {@code (chapter_id, revision)} 对任意已发生过的版本号都能解析出当时的原文——
 * 黄金集样本与断言出处就是按这对坐标引用的（§12），少一行就有一段历史查不回来。
 */
@Data
@TableName("chapter_revision")
public class ChapterRevision {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long chapterId;

    private Integer revision;

    private String content;

    /** 快照正文的 sha256（hex）：gen_job 的幂等键里也有这把哈希，两处必须能对上 */
    private String contentHash;

    /** 作者手改记 user_id，Agent 写记 NULL——这条区分是「谁动了正文」的唯一痕迹 */
    private Long createdBy;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;
}
