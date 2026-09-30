package com.goodzheng.po.recipe.tts;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** 讯飞超融合语音合成（TTS v2）鉴权与音色配置，值来自环境变量，勿明文提交。 */
@Data
@Component
@ConfigurationProperties(prefix = "xfyun.tts")
public class XfyunTtsProperties {

    private String appId;
    private String apiKey;
    private String apiSecret;
    /** 发音人，默认 xiaoyan（标准女声） */
    private String vcn = "xiaoyan";
}
