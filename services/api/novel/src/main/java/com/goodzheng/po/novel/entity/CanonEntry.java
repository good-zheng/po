package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 正典断言（L0 层核心表）。
 *
 * <p>演进方式是 append-only：事实变化靠关闭旧区间（{@code validUntilChapter}）再追加新行，
 * 而不是覆盖旧行——覆盖会让「第 12 章时作者知道什么」这类 as-of 查询失去依据。
 */
@Data
@TableName("canon_entry")
public class CanonEntry {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    /** world_rule/character/relation/location/item/theme/style */
    private String kind;

    /** 别名归一后的实体键，如 char:shenqing */
    private String subjectKey;

    /** 机器可比谓词，如 eye_color/is_alive/cannot_use */
    private String predicate;

    /** 值，比对用它 */
    private String objectText;

    /** 给提示词读的自然语言句，注入用它 */
    private String restatement;

    /** author/text/model，优先级由服务端判定，绝不接受调用方传值 */
    private String authority;

    /** author 恒 1.00 */
    private BigDecimal confidence;

    /** 第几章确立，NULL 表示开篇即有的全局设定 */
    private Integer establishedChapter;

    private Integer validFromChapter;

    /** NULL 至今有效 */
    private Integer validUntilChapter;

    /** 被本条取代的旧断言 */
    private Long supersedesId;

    /** confirmed/disputed/todo(缺口)/rejected */
    private String status;

    private Long sourceChapterId;

    private Integer sourceStart;

    private Integer sourceEnd;

    /** 入库时的原文逐字片段，作者改正文后按它重定位 */
    private String evidenceQuote;

    private String promptVersion;

    private String model;

    /** 作者裁定人，authority=author 时必填 */
    private Long decidedBy;

    private LocalDateTime decidedAt;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;

    /** 更新时由 AuditMetaObjectHandler 填充；close 只改区间，时间戳必须跟着走 */
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt;
}
