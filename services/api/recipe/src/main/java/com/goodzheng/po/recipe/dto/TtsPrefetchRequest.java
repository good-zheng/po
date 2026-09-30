package com.goodzheng.po.recipe.dto;

import java.util.List;
import lombok.Data;

/** TTS 批量预热请求 */
@Data
public class TtsPrefetchRequest {

    /** 这批播报属于哪道菜，决定桶内目录；为空则归入 misc */
    private Long recipeId;

    /** 待预热的音频，顺序即后台合成排队顺序 */
    private List<TtsClip> clips;
}
