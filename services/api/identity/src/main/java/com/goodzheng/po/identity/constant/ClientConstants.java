package com.goodzheng.po.identity.constant;

/**
 * 登录来源（客户端）标识。
 * 管理端与移动端双向隔离：管理端只接受管理员角色，移动端只接受普通用户角色。
 */
public final class ClientConstants {

    /** 管理后台（Ant Design Pro） */
    public static final String ADMIN = "admin";

    /** 移动端 App（Expo） */
    public static final String APP = "app";

    private ClientConstants() {
    }

    public static boolean isValid(String client) {
        return ADMIN.equals(client) || APP.equals(client);
    }

    /** 该来源允许登录的角色 */
    public static boolean allowsRole(String client, String role) {
        if (ADMIN.equals(client)) {
            return RoleConstants.ADMIN.equals(role) || RoleConstants.SUPER_ADMIN.equals(role);
        }
        if (APP.equals(client)) {
            return RoleConstants.USER.equals(role);
        }
        return false;
    }
}
