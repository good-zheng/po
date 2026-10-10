package com.goodzheng.po.novel.dto;

import com.goodzheng.po.novel.entity.ReviewFinding;
import lombok.Data;
import lombok.EqualsAndHashCode;

/**
 * 台账行 + 章节坐标。
 *
 * <p>跨书台账里光有 chapterId 作者看不出是哪一段，多带章号与章题就不用前端再拉一次章节列表；
 * 出处高亮所需的 text_start/end 与 evidence_quote 沿用 Finding 本体的字段。
 */
@Data
@EqualsAndHashCode(callSuper = true)
public class FindingView extends ReviewFinding {

    private Integer chapterIndex;

    private String chapterTitle;

    private Integer chapterWords;

    /** 章节状态：改写正文后回 draft，作者据此知道哪一章又欠了一次重校验 */
    private String chapterStatus;
}
