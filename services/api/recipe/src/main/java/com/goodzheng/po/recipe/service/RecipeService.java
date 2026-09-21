package com.goodzheng.po.recipe.service;

import com.goodzheng.po.recipe.dto.RecipeRequest;
import com.goodzheng.po.recipe.entity.Recipe;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface RecipeService {

    Recipe create(RecipeRequest request, Long authorId);

    Recipe getById(Long id);

    Page<Recipe> list(Pageable pageable);

    Page<Recipe> listByAuthor(Long authorId, Pageable pageable);

    Page<Recipe> listByCategories(List<Long> categoryIds, Pageable pageable);

    Page<Recipe> search(String keyword, Pageable pageable);

    Recipe update(Long id, RecipeRequest request, Long authorId);

    void delete(Long id, Long authorId);
}
