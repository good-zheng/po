package com.goodzheng.po.recipe.constant;

/**
 * 菜谱审核状态。
 * App 用户创建的菜谱进入 pending，管理端审核后流转为 approved / rejected。
 */
public final class RecipeStatusConstants {

    public static final String PENDING = "pending";

    public static final String APPROVED = "approved";

    public static final String REJECTED = "rejected";

    private RecipeStatusConstants() {
    }

    public static boolean isValid(String status) {
        return PENDING.equals(status) || APPROVED.equals(status) || REJECTED.equals(status);
    }
}
