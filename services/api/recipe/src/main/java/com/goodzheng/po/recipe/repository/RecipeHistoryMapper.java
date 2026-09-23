package com.goodzheng.po.recipe.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.entity.RecipeHistory;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface RecipeHistoryMapper extends BaseMapper<RecipeHistory> {

    /** 记录浏览：同用户同菜谱重复浏览时覆盖 viewed_at（SQL 见 resources/mapper/RecipeHistoryMapper.xml） */
    void upsertView(@Param("userId") Long userId, @Param("recipeId") Long recipeId);

    /** 我的浏览历史分页（JOIN recipe，按最近浏览时间倒序，SQL 见 resources/mapper/RecipeHistoryMapper.xml） */
    Page<Recipe> selectHistoryPage(Page<Recipe> page, @Param("userId") Long userId);
}
