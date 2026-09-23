package com.goodzheng.po.recipe.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.Data;

@Data
@TableName("recipe_ingredient")
public class Ingredient {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** 所属菜谱 ID（原 JPA @ManyToOne 关联，MyBatis-Plus 用普通外键字段） */
    @JsonIgnore
    private Long recipeId;

    private String name;

    private String amount;

    private String unit;

    /** 是否必需（区分主料和辅料） */
    private Boolean isEssential = true;

    /** 排序 */
    private Integer sortOrder = 0;

    /** 食材图片（相对路径，如 /api/ingredients/xx.jpg） */
    private String imageUrl;
}
