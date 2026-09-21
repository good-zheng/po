package com.goodzheng.po.identity.controller;

import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.dto.ChangePasswordRequest;
import com.goodzheng.po.identity.dto.ProfileRequest;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.identity.dto.UserRequest;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserRepository;
import com.goodzheng.po.identity.service.UserService;
import com.goodzheng.po.identity.security.JwtUtil;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
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

@RestController
@RequestMapping("/users")
@CrossOrigin(origins = "*")
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
    private final JwtUtil jwtUtil;
    private final UserRepository userRepository;

    // ── 分页列表（管理员及以上） ────────────────────────
    @GetMapping
    public Result<Page<User>> list(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String keyword) {
        try {
            requireManager(resolveUser(auth));
            PageRequest pageRequest = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createTime"));
            Page<User> result;
            if (keyword != null && !keyword.isBlank()) {
                result = userService.search(keyword, pageRequest);
            } else {
                result = userService.list(pageRequest);
            }
            return Result.success(result);
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 单个详情（管理员及以上） ────────────────────────
    @GetMapping("/{id}")
    public Result<User> getById(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @PathVariable Long id) {
        try {
            requireManager(resolveUser(auth));
            return Result.success(userService.getById(id));
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 当前登录用户信息（仅需有效登录） ────────────────
    @GetMapping("/me")
    public Result<User> me(@RequestHeader(value = "Authorization", required = false) String auth) {
        try {
            return Result.success(resolveUser(auth));
        } catch (RuntimeException e) {
            return Result.error(401, e.getMessage());
        }
    }

    // ── 更新当前用户个人资料（仅需有效登录） ────────────
    @PutMapping("/me")
    public Result<User> updateMe(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestBody ProfileRequest request) {
        try {
            User user = resolveUser(auth);
            // 仅放行基本资料字段，角色/状态/密码不可自助修改
            UserRequest safe = new UserRequest();
            safe.setNickname(request.getNickname());
            safe.setEmail(request.getEmail());
            safe.setPhoneNumber(request.getPhoneNumber());
            safe.setAvatar(request.getAvatar());
            return Result.success(userService.update(user.getId(), safe));
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 修改当前用户密码（仅需有效登录） ────────────
    @PutMapping("/me/password")
    public Result<String> changePassword(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestBody ChangePasswordRequest request) {
        try {
            User user = resolveUser(auth);
            userService.changePassword(user.getId(), request.getOldPassword(), request.getNewPassword());
            return Result.success("密码修改成功", null);
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 上传头像（当前登录用户） ─────────────────────────
    @PostMapping("/me/avatar")
    public Result<String> uploadAvatar(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestParam("file") MultipartFile file) {
        try {
            User user = resolveUser(auth);
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
            Path dir = Paths.get("uploads", "avatars");
            try (InputStream in = file.getInputStream()) {
                Files.createDirectories(dir);
                Files.copy(in, dir.resolve(filename), StandardCopyOption.REPLACE_EXISTING);
            } catch (IOException e) {
                throw new RuntimeException("头像保存失败: " + e.getMessage());
            }
            // 直接写入当前用户 avatar 字段，前端无需二次提交
            String url = "/api/avatars/" + filename;
            UserRequest request = new UserRequest();
            request.setAvatar(url);
            userService.update(user.getId(), request);
            return Result.success("头像上传成功", url);
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 创建用户（管理员及以上） ────────────────────────
    @PostMapping
    public Result<User> create(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @Valid @RequestBody UserRequest request) {
        try {
            User operator = requireManager(resolveUser(auth));
            validateRoleAssignment(operator, request.getRole());
            return Result.success(userService.create(request));
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 更新用户（管理员及以上） ────────────────────────
    @PutMapping("/{id}")
    public Result<User> update(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @PathVariable Long id,
            @RequestBody UserRequest request) {
        try {
            User operator = requireManager(resolveUser(auth));
            User target = userService.getById(id);

            // 管理员不能修改超级管理员
            if (!isSuperAdmin(operator) && isSuperAdmin(target)) {
                throw new RuntimeException("管理员不能修改超级管理员");
            }
            // 超级管理员不能修改自己的角色（防止失去系统控制权）
            if (isSuperAdmin(operator) && operator.getId().equals(id)
                    && request.getRole() != null && !request.getRole().equals(target.getRole())) {
                throw new RuntimeException("不能修改自己的角色");
            }
            // 校验目标角色是否在操作者权限范围内
            validateRoleAssignment(operator, request.getRole());
            // 管理员不能把管理员降级为超级管理员之外的越权操作已由上面覆盖

            return Result.success(userService.update(id, request));
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 修改用户角色（管理员及以上） ────────────────────
    @PutMapping("/{id}/role")
    public Result<User> updateRole(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @PathVariable Long id,
            @RequestBody Map<String, String> body) {
        try {
            User operator = requireManager(resolveUser(auth));
            User target = userService.getById(id);
            String newRole = body.get("role");

            if (newRole == null || !RoleConstants.isValid(newRole)) {
                throw new RuntimeException("非法角色值");
            }
            if (!isSuperAdmin(operator) && isSuperAdmin(target)) {
                throw new RuntimeException("管理员不能修改超级管理员的角色");
            }
            if (isSuperAdmin(operator) && operator.getId().equals(id)
                    && !newRole.equals(target.getRole())) {
                throw new RuntimeException("不能修改自己的角色");
            }
            validateRoleAssignment(operator, newRole);

            UserRequest request = new UserRequest();
            request.setUsername(target.getUsername());
            request.setRole(newRole);
            return Result.success(userService.update(id, request));
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 删除用户（管理员及以上） ────────────────────────
    @DeleteMapping("/{id}")
    public Result<String> delete(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @PathVariable Long id) {
        try {
            User operator = requireManager(resolveUser(auth));
            User target = userService.getById(id);
            if (operator.getId().equals(id)) {
                throw new RuntimeException("不能删除自己");
            }
            if (!isSuperAdmin(operator) && isSuperAdmin(target)) {
                throw new RuntimeException("管理员不能删除超级管理员");
            }
            userService.delete(id);
            return Result.success("删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 批量删除（管理员及以上） ────────────────────────
    @DeleteMapping("/batch")
    public Result<String> batchDelete(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestBody List<Long> ids) {
        try {
            User operator = requireManager(resolveUser(auth));
            if (ids.contains(operator.getId())) {
                throw new RuntimeException("不能删除自己");
            }
            if (!isSuperAdmin(operator)) {
                List<User> targets = userRepository.findAllById(ids);
                boolean hasSuperAdmin = targets.stream().anyMatch(this::isSuperAdmin);
                if (hasSuperAdmin) {
                    throw new RuntimeException("管理员不能删除超级管理员");
                }
            }
            userService.batchDelete(ids);
            return Result.success("批量删除成功", null);
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 批量修改状态（管理员及以上） ────────────────────
    @PutMapping("/batch/status")
    public Result<String> batchUpdateStatus(
            @RequestHeader(value = "Authorization", required = false) String auth,
            @RequestBody Map<String, Object> body) {
        try {
            User operator = requireManager(resolveUser(auth));
            @SuppressWarnings("unchecked")
            List<Number> idNumbers = (List<Number>) body.get("ids");
            List<Long> ids = idNumbers.stream().map(Number::longValue).toList();
            String status = (String) body.get("status");

            if (ids.contains(operator.getId())) {
                throw new RuntimeException("不能修改自己的状态");
            }
            if (!isSuperAdmin(operator)) {
                List<User> targets = userRepository.findAllById(ids);
                boolean hasSuperAdmin = targets.stream().anyMatch(this::isSuperAdmin);
                if (hasSuperAdmin) {
                    throw new RuntimeException("管理员不能修改超级管理员的状态");
                }
            }
            userService.batchUpdateStatus(ids, status);
            return Result.success("状态更新成功", null);
        } catch (RuntimeException e) {
            return Result.error(forbiddenOrUnauthorized(e), e.getMessage());
        }
    }

    // ── 权限校验辅助方法 ────────────────────────────────

    /** 从 Authorization 头解析当前登录用户（token 无效时抛出 401 语义异常） */
    private User resolveUser(String authHeader) {
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            throw new InvalidTokenException("未登录或令牌缺失");
        }
        String token = authHeader.substring(7);
        if (!jwtUtil.validateToken(token)) {
            throw new InvalidTokenException("令牌无效或已过期");
        }
        String username = jwtUtil.getUsernameFromToken(token);
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new InvalidTokenException("用户不存在"));
    }

    /** 要求管理员及以上角色 */
    private User requireManager(User operator) {
        if (!isSuperAdmin(operator) && !RoleConstants.ADMIN.equals(operator.getRole())) {
            throw new ForbiddenException("需要管理员或超级管理员权限");
        }
        // 被禁用的账号不能执行管理操作
        if (!"active".equals(operator.getStatus())) {
            throw new ForbiddenException("账号已被禁用");
        }
        return operator;
    }

    /** 校验操作者是否有权授予目标角色 */
    private void validateRoleAssignment(User operator, String targetRole) {
        if (targetRole == null) {
            return;
        }
        if (!RoleConstants.isValid(targetRole)) {
            throw new RuntimeException("非法角色值: " + targetRole);
        }
        // 仅超级管理员可以授予/撤销超级管理员角色
        if (RoleConstants.SUPER_ADMIN.equals(targetRole) && !isSuperAdmin(operator)) {
            throw new ForbiddenException("仅超级管理员可以授予超级管理员角色");
        }
    }

    private boolean isSuperAdmin(User user) {
        return RoleConstants.SUPER_ADMIN.equals(user.getRole());
    }

    /** 区分 401（未认证）与 403（权限不足） */
    private int forbiddenOrUnauthorized(RuntimeException e) {
        if (e instanceof InvalidTokenException) {
            return 401;
        }
        if (e instanceof ForbiddenException) {
            return 403;
        }
        return 400;
    }

    /** 未认证异常（映射 HTTP 401） */
    private static class InvalidTokenException extends RuntimeException {
        InvalidTokenException(String message) {
            super(message);
        }
    }

    /** 权限不足异常（映射 HTTP 403） */
    private static class ForbiddenException extends RuntimeException {
        ForbiddenException(String message) {
            super(message);
        }
    }
}
