package com.goodzheng.po.talk.asr;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** 讯飞语音听写（IAT v2，WebSocket）鉴权与识别参数，值来自 application-local.yaml / 环境变量，勿明文提交。 */
@Data
@Component
@ConfigurationProperties(prefix = "xfyun.iat")
public class XfyunAsrProperties {

    private String appId;
    private String apiKey;
    private String apiSecret;

    /** 语种：zh_cn 中文，en_us 英文 */
    private String language = "zh_cn";

    /** 口音：mandarin 普通话 */
    private String accent = "mandarin";

    /**
     * 单个讯飞会话的音频时长上限（秒）。
     * 讯飞硬限制 60s，这里留 5s 余量主动收尾并重开连接，避免服务端直接掐断丢字。
     */
    private int maxSeconds = 55;
}
