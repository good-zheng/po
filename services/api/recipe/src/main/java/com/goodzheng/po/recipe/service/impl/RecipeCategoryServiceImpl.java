package com.goodzheng.po.recipe.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.recipe.dto.RecipeCategoryRequest;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.entity.RecipeCategory;
import com.goodzheng.po.recipe.repository.RecipeCategoryMapper;
import com.goodzheng.po.recipe.repository.RecipeMapper;
import com.goodzheng.po.recipe.service.RecipeCategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RecipeCategoryServiceImpl implements RecipeCategoryService {

    private final RecipeCategoryMapper recipeCategoryMapper;
    private final RecipeMapper recipeMapper;

    @Override
    @Transactional(readOnly = true)
    public List<RecipeCategory> listAll() {
        return recipeCategoryMapper.selectList(new LambdaQueryWrapper<RecipeCategory>()
                .isNull(RecipeCategory::getDeletedAt)
                .orderByAsc(RecipeCategory::getSortOrder)
                .orderByAsc(RecipeCategory::getId));
    }

    @Override
    @Transactional
    public RecipeCategory create(RecipeCategoryRequest request) {
        assertNameUnique(request.getName(), null);
        RecipeCategory category = new RecipeCategory();
        category.setName(request.getName());
        category.setIcon(request.getIcon());
        category.setDescription(request.getDescription());
        category.setSortOrder(request.getSortOrder() != null ? request.getSortOrder() : 0);
        recipeCategoryMapper.insert(category);
        return category;
    }

    @Override
    @Transactional
    public RecipeCategory update(Long id, RecipeCategoryRequest request) {
        RecipeCategory category = requireCategory(id);
        assertNameUnique(request.getName(), id);
        category.setName(request.getName());
        category.setIcon(request.getIcon());
        category.setDescription(request.getDescription());
        category.setSortOrder(request.getSortOrder() != null ? request.getSortOrder() : 0);
        recipeCategoryMapper.updateById(category);
        return category;
    }

    @Override
    @Transactional
    public void delete(Long id) {
        RecipeCategory category = requireCategory(id);
        // 分类名以字符串形式冗余在菜谱上，仍有未删除菜谱引用时不允许删除
        Long referenced = recipeMapper.selectCount(new LambdaQueryWrapper<Recipe>()
                .eq(Recipe::getCategory, category.getName())
                .isNull(Recipe::getDeletedAt));
        if (referenced > 0) {
            throw new RuntimeException("该分类下仍有 " + referenced + " 道菜，请先调整这些菜谱的分类");
        }
        category.setDeletedAt(LocalDateTime.now());
        recipeCategoryMapper.updateById(category);
    }

    private RecipeCategory requireCategory(Long id) {
        RecipeCategory category = recipeCategoryMapper.selectById(id);
        if (category == null || category.getDeletedAt() != null) {
            throw new RuntimeException("分类不存在");
        }
        return category;
    }

    private void assertNameUnique(String name, Long excludeId) {
        Long count = recipeCategoryMapper.selectCount(new LambdaQueryWrapper<RecipeCategory>()
                .eq(RecipeCategory::getName, name)
                .isNull(RecipeCategory::getDeletedAt)
                .ne(excludeId != null, RecipeCategory::getId, excludeId));
        if (count > 0) {
            throw new RuntimeException("分类名称已存在: " + name);
        }
    }
}
