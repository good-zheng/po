package com.goodzheng.po.identity.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class LoginResponse {

    private Long id;
    private String token;
    private String username;
    private String nickname;
    private String role;
}
