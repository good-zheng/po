package com.goodzheng.po.recipe.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "recipe_category")
public class RecipeCategory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /** 分类名称，如：家常菜、湘菜 */
    @Column(nullable = false, length = 50, unique = true)
    private String name;

    /** 图标（Lucide 图标名或 emoji） */
    @Column(length = 100)
    private String icon;

    /** 分类描述 */
    @Column(length = 200)
    private String description;

    /** 排序权重，越小越靠前 */
    @Column(nullable = false)
    private Integer sortOrder = 0;

    // ── 软删除 ────────────────────────────────────────────
    private LocalDateTime deletedAt;

    @Column(updatable = false)
    private LocalDateTime createdAt = LocalDateTime.now();

    private LocalDateTime updatedAt = LocalDateTime.now();

    @PreUpdate
    protected void onUpdate() {
        this.updatedAt = LocalDateTime.now();
    }
}
