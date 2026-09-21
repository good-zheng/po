package com.goodzheng.po.recipe.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;

@Data
@Entity
@Table(name = "recipe_ingredient")
public class Ingredient {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "recipe_id", nullable = false)
    @JsonIgnore
    @EqualsAndHashCode.Exclude
    @ToString.Exclude
    private Recipe recipe;

    @Column(nullable = false, length = 100)
    private String name;

    @Column(length = 50)
    private String amount;

    @Column(length = 20)
    private String unit;

    /** 是否必需（区分主料和辅料） */
    @Column(nullable = false)
    private Boolean isEssential = true;

    /** 排序 */
    @Column(nullable = false)
    private Integer sortOrder = 0;
}
