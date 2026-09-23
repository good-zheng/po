package com.goodzheng.po.recipe.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("recipe_history")
public class RecipeHistory {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long recipeId;

    /** 最近浏览时间；重复浏览同一路径时覆盖更新 */
    private LocalDateTime viewedAt = LocalDateTime.now();
}
