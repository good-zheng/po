package com.goodzheng.po.recipe.repository;

import com.goodzheng.po.recipe.entity.RecipeCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface RecipeCategoryRepository extends JpaRepository<RecipeCategory, Long> {

    List<RecipeCategory> findByDeletedAtIsNullOrderBySortOrderAscIdAsc();

    /** 根据 ID 列表查询分类名称 */
    @Query("SELECT c.name FROM RecipeCategory c WHERE c.id IN :ids")
    List<String> findNamesByIdIn(@Param("ids") List<Long> ids);
}
