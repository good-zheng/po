package com.goodzheng.po.recipe.service.impl;

import com.goodzheng.po.recipe.dto.RecipeRequest;
import com.goodzheng.po.recipe.entity.Ingredient;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.entity.Step;
import com.goodzheng.po.recipe.repository.RecipeCategoryRepository;
import com.goodzheng.po.recipe.repository.RecipeRepository;
import com.goodzheng.po.recipe.service.RecipeService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RecipeServiceImpl implements RecipeService {

    private final RecipeRepository recipeRepository;
    private final RecipeCategoryRepository recipeCategoryRepository;

    @Override
    @Transactional
    public Recipe create(RecipeRequest req, Long authorId) {
        Recipe recipe = new Recipe();
        mapToEntity(req, recipe);
        recipe.setAuthorId(authorId);

        if (req.getIngredients() != null) {
            for (RecipeRequest.IngredientItem item : req.getIngredients()) {
                Ingredient ing = new Ingredient();
                ing.setName(item.getName());
                ing.setAmount(item.getAmount());
                ing.setUnit(item.getUnit());
                ing.setIsEssential(item.getIsEssential());
                ing.setSortOrder(item.getSortOrder());
                ing.setRecipe(recipe);
                recipe.getIngredients().add(ing);
            }
        }

        if (req.getSteps() != null) {
            for (RecipeRequest.StepItem item : req.getSteps()) {
                Step step = new Step();
                step.setStepNumber(item.getStepNumber());
                step.setContent(item.getContent());
                step.setImageUrl(item.getImageUrl());
                step.setVideoUrl(item.getVideoUrl());
                step.setDuration(item.getDuration());
                step.setRecipe(recipe);
                recipe.getSteps().add(step);
            }
        }

        return recipeRepository.save(recipe);
    }

    @Override
    @Transactional(readOnly = true)
    public Recipe getById(Long id) {
        Recipe recipe = recipeRepository.findByIdWithDetails(id)
                .orElseThrow(() -> new RuntimeException("菜谱不存在"));
        if (recipe.getDeletedAt() != null) {
            throw new RuntimeException("菜谱已删除");
        }
        return recipe;
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> list(Pageable pageable) {
        return recipeRepository.findByDeletedAtIsNull(pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> listByAuthor(Long authorId, Pageable pageable) {
        return recipeRepository.findByAuthorIdAndDeletedAtIsNull(authorId, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> listByCategories(List<Long> categoryIds, Pageable pageable) {
        List<String> categoryNames = recipeCategoryRepository.findNamesByIdIn(categoryIds);
        return recipeRepository.findByCategoryInAndDeletedAtIsNull(categoryNames, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> search(String keyword, Pageable pageable) {
        return recipeRepository.findByDeletedAtIsNullAndTitleContainingOrDeletedAtIsNullAndDescriptionContaining(
                keyword, keyword, pageable);
    }

    @Override
    @Transactional
    public Recipe update(Long id, RecipeRequest req, Long authorId) {
        Recipe recipe = getById(id);
        if (!recipe.getAuthorId().equals(authorId)) {
            throw new RuntimeException("无权修改他人菜谱");
        }

        mapToEntity(req, recipe);

        // 替换食材列表
        recipe.getIngredients().clear();
        if (req.getIngredients() != null) {
            for (RecipeRequest.IngredientItem item : req.getIngredients()) {
                Ingredient ing = new Ingredient();
                ing.setName(item.getName());
                ing.setAmount(item.getAmount());
                ing.setUnit(item.getUnit());
                ing.setIsEssential(item.getIsEssential());
                ing.setSortOrder(item.getSortOrder());
                ing.setRecipe(recipe);
                recipe.getIngredients().add(ing);
            }
        }

        // 替换步骤列表
        recipe.getSteps().clear();
        if (req.getSteps() != null) {
            for (RecipeRequest.StepItem item : req.getSteps()) {
                Step step = new Step();
                step.setStepNumber(item.getStepNumber());
                step.setContent(item.getContent());
                step.setImageUrl(item.getImageUrl());
                step.setVideoUrl(item.getVideoUrl());
                step.setDuration(item.getDuration());
                step.setRecipe(recipe);
                recipe.getSteps().add(step);
            }
        }

        return recipeRepository.save(recipe);
    }

    @Override
    @Transactional
    public void delete(Long id, Long authorId) {
        Recipe recipe = getById(id);
        if (!recipe.getAuthorId().equals(authorId)) {
            throw new RuntimeException("无权删除他人菜谱");
        }
        recipe.setDeletedAt(LocalDateTime.now());
        recipeRepository.save(recipe);
    }

    // ── 工具方法 ──────────────────────────────────────────
    private void mapToEntity(RecipeRequest req, Recipe recipe) {
        recipe.setTitle(req.getTitle());
        recipe.setDescription(req.getDescription());
        recipe.setCoverImageUrl(req.getCoverImageUrl());
        recipe.setPrepTime(req.getPrepTime());
        recipe.setCookTime(req.getCookTime());
        recipe.setTotalTime(req.getTotalTime());
        recipe.setDifficulty(req.getDifficulty());
        recipe.setServings(req.getServings());
        recipe.setCategory(req.getCategory());
        recipe.setTags(req.getTags());
        recipe.setIsPublic(req.getIsPublic());
        recipe.setCalories(req.getCalories());
        recipe.setProtein(req.getProtein());
        recipe.setFat(req.getFat());
        recipe.setCarbs(req.getCarbs());
        recipe.setTips(req.getTips());
        recipe.setFlavorProfile(req.getFlavorProfile());
    }
}
