package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("book_chapter")
public class BookChapter {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 所属书籍 ID（原 JPA @ManyToOne 关联，MyBatis-Plus 用普通外键字段） */
    @JsonIgnore
    private Long bookId;

    /** 章节索引/序号 */
    private Integer chapterIndex;

    private String title;

    private String content;

    /** 章节字数（不含空白字符） */
    private Integer wordCount = 0;

    /** draft 草稿 / pending_review 待复核 / committed 已定稿（正典出处的可信度分界，见 NOVEL_AGENT_PRD §10.5） */
    private String status = "draft";

    /** 每次保存加 1；正典断言的出处与黄金集样本按 (chapterId, revision) 引用，防止改正文洗掉评测基线 */
    private Integer revision = 1;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    /** 不允许更新（等价原 JPA updatable = false） */
    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt = LocalDateTime.now();

    /** 更新时由 MetaObjectHandler 自动填充为当前时间 */
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt = LocalDateTime.now();
}
