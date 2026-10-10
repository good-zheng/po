package com.goodzheng.po.talk.asr;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.io.IOException;
import java.util.Base64;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;

/**
 * 小程序 ASR 网关：接收 PCM 音频帧，代理讯飞语音听写，回传增量转写文本。
 *
 * <p>上行：{@code start} / {@code frame}（base64 PCM）/ {@code stop}
 * 下行：{@code ready} / {@code partial} / {@code final} / {@code segment_end} / {@code error}
 *
 * <p>两个硬限制在这里兜住：讯飞单会话 60 秒（到点主动收尾重开，segment 递增）、
 * 微信单次录音 10 分钟（由小程序重开录音，服务端无感，只是 segment 继续递增）。
 *
 * <p>音频不落盘、不落对象存储：本服务只做转发，转写文本由小程序调 /talk 接口落库。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class AsrSocketHandler extends TextWebSocketHandler {

    static final String ATTR_USER_ID = "asrUserId";
    static final String ATTR_SESSION_ID = "asrSessionId";

    /** 等待讯飞确认收尾的最长时间（在入站线程上等，期间端上的帧会堆积） */
    private static final int FINISH_WAIT_SECONDS = 2;
    /** 建立失败后重开的最小间隔：避免每帧都去握手 */
    private static final long REOPEN_MIN_INTERVAL_MS = 2000;
    /** 单帧音频上限：32KB，超过即视为异常请求丢弃（正常帧为 1280 字节） */
    private static final int MAX_FRAME_BYTES = 32 * 1024;

    private final XfyunAsrProperties properties;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Map<String, Conn> connections = new ConcurrentHashMap<>();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) throws Exception {
        Long userId = (Long) session.getAttributes().get(ATTR_USER_ID);
        Long sessionId = (Long) session.getAttributes().get(ATTR_SESSION_ID);
        connections.put(session.getId(), new Conn(userId, sessionId));

        if (!propertiesConfigured()) {
            send(session, error("ASR_NOT_CONFIGURED", "讯飞听写未配置，请改用文字输入"));
            return;
        }
        openSegment(session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        Conn conn = connections.get(session.getId());
        if (conn == null) {
            return;
        }
        JsonNode node;
        try {
            node = objectMapper.readTree(message.getPayload());
        } catch (IOException e) {
            send(session, error("BAD_FRAME", "无法解析的帧"));
            return;
        }
        String type = node.path("type").asText("");
        switch (type) {
            // 建连时已经开好一段讯飞会话，start 只表示「端上可以发音频了」：
            // 这里再 open 一次会 abort 掉正在积累的会话，白耗一次讯飞握手，还可能丢掉最先几百毫秒音频
            case "start" -> {
                if (conn.xfSession == null) {
                    openSegment(session);
                }
            }
            case "frame" -> onFrame(session, node);
            case "stop" -> stop(session, "stop");
            default -> send(session, error("UNKNOWN_TYPE", "未知帧类型: " + type));
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        Conn conn = connections.remove(session.getId());
        if (conn != null && conn.xfSession != null) {
            conn.xfSession.abort();
        }
        // 票据已改为自带签名的无状态短令牌，过期由 exp 自校验，无需再清理存储
    }

    @Override
    public void handleTransportError(WebSocketSession session, Throwable exception) {
        log.warn("ASR 连接异常: {}", exception.getMessage());
        afterConnectionClosed(session, CloseStatus.SERVER_ERROR);
    }

    // ── 帧处理 ────────────────────────────────────────────

    private void onFrame(WebSocketSession session, JsonNode node) {
        Conn conn = connections.get(session.getId());
        if (conn == null) {
            return;
        }
        byte[] pcm;
        try {
            pcm = Base64.getDecoder().decode(node.path("audio").asText(""));
        } catch (IllegalArgumentException e) {
            send(session, error("BAD_AUDIO", "音频帧不是合法 base64"));
            return;
        }
        if (pcm.length == 0 || pcm.length > MAX_FRAME_BYTES) {
            return;
        }
        if (conn.xfSession == null) {
            // 上一段建立失败或被收尾：限频重开，而不是静默丢掉后续所有帧
            // （静默丢弃的表现是「帧数在涨、一个字都没有」，端上完全看不出断在哪）
            if (System.currentTimeMillis() - conn.lastOpenAttemptAt > REOPEN_MIN_INTERVAL_MS) {
                openSegment(session);
            }
            return;
        }
        // 讯飞 60s 硬限制：到点先收尾当前会话，再开下一段
        long elapsed = System.currentTimeMillis() - conn.segmentStartedAt;
        if (elapsed > properties.getMaxSeconds() * 1000L) {
            rotateSegment(session, "max60s");
        }
        conn.xfSession.sendAudio(pcm);
    }

    /** 开一段新的讯飞会话（首次连接、60s 轮换或建立失败后重试） */
    private void openSegment(WebSocketSession session) {
        Conn conn = connections.get(session.getId());
        if (conn == null) {
            return;
        }
        if (conn.xfSession != null) {
            conn.xfSession.abort();
        }
        conn.segment += 1;
        conn.segmentStartedAt = System.currentTimeMillis();
        conn.lastOpenAttemptAt = conn.segmentStartedAt;
        conn.closing = new CompletableFuture<>();
        conn.xfSession = new XfyunAsrSession(properties, new XfyunAsrSession.Sink() {
            @Override
            public void onPartial(String text) {
                send(session, frame("partial").put("text", text).put("segment", conn.segment));
            }

            @Override
            public void onFinal(String text) {
                if (!text.isBlank()) {
                    send(session, frame("final").put("text", text).put("segment", conn.segment));
                }
            }

            @Override
            public void onError(String code, String message) {
                send(session, error(code, message));
            }

            @Override
            public void onClosed() {
                if (conn.closing != null) {
                    conn.closing.complete(null);
                }
            }
        });
        try {
            conn.xfSession.open();
            send(session, frame("ready").put("segment", conn.segment));
        } catch (Exception e) {
            log.error("讯飞会话建立失败", e);
            // 必须清掉：留着这条 socket==null 的会话，端上的帧会被 sendAudio 静默吞掉，
            // 而且后续 start 帧看到非 null 就不再重开，整次录音都出不了字
            XfyunAsrSession failed = conn.xfSession;
            conn.xfSession = null;
            failed.abort();
            send(session, error("XF_CONNECT_FAILED", "语音服务连接失败，请改用文字输入"));
            closeQuietly(session);
        }
    }

    private void closeQuietly(WebSocketSession session) {
        try {
            session.close(CloseStatus.SERVER_ERROR);
        } catch (IOException ignore) {
            // 连接已断，无需处理
        }
    }

    /** 收尾当前段并立即开启下一段（讯飞 60s 到期） */
    private void rotateSegment(WebSocketSession session, String reason) {
        Conn conn = connections.get(session.getId());
        if (conn == null || conn.xfSession == null) {
            return;
        }
        finishCurrentSegment(conn);
        send(session, frame("segment_end").put("reason", reason).put("segment", conn.segment));
        openSegment(session);
    }

    /** 停止：收尾后关闭连接 */
    private void stop(WebSocketSession session, String reason) {
        Conn conn = connections.get(session.getId());
        if (conn == null) {
            return;
        }
        finishCurrentSegment(conn);
        send(session, frame("segment_end").put("reason", reason).put("segment", conn.segment));
        try {
            session.close(CloseStatus.NORMAL);
        } catch (IOException ignore) {
            // 关闭失败不影响已下发的文本
        }
    }

    private void finishCurrentSegment(Conn conn) {
        if (conn.xfSession == null) {
            return;
        }
        conn.xfSession.finish();
        try {
            conn.closing.get(FINISH_WAIT_SECONDS, TimeUnit.SECONDS);
        } catch (Exception ignore) {
            // 超时未确认也继续：结果可能已下发，未下发的部分丢弃
        }
        conn.xfSession.abort();
        conn.xfSession = null;
    }

    // ── 下行 ─────────────────────────────────────────────

    private ObjectNode frame(String type) {
        ObjectNode node = objectMapper.createObjectNode();
        node.put("type", type);
        return node;
    }

    private ObjectNode error(String code, String message) {
        return frame("error").put("code", code).put("message", message);
    }

    private void send(WebSocketSession session, ObjectNode payload) {
        Conn conn = connections.get(session.getId());
        Object lock = conn == null ? session : conn;
        synchronized (lock) {
            if (!session.isOpen()) {
                return;
            }
            try {
                session.sendMessage(new TextMessage(payload.toString()));
            } catch (IOException e) {
                log.warn("ASR 下行发送失败: {}", e.getMessage());
            }
        }
    }

    private boolean propertiesConfigured() {
        return notBlank(properties.getAppId())
                && notBlank(properties.getApiKey())
                && notBlank(properties.getApiSecret());
    }

    private static boolean notBlank(String value) {
        return value != null && !value.isBlank();
    }

    /** 单条连接的运行时状态 */
    private static final class Conn {
        private final Long userId;
        private final Long sessionId;
        private int segment;
        private long segmentStartedAt;
        private volatile long lastOpenAttemptAt;
        private volatile XfyunAsrSession xfSession;
        private volatile CompletableFuture<Void> closing;

        private Conn(Long userId, Long sessionId) {
            this.userId = userId;
            this.sessionId = sessionId;
        }
    }
}
