package com.goodzheng.po.talk.asr;

import com.goodzheng.po.identity.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * ASR 一次性票据：换取 → 60 秒内建立 WebSocket → 用后即焚（靠 exp 保证单次时效）。
 *
 * <p>微信小程序 WebSocket 不支持自定义请求头，JWT 只能拼在 query 上，会被网关访问日志留存。
 * 票据让握手 URL 里只出现一次性随机串（实为自校验的短 JWT），真正的身份在服务内解析。
 *
 * <p>实现选择：票据是<b>自带签名、可自校验</b>的短 JWT（与用户登录 JWT 同源密钥），
 * 不再依赖任何进程内/共享存储。因此发票据的后端实例与收 WS 握手的后端实例无需是同一个——
 * 多副本部署、或由网关把 REST 与 WS 路由到不同实例时都能正常校验，不会出现「查无此票 → 401」。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AsrTicketService {

    private static final long TTL_MILLIS = 60_000L;

    private final JwtUtil jwtUtil;

    /** 签发：返回票据与有效期秒数 */
    public AsrTicket issue(Long userId, Long sessionId) {
        String ticket = jwtUtil.generateAsrTicket(userId, sessionId, TTL_MILLIS);
        return new AsrTicket(ticket, (int) (TTL_MILLIS / 1000));
    }

    /** 消费：握手时校验并解析身份；无效 / 过期 / 类型不符返回 null（无状态，天然单次有效） */
    public AsrTicketHolder consume(String ticket) {
        if (ticket == null || ticket.isBlank()) {
            return null;
        }
        JwtUtil.AsrTicketClaims claims = jwtUtil.parseAsrTicket(ticket);
        if (claims == null) {
            log.warn("ASR 握手被拒绝：ticket 无效或已过期");
            return null;
        }
        return new AsrTicketHolder(claims.userId(), claims.sessionId());
    }

    /** 签发给小程序的票据 */
    public record AsrTicket(String ticket, int expiresIn) {
    }

    /** 握手时解析出的身份 */
    public record AsrTicketHolder(Long userId, Long sessionId) {
    }
}
