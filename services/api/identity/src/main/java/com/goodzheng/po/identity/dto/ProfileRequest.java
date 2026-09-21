package com.goodzheng.po.identity.dto;

import lombok.Data;

/**
 * 当前用户自助更新个人资料的请求体（不含角色/状态/密码等敏感字段）
 */
@Data
public class ProfileRequest {

    private String nickname;

    private String email;

    private String phoneNumber;

    private String avatar;
}
