package com.goodzheng.po.identity.service.impl;

import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.dto.LoginRequest;
import com.goodzheng.po.identity.dto.LoginResponse;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserRepository;
import com.goodzheng.po.identity.service.AuthService;
import com.goodzheng.po.identity.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserRepository userRepository;
    private final JwtUtil jwtUtil;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Override
    public String register(String username, String password, String email) {
        if (userRepository.existsByUsername(username)) {
            throw new RuntimeException("用户名已存在");
        }
        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setEmail(email);
        user.setNickname(username);
        // 注册用户默认为普通用户，管理员及以上角色由超级管理员/管理员分配
        user.setRole(RoleConstants.USER);
        userRepository.save(user);
        return "注册成功";
    }

    @Override
    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("用户名或密码错误"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("用户名或密码错误");
        }

        String token = jwtUtil.generateToken(user.getUsername());
        return new LoginResponse(user.getId(), token, user.getUsername(), user.getNickname(), user.getRole());
    }
}
