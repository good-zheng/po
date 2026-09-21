package com.goodzheng.po.recipe.service;

import com.goodzheng.po.recipe.entity.RecipeCategory;

import java.util.List;

public interface RecipeCategoryService {

    /** 查询所有未删除的分类，按 sortOrder 升序 */
    List<RecipeCategory> listAll();
}
