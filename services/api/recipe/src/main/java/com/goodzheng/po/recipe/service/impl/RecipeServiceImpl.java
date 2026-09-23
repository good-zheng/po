package com.goodzheng.po.recipe.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.recipe.constant.RecipeStatusConstants;
import com.goodzheng.po.recipe.dto.RecipeRequest;
import com.goodzheng.po.recipe.entity.Ingredient;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.entity.RecipeCategory;
import com.goodzheng.po.recipe.entity.Step;
import com.goodzheng.po.recipe.repository.IngredientMapper;
import com.goodzheng.po.recipe.repository.RecipeCategoryMapper;
import com.goodzheng.po.recipe.repository.RecipeMapper;
import com.goodzheng.po.recipe.repository.StepMapper;
import com.goodzheng.po.recipe.service.RecipeService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class RecipeServiceImpl implements RecipeService {

    private final RecipeMapper recipeMapper;
    private final IngredientMapper ingredientMapper;
    private final StepMapper stepMapper;
    private final RecipeCategoryMapper recipeCategoryMapper;

    @Override
    @Transactional
    public Recipe create(RecipeRequest req, Long authorId, String initialStatus) {
        Recipe recipe = new Recipe();
        mapToEntity(req, recipe);
        recipe.setAuthorId(authorId);
        recipe.setStatus(initialStatus);
        recipe.setRejectReason(null);
        recipeMapper.insert(recipe);
        saveChildren(recipe, req);
        return recipe;
    }

    @Override
    @Transactional(readOnly = true)
    public Recipe getById(Long id) {
        Recipe recipe = recipeMapper.selectDetailWithChildren(id);
        if (recipe == null) {
            throw new RuntimeException("菜谱不存在");
        }
        if (recipe.getDeletedAt() != null) {
            throw new RuntimeException("菜谱已删除");
        }
        return recipe;
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> filteredList(String keyword, List<Long> categoryIds, Integer difficulty,
            String sort, Pageable pageable) {
        List<String> categoryNames = resolveCategoryNames(categoryIds);
        if (categoryIds != null && !categoryIds.isEmpty() && categoryNames.isEmpty()) {
            // 传入的分类不存在，结果必为空
            return new PageImpl<>(List.of(), pageable, 0);
        }
        String orderBy = toOrderBy(sort);
        var mpPage = MyBatisPages.<Recipe>toMpPage(pageable);
        recipeMapper.selectFilteredPage(mpPage, keyword, categoryNames, difficulty, orderBy);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> reviewList(String status, String keyword, Pageable pageable) {
        LambdaQueryWrapper<Recipe> wrapper = new LambdaQueryWrapper<Recipe>()
                .isNull(Recipe::getDeletedAt);
        if (status != null && !status.isBlank()) {
            if (!RecipeStatusConstants.isValid(status)) {
                throw new RuntimeException("非法审核状态: " + status);
            }
            wrapper.eq(Recipe::getStatus, status);
        }
        if (keyword != null && !keyword.isBlank()) {
            wrapper.like(Recipe::getTitle, keyword);
        }
        wrapper.orderByAsc(Recipe::getCreatedAt);
        return page(wrapper, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> listByAuthor(Long authorId, Pageable pageable) {
        return page(new LambdaQueryWrapper<Recipe>()
                .eq(Recipe::getAuthorId, authorId)
                .isNull(Recipe::getDeletedAt), pageable);
    }

    @Override
    @Transactional
    public Recipe update(Long id, RecipeRequest req, Long operatorId, boolean operatorManager) {
        Recipe recipe = getById(id);
        checkOwnership(recipe, operatorId, operatorManager);

        mapToEntity(req, recipe);
        if (!operatorManager) {
            // 普通作者修改后重新送审
            recipe.setStatus(RecipeStatusConstants.PENDING);
            recipe.setRejectReason(null);
        }
        recipeMapper.updateById(recipe);

        // 替换食材与步骤：先删后插（等价原 JPA orphanRemoval 的删旧插新行为）
        ingredientMapper.delete(new LambdaQueryWrapper<Ingredient>().eq(Ingredient::getRecipeId, id));
        stepMapper.delete(new LambdaQueryWrapper<Step>().eq(Step::getRecipeId, id));
        recipe.getIngredients().clear();
        recipe.getSteps().clear();
        saveChildren(recipe, req);

        return recipe;
    }

    @Override
    @Transactional
    public void delete(Long id, Long operatorId, boolean operatorManager) {
        Recipe recipe = getById(id);
        checkOwnership(recipe, operatorId, operatorManager);
        recipe.setDeletedAt(LocalDateTime.now());
        recipeMapper.updateById(recipe);
    }

    @Override
    @Transactional
    public void audit(Long id, String action, String reason) {
        Recipe recipe = getById(id);
        if ("approve".equals(action)) {
            recipe.setStatus(RecipeStatusConstants.APPROVED);
            recipe.setRejectReason(null);
        } else if ("reject".equals(action)) {
            if (reason == null || reason.isBlank()) {
                throw new RuntimeException("驳回必须填写原因");
            }
            recipe.setStatus(RecipeStatusConstants.REJECTED);
            recipe.setRejectReason(reason);
        } else {
            throw new RuntimeException("非法审核动作: " + action);
        }
        recipeMapper.updateById(recipe);
    }

    @Override
    public boolean isVisible(Recipe recipe) {
        return RecipeStatusConstants.APPROVED.equals(recipe.getStatus())
                && Boolean.TRUE.equals(recipe.getIsPublic())
                && recipe.getDeletedAt() == null;
    }

    // ── 工具方法 ──────────────────────────────────────────

    /** 排序白名单（拼接进 ORDER BY，只允许这里的固定值，防止 SQL 注入） */
    private String toOrderBy(String sort) {
        if ("likes".equals(sort)) {
            return "r.likes_count DESC, r.id DESC";
        }
        if ("newest".equals(sort)) {
            return "r.created_at DESC, r.id DESC";
        }
        // recommend（默认）：点赞加权 - 时间衰减（小时），新发布的高赞内容优先
        return "(r.likes_count * 5 - TIMESTAMPDIFF(HOUR, r.created_at, NOW())) DESC, r.id DESC";
    }

    private List<String> resolveCategoryNames(List<Long> categoryIds) {
        if (categoryIds == null || categoryIds.isEmpty()) {
            return List.of();
        }
        return recipeCategoryMapper.selectList(new LambdaQueryWrapper<RecipeCategory>()
                        .select(RecipeCategory::getName)
                        .in(RecipeCategory::getId, categoryIds))
                .stream().map(RecipeCategory::getName).toList();
    }

    private void checkOwnership(Recipe recipe, Long operatorId, boolean operatorManager) {
        if (operatorManager) {
            return;
        }
        if (recipe.getAuthorId() == null || !recipe.getAuthorId().equals(operatorId)) {
            throw new RuntimeException("只能操作自己创建的菜谱");
        }
    }

    private Page<Recipe> page(LambdaQueryWrapper<Recipe> wrapper, Pageable pageable) {
        var mpPage = MyBatisPages.<Recipe>toMpPage(pageable);
        recipeMapper.selectPage(mpPage, wrapper);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    private void saveChildren(Recipe recipe, RecipeRequest req) {
        if (req.getIngredients() != null) {
            for (RecipeRequest.IngredientItem item : req.getIngredients()) {
                Ingredient ing = new Ingredient();
                ing.setName(item.getName());
                ing.setAmount(item.getAmount());
                ing.setUnit(item.getUnit());
                ing.setIsEssential(item.getIsEssential());
                ing.setSortOrder(item.getSortOrder());
                ing.setImageUrl(item.getImageUrl());
                ing.setRecipeId(recipe.getId());
                ingredientMapper.insert(ing);
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
                step.setRecipeId(recipe.getId());
                stepMapper.insert(step);
                recipe.getSteps().add(step);
            }
        }
    }

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
