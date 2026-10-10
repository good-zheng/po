package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/** 伏笔台账（C6 烂尾的抓手）：payoffChapter 为 NULL 即未收。 */
@Data
@TableName("foreshadow")
public class Foreshadow {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    private Integer plantedChapter;

    private String content;

    /** 计划在哪个 arc 前收回 */
    private Integer dueByArc;

    private Integer payoffChapter;

    /** opened/paid/abandoned */
    private String status;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;
}
