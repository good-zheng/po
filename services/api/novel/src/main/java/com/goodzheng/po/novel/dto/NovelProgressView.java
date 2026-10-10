package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 进度看板（§10.2「进度」Tab，只读）。
 *
 * <p>失败终态必须在这里看得见：{@code jobsByStage} 直接透出 gen_job 的 stage 分布，
 * failed 不为零时前端要标红——「写库失败要有终态、不许仅记日志」这条要求只有被作者
 * 看见才真的成立。
 */
@Data
public class NovelProgressView {

    private Long bookId;

    /** 未删除章节数 */
    private long chapterCount;

    private long wordCount;

    /** 章节状态分布：draft/pending_review/committed */
    private Map<String, Long> chaptersByStatus = new LinkedHashMap<>();

    /** 断言状态分布：confirmed/disputed/todo/rejected */
    private Map<String, Long> canonByStatus = new LinkedHashMap<>();

    /** 权威级分布：author/text/model，作者能一眼看出正典里有多少是模型自证的 */
    private Map<String, Long> canonByAuthority = new LinkedHashMap<>();

    /** 台账状态分布：open/adopted/rejected/waived/orphaned */
    private Map<String, Long> findingsByStatus = new LinkedHashMap<>();

    /** 未裁定 Finding 的严重度分布 */
    private Map<String, Long> openFindingsBySeverity = new LinkedHashMap<>();

    private long openForeshadows;

    /** gen_job 阶段分布 */
    private Map<String, Long> jobsByStage = new LinkedHashMap<>();
}
