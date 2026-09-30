package com.goodzheng.po.identity.controller;

import com.goodzheng.po.identity.dto.AppRegisterRequest;
import com.goodzheng.po.identity.dto.LoginRequest;
import com.goodzheng.po.identity.dto.LoginResponse;
import com.goodzheng.po.identity.dto.OpenIdLoginRequest;
import com.goodzheng.po.identity.dto.WeChatLoginRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.identity.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/login")
    public Result<LoginResponse> login(@Valid @RequestBody LoginRequest request) {
        try {
            LoginResponse response = authService.login(request);
            return Result.success(response);
        } catch (RuntimeException e) {
            return Result.error(401, e.getMessage());
        }
    }

    @PostMapping("/register")
    public Result<String> register(@RequestParam String username,
                                   @RequestParam String password,
                                   @RequestParam(required = false) String email) {
        try {
            String msg = authService.register(username, password, email);
            return Result.success(msg, null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/app-register")
    public Result<LoginResponse> appRegister(@Valid @RequestBody AppRegisterRequest request) {
        try {
            LoginResponse response = authService.appRegister(request);
            return Result.success(response);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    @PostMapping("/openid-login")
    public Result<LoginResponse> openIdLogin(@Valid @RequestBody OpenIdLoginRequest request) {
        try {
            LoginResponse response = authService.openIdLogin(request);
            return Result.success(response);
        } catch (RuntimeException e) {
            return Result.error(401, e.getMessage());
        }
    }

    @PostMapping("/wechat-login")
    public Result<LoginResponse> wechatLogin(@Valid @RequestBody WeChatLoginRequest request) {
        try {
            LoginResponse response = authService.wechatLogin(request);
            return Result.success(response);
        } catch (RuntimeException e) {
            return Result.error(401, e.getMessage());
        }
    }
}
