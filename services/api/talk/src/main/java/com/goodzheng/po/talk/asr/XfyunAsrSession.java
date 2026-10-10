package com.goodzheng.po.talk.asr;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.goodzheng.po.shared.xfyun.XfyunSigner;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.WebSocket;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Base64;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import lombok.extern.slf4j.Slf4j;

/**
 * 一条讯飞语音听写会话（对应讯飞的 60 秒上限）。
 *
 * <p>协议要点：首帧带 common/business/data 且 data.status=0，中间帧只带 data.status=1，
 * 收尾帧 data.status=2 且音频为空。开启动态修正（{@code dwa=wpgs}）后，服务端会对已返回的
 * 中间结果做替换修正：{@code pgs=apd} 追加、{@code pgs=rpl} 替换，按 {@code sn} 分句维护。
 *
 * <p>音频按 40ms / 1280 字节发包（讯飞官方建议），16k/16bit/单声道，与小程序
 * RecorderManager 的 PCM 分片直接对接，无需转码。
 */
@Slf4j
public class XfyunAsrSession {

    private static final String HOST = "iat-api.xfyun.cn";
    private static final String PATH = "/v2/iat";
    /** 音频属性：16k 采样、16bit、单声道 */
    private static final String FORMAT = "audio/L16;rate=16000";
    /** 讯飞握手超时：拿不到连接就快速失败，不能让调用线程（Spring 入站线程）无限等 */
    private static final long HANDSHAKE_TIMEOUT_SECONDS = 5;

    /**
     * 全服务共用一个 HTTP 客户端。
     *
     * <p>每条会话都 {@code newHttpClient()} 会各留一条选择器线程（每轮换一段就多一条，长录音越积越多），
     * 而且默认没有连接超时：讯飞握手挂住时 {@code join()} 会把入站线程一起挂死，
     * 表现是帧一直在上行却一个字都出不来。
     */
    private static final HttpClient HTTP_CLIENT = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(HANDSHAKE_TIMEOUT_SECONDS))
            .build();

    /** 会话回调：由持有者（WebSocket handler）实现，注意回调发生在 HttpClient 线程上 */
    public interface Sink {
        /** 中间结果（可能含动态修正后的整段文本） */
        void onPartial(String text);

        /** 一句定稿：ls=true 触发 */
        void onFinal(String text);

        /** 讯飞返回错误码 */
        void onError(String code, String message);

        /** 服务端确认会话结束（data.status=2） */
        void onClosed();
    }

    private final XfyunAsrProperties properties;
    private final Sink sink;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private volatile WebSocket socket;
    private volatile boolean firstFrameSent;
    private volatile boolean finished;
    /** sn → 该句当前文本（未定稿）；被 {@code rg} 区间覆盖的旧 sn 要删掉 */
    private final Map<Integer, String> sentences = new TreeMap<>();
    /** 已定稿（ls=true）的句子，拼在每次结果最前面 */
    private final StringBuilder committed = new StringBuilder();
    private final StringBuilder frameBuffer = new StringBuilder();

    /**
     * JDK WebSocket 同一时刻只允许一个在途发送：前一次 {@code sendText} 的 Future 未完成就再发，
     * 会直接抛 {@code IllegalStateException}，异常从 Spring 的消息线程逃出还会掐断小程序连接。
     * 所以所有出网帧（含收尾帧）都排进这条单线程队列，发完一帧再发下一帧。
     */
    private final ExecutorService sender = Executors.newSingleThreadExecutor(runnable -> {
        Thread thread = new Thread(runnable, "xfyun-asr-sender");
        thread.setDaemon(true);
        return thread;
    });

    public XfyunAsrSession(XfyunAsrProperties properties, Sink sink) {
        this.properties = properties;
        this.sink = sink;
    }

    public void open() {
        String url = XfyunSigner.signedWebSocketUrl(HOST, PATH, properties.getApiKey(), properties.getApiSecret());
        CompletableFuture<WebSocket> handshaking = HTTP_CLIENT.newWebSocketBuilder()
                .connectTimeout(Duration.ofSeconds(HANDSHAKE_TIMEOUT_SECONDS))
                .buildAsync(URI.create(url), new Listener());
        try {
            this.socket = handshaking.get(HANDSHAKE_TIMEOUT_SECONDS, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            abandon(handshaking);
            throw new IllegalStateException("讯飞会话建立被中断", e);
        } catch (ExecutionException | TimeoutException e) {
            // 超时后握手仍可能在后台完成：拿到就把这条孤儿连接关掉，别留半开会话
            abandon(handshaking);
            throw new IllegalStateException("讯飞会话建立失败: " + e.getMessage(), e);
        }
    }

    private static void abandon(CompletableFuture<WebSocket> handshaking) {
        handshaking.whenComplete((webSocket, error) -> {
            if (webSocket != null) {
                webSocket.abort();
            }
        });
    }

    private final class Listener implements WebSocket.Listener {
        @Override
        public void onOpen(WebSocket webSocket) {
            webSocket.request(1);
        }

        @Override
        public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
            frameBuffer.append(data);
            if (!last) {
                webSocket.request(1);
                return null;
            }
            String message = frameBuffer.toString();
            frameBuffer.setLength(0);
            handleFrame(message);
            // 无条件续期：JDK 的接收是按 permit 计数的，这里若按 finished 收手，
            // 收尾帧（ls=true/status=2，实测 100ms 后就到）永远拿不到投递额度 ——
            // 表现是 stop 之后一条 final 都等不到，网关白等满超时才回 segment_end
            webSocket.request(1);
            return null;
        }

        @Override
        public void onError(WebSocket webSocket, Throwable error) {
            sink.onError("LOCAL", String.valueOf(error.getMessage()));
        }
    }

    /** 发送一帧音频（建议 1280 字节）；首帧自动带上 common/business */
    public void sendAudio(byte[] pcm) {
        if (socket == null || finished) {
            return;
        }
        int status = firstFrameSent ? 1 : 0;
        firstFrameSent = true;
        enqueue(buildFrame(status, pcm));
    }

    /** 收尾：发 status=2 的空音频帧，等待服务端返回最后结果 */
    public void finish() {
        if (socket == null || finished) {
            return;
        }
        finished = true;
        sender.execute(() -> {
            try {
                socket.sendText(buildFrame(2, new byte[0]), true).join();
            } catch (Exception e) {
                log.warn("讯飞收尾帧发送失败: {}", e.getMessage());
            } finally {
                sender.shutdown();
            }
        });
    }

    /** 立即断开，不等服务端确认 */
    public void abort() {
        finished = true;
        sender.shutdownNow();
        try {
            if (socket != null && !socket.isInputClosed()) {
                socket.abort();
            }
        } catch (Exception ignore) {
            // 收尾失败不影响主流程
        }
    }

    private void enqueue(String frame) {
        sender.execute(() -> {
            try {
                socket.sendText(frame, true).join();
            } catch (Exception e) {
                log.warn("讯飞音频帧发送失败: {}", e.getMessage());
            }
        });
    }

    private void handleFrame(String message) {
        try {
            JsonNode node = objectMapper.readTree(message);
            int code = node.path("code").asInt(-1);
            if (code != 0) {
                sink.onError(String.valueOf(code), node.path("message").asText("讯飞返回错误"));
                return;
            }
            JsonNode data = node.path("data");
            JsonNode result = data.path("result");
            if (!result.isMissingNode()) {
                int sn = result.path("sn").asInt(1);
                String pgs = result.path("pgs").asText("apd");
                String segment = concatWords(result.path("ws"));
                if ("rpl".equals(pgs)) {
                    // 动态修正的语义是「本条替换 rg=[起,止] 区间里的旧 sn」，
                    // 不删就直接把每次修正结果再累加一遍，上屏变成「今今天今天这……」
                    JsonNode rg = result.path("rg");
                    if (rg.isArray() && rg.size() >= 2) {
                        for (int old = rg.get(0).asInt(); old <= rg.get(1).asInt(); old += 1) {
                            sentences.remove(old);
                        }
                    }
                }
                sentences.put(sn, segment);
                String pending = String.join("", sentences.values());
                if (result.path("ls").asBoolean(false)) {
                    // 该句定稿：并入已定稿区后清空待定区，下一句从干净状态继续
                    committed.append(pending);
                    sentences.clear();
                    String text = committed.toString();
                    if (!text.isBlank()) {
                        sink.onFinal(text);
                    }
                } else {
                    String text = committed + pending;
                    if (!text.isBlank()) {
                        sink.onPartial(text);
                    }
                }
            }
            if (data.path("status").asInt(0) == 2) {
                sink.onClosed();
            }
        } catch (Exception e) {
            log.warn("解析讯飞响应失败: {}", e.getMessage());
            sink.onError("PARSE", "解析讯飞响应失败");
        }
    }

    private static String concatWords(JsonNode wsArray) {
        StringBuilder sb = new StringBuilder();
        if (wsArray != null && wsArray.isArray()) {
            for (JsonNode ws : wsArray) {
                JsonNode cw = ws.path("cw");
                if (cw.isArray()) {
                    for (JsonNode word : cw) {
                        sb.append(word.path("w").asText(""));
                    }
                }
            }
        }
        return sb.toString();
    }

    private String buildFrame(int status, byte[] pcm) {
        ObjectNode root = objectMapper.createObjectNode();
        if (status == 0) {
            ObjectNode common = root.putObject("common");
            common.put("app_id", properties.getAppId());

            ObjectNode business = root.putObject("business");
            business.put("domain", "iat");
            business.put("language", properties.getLanguage());
            business.put("accent", properties.getAccent());
            // 动态修正仅中文支持：开启后中间结果会被后续结果替换修正，上屏更准
            if ("zh_cn".equals(properties.getLanguage())) {
                business.put("dwa", "wpgs");
            }
            // 静音 5s 判定句末；ptt=0 不做标点符号规整以外的处理
            business.put("vad_eos", 5000);
            business.put("ptt", 0);
        }
        ObjectNode data = root.putObject("data");
        data.put("status", status);
        data.put("format", FORMAT);
        data.put("encoding", "raw");
        data.put("audio", Base64.getEncoder().encodeToString(pcm));
        return root.toString();
    }
}
