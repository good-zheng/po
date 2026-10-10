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
@TableName("book_character")
public class BookCharacter {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 所属书籍 ID（原 JPA @ManyToOne 关联，MyBatis-Plus 用普通外键字段） */
    @JsonIgnore
    private Long bookId;

    private String name;

    private String description;

    /** 角色图片URL */
    private String avatar;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    /** 不允许更新（等价原 JPA updatable = false） */
    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt = LocalDateTime.now();

    /** 更新时由 MetaObjectHandler 自动填充为当前时间 */
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt = LocalDateTime.now();
}
