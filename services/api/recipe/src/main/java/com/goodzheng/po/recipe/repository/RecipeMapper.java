package com.goodzheng.po.recipe.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.goodzheng.po.recipe.entity.Recipe;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface RecipeMapper extends BaseMapper<Recipe> {

    /** 一次连表查询菜谱详情及其食材、步骤（SQL 见 resources/mapper/RecipeMapper.xml） */
    Recipe selectDetailWithChildren(@Param("id") Long id);

    /**
     * 公开列表筛选排序分页（SQL 见 resources/mapper/RecipeMapper.xml）。
     * 固定只返回已通过审核、公开、未删除的菜谱；orderBy 由 Service 排序白名单生成。
     */
    Page<Recipe> selectFilteredPage(Page<Recipe> page, @Param("keyword") String keyword,
            @Param("categories") List<String> categories, @Param("difficulty") Integer difficulty,
            @Param("orderBy") String orderBy);
}
