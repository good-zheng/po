package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.math.BigDecimal;

/**
 * 作者手改正典的入参（POST novel books/{bookId}/canon 与 PATCH novel canon/{id}）。
 *
 * <p>这里<b>没有</b> authority 字段，也不是「传了会被忽略」而是契约层就不存在：
 * authority 是本方案里唯一不可被模型覆盖的权威级，任何能调这个端点的一方若能自报
 * {@code author}，提权路径就从接口层漏了（§10.5-②）。管理端写死 author，内部通道写死 model。
 */
@Data
public class CanonRequest {

    /** world_rule/character/relation/location/item/theme/style */
    private String kind;

    /** 别名归一后的实体键，如 char:shenqing */
    private String subjectKey;

    /** 机器可比谓词，如 eye_color/is_alive */
    private String predicate;

    private String objectText;

    /** 给提示词读的自然语言句 */
    private String restatement;

    private BigDecimal confidence;

    private Integer establishedChapter;

    private Integer validFromChapter;

    private Integer validUntilChapter;

    /** confirmed/disputed/todo，缺省 confirmed */
    private String status;
}
