package com.goodzheng.po.recipe.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.goodzheng.po.recipe.entity.Step;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface StepMapper extends BaseMapper<Step> {
}
