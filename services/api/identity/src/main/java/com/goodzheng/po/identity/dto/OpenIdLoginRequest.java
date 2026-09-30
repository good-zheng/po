package com.goodzheng.po.identity.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class OpenIdLoginRequest {

    @NotBlank(message = "微信登录 code 不能为空")
    private String loginCode;
}
