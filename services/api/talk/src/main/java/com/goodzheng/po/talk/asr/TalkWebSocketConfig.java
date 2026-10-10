package com.goodzheng.po.talk.asr;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.WebSocketConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketHandlerRegistry;

/**
 * 注册 ASR 网关端点。
 *
 * <p>路径不含 context-path：Spring Boot 的 server.servlet.context-path=/api 会作用在
 * WebSocket 端点上，因此对外实际地址为 <b>/api/ws/asr</b>。Nginx 把外部 /ws/asr 重写到
 * /api/ws/asr 并带上 Upgrade 头，小程序只需连 wss://网关/ws/asr。
 */
@Configuration
@EnableWebSocket
@RequiredArgsConstructor
public class TalkWebSocketConfig implements WebSocketConfigurer {

    private final AsrSocketHandler asrSocketHandler;
    private final AsrHandshakeInterceptor asrHandshakeInterceptor;

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(asrSocketHandler, "/ws/asr")
                .addInterceptors(asrHandshakeInterceptor)
                // 小程序 WebSocket 不携带 Origin，须放开来源校验
                .setAllowedOriginPatterns("*");
    }
}
