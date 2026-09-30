package com.goodzheng.po.identity.dto;

import lombok.Data;

@Data
public class LoginResponse {

    private Long id;
    private String token;
    private String username;
    private String nickname;
    private String role;
    private String phoneNumber;
    private String approvalStatus;

    public LoginResponse(Long id, String token, String username, String nickname, String role,
                         String phoneNumber, String approvalStatus) {
        this.id = id;
        this.token = token;
        this.username = username;
        this.nickname = nickname;
        this.role = role;
        this.phoneNumber = phoneNumber;
        this.approvalStatus = approvalStatus;
    }

    public static LoginResponse approved(Long id, String token, String username, String nickname,
                                         String role, String phoneNumber) {
        return new LoginResponse(id, token, username, nickname, role, phoneNumber, "approved");
    }

    public static LoginResponse pending(Long id, String username, String nickname) {
        return new LoginResponse(id, null, username, nickname, "user", null, "pending");
    }

    public static LoginResponse rejected(Long id, String username, String nickname) {
        return new LoginResponse(id, null, username, nickname, "user", null, "rejected");
    }
}
