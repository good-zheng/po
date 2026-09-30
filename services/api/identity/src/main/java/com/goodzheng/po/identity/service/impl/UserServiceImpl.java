package com.goodzheng.po.identity.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.goodzheng.po.identity.constant.ApprovalStatusConstants;
import com.goodzheng.po.identity.dto.UserRequest;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserMapper;
import com.goodzheng.po.identity.service.UserService;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
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

    private final UserMapper userMapper;
    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Override
    @Transactional(readOnly = true)
    public Page<User> list(Pageable pageable) {
        var mpPage = MyBatisPages.<User>toMpPage(pageable);
        userMapper.selectPage(mpPage, null);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<User> search(String keyword, Pageable pageable) {
        String pattern = "%" + keyword.toLowerCase() + "%";
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.and(w -> w
                .apply("LOWER(username) LIKE {0}", pattern)
                .or().apply("LOWER(email) LIKE {0}", pattern)
                .or().apply("LOWER(first_name) LIKE {0}", pattern)
                .or().apply("LOWER(last_name) LIKE {0}", pattern));
        var mpPage = MyBatisPages.<User>toMpPage(pageable);
        userMapper.selectPage(mpPage, wrapper);
        return MyBatisPages.toPage(mpPage, pageable);
    }

    @Override
    @Transactional(readOnly = true)
    public User getById(Long id) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        return user;
    }

    @Override
    @Transactional(readOnly = true)
    public List<User> listByApprovalStatus(String approvalStatus) {
        return userMapper.findByApprovalStatus(approvalStatus);
    }

    @Override
    @Transactional
    public User create(UserRequest request) {
        if (userMapper.existsByUsername(request.getUsername())) {
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
        userMapper.insert(user);
        return user;
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
        userMapper.updateById(user);
        return user;
    }

    @Override
    @Transactional
    public User updateApprovalStatus(Long id, String approvalStatus) {
        if (!ApprovalStatusConstants.isValid(approvalStatus)) {
            throw new RuntimeException("非法审批状态");
        }
        User user = getById(id);
        user.setApprovalStatus(approvalStatus);
        userMapper.updateById(user);
        return user;
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
        userMapper.updateById(user);
    }

    @Override
    @Transactional
    public void delete(Long id) {
        if (userMapper.selectById(id) == null) {
            throw new RuntimeException("用户不存在");
        }
        userMapper.deleteById(id);
    }

    @Override
    @Transactional
    public void batchDelete(List<Long> ids) {
        userMapper.deleteBatchIds(ids);
    }

    @Override
    @Transactional
    public void batchUpdateStatus(List<Long> ids, String status) {
        List<User> users = userMapper.selectBatchIds(ids);
        users.forEach(u -> u.setStatus(status));
        users.forEach(userMapper::updateById);
    }
}
