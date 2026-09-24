package com.goodzheng.po.recipe.service;

import com.goodzheng.po.recipe.dto.RecipeCategoryRequest;
import com.goodzheng.po.recipe.entity.RecipeCategory;

import java.util.List;

public interface RecipeCategoryService {

    /** 查询所有未删除的分类，按 sortOrder 升序 */
    List<RecipeCategory> listAll();

    /** 新建分类（名称去重） */
    RecipeCategory create(RecipeCategoryRequest request);

    /** 更新分类（名称去重） */
    RecipeCategory update(Long id, RecipeCategoryRequest request);

    /** 软删除分类（分类下仍有启用菜谱时不允许删除） */
    void delete(Long id);
}
