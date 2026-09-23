package com.goodzheng.po.identity.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

/**
 * 当前用户自助更新个人资料的请求体（不含角色/状态/密码等敏感字段）
 */
@Data
public class ProfileRequest {

    @Size(max = 30, message = "昵称不能超过 30 个字符")
    private String nickname;

    @Email(message = "邮箱格式不正确")
    @Size(max = 100)
    private String email;

    /** 中国大陆手机号，允许空串表示清除已填写的手机号 */
    @Pattern(regexp = "^$|^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phoneNumber;

    private String avatar;
}
