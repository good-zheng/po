package com.goodzheng.po.recipe.service;

import com.goodzheng.po.recipe.dto.LikeResult;
import com.goodzheng.po.recipe.entity.Recipe;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

/** 菜谱交互：收藏、点赞、浏览历史（均需登录，仅对已发布的菜谱生效） */
public interface RecipeInteractionService {

    /** 收藏（幂等，重复收藏无副作用） */
    void favorite(Long userId, Long recipeId);

    /** 取消收藏（幂等） */
    void unfavorite(Long userId, Long recipeId);

    /** 我的收藏列表（按收藏时间倒序，仅未删除菜谱） */
    Page<Recipe> listFavorites(Long userId, Pageable pageable);

    /** 点赞/取消点赞切换，返回切换后状态与最新点赞数 */
    LikeResult toggleLike(Long userId, Long recipeId);

    /** 记录浏览（同菜谱重复浏览覆盖时间），仅对公开可见菜谱生效 */
    void recordHistory(Long userId, Long recipeId);

    /** 我的浏览历史（按最近浏览时间倒序，仅未删除菜谱） */
    Page<Recipe> listHistory(Long userId, Pageable pageable);

    /** 批量填充当前用户视角的 isFavorited / isLiked 标记（列表接口用） */
    void fillFlags(Long userId, List<Recipe> recipes);
}
