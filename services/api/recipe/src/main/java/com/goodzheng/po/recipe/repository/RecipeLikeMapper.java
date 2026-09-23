package com.goodzheng.po.recipe.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.goodzheng.po.recipe.entity.RecipeLike;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface RecipeLikeMapper extends BaseMapper<RecipeLike> {
}
