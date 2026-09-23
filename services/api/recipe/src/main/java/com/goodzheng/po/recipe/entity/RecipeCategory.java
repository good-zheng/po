package com.goodzheng.po.recipe.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("recipe_category")
public class RecipeCategory {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 分类名称，如：家常菜、湘菜 */
    private String name;

    /** 图标（Lucide 图标名或 emoji） */
    private String icon;

    /** 分类描述 */
    private String description;

    /** 排序权重，越小越靠前 */
    private Integer sortOrder = 0;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    /** 不允许更新（等价原 JPA updatable = false） */
    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt = LocalDateTime.now();

    /** 更新时由 MetaObjectHandler 自动填充为当前时间 */
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt = LocalDateTime.now();
}
