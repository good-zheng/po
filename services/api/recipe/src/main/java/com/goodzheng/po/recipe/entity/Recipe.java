package com.goodzheng.po.recipe.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.LinkedHashSet;
import java.util.Set;

@Data
@TableName("recipe")
public class Recipe {

    @TableId(type = IdType.AUTO)
    private Long id;

    private String title;

    private String description;

    private String coverImageUrl;

    // ── 时间与难度 ─────────────────────────────────────────
    private Integer prepTime;
    private Integer cookTime;
    private Integer totalTime;

    /** 难度: 1-简单, 2-中等, 3-困难 */
    private Integer difficulty = 1;

    /** 建议食用人数 */
    private Integer servings;

    // ── 分类与标签 ─────────────────────────────────────────
    private String category;

    /** 标签，存为逗号分隔字符串，如: 下饭,低脂,快手菜 */
    private String tags;

    // ── 作者与统计 ─────────────────────────────────────────
    private Long authorId;

    private Boolean isPublic = true;

    private Integer likesCount = 0;

    // ── 扩展字段 ──────────────────────────────────────────
    private Integer calories;
    private Double protein;
    private Double fat;
    private Double carbs;

    private String tips;

    private String flavorProfile;

    // ── 审核流 ────────────────────────────────────────────
    /** 审核状态: pending=待审核, approved=已通过, rejected=已驳回（见 RecipeStatusConstants） */
    private String status = "approved";

    /** 驳回原因（status=rejected 时有值） */
    private String rejectReason;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    // ── 时间戳 ────────────────────────────────────────────
    /** 不允许更新（等价原 JPA updatable = false） */
    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt = LocalDateTime.now();

    /** 更新时由 MetaObjectHandler 自动填充为当前时间 */
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime updatedAt = LocalDateTime.now();

    // ── 关联数据（非本表字段，由 Service 显式查询填充） ──────
    @TableField(exist = false)
    private Set<Ingredient> ingredients = new LinkedHashSet<>();

    @TableField(exist = false)
    private Set<Step> steps = new LinkedHashSet<>();

    // ── 当前用户视角的交互标记（非本表字段，由 Service 批量填充） ──
    @TableField(exist = false)
    private Boolean isFavorited;

    @TableField(exist = false)
    private Boolean isLiked;

    /** 收藏时间（收藏列表返回） */
    @TableField(exist = false)
    private LocalDateTime favoritedAt;

    /** 最近浏览时间（历史列表返回） */
    @TableField(exist = false)
    private LocalDateTime viewedAt;
}
