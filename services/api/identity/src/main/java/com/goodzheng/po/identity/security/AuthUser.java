package com.goodzheng.po.identity.security;

import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.constant.UserStatusConstants;

/**
 * JWT 解析出的登录主体。
 * 角色、状态、来源均随令牌下发，鉴权时不再回库查询。
 */
public record AuthUser(Long id, String username, String role, String status, String client) {

    public boolean isActive() {
        return UserStatusConstants.ACTIVE.equals(status);
    }

    public boolean isSuperAdmin() {
        return RoleConstants.SUPER_ADMIN.equals(role);
    }

    /** 管理员或超级管理员 */
    public boolean isManager() {
        return isSuperAdmin() || RoleConstants.ADMIN.equals(role);
    }
}
