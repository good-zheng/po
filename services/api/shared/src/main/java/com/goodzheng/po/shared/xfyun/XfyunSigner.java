package com.goodzheng.po.shared.xfyun;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Base64;
import java.util.Locale;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

/**
 * 讯飞开放平台 WebAPI 的统一鉴权（语音合成 TTS / 语音听写 IAT 共用同一套签名）。
 *
 * <p>签名原始串固定为 {@code host: {host}\ndate: {date}\nGET {path} HTTP/1.1}，
 * <b>结尾不能带换行</b>，否则讯飞判定 HMAC 不匹配（返回 10163 / 401）。
 * 参与签名的头固定写作 "host date request-line"（是参数名而非值）。
 *
 * <p>只依赖 JDK（javax.crypto），无第三方依赖，shared 模块可直接承载。
 */
public final class XfyunSigner {

    /**
     * 讯飞要求的日期串是「个位数日期也补零」的 RFC1123（官方 demo 用 {@code dd}）。
     * JDK 自带的 {@code RFC_1123_DATE_TIME} 不补零（"1 Oct"），讯飞判定 date 无效，
     * 回 403 "a valid date or x-date header is required" —— 而每月 10-31 号两种格式一模一样，
     * 只有 1-9 号才暴露，所以这个坑会在每月月初准时复现。
     */
    private static final DateTimeFormatter HTTP_DATE =
            DateTimeFormatter.ofPattern("EEE, dd MMM yyyy HH:mm:ss 'GMT'", Locale.ENGLISH);

    private XfyunSigner() {
    }

    /** RFC1123 格式的 UTC 时间，如 Tue, 14 May 2024 08:43:39 GMT（日补零：01, 09） */
    public static String rfc1123Date() {
        return HTTP_DATE.format(ZonedDateTime.now(ZoneOffset.UTC));
    }

    /**
     * 构造带鉴权参数的 wss 地址。
     *
     * @param host      如 tts-api.xfyun.cn / iat-api.xfyun.cn
     * @param path      如 /v2/tts / /v2/iat
     * @param apiKey    控制台 APIKey
     * @param apiSecret 控制台 APISecret
     */
    public static String signedWebSocketUrl(String host, String path, String apiKey, String apiSecret) {
        String date = rfc1123Date();
        String origin = "host: " + host + "\n" + "date: " + date + "\n" + "GET " + path + " HTTP/1.1";
        String signature = hmacSha256Base64(apiSecret, origin);
        String authOrigin = "api_key=\"" + apiKey
                + "\", algorithm=\"hmac-sha256\", headers=\"host date request-line\", signature=\"" + signature + "\"";
        String authorization = Base64.getEncoder().encodeToString(authOrigin.getBytes(StandardCharsets.UTF_8));

        return "wss://" + host + path
                + "?authorization=" + urlEncode(authorization)
                + "&host=" + urlEncode(host)
                + "&date=" + urlEncode(date);
    }

    public static String hmacSha256Base64(String secret, String data) {
        try {
            Mac mac = Mac.getInstance("HmacSHA256");
            mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
            return Base64.getEncoder().encodeToString(mac.doFinal(data.getBytes(StandardCharsets.UTF_8)));
        } catch (Exception e) {
            throw new IllegalStateException("讯飞签名计算失败", e);
        }
    }

    /** URLEncoder 把空格编成 +，讯飞按 RFC 要求空格必须是 %20 */
    public static String urlEncode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8).replace("+", "%20");
    }
}
