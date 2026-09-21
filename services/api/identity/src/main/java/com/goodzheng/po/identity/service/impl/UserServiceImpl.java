package com.goodzheng.po.identity.service.impl;

import com.goodzheng.po.identity.dto.UserRequest;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserRepository;
import com.goodzheng.po.identity.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Override
    @Transactional(readOnly = true)
    public Page<User> list(Pageable pageable) {
        return userRepository.findAll(pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<User> search(String keyword, Pageable pageable) {
        return userRepository.searchByKeyword(keyword, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public User getById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
    }

    @Override
    @Transactional
    public User create(UserRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("用户名已存在");
        }
        User user = new User();
        user.setUsername(request.getUsername());
        user.setPassword(passwordEncoder.encode(
                request.getPassword() != null ? request.getPassword() : "123456"));
        user.setEmail(request.getEmail());
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhoneNumber(request.getPhoneNumber());
        user.setRole(request.getRole() != null ? request.getRole() : "user");
        user.setStatus(request.getStatus() != null ? request.getStatus() : "active");
        user.setNickname(request.getNickname() != null ? request.getNickname() : request.getUsername());
        user.setAvatar(request.getAvatar());
        return userRepository.save(user);
    }

    @Override
    @Transactional
    public User update(Long id, UserRequest request) {
        User user = getById(id);
        // username 不允许修改
        if (request.getEmail() != null) user.setEmail(request.getEmail());
        if (request.getFirstName() != null) user.setFirstName(request.getFirstName());
        if (request.getLastName() != null) user.setLastName(request.getLastName());
        if (request.getPhoneNumber() != null) user.setPhoneNumber(request.getPhoneNumber());
        if (request.getRole() != null) user.setRole(request.getRole());
        if (request.getStatus() != null) user.setStatus(request.getStatus());
        if (request.getNickname() != null) user.setNickname(request.getNickname());
        if (request.getAvatar() != null) user.setAvatar(request.getAvatar());
        // 密码可选更新
        if (request.getPassword() != null && !request.getPassword().isBlank()) {
            user.setPassword(passwordEncoder.encode(request.getPassword()));
        }
        return userRepository.save(user);
    }

    @Override
    @Transactional
    public void changePassword(Long id, String oldPassword, String newPassword) {
        if (oldPassword == null || oldPassword.isBlank()) {
            throw new RuntimeException("原密码不能为空");
        }
        if (newPassword == null || newPassword.length() < 6 || newPassword.length() > 32) {
            throw new RuntimeException("新密码长度需在 6-32 位之间");
        }
        User user = getById(id);
        if (!passwordEncoder.matches(oldPassword, user.getPassword())) {
            throw new RuntimeException("原密码不正确");
        }
        if (oldPassword.equals(newPassword)) {
            throw new RuntimeException("新密码不能与原密码相同");
        }
        user.setPassword(passwordEncoder.encode(newPassword));
        userRepository.save(user);
    }

    @Override
    @Transactional
    public void delete(Long id) {
        if (!userRepository.existsById(id)) {
            throw new RuntimeException("用户不存在");
        }
        userRepository.deleteById(id);
    }

    @Override
    @Transactional
    public void batchDelete(List<Long> ids) {
        userRepository.deleteAllByIdInBatch(ids);
    }

    @Override
    @Transactional
    public void batchUpdateStatus(List<Long> ids, String status) {
        List<User> users = userRepository.findAllById(ids);
        users.forEach(u -> u.setStatus(status));
        userRepository.saveAll(users);
    }
}
