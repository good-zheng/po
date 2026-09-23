package com.goodzheng.po.identity.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class LoginRequest {

    @NotBlank(message = "用户名不能为空")
    private String username;

    @NotBlank(message = "密码不能为空")
    private String password;

    /** 登录来源：admin=管理后台，app=移动端；决定可登录的角色范围 */
    @NotBlank(message = "登录来源不能为空")
    private String client;
}
