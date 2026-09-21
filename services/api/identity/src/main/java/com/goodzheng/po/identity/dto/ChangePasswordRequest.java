package com.goodzheng.po.identity.dto;

import lombok.Data;

/**
 * 当前用户修改密码的请求体（规则校验在 Service 层执行，保证错误响应统一走 Result 结构）
 */
@Data
public class ChangePasswordRequest {

    private String oldPassword;

    private String newPassword;
}
