package com.goodzheng.po.identity.wechat;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Data
@Component
@ConfigurationProperties(prefix = "wechat.mini")
public class WeChatProperties {

    private String appId;

    private String appSecret;

    /** 微信接口基址；本地 https，云托管内开启「开放接口服务」后走内网 http。 */
    private String apiBaseUrl = "https://api.weixin.qq.com";
}
