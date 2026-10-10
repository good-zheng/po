package com.goodzheng.po.identity.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
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

    /**
     * 签发 ASR 一次性票据：短时效、自校验（无共享存储，多实例安全）。
     * 仅携带 uid/sid/exp/typ，不暴露用户名等敏感信息；密钥与用户 JWT 同源，故任意后端实例都能校验。
     */
    public String generateAsrTicket(Long userId, Long sessionId, long ttlMillis) {
        Date now = new Date();
        return Jwts.builder()
                .claim("uid", userId)
                .claim("sid", sessionId)
                .claim("typ", "asr")
                .issuedAt(now)
                .expiration(new Date(now.getTime() + ttlMillis))
                .signWith(key)
                .compact();
    }

    /** 校验 ASR 票据；无效 / 过期 / 类型不符返回 null */
    public AsrTicketClaims parseAsrTicket(String token) {
        try {
            Claims claims = getClaims(token);
            if (!"asr".equals(claims.get("typ"))) {
                return null;
            }
            return new AsrTicketClaims(claims.get("uid", Long.class), claims.get("sid", Long.class));
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /** ASR 票据解析出的身份（与 talk 模块的 AsrTicketHolder 对应） */
    public record AsrTicketClaims(Long userId, Long sessionId) {
    }

    /**
     * 签发 chat WebSocket 的一次性握手票据，口径同 ASR 票据（短时效、自校验、无共享存储）。
     *
     * <p>存在的理由不是「多一层签名」而是浏览器与微信小程序都不能给 WS 握手带请求头：JWT 只能拼进
     * query，而 query 会被网关访问日志原样留存。票据让握手 URL 里只出现 60 秒即失效的一次性串，
     * 真正的用户令牌不过网。
     *
     * <p>载荷刻意只有 {@code uid} 与 {@code typ}：不带 {@code role}/{@code client}/{@code status}，
     * 所以 {@link #parse} 即便解出来也还原不出可用登录态（{@code isActive()} 因 status 为 null 而假），
     * 票据不能当会话令牌拿去打普通接口。
     */
    public String generateChatTicket(Long userId, long ttlMillis) {
        Date now = new Date();
        return Jwts.builder()
                .claim("uid", userId)
                .claim("typ", "chat")
                .issuedAt(now)
                .expiration(new Date(now.getTime() + ttlMillis))
                .signWith(key)
                .compact();
    }

    /** 校验 chat 握手票据；无效 / 过期 / 类型不符返回 null */
    public ChatTicketClaims parseChatTicket(String token) {
        try {
            Claims claims = getClaims(token);
            if (!"chat".equals(claims.get("typ"))) {
                return null;
            }
            return new ChatTicketClaims(claims.get("uid", Long.class));
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /** chat 握手票据解析出的身份 */
    public record ChatTicketClaims(Long userId) {
    }
}
