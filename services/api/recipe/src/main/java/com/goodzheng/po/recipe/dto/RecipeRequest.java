package com.goodzheng.po.recipe.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

@Data
public class RecipeRequest {

    @NotBlank(message = "菜谱名称不能为空")
    private String title;

    private String description;
    private String coverImageUrl;

    private Integer prepTime;
    private Integer cookTime;
    private Integer totalTime;

    @NotNull(message = "难度不能为空")
    private Integer difficulty = 1;

    private Integer servings;

    private String category;
    private String tags;
    private Boolean isPublic = true;

    // 扩展
    private Integer calories;
    private Double protein;
    private Double fat;
    private Double carbs;
    private String tips;
    private String flavorProfile;

    // 嵌套数据
    private List<@Valid IngredientItem> ingredients;

    private List<@Valid StepItem> steps;

    @Data
    public static class IngredientItem {
        @NotBlank(message = "食材名称不能为空")
        private String name;
        private String amount;
        private String unit;
        private Boolean isEssential = true;
        private Integer sortOrder = 0;
    }

    @Data
    public static class StepItem {
        @NotNull(message = "步骤序号不能为空")
        private Integer stepNumber;
        @NotBlank(message = "步骤描述不能为空")
        private String content;
        private String imageUrl;
        private String videoUrl;
        private Integer duration;
    }
}
