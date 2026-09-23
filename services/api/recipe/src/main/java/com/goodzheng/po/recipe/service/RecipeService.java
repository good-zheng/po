package com.goodzheng.po.recipe.service;

import com.goodzheng.po.recipe.dto.RecipeRequest;
import com.goodzheng.po.recipe.entity.Recipe;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

public interface RecipeService {

    /**
     * 创建菜谱。
     *
     * @param initialStatus 初始审核状态：管理端创建为 approved，App 用户创建为 pending（待审核）
     */
    Recipe create(RecipeRequest request, Long authorId, String initialStatus);

    Recipe getById(Long id);

    /**
     * 筛选排序列表（公开浏览入口）：仅返回已通过审核且公开、未删除的菜谱。
     *
     * @param keyword    名称/描述/标签模糊搜索，可空
     * @param categoryIds 分类 ID 列表（先解析为分类名再匹配），可空
     * @param difficulty 难度 1/2/3，可空
     * @param sort       recommend（默认，点赞加权+时间衰减）/ likes（点赞降序）/ newest（最新发布）
     */
    Page<Recipe> filteredList(String keyword, List<Long> categoryIds, Integer difficulty,
            String sort, Pageable pageable);

    /** 管理端审核队列：按状态筛选（可空=全部），关键词模糊匹配标题 */
    Page<Recipe> reviewList(String status, String keyword, Pageable pageable);

    /** 我的菜谱：返回作者全部状态（含待审核/已驳回），用于移动端审核状态展示 */
    Page<Recipe> listByAuthor(Long authorId, Pageable pageable);

    /**
     * 更新菜谱。管理员可改任意菜谱；作者本人只能改自己的，
     * 普通作者每次修改后状态重置为 pending（重新送审）、清空驳回原因。
     */
    Recipe update(Long id, RecipeRequest request, Long operatorId, boolean operatorManager);

    /** 删除（软删除）。管理员可删任意；作者只能删自己的。 */
    void delete(Long id, Long operatorId, boolean operatorManager);

    /** 管理端审核：action=approve 通过 / reject 驳回（驳回必须填原因） */
    void audit(Long id, String action, String reason);

    /** 是否公开可见：已通过审核 + 公开 + 未删除 */
    boolean isVisible(Recipe recipe);
}
