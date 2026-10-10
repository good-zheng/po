package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/**
 * 提议卡裁定的结果。
 *
 * <p>{@code conflictIds} 让「撞了哪几条」在响应里也留一份：前端二次确认时读的是它，
 * 落库后再回看这次采纳覆盖了什么，不必拿时间戳去猜。
 */
@Data
public class ProposalDecisionView {

    private Long proposalId;

    /** adopted/dismissed */
    private String status;

    /** adopt 后新立的 author 级断言 id */
    private Long entryId;

    /** 本次被闭掉有效区间的旧断言 */
    private List<Long> closedAssertionIds = new ArrayList<>();

    /** 撞车的既有断言 id：与本次提议同主同谓、as-of 可见、值不同 */
    private List<Long> conflictIds = new ArrayList<>();
}
