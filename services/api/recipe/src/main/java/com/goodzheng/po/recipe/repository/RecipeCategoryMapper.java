package com.goodzheng.po.recipe.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.goodzheng.po.recipe.entity.RecipeCategory;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface RecipeCategoryMapper extends BaseMapper<RecipeCategory> {
}
