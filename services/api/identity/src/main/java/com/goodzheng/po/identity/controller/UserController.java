package com.goodzheng.po.identity.controller;

import com.goodzheng.po.identity.constant.ApprovalStatusConstants;
import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.dto.ApprovalRequest;
import com.goodzheng.po.identity.dto.ChangePasswordRequest;
import com.goodzheng.po.identity.dto.ProfileRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.shared.storage.ObjectStorage;
import com.goodzheng.po.identity.dto.UserRequest;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserMapper;
import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.identity.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 用户接口。
 * 访问控制（登录态、角色、登录来源）由 SecurityConfig 过滤器链统一完成，
 * 这里只处理业务规则。
 */
@RestController
@RequestMapping("/users")
@RequiredArgsConstructor
public class UserController {

    /** 允许上传的头像图片类型及对应扩展名 */
    private static final Map<String, String> ALLOWED_IMAGE_TYPES = Map.of(
            "image/jpeg", "jpg",
            "image/png", "png",
            "image/gif", "gif",
            "image/webp", "webp");

    /** 头像文件大小上限：2MB */
    private static final long MAX_AVATAR_SIZE = 2 * 1024 * 1024;

    private final UserService userService;
    private final UserMapper userMapper;
    private final ObjectStorage storage;

    // ── 分页列表（管理员及以上） ────────────────────────
    @GetMapping
    public Result<Page<User>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String keyword) {
        PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createTime"));
        Page<User> result = (keyword != null && !keyword.isBlank())
                ? userService.search(keyword, pageRequest)
                : userService.list(pageRequest);
        return Result.success(result);
    }

    // ── 待审批用户列表（管理员及以上） ────────────────────
    @GetMapping("/pending")
    public Result<List<User>> pendingList() {
        List<User> users = userService.listByApprovalStatus(ApprovalStatusConstants.PENDING);
        return Result.success(users);
    }

    // ── 单个详情（管理员及以上） ────────────────────────
    @GetMapping("/{id}")
    public Result<User> getById(@PathVariable Long id) {
        try {
            return Result.success(userService.getById(id));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 当前登录用户信息 ────────────────────────────────
    @GetMapping("/me")
    public Result<User> me(@AuthenticationPrincipal AuthUser principal) {
        try {
            return Result.success(currentUser(principal));
        } catch (RuntimeException e) {
            return Result.error(401, e.getMessage());
        }
    }

    // ── 更新当前用户个人资料 ────────────────────────────
    @PutMapping("/me")
    public Result<User> updateMe(
            @AuthenticationPrincipal AuthUser principal,
            @Valid @RequestBody ProfileRequest request) {
        try {
            User user = currentUser(principal);
            // 仅放行基本资料字段，角色/状态/密码不可自助修改
            UserRequest safe = new UserRequest();
            safe.setNickname(request.getNickname());
            safe.setEmail(request.getEmail());
            safe.setPhoneNumber(request.getPhoneNumber());
            safe.setAvatar(request.getAvatar());
            return Result.success(userService.update(user.getId(), safe));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 修改当前用户密码 ────────────────────────────
    @PutMapping("/me/password")
    public Result<String> changePassword(
            @AuthenticationPrincipal AuthUser principal,
            @RequestBody ChangePasswordRequest request) {
        try {
            User user = currentUser(principal);
            userService.changePassword(user.getId(), request.getOldPassword(), request.getNewPassword());
            return Result.success("密码修改成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 上传头像（当前登录用户） ─────────────────────────
    @PostMapping("/me/avatar")
    public Result<String> uploadAvatar(
            @AuthenticationPrincipal AuthUser principal,
            @RequestParam("file") MultipartFile file) {
        try {
            User user = currentUser(principal);
            if (file == null || file.isEmpty()) {
                throw new RuntimeException("请选择要上传的图片");
            }
            String contentType = file.getContentType();
            if (contentType == null || !ALLOWED_IMAGE_TYPES.containsKey(contentType)) {
                throw new RuntimeException("仅支持 jpg/png/gif/webp 格式的图片");
            }
            if (file.getSize() > MAX_AVATAR_SIZE) {
                throw new RuntimeException("头像图片不能超过 2MB");
            }
            String filename = UUID.randomUUID().toString().replace("-", "")
                    + "." + ALLOWED_IMAGE_TYPES.get(contentType);
            // 落腾讯云 COS，返回桶公网 URL（云托管本地磁盘临时、多实例不共享）
            String url;
            try {
                url = storage.upload("avatars/" + filename, file.getBytes(), contentType);
            } catch (IOException e) {
                throw new RuntimeException("头像保存失败: " + e.getMessage());
            }
            // 直接写入当前用户 avatar 字段，前端无需二次提交
            UserRequest request = new UserRequest();
            request.setAvatar(url);
            userService.update(user.getId(), request);
            return Result.success("头像上传成功", url);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 创建用户（管理员及以上） ────────────────────────
    @PostMapping
    public Result<User> create(
            @AuthenticationPrincipal AuthUser principal,
            @Valid @RequestBody UserRequest request) {
        try {
            validateRoleAssignment(principal, request.getRole());
            return Result.success(userService.create(request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 更新用户（管理员及以上） ────────────────────────
    @PutMapping("/{id}")
    public Result<User> update(
            @AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id,
            @RequestBody UserRequest request) {
        try {
            User target = userService.getById(id);

            // 管理员不能修改超级管理员
            if (!principal.isSuperAdmin() && isSuperAdmin(target)) {
                throw new RuntimeException("管理员不能修改超级管理员");
            }
            // 超级管理员不能修改自己的角色（防止失去系统控制权）
            if (principal.isSuperAdmin() && principal.id().equals(id)
                    && request.getRole() != null && !request.getRole().equals(target.getRole())) {
                throw new RuntimeException("不能修改自己的角色");
            }
            // 校验目标角色是否在操作者权限范围内
            validateRoleAssignment(principal, request.getRole());

            return Result.success(userService.update(id, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 修改用户角色（管理员及以上） ────────────────────
    @PutMapping("/{id}/role")
    public Result<User> updateRole(
            @AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        try {
            User target = userService.getById(id);
            String newRole = body.get("role");

            if (newRole == null || !RoleConstants.isValid(newRole)) {
                throw new RuntimeException("非法角色值");
            }
            if (!principal.isSuperAdmin() && isSuperAdmin(target)) {
                throw new RuntimeException("管理员不能修改超级管理员的角色");
            }
            if (principal.isSuperAdmin() && principal.id().equals(id)
                    && !newRole.equals(target.getRole())) {
                throw new RuntimeException("不能修改自己的角色");
            }
            validateRoleAssignment(principal, newRole);

            UserRequest request = new UserRequest();
            request.setUsername(target.getUsername());
            request.setRole(newRole);
            return Result.success(userService.update(id, request));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 审批用户（管理员及以上） ────────────────────────
    @PutMapping("/{id}/approval")
    public Result<User> approve(
            @PathVariable Long id,
            @RequestBody ApprovalRequest request) {
        try {
            String action = request.getAction();
            if (!ApprovalStatusConstants.APPROVED.equals(action) && !ApprovalStatusConstants.REJECTED.equals(action)) {
                throw new RuntimeException("审批操作无效，仅支持 approved 或 rejected");
            }
            return Result.success(userService.updateApprovalStatus(id, action));
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 删除用户（管理员及以上） ────────────────────────
    @DeleteMapping("/{id}")
    public Result<String> delete(
            @AuthenticationPrincipal AuthUser principal,
            @PathVariable Long id) {
        try {
            User target = userService.getById(id);
            if (principal.id().equals(id)) {
                throw new RuntimeException("不能删除自己");
            }
            if (!principal.isSuperAdmin() && isSuperAdmin(target)) {
                throw new RuntimeException("管理员不能删除超级管理员");
            }
            userService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 批量删除（管理员及以上） ────────────────────────
    @DeleteMapping("/batch")
    public Result<String> batchDelete(
            @AuthenticationPrincipal AuthUser principal,
            @RequestBody List<Long> ids) {
        try {
            if (ids.contains(principal.id())) {
                throw new RuntimeException("不能删除自己");
            }
            if (!principal.isSuperAdmin()) {
                List<User> targets = userMapper.findAllById(ids);
                boolean hasSuperAdmin = targets.stream().anyMatch(this::isSuperAdmin);
                if (hasSuperAdmin) {
                    throw new RuntimeException("管理员不能删除超级管理员");
                }
            }
            userService.batchDelete(ids);
            return Result.success("批量删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 批量修改状态（管理员及以上） ────────────────────
    @PutMapping("/batch/status")
    public Result<String> batchUpdateStatus(
            @AuthenticationPrincipal AuthUser principal,
            @RequestBody Map<String, Object> body) {
        try {
            @SuppressWarnings("unchecked")
            List<Number> idNumbers = (List<Number>) body.get("ids");
            List<Long> ids = idNumbers.stream().map(Number::longValue).toList();
            String status = (String) body.get("status");

            if (ids.contains(principal.id())) {
                throw new RuntimeException("不能修改自己的状态");
            }
            if (!principal.isSuperAdmin()) {
                List<User> targets = userMapper.findAllById(ids);
                boolean hasSuperAdmin = targets.stream().anyMatch(this::isSuperAdmin);
                if (hasSuperAdmin) {
                    throw new RuntimeException("管理员不能修改超级管理员的状态");
                }
            }
            userService.batchUpdateStatus(ids, status);
            return Result.success("状态更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(400, e.getMessage());
        }
    }

    // ── 权限校验辅助方法 ────────────────────────────────

    /** 当前登录用户实体（认证由过滤器链完成，这里仅为业务操作取实体） */
    private User currentUser(AuthUser principal) {
        User user = userMapper.selectById(principal.id());
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        return user;
    }

    /** 校验操作者是否有权授予目标角色 */
    private void validateRoleAssignment(AuthUser operator, String targetRole) {
        if (targetRole == null) {
            return;
        }
        if (!RoleConstants.isValid(targetRole)) {
            throw new RuntimeException("非法角色值: " + targetRole);
        }
        // 仅超级管理员可以授予/撤销超级管理员角色
        if (RoleConstants.SUPER_ADMIN.equals(targetRole) && !operator.isSuperAdmin()) {
            throw new RuntimeException("仅超级管理员可以授予超级管理员角色");
        }
    }

    private boolean isSuperAdmin(User user) {
        return RoleConstants.SUPER_ADMIN.equals(user.getRole());
    }
}
