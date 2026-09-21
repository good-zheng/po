package com.goodzheng.po.identity.constant;

/**
 * 系统角色常量（三级权限体系）
 */
public final class RoleConstants {

    /** 超级管理员：拥有全部权限，可管理任何用户及其角色 */
    public static final String SUPER_ADMIN = "superadmin";

    /** 管理员：可管理普通用户（含角色调整 user<->admin），不能操作超级管理员 */
    public static final String ADMIN = "admin";

    /** 普通用户：仅基础业务权限 */
    public static final String USER = "user";

    private RoleConstants() {
    }

    /** 判断是否为合法角色值 */
    public static boolean isValid(String role) {
        return SUPER_ADMIN.equals(role) || ADMIN.equals(role) || USER.equals(role);
    }
}
