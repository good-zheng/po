package com.goodzheng.po.recipe.tts;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.goodzheng.po.shared.xfyun.XfyunSigner;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.WebSocket;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.TimeUnit;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * 调用讯飞语音合成 v2（WebSocket）把文本合成为 MP3 字节。
 *
 * <p>鉴权要点：对 {@code host: {host}\ndate: {date}\nGET /v2/tts HTTP/1.1}（注意结尾无换行）
 * 用 APISecret 做 HMAC-SHA256，base64 后拼进 authorization。
 * 短文本一次性发 status=2 的收尾帧，服务端分帧返回 base64 音频，拼接后解码即 MP3。
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class XfyunTtsService {

    private static final String HOST = "tts-api.xfyun.cn";
    private static final String PATH = "/v2/tts";
    private static final int TIMEOUT_SECONDS = 15;

    private final XfyunTtsProperties properties;
    private final ObjectMapper objectMapper = new ObjectMapper();

    /** 合成成功返回 MP3 字节；鉴权/参数/网络异常一律抛出，交由上层不落盘。 */
    public byte[] synthesize(String text) {
        if (isBlank(properties.getAppId()) || isBlank(properties.getApiKey()) || isBlank(properties.getApiSecret())) {
            throw new IllegalStateException("讯飞 TTS 未配置（缺 appId/apiKey/apiSecret）");
        }

        String url = buildAuthUrl();
        StringBuilder audio = new StringBuilder();
        CompletableFuture<byte[]> result = new CompletableFuture<>();

        WebSocket ws = HttpClient.newHttpClient()
                .newWebSocketBuilder()
                .buildAsync(URI.create(url), new WebSocket.Listener() {
                    private final StringBuilder buffer = new StringBuilder();

                    @Override
                    public void onOpen(WebSocket webSocket) {
                        webSocket.request(1);
                    }

                    @Override
                    public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
                        buffer.append(data);
                        if (!last) {
                            webSocket.request(1);
                            return null;
                        }
                        String message = buffer.toString();
                        buffer.setLength(0);
                        handleFrame(message, audio, result, webSocket);
                        webSocket.request(1);
                        return null;
                    }

                    @Override
                    public void onError(WebSocket webSocket, Throwable error) {
                        result.completeExceptionally(error);
                    }
                })
                .join();

        ws.sendText(buildRequest(text), true);

        try {
            return result.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
        } catch (Exception e) {
            throw new RuntimeException("讯飞 TTS 合成失败: " + rootMessage(e), e);
        } finally {
            if (!ws.isInputClosed() && !ws.isOutputClosed()) {
                try {
                    ws.abort();
                } catch (Exception ignore) {
                    // 收尾失败不影响结果
                }
            }
        }
    }

    private void handleFrame(String message, StringBuilder audio, CompletableFuture<byte[]> result, WebSocket ws) {
        try {
            JsonNode node = objectMapper.readTree(message);
            int code = node.path("code").asInt(-1);
            if (code != 0) {
                result.completeExceptionally(
                        new IllegalStateException("讯飞返回错误 code=" + code + " msg=" + node.path("message").asText()));
                close(ws);
                return;
            }
            JsonNode data = node.path("data");
            String chunk = data.path("audio").asText(null);
            if (chunk != null && !chunk.isEmpty()) {
                audio.append(chunk);
            }
            if (data.path("status").asInt(0) == 2) {
                if (audio.length() == 0) {
                    result.completeExceptionally(new IllegalStateException("讯飞未返回音频数据"));
                } else {
                    result.complete(Base64.getDecoder().decode(audio.toString()));
                }
                close(ws);
            }
        } catch (Exception e) {
            result.completeExceptionally(e);
            close(ws);
        }
    }

    private String buildRequest(String text) {
        Map<String, Object> common = new LinkedHashMap<>();
        common.put("app_id", properties.getAppId());

        Map<String, Object> business = new LinkedHashMap<>();
        business.put("aue", "lame"); // mp3
        business.put("vcn", isBlank(properties.getVcn()) ? "xiaoyan" : properties.getVcn());
        business.put("tte", "UTF8");

        Map<String, Object> data = new LinkedHashMap<>();
        data.put("status", 2); // 单帧即完整文本
        data.put("text", Base64.getEncoder().encodeToString(text.getBytes(StandardCharsets.UTF_8)));

        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("common", common);
        payload.put("business", business);
        payload.put("data", data);

        try {
            return objectMapper.writeValueAsString(payload);
        } catch (Exception e) {
            throw new IllegalStateException("构造讯飞请求失败", e);
        }
    }

    private String buildAuthUrl() {
        // 签名逻辑统一收敛到 shared 的 XfyunSigner（TTS / IAT 同套签名）
        return XfyunSigner.signedWebSocketUrl(HOST, PATH, properties.getApiKey(), properties.getApiSecret());
    }

    private static void close(WebSocket ws) {
        try {
            ws.sendClose(WebSocket.NORMAL_CLOSURE, "done");
        } catch (Exception ignore) {
            // 关闭异常忽略
        }
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private static String rootMessage(Throwable e) {
        Throwable cur = e;
        while (cur.getCause() != null && cur.getCause() != cur) {
            cur = cur.getCause();
        }
        return cur.getMessage();
    }
}
