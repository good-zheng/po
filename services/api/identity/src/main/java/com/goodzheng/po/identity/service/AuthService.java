package com.goodzheng.po.identity.service;

import com.goodzheng.po.identity.dto.AppRegisterRequest;
import com.goodzheng.po.identity.dto.LoginRequest;
import com.goodzheng.po.identity.dto.LoginResponse;
import com.goodzheng.po.identity.dto.OpenIdLoginRequest;
import com.goodzheng.po.identity.dto.WeChatLoginRequest;

public interface AuthService {

    String register(String username, String password, String email);

    LoginResponse appRegister(AppRegisterRequest request);

    LoginResponse login(LoginRequest request);

    LoginResponse openIdLogin(OpenIdLoginRequest request);

    LoginResponse wechatLogin(WeChatLoginRequest request);
}
