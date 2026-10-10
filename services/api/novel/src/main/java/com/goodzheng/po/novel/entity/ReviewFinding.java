package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 冲突台账（双闸门的产物）。
 *
 * <p>{@code revision} 必挂版本：作者改正文会让旧 Finding 指向不存在的内容，
 * 挂版本后已录的黄金集样本与裁定记录仍可对上当时的原文。
 */
@Data
@TableName("review_finding")
public class ReviewFinding {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    private Long chapterId;

    private Integer revision;

    /** 冲突编码，对应 C1-C6 */
    private String code;

    /** blocker/major/minor */
    private String severity;

    /** rule 规则引擎 / judge 语义裁判 */
    private String checker;

    /** 被违反的 canon 编号列表，JSON 数组文本 */
    private String canonRefs;

    private Integer textStart;

    private Integer textEnd;

    /** 裁判必须引原文，与正文逐字相等才收下 */
    private String evidenceQuote;

    private String explanation;

    /** 定向修补指令 */
    private String fixInstruction;

    /** open/adopted/rejected/waived/orphaned */
    private String status;

    private Long decidedBy;

    private LocalDateTime decidedAt;

    private String basis;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;
}
