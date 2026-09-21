package com.goodzheng.po.recipe.service.impl;

import com.goodzheng.po.recipe.entity.RecipeCategory;
import com.goodzheng.po.recipe.repository.RecipeCategoryRepository;
import com.goodzheng.po.recipe.service.RecipeCategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class RecipeCategoryServiceImpl implements RecipeCategoryService {

    private final RecipeCategoryRepository recipeCategoryRepository;

    @Override
    @Transactional(readOnly = true)
    public List<RecipeCategory> listAll() {
        return recipeCategoryRepository.findByDeletedAtIsNullOrderBySortOrderAscIdAsc();
    }
}
