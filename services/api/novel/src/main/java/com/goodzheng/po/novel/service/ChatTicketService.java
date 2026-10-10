package com.goodzheng.po.novel.service;

import com.goodzheng.po.identity.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * 对话面板（{@code /ws/chat} 的 novel-chat 插槽）的一次性握手票据。
 *
 * <p>为什么要有这张票而不是让客户端把 JWT 拼在 WS URL 上：浏览器与微信小程序都不能给握手带
 * 请求头，而 query 会被网关访问日志原样留存——24 小时有效期的用户令牌进日志等于把长期凭据
 * 交给了日志系统。口径与 talk 模块的 ASR 票据一致：自签短票、无共享存储，因此发票据的实例
 * 与收握手的实例不必是同一个。
 *
 * <p>刻意只带 uid：正典读口的作者作用域只需要知道「谁在读」。角色与来源不进票据，
 * 免得这张 60 秒的票被拿去当会话令牌打普通接口。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ChatTicketService {

    private static final long TTL_MILLIS = 60_000L;

    private final JwtUtil jwtUtil;

    /** 签发：票据字符串（{@code expiresIn} 秒内建立连接有效） */
    public String issue(Long userId) {
        return jwtUtil.generateChatTicket(userId, TTL_MILLIS);
    }

    public int expiresIn() {
        return (int) (TTL_MILLIS / 1000);
    }

    /** 消费：校验并解析出作者身份；无效 / 过期 / 类型不符返回 null */
    public Long consume(String ticket) {
        if (ticket == null || ticket.isBlank()) {
            return null;
        }
        JwtUtil.ChatTicketClaims claims = jwtUtil.parseChatTicket(ticket);
        if (claims == null || claims.userId() == null) {
            log.warn("chat 握手票据无效或已过期");
            return null;
        }
        return claims.userId();
    }
}
