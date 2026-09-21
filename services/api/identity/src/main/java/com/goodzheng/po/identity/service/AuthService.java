package com.goodzheng.po.identity.service;

import com.goodzheng.po.identity.dto.LoginRequest;
import com.goodzheng.po.identity.dto.LoginResponse;

public interface AuthService {

    String register(String username, String password, String email);

    LoginResponse login(LoginRequest request);
}
