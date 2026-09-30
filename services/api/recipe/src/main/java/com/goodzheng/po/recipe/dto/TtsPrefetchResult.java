package com.goodzheng.po.recipe.dto;

import java.util.Map;
import lombok.AllArgsConstructor;
import lombok.Data;

/** TTS 批量预热结果：只含桶里已经就绪的条目 */
@Data
@AllArgsConstructor
public class TtsPrefetchResult {

    /** 请求里的 clip name → 音频公网 URL；未就绪的条目不出现在这里，由后台合成 */
    private Map<String, String> urls;
}
