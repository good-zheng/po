package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("book")
public class Book {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 创建用户ID */
    private Long authorId;

    private String title;

    private String description;

    private String coverImage;

    /** 书籍类型，如：fantasy-玄幻、wuxia-武侠、scifi-科幻 */
    private String genre;

    /** 创作状态: ongoing-连载中, completed-已完结, paused-暂停更新 */
    private String status = "ongoing";

    /** 书籍总字数（各未删除章节字数合计） */
    private Integer wordCount = 0;

    /** 作者署名 */
    private String author;

    /** Tier-0 常驻注入的世界观摘要 + 主线进度，不是对外简介文案（那是 description） */
    private String summary;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    /** 不允许更新（等价原 JPA updatable = false） */
    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt = LocalDateTime.now();

    /** 更新时由 MetaObjectHandler 自动填充为当前时间 */
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt = LocalDateTime.now();
}
