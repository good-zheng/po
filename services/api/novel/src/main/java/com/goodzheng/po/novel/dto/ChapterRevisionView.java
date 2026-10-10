package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.time.LocalDateTime;

/**
 * 章节的一个历史版本（含当前版本）。
 *
 * <p>当前版本不在 {@code chapter_revision} 表里（那张表只存让位出去的旧文），这里现场拼成一行：
 * 前端做 diff 只要按 {@code revision} 取两条即可，不必自己分清哪条来自表、哪条来自章节本身。
 */
@Data
public class ChapterRevisionView {

    private Long chapterId;

    private Integer revision;

    private String content;

    /** 正文的 sha256；无快照的行也照样给出，比对是否被改过用 */
    private String contentHash;

    /** 手改的作者 ID；Agent 写库为 null；当前版本取章节的最近改动人，无法回溯时为 null */
    private Long createdBy;

    private LocalDateTime createdAt;

    /** true 表示这条就是 book_chapter.content，不可当历史读取 */
    private boolean current;
}
