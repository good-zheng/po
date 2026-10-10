package com.goodzheng.po.novel.dto;

import lombok.Data;

/** 伏笔台账手写/修订入参（POST/PATCH /novel/books/{bookId}/foreshadows）。 */
@Data
public class ForeshadowRequest {

    private String content;

    private Integer plantedChapter;

    /** 计划在哪个 arc 之前收回 */
    private Integer dueByArc;

    /** 实际收回章号；写了就视为已收 */
    private Integer payoffChapter;

    /** opened/paid/abandoned；缺省按 payoffChapter 推导 */
    private String status;
}
