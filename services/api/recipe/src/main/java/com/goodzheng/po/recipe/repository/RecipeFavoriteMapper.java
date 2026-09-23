package com.goodzheng.po.recipe.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.goodzheng.po.recipe.entity.Recipe;
import com.goodzheng.po.recipe.entity.RecipeFavorite;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface RecipeFavoriteMapper extends BaseMapper<RecipeFavorite> {

    /** 我的收藏分页（JOIN recipe，按收藏时间倒序，SQL 见 resources/mapper/RecipeFavoriteMapper.xml） */
    Page<Recipe> selectFavoritePage(Page<Recipe> page, @Param("userId") Long userId);
}

