package com.goodzheng.po.identity.service.impl;

import com.goodzheng.po.identity.constant.ClientConstants;
import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.constant.UserStatusConstants;
import com.goodzheng.po.identity.dto.LoginRequest;
import com.goodzheng.po.identity.dto.LoginResponse;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserMapper;
import com.goodzheng.po.identity.security.JwtUtil;
import com.goodzheng.po.identity.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Override
    public String register(String username, String password, String email) {
        if (userMapper.existsByUsername(username)) {
            throw new RuntimeException("用户名已存在");
        }
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setEmail(email);
        user.setNickname(username);
        // 注册用户默认为普通用户，管理员及以上角色由超级管理员/管理员分配
        user.setRole(RoleConstants.USER);
        userMapper.insert(user);
        return "注册成功";
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        String client = request.getClient();
        if (!ClientConstants.isValid(client)) {
            throw new RuntimeException("非法登录来源");
        }

        User user = userMapper.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("用户名或密码错误"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        if (!UserStatusConstants.ACTIVE.equals(user.getStatus())) {
            throw new RuntimeException("账号已被禁用，请联系管理员");
        }

        // 双向隔离：管理端仅管理员可用，移动端仅普通用户可用
        if (!ClientConstants.allowsRole(client, user.getRole())) {
            throw new RuntimeException(ClientConstants.ADMIN.equals(client)
                    ? "该账号没有管理后台登录权限"
                    : "该账号无法登录移动端");
        }

        String token = jwtUtil.generateToken(
                user.getId(), user.getUsername(), user.getRole(), user.getStatus(), client);
        return new LoginResponse(user.getId(), token, user.getUsername(), user.getNickname(), user.getRole());
    }
}
