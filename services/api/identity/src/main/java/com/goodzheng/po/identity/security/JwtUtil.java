package com.goodzheng.po.identity.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.util.Base64;
import java.util.Date;

@Component
public class JwtUtil {

    private final SecretKey key;
    private final long expiration;

    public JwtUtil(@Value("${jwt.secret}") String secret,
                   @Value("${jwt.expiration}") long expiration) {
        this.key = Keys.hmacShaKeyFor(Base64.getDecoder().decode(secret));
        this.expiration = expiration;
    }

    /** 令牌携带用户标识、角色、状态与登录来源，供过滤器链直接鉴权 */
    public String generateToken(Long userId, String username, String role, String status, String client) {
        Date now = new Date();
        return Jwts.builder()
                .subject(username)
                .claim("uid", userId)
                .claim("role", role)
                .claim("status", status)
                .claim("client", client)
                .issuedAt(now)
                .expiration(new Date(now.getTime() + expiration))
                .signWith(key)
                .compact();
    }

    /** 解析并校验令牌（签名、有效期）；无效令牌抛出 io.jsonwebtoken.JwtException */
    public AuthUser parse(String token) {
        Claims claims = getClaims(token);
        return new AuthUser(
                claims.get("uid", Long.class),
                claims.getSubject(),
                claims.get("role", String.class),
                claims.get("status", String.class),
                claims.get("client", String.class));
    }

    private Claims getClaims(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
