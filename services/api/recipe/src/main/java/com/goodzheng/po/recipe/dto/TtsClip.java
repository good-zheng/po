package com.goodzheng.po.recipe.dto;

import lombok.Data;

/** 一条待合成的播报：语义名 + 文案 */
@Data
public class TtsClip {

    /**
     * 音频文件名的语义部分，同时也是响应里的标识，如 step-3、finish。
     * 只允许字母数字与 - _；非法或缺失时文件名退化为纯哈希。
     */
    private String name;

    /** 要合成成语音的文本 */
    private String text;
}
