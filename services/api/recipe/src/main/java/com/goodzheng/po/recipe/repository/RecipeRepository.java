package com.goodzheng.po.recipe.repository;

import com.goodzheng.po.recipe.entity.Recipe;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface RecipeRepository extends JpaRepository<Recipe, Long> {

    /** 查询单个菜谱（JOIN FETCH 预加载食材和步骤，避免 LazyInitializationException） */
    @Query("SELECT r FROM Recipe r LEFT JOIN FETCH r.ingredients LEFT JOIN FETCH r.steps WHERE r.id = :id")
    Optional<Recipe> findByIdWithDetails(Long id);

    /** 查询未软删除的菜谱（分页） */
    Page<Recipe> findByDeletedAtIsNull(Pageable pageable);

    /** 按作者查询未删除的菜谱 */
    Page<Recipe> findByAuthorIdAndDeletedAtIsNull(Long authorId, Pageable pageable);

    /** 按分类查询（单个） */
    Page<Recipe> findByCategoryAndDeletedAtIsNull(String category, Pageable pageable);

    /** 按多个分类查询（OR 包含关系） */
    Page<Recipe> findByCategoryInAndDeletedAtIsNull(List<String> categories, Pageable pageable);

    /** 关键字搜索（标题/描述） */
    Page<Recipe> findByDeletedAtIsNullAndTitleContainingOrDeletedAtIsNullAndDescriptionContaining(
            String title, String description, Pageable pageable);
}
