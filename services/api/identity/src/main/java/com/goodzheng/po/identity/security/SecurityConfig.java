package com.goodzheng.po.identity.security;

import com.goodzheng.po.identity.constant.ClientConstants;
import com.goodzheng.po.identity.constant.RoleConstants;
import com.goodzheng.po.shared.dto.Result;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.authorization.AuthorityAuthorizationManager;
import org.springframework.security.authorization.AuthorizationManager;
import org.springframework.security.authorization.AuthorizationManagers;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.access.intercept.RequestAuthorizationContext;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import tools.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

/**
 * 统一鉴权入口：无状态 JWT 过滤器链。
 * 路径匹配不包含 context-path（/api），即 /auth/login 对应 /api/auth/login。
 */
@Configuration
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    /** 管理端管理员/超级管理员：管理接口与内容写操作的唯一合法身份 */
    private static final AuthorizationManager<RequestAuthorizationContext> ADMIN_CLIENT =
            AuthorizationManagers.allOf(
                    AuthorityAuthorizationManager.hasAnyAuthority(
                            "ROLE_" + RoleConstants.ADMIN, "ROLE_" + RoleConstants.SUPER_ADMIN),
                    AuthorityAuthorizationManager.hasAuthority("CLIENT_" + ClientConstants.ADMIN));

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final ObjectMapper objectMapper;

    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .cors(Customizer.withDefaults())
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        // 公开：登录/注册/微信登录/OpenID登录/App注册
                        .requestMatchers("/auth/login", "/auth/register", "/auth/wechat-login",
                                "/auth/openid-login", "/auth/app-register").permitAll()
                        // 容器错误转发（404/405/500 等）：放行以免真实状态码被改写成 401
                        .requestMatchers("/error").permitAll()
                        // 个人中心：任何已登录来源（App 用户维护自己的资料、密码、头像）
                        .requestMatchers("/users/me", "/users/me/**").authenticated()
                        // 我的菜谱/收藏/浏览历史：需登录（须在 GET /recipes/* 公开规则之前）
                        .requestMatchers("/recipes/mine", "/recipes/favorites", "/recipes/history").authenticated()
                        // 菜谱互动（收藏/点赞）与创建：需登录（归属权由 Service 层校验）
                        .requestMatchers(HttpMethod.POST, "/recipes", "/recipes/*/favorite", "/recipes/*/like").authenticated()
                        .requestMatchers(HttpMethod.DELETE, "/recipes/*/favorite").authenticated()
                        // 通用文件上传：任何已登录用户；上传产物 /files/** 公开可读
                        .requestMatchers(HttpMethod.POST, "/files/upload").authenticated()
                        .requestMatchers(HttpMethod.GET, "/files/**").permitAll()
                        // TTS 合成/预热消耗讯飞额度，交由末尾 anyRequest().authenticated() 收口：音频产物是 COS
                        // 公网 URL，播放器不经过本服务，所以不必为播放器公开。/auth/openid-login 只认 loginCode，
                        // 不再接受请求头里的 openid（普通域名可伪造）。
                        // 审核队列与审核操作：仅管理端管理员（须在 GET /recipes/* 与 PUT /recipes/* 规则之前）
                        .requestMatchers("/recipes/review").access(ADMIN_CLIENT)
                        .requestMatchers(HttpMethod.PUT, "/recipes/*/audit").access(ADMIN_CLIENT)
                        // 编辑/删除菜谱：需登录，作者本人或管理员（归属权由 Service 层校验）
                        .requestMatchers(HttpMethod.PUT, "/recipes/*").authenticated()
                        .requestMatchers(HttpMethod.DELETE, "/recipes/*").authenticated()
                        // 公开：内容浏览（未登录也能看列表与详情）
                        .requestMatchers(HttpMethod.GET,
                                "/recipes", "/recipes/*",
                                "/recipe-categories", "/recipe-categories/*",
                                "/avatars/**", "/covers/**", "/ingredients/**", "/sounds/**").permitAll()
                        // 探活端点公开（云托管滚动发布要读它）；metrics/prometheus/info 只给管理端
                        .requestMatchers("/actuator/health", "/actuator/health/**").permitAll()
                        .requestMatchers("/actuator/**").access(ADMIN_CLIENT)
                        // 用户管理：仅管理端管理员
                        .requestMatchers("/users/**").access(ADMIN_CLIENT)
                        // 内容写操作：仅管理端管理员（App 普通用户不能创建/修改/删除内容）
                        .requestMatchers("/recipes/**", "/recipe-categories/**").access(ADMIN_CLIENT)
                        .anyRequest().authenticated())
                .exceptionHandling(handler -> handler
                        .authenticationEntryPoint(this::writeUnauthorized)
                        .accessDeniedHandler(this::writeForbidden))
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);
        return http.build();
    }

    /** 前后端分离部署时的直连场景；Web 端开发与网关同源，本配置仅为兜底 */
    @Bean
    CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOriginPatterns(List.of("*"));
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setMaxAge(3600L);
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }

    /** 401：未登录、令牌缺失或已失效 */
    private void writeUnauthorized(HttpServletRequest request, HttpServletResponse response,
                                   AuthenticationException exception) throws IOException {
        writeResult(response, HttpServletResponse.SC_UNAUTHORIZED, Result.error(401, "未登录或登录状态已失效"));
    }

    /** 403：已登录但无权访问（普通用户访问管理接口、App 端访问管理接口） */
    private void writeForbidden(HttpServletRequest request, HttpServletResponse response,
                                AccessDeniedException exception) throws IOException {
        writeResult(response, HttpServletResponse.SC_FORBIDDEN, Result.error(403, "没有访问权限"));
    }

    private void writeResult(HttpServletResponse response, int status, Result<?> body) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        objectMapper.writeValue(response.getWriter(), body);
    }
}
