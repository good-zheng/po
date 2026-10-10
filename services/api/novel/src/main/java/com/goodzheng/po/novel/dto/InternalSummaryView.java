package com.goodzheng.po.novel.dto;

import lombok.Data;

/**
 * 摘要读取端点（GET /novel/internal/canon/summaries）交给 L1 编译器的行形状。
 *
 * <p>为什么不直接回 {@code ChapterSummary} 实体：编译器只需要层级、区间位置和正文，
 * bookId/sourceVersion 属于库内治理字段，透出去只会让调用方按它们分支，而它们的口径随时会变。
 */
@Data
public class InternalSummaryView {

    private Long id;

    /** scene/chapter/arc */
    private String level;

    /** 覆盖区间起始章（即 from_chapter），编译器按它排上下文 */
    private Integer chapterNo;

    /** scene 级是场景序号；chapter 级固定 0；arc 级是弧序号 */
    private Integer sceneNo;

    private String content;

    private Integer tokens;
}
