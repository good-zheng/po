package com.goodzheng.po.recipe.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.recipe.entity.RecipeCategory;
import com.goodzheng.po.recipe.repository.RecipeCategoryMapper;
import com.goodzheng.po.recipe.service.RecipeCategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RecipeCategoryServiceImpl implements RecipeCategoryService {

    private final RecipeCategoryMapper recipeCategoryMapper;

    @Override
    @Transactional(readOnly = true)
    public List<RecipeCategory> listAll() {
        return recipeCategoryMapper.selectList(new LambdaQueryWrapper<RecipeCategory>()
                .isNull(RecipeCategory::getDeletedAt)
                .orderByAsc(RecipeCategory::getSortOrder)
                .orderByAsc(RecipeCategory::getId));
    }
}
