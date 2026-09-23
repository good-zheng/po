package com.goodzheng.po.recipe.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.goodzheng.po.recipe.dto.LikeResult;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.entity.RecipeFavorite;
import com.goodzheng.po.recipe.entity.RecipeLike;
import com.goodzheng.po.recipe.repository.RecipeFavoriteMapper;
import com.goodzheng.po.recipe.repository.RecipeHistoryMapper;
import com.goodzheng.po.recipe.repository.RecipeLikeMapper;
import com.goodzheng.po.recipe.repository.RecipeMapper;
import com.goodzheng.po.recipe.service.RecipeInteractionService;
import com.goodzheng.po.recipe.service.RecipeService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RecipeInteractionServiceImpl implements RecipeInteractionService {

    private final RecipeMapper recipeMapper;
    private final RecipeFavoriteMapper favoriteMapper;
    private final RecipeLikeMapper likeMapper;
    private final RecipeHistoryMapper historyMapper;
    private final RecipeService recipeService;

    @Override
    @Transactional
    public void favorite(Long userId, Long recipeId) {
        checkVisible(recipeId);
        Long count = favoriteMapper.selectCount(new LambdaQueryWrapper<RecipeFavorite>()
                .eq(RecipeFavorite::getUserId, userId)
                .eq(RecipeFavorite::getRecipeId, recipeId));
        if (count == 0) {
            RecipeFavorite favorite = new RecipeFavorite();
            favorite.setUserId(userId);
            favorite.setRecipeId(recipeId);
            try {
                favoriteMapper.insert(favorite);
            } catch (DuplicateKeyException ignored) {
                // 并发重复收藏，唯一键兜底
            }
        }
    }

    @Override
    @Transactional
    public void unfavorite(Long userId, Long recipeId) {
        favoriteMapper.delete(new LambdaQueryWrapper<RecipeFavorite>()
                .eq(RecipeFavorite::getUserId, userId)
                .eq(RecipeFavorite::getRecipeId, recipeId));
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> listFavorites(Long userId, Pageable pageable) {
        var mpPage = MyBatisPages.<Recipe>toMpPage(pageable);
        favoriteMapper.selectFavoritePage(mpPage, userId);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional
    public LikeResult toggleLike(Long userId, Long recipeId) {
        checkVisible(recipeId);
        Long count = likeMapper.selectCount(new LambdaQueryWrapper<RecipeLike>()
                .eq(RecipeLike::getUserId, userId)
                .eq(RecipeLike::getRecipeId, recipeId));
        boolean liked;
        if (count > 0) {
            likeMapper.delete(new LambdaQueryWrapper<RecipeLike>()
                    .eq(RecipeLike::getUserId, userId)
                    .eq(RecipeLike::getRecipeId, recipeId));
            // likes_count >= 1 才减，防止并发下减成负数
            recipeMapper.update(null, new UpdateWrapper<Recipe>()
                    .eq("id", recipeId)
                    .ge("likes_count", 1)
                    .setSql("likes_count = likes_count - 1"));
            liked = false;
        } else {
            RecipeLike like = new RecipeLike();
            like.setUserId(userId);
            like.setRecipeId(recipeId);
            try {
                likeMapper.insert(like);
                recipeMapper.update(null, new UpdateWrapper<Recipe>()
                        .eq("id", recipeId)
                        .setSql("likes_count = likes_count + 1"));
            } catch (DuplicateKeyException ignored) {
                // 并发重复点赞，唯一键兜底；计数不重复加
            }
            liked = true;
        }
        Recipe updated = recipeMapper.selectById(recipeId);
        return new LikeResult(liked, updated.getLikesCount() == null ? 0 : updated.getLikesCount());
    }

    @Override
    @Transactional
    public void recordHistory(Long userId, Long recipeId) {
        Recipe recipe = recipeMapper.selectById(recipeId);
        if (recipe == null || !recipeService.isVisible(recipe)) {
            return;
        }
        historyMapper.upsertView(userId, recipeId);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<Recipe> listHistory(Long userId, Pageable pageable) {
        var mpPage = MyBatisPages.<Recipe>toMpPage(pageable);
        historyMapper.selectHistoryPage(mpPage, userId);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public void fillFlags(Long userId, List<Recipe> recipes) {
        if (userId == null || recipes == null || recipes.isEmpty()) {
            return;
        }
        List<Long> ids = recipes.stream().map(Recipe::getId).toList();
        Set<Long> favorited = favoriteMapper.selectList(new LambdaQueryWrapper<RecipeFavorite>()
                        .select(RecipeFavorite::getRecipeId)
                        .eq(RecipeFavorite::getUserId, userId)
                        .in(RecipeFavorite::getRecipeId, ids))
                .stream().map(RecipeFavorite::getRecipeId).collect(Collectors.toSet());
        Set<Long> liked = likeMapper.selectList(new LambdaQueryWrapper<RecipeLike>()
                        .select(RecipeLike::getRecipeId)
                        .eq(RecipeLike::getUserId, userId)
                        .in(RecipeLike::getRecipeId, ids))
                .stream().map(RecipeLike::getRecipeId).collect(Collectors.toSet());
        recipes.forEach(r -> {
            r.setIsFavorited(favorited.contains(r.getId()));
            r.setIsLiked(liked.contains(r.getId()));
        });
    }

    private void checkVisible(Long recipeId) {
        Recipe recipe = recipeMapper.selectById(recipeId);
        if (recipe == null || !recipeService.isVisible(recipe)) {
            throw new RuntimeException("菜谱不存在或未发布");
        }
    }
}
