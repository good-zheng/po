package com.goodzheng.po.identity.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class UserRequest {

    @NotBlank(message = "用户名不能为空")
    private String username;

    private String password;

    private String email;

    private String firstName;

    private String lastName;

    private String phoneNumber;

    private String role;

    private String status;

    private String nickname;

    private String avatar;
}
