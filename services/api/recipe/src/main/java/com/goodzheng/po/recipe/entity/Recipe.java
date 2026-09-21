package com.goodzheng.po.recipe.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.LinkedHashSet;
import java.util.Set;

@Data
@Entity
@Table(name = "recipe")
public class Recipe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 100)
    private String title;

    @Column(length = 500)
    private String description;

    @Column(length = 500)
    private String coverImageUrl;

    // ── 时间与难度 ─────────────────────────────────────────
    private Integer prepTime;
    private Integer cookTime;
    private Integer totalTime;

    /** 难度: 1-简单, 2-中等, 3-困难 */
    @Column(nullable = false)
    private Integer difficulty = 1;

    /** 建议食用人数 */
    private Integer servings;

    // ── 分类与标签 ─────────────────────────────────────────
    @Column(length = 50)
    private String category;

    /** 标签，存为逗号分隔字符串，如: 下饭,低脂,快手菜 */
    @Column(length = 500)
    private String tags;

    // ── 作者与统计 ─────────────────────────────────────────
    @Column(nullable = false)
    private Long authorId;

    @Column(nullable = false)
    private Boolean isPublic = true;

    @Column(nullable = false)
    private Integer likesCount = 0;

    // ── 扩展字段 ──────────────────────────────────────────
    private Integer calories;
    private Double protein;
    private Double fat;
    private Double carbs;

    @Column(length = 500)
    private String tips;

    @Column(length = 100)
    private String flavorProfile;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    // ── 时间戳 ────────────────────────────────────────────
    @Column(updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    private LocalDateTime updatedAt = LocalDateTime.now();

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }

    // ── 关联关系 ──────────────────────────────────────────
    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("sortOrder ASC")
    private Set<Ingredient> ingredients = new LinkedHashSet<>();

    @OneToMany(mappedBy = "recipe", cascade = CascadeType.ALL, orphanRemoval = true)
    @OrderBy("stepNumber ASC")
    private Set<Step> steps = new LinkedHashSet<>();
}
