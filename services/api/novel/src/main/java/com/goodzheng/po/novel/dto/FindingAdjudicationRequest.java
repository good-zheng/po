package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.List;

/**
 * 冲突裁定入参（PUT /novel/reviews/{findingId}）。
 *
 * <p>四态语义见 §10.6：adopt 会<b>写一条 author 断言并闭掉被违反的旧区间</b>，
 * reject/waive 只动台账不动正典，rewrite 把章节退回草稿等定向修补。
 */
@Data
public class FindingAdjudicationRequest {

    /** adopt/reject/waive/rewrite */
    private String action;

    /** 裁定依据；reject/waive 必填——不留依据的放行等于给误判盖章 */
    private String basis;

    /** adopt 必填：作者认定的事实本身 */
    private CanonRequest assertion;

    /**
     * adopt 时要关闭有效期的旧断言。缺省取该 Finding 的 canon_refs，
     * 也就是「作者说这条不对，那就按作者的说法把被撞的旧事实停掉」。
     */
    private List<Long> closeAssertionIds;
}
