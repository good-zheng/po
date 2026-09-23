package com.goodzheng.po.config;

import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.identity.entity.User;
import com.goodzheng.po.identity.repository.UserMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 系统初始化：默认不创建任何账号。
 * 仅当显式开启 app.seed.default.admin（环境变量 APP_SEED_DEFAULT_ADMIN）且
 * 系统中不存在超级管理员时，才创建默认账号 superadmin/123456。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class DataInitializer implements CommandLineRunner {

    private final UserMapper userMapper;

    @Value("${app.seed.default.admin:false}")
    private boolean seedDefaultAdmin;

    @Override
    public void run(String... args) {
        if (!seedDefaultAdmin) {
            return;
        }
        boolean hasSuperAdmin = userMapper.selectList(null).stream()
                .anyMatch(u -> RoleConstants.SUPER_ADMIN.equals(u.getRole()));
        if (!hasSuperAdmin) {
            BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
            User superAdmin = new User();
            superAdmin.setUsername("superadmin");
            superAdmin.setPassword(encoder.encode("123456"));
            superAdmin.setNickname("超级管理员");
            superAdmin.setRole(RoleConstants.SUPER_ADMIN);
            userMapper.insert(superAdmin);
            log.warn("已创建默认超级管理员账号: superadmin / 123456，请立即登录修改密码");
        }
    }
}
