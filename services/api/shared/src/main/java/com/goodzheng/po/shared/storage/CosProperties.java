package com.goodzheng.po.shared.storage;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * 腾讯云 COS 对象存储配置。密钥仅从环境变量注入，不落库、不打进镜像。
 * 缺省对齐本项目：地域 ap-shanghai，桶为云托管绑定的 COS 桶。
 */
@Data
@Component
@ConfigurationProperties(prefix = "cos")
public class CosProperties {

    /** API 密钥 SecretId（云托管/腾讯云账号或子账号，需 COS 读写权限） */
    private String secretId;

    /** API 密钥 SecretKey */
    private String secretKey;

    /** 地域，如 ap-shanghai */
    private String region = "ap-shanghai";

    /** 桶名（含 APPID 后缀），如 7072-prod-xxxx-1496875399 */
    private String bucket;

    /** 对象 key 统一前缀（目录），为空则不加 */
    private String keyPrefix = "po";

    /**
     * 自定义访问域名（CDN / 静态源站域名）。留空则用默认公网域名
     * https://{bucket}.cos.{region}.myqcloud.com
     */
    private String baseUrl = "";

    /** 对外可访问的基地址（不含结尾斜杠）。 */
    public String publicBaseUrl() {
        String base = (baseUrl == null || baseUrl.isBlank())
                ? "https://" + bucket + ".cos." + region + ".myqcloud.com"
                : baseUrl;
        return base.endsWith("/") ? base.substring(0, base.length() - 1) : base;
    }
}
