package com.goodzheng.po.identity.service.impl;

import com.goodzheng.po.identity.constant.ApprovalStatusConstants;
import com.goodzheng.po.identity.constant.ClientConstants;
import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.constant.UserStatusConstants;
import com.goodzheng.po.identity.dto.AppRegisterRequest;
import com.goodzheng.po.identity.dto.LoginRequest;
import com.goodzheng.po.identity.dto.LoginResponse;
import com.goodzheng.po.identity.dto.OpenIdLoginRequest;
import com.goodzheng.po.identity.dto.WeChatLoginRequest;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserMapper;
import com.goodzheng.po.identity.security.JwtUtil;
import com.goodzheng.po.identity.service.AuthService;
import com.goodzheng.po.identity.wechat.WeChatService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final UserMapper userMapper;
    private final JwtUtil jwtUtil;
    private final WeChatService weChatService;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    // 微信云托管会在请求头注入 X-Wx-Openid（免服务端调 jscode2session）；本地/Expo 无此头时回退用 code 换 openid
    private String resolveOpenId(String wxOpenid, String loginCode) {
        if (wxOpenid != null && !wxOpenid.isBlank()) {
            return wxOpenid;
        }
        return weChatService.getOpenIdByCode(loginCode);
    }

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
        user.setRole(RoleConstants.USER);
        userMapper.insert(user);
        return "注册成功";
    }

    @Override
    public LoginResponse appRegister(AppRegisterRequest request) {
        if (userMapper.existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setNickname(request.getNickname() != null ? request.getNickname() : request.getUsername());
        user.setRole(RoleConstants.USER);
        user.setStatus(UserStatusConstants.ACTIVE);
        user.setApprovalStatus(ApprovalStatusConstants.PENDING);
        userMapper.insert(user);
        return LoginResponse.pending(user.getId(), user.getUsername(), user.getNickname());
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

        if (!ApprovalStatusConstants.APPROVED.equals(user.getApprovalStatus())) {
            if (ApprovalStatusConstants.REJECTED.equals(user.getApprovalStatus())) {
                return LoginResponse.rejected(user.getId(), user.getUsername(), user.getNickname());
            }
            return LoginResponse.pending(user.getId(), user.getUsername(), user.getNickname());
        }

        if (!ClientConstants.allowsRole(client, user.getRole())) {
            throw new RuntimeException(ClientConstants.ADMIN.equals(client)
                    ? "该账号没有管理后台登录权限"
                    : "该账号无法登录移动端");
        }

        String token = jwtUtil.generateToken(
                user.getId(), user.getUsername(), user.getRole(), user.getStatus(), client);
        return LoginResponse.approved(user.getId(), token, user.getUsername(),
                user.getNickname(), user.getRole(), user.getPhoneNumber());
    }

    @Override
    public LoginResponse openIdLogin(OpenIdLoginRequest request, String wxOpenid) {
        String openId = resolveOpenId(wxOpenid, request.getLoginCode());

        Optional<User> existing = userMapper.findByWechatOpenid(openId);
        User user;

        if (existing.isPresent()) {
            user = existing.get();
        } else {
            user = new User();
            user.setUsername("wx_" + openId);
            user.setPassword(passwordEncoder.encode(openId));
            user.setWechatOpenid(openId);
            user.setNickname("微信用户");
            user.setRole(RoleConstants.USER);
            user.setStatus(UserStatusConstants.ACTIVE);
            user.setApprovalStatus(ApprovalStatusConstants.PENDING);
            userMapper.insert(user);
        }

        if (!UserStatusConstants.ACTIVE.equals(user.getStatus())) {
            throw new RuntimeException("账号已被禁用，请联系管理员");
        }

        if (!ApprovalStatusConstants.APPROVED.equals(user.getApprovalStatus())) {
            if (ApprovalStatusConstants.REJECTED.equals(user.getApprovalStatus())) {
                return LoginResponse.rejected(user.getId(), user.getUsername(), user.getNickname());
            }
            return LoginResponse.pending(user.getId(), user.getUsername(), user.getNickname());
        }

        String client = ClientConstants.APP;
        String token = jwtUtil.generateToken(
                user.getId(), user.getUsername(), user.getRole(), user.getStatus(), client);
        return LoginResponse.approved(user.getId(), token, user.getUsername(),
                user.getNickname(), user.getRole(), user.getPhoneNumber());
    }

    @Override
    public LoginResponse wechatLogin(WeChatLoginRequest request) {
        String openId = weChatService.getOpenIdByCode(request.getLoginCode());
        String phoneNumber = weChatService.getPhoneNumberByCode(request.getPhoneCode());

        Optional<User> existingByOpenId = userMapper.findByWechatOpenid(openId);
        User user;

        if (existingByOpenId.isPresent()) {
            user = existingByOpenId.get();
            if (!phoneNumber.equals(user.getPhoneNumber())) {
                user.setPhoneNumber(phoneNumber);
                userMapper.updateById(user);
            }
        } else {
            Optional<User> existingByPhone = userMapper.findByPhoneNumber(phoneNumber);
            if (existingByPhone.isPresent()) {
                user = existingByPhone.get();
                user.setWechatOpenid(openId);
                userMapper.updateById(user);
            } else {
                user = new User();
                user.setUsername("wx_" + openId);
                user.setPassword(passwordEncoder.encode(openId));
                user.setPhoneNumber(phoneNumber);
                user.setWechatOpenid(openId);
                user.setNickname("微信用户");
                user.setRole(RoleConstants.USER);
                user.setStatus(UserStatusConstants.ACTIVE);
                user.setApprovalStatus(ApprovalStatusConstants.PENDING);
                userMapper.insert(user);
            }
        }

        if (!UserStatusConstants.ACTIVE.equals(user.getStatus())) {
            throw new RuntimeException("账号已被禁用，请联系管理员");
        }

        if (!ApprovalStatusConstants.APPROVED.equals(user.getApprovalStatus())) {
            if (ApprovalStatusConstants.REJECTED.equals(user.getApprovalStatus())) {
                return LoginResponse.rejected(user.getId(), user.getUsername(), user.getNickname());
            }
            return LoginResponse.pending(user.getId(), user.getUsername(), user.getNickname());
        }

        String client = ClientConstants.APP;
        String token = jwtUtil.generateToken(
                user.getId(), user.getUsername(), user.getRole(), user.getStatus(), client);
        return LoginResponse.approved(user.getId(), token, user.getUsername(),
                user.getNickname(), user.getRole(), user.getPhoneNumber());
    }
}
