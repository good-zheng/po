package com.goodzheng.po.shared.storage;

import com.qcloud.cos.COSClient;
import com.qcloud.cos.ClientConfig;
import com.qcloud.cos.auth.BasicCOSCredentials;
import com.qcloud.cos.auth.COSCredentials;
import com.qcloud.cos.model.ObjectMetadata;
import com.qcloud.cos.model.PutObjectRequest;
import com.qcloud.cos.region.Region;
import java.io.ByteArrayInputStream;
import org.springframework.beans.factory.DisposableBean;
import org.springframework.stereotype.Component;

/**
 * 腾讯云 COS 对象存储：把上传的图片与 TTS 音频写进桶并返回公网 URL。
 * 云托管容器本地磁盘是临时的、且多实例不共享，用户产物一律落桶，不再写 file:uploads/。
 * COSClient 首次用到时才建，避免未配置密钥时拖垮启动；返回的绝对 URL 小程序端直接可用。
 */
@Component
public class ObjectStorage implements DisposableBean {

    private final CosProperties props;
    private volatile COSClient client;

    public ObjectStorage(CosProperties props) {
        this.props = props;
    }

    /** 上传字节，返回对象公网 URL。path 为桶内相对路径，如 "tts/xxx.mp3"。 */
    public String upload(String path, byte[] content, String contentType) {
        String key = fullKey(path);
        ObjectMetadata meta = new ObjectMetadata();
        meta.setContentLength(content.length);
        if (contentType != null && !contentType.isBlank()) {
            meta.setContentType(contentType);
        }
        cos().putObject(new PutObjectRequest(props.getBucket(), key, new ByteArrayInputStream(content), meta));
        return urlFor(path);
    }

    /** 桶内是否已存在该对象（TTS 命中缓存，避免重复合成）。 */
    public boolean exists(String path) {
        return cos().doesObjectExist(props.getBucket(), fullKey(path));
    }

    /** 对象公网访问 URL。 */
    public String urlFor(String path) {
        return props.publicBaseUrl() + "/" + fullKey(path);
    }

    private String fullKey(String path) {
        String prefix = props.getKeyPrefix();
        String head = (prefix == null || prefix.isBlank()) ? "" : trimSlashes(prefix) + "/";
        return head + trimLeadingSlash(path);
    }

    private COSClient cos() {
        COSClient current = client;
        if (current != null) {
            return current;
        }
        synchronized (this) {
            if (client == null) {
                if (isBlank(props.getSecretId()) || isBlank(props.getSecretKey())
                        || isBlank(props.getRegion()) || isBlank(props.getBucket())) {
                    throw new IllegalStateException("腾讯云 COS 未配置（secretId/secretKey/region/bucket）");
                }
                COSCredentials cred = new BasicCOSCredentials(props.getSecretId(), props.getSecretKey());
                client = new COSClient(cred, new ClientConfig(new Region(props.getRegion())));
            }
            return client;
        }
    }

    @Override
    public void destroy() {
        if (client != null) {
            client.shutdown();
        }
    }

    private static boolean isBlank(String value) {
        return value == null || value.isBlank();
    }

    private static String trimSlashes(String value) {
        String v = value.endsWith("/") ? value.substring(0, value.length() - 1) : value;
        return trimLeadingSlash(v);
    }

    private static String trimLeadingSlash(String value) {
        return value.startsWith("/") ? value.substring(1) : value;
    }
}
