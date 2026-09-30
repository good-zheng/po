package com.goodzheng.po.identity.wechat;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.converter.StringHttpMessageConverter;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class WeChatService {

    private static final String JS_CODE_SESSION_PATH =
            "/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code";

    private static final String ACCESS_TOKEN_PATH =
            "/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}";

    private static final String GET_PHONE_NUMBER_PATH =
            "/wxa/business/getuserphonenumber?access_token={access_token}";

    private final WeChatProperties weChatProperties;
    private final RestTemplate restTemplate = createRestTemplate();

    private static RestTemplate createRestTemplate() {
        RestTemplate rt = new RestTemplate();
        rt.setMessageConverters(Arrays.asList(
                new StringHttpMessageConverter(StandardCharsets.UTF_8)
        ));
        return rt;
    }

    private volatile String cachedAccessToken;
    private volatile Instant tokenExpiresAt = Instant.MIN;

    public String getOpenIdByCode(String code) {
        String url = wxUrl(JS_CODE_SESSION_PATH)
                .replace("{appid}", weChatProperties.getAppId())
                .replace("{secret}", weChatProperties.getAppSecret())
                .replace("{code}", code);

        Map<String, Object> response = wxGet(url);

        if (response.containsKey("errcode") && !Integer.valueOf(0).equals(response.get("errcode"))) {
            log.warn("wx jscode2session failed: {}", response);
            throw new RuntimeException("微信登录失败: " + response.get("errmsg"));
        }

        String openId = (String) response.get("openid");
        if (openId == null || openId.isEmpty()) {
            throw new RuntimeException("微信登录失败: 未获取到 openid");
        }
        return openId;
    }

    public String getPhoneNumberByCode(String code) {
        String accessToken = getAccessToken();
        String url = wxUrl(GET_PHONE_NUMBER_PATH).replace("{access_token}", accessToken);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<String> entity = new HttpEntity<>("{\"code\":\"" + code + "\"}", headers);

        String raw = restTemplate.postForObject(url, entity, String.class);
        Map<String, Object> response = parseJson(raw);

        Integer errCode = (Integer) response.get("errcode");
        if (errCode == null || errCode != 0) {
            log.warn("wx getPhoneNumber failed: {}", response);
            throw new RuntimeException("获取手机号失败: " + response.get("errmsg"));
        }

        @SuppressWarnings("unchecked")
        Map<String, Object> phoneInfo = (Map<String, Object>) response.get("phone_info");
        if (phoneInfo == null) {
            throw new RuntimeException("获取手机号失败: 无 phone_info");
        }

        String phoneNumber = (String) phoneInfo.get("purePhoneNumber");
        if (phoneNumber == null || phoneNumber.isEmpty()) {
            throw new RuntimeException("获取手机号失败: 无手机号");
        }
        return phoneNumber;
    }

    private String getAccessToken() {
        if (cachedAccessToken != null && Instant.now().isBefore(tokenExpiresAt)) {
            return cachedAccessToken;
        }
        synchronized (this) {
            if (cachedAccessToken != null && Instant.now().isBefore(tokenExpiresAt)) {
                return cachedAccessToken;
            }
            String url = wxUrl(ACCESS_TOKEN_PATH)
                    .replace("{appid}", weChatProperties.getAppId())
                    .replace("{secret}", weChatProperties.getAppSecret());

            Map<String, Object> response = wxGet(url);
            if (!response.containsKey("access_token")) {
                log.warn("wx getAccessToken failed: {}", response);
                throw new RuntimeException("获取微信 access_token 失败: " + response.get("errmsg"));
            }

            cachedAccessToken = (String) response.get("access_token");
            int expiresIn = (int) response.getOrDefault("expires_in", 7200);
            tokenExpiresAt = Instant.now().plusSeconds(expiresIn - 300);
            return cachedAccessToken;
        }
    }

    private String wxUrl(String path) {
        return weChatProperties.getApiBaseUrl() + path;
    }

    private Map<String, Object> wxGet(String url) {
        String raw = restTemplate.getForObject(url, String.class);
        log.debug("wx response: {}", raw);
        return parseJson(raw);
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> parseJson(String raw) {
        if (raw == null || raw.isEmpty()) {
            throw new RuntimeException("微信接口返回为空");
        }
        try {
            return org.springframework.boot.json.JsonParserFactory.getJsonParser()
                    .parseMap(raw);
        } catch (Exception e) {
            log.error("Failed to parse wx response: {}", raw, e);
            throw new RuntimeException("微信接口返回格式异常");
        }
    }
}
