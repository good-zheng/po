package com.goodzheng.po.talk.asr;

import com.goodzheng.po.talk.asr.AsrTicketService.AsrTicketHolder;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.WebSocketHandler;
import org.springframework.web.socket.server.HandshakeInterceptor;

/**
 * ASR 握手拦截：在 HTTP 握手阶段校验一次性 ticket，无效直接拒绝建连。
 *
 * <p>不放行到 handler 再校验，是为了避免无效连接占用讯飞会话额度。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AsrHandshakeInterceptor implements HandshakeInterceptor {

    private final AsrTicketService ticketService;

    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response,
                                   WebSocketHandler wsHandler, Map<String, Object> attributes) {
        String ticket = request instanceof org.springframework.http.server.ServletServerHttpRequest servletRequest
                ? servletRequest.getServletRequest().getParameter("ticket")
                : null;
        AsrTicketHolder holder = ticketService.consume(ticket);
        if (holder == null) {
            log.warn("ASR 握手被拒绝：ticket 无效或已过期");
            response.setStatusCode(org.springframework.http.HttpStatus.UNAUTHORIZED);
            return false;
        }
        attributes.put(AsrSocketHandler.ATTR_USER_ID, holder.userId());
        attributes.put(AsrSocketHandler.ATTR_SESSION_ID, holder.sessionId());
        return true;
    }

    @Override
    public void afterHandshake(ServerHttpRequest request, ServerHttpResponse response,
                               WebSocketHandler wsHandler, Exception exception) {
        // 无资源需要释放：票据已在 beforeHandshake 消费
    }
}
