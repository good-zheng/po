package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/** 裁定结果（PUT /novel/reviews/{findingId} 的响应）。 */
@Data
public class FindingAdjudicationView {

    private Long findingId;

    /** adopted/rejected/waived */
    private String status;

    /** adopt 新写入的 author 断言 id */
    private Long assertionId;

    private List<Long> closedAssertionIds = new ArrayList<>();

    /** rewrite 时该章已退回草稿 */
    private boolean chapterBackToDraft;

    /** rewrite 回带给前端的定向修补指令 */
    private String fixInstruction;
}
