package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.List;

/**
 * 提议卡的裁定入参（{@code .../adopt} 与 {@code .../dismiss}）。
 */
@Data
public class ProposalDecisionRequest {

    /**
     * adopt 时要把哪些既有断言闭区间。
     *
     * <p>与撞车条目的对应关系：服务端会先算一遍确定性冲突预览，非空时<b>必须</b>显式给出这里的
     * 子集才落库——「作者已确认」不能靠前端自觉，否则污染拿到正名（§10.6）。
     */
    private List<Long> closeAssertionIds;

    /** 采纳时给断言的一句自然语言复述，留空由服务端取 objectText */
    private String restatement;

    /** dismiss 必填：为什么驳回，否则下一轮对话只能重新猜 */
    private String basis;
}
