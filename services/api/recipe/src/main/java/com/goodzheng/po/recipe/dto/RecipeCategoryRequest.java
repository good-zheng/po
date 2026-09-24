package com.goodzheng.po.recipe.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 菜谱分类创建/更新的请求体
 */
@Data
public class RecipeCategoryRequest {

    @NotBlank(message = "分类名称不能为空")
    @Size(max = 50, message = "分类名称不能超过 50 个字符")
    private String name;

    /** 图标（Lucide 图标名或 emoji） */
    @Size(max = 100)
    private String icon;

    @Size(max = 200, message = "分类描述不能超过 200 个字符")
    private String description;

    @Min(value = 0, message = "排序权重不能为负数")
    private Integer sortOrder;
}
