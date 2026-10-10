package com.goodzheng.po.novel.dto;

import lombok.Data;

/**
 * 关闭断言有效期（POST /novel/internal/assertions:close）。
 *
 * <p>演进靠闭区间而不是删行或覆盖：旧事实必须留在库里，as-of 查询才答得出
 * 「第 N 章时作者已知什么」；删行会让历史注入无法复现。
 */
@Data
public class InternalAssertionCloseRequest {

    private Long assertionId;

    /** 从第几章起不再成立 */
    private Integer untilChapter;

    /** 关闭理由，写进日志与后续作者复核线索 */
    private String reason;
}
