package com.goodzheng.po.recipe.controller;

import com.goodzheng.po.recipe.dto.TtsClip;
import com.goodzheng.po.recipe.dto.TtsPrefetchRequest;
import com.goodzheng.po.recipe.dto.TtsPrefetchResult;
import com.goodzheng.po.recipe.tts.TtsAudioStore;
import com.goodzheng.po.shared.dto.Result;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * TTS 语音合成接口：返回中文语音 MP3 的腾讯云 COS 公网 URL。
 * 云托管本地磁盘临时且多实例不共享，故不落 uploads/；缓存与目录布局由 {@link TtsAudioStore} 负责。
 */
@Slf4j
@RestController
@RequestMapping("/tts")
@RequiredArgsConstructor
public class TtsController {

    /** 单次预热的条数上限：一道菜只有十几步，超出部分视为异常请求，截断即可 */
    private static final int MAX_PREFETCH_CLIPS = 50;

    private final TtsAudioStore audioStore;

    /**
     * 合成单条播报。recipeId / name 可选，只决定音频落在哪个目录、叫什么名字，
     * 内容与缓存仍由文案哈希决定；预热过的条目带上这两个参数才能命中同一份对象。
     */
    @GetMapping
    public Result<Map<String, String>> synthesize(
            @RequestParam String text,
            @RequestParam(required = false) Long recipeId,
            @RequestParam(required = false) String name) {
        if (text == null || text.isBlank()) {
            return Result.error("文本不能为空");
        }
        try {
            Map<String, String> data = new HashMap<>();
            data.put("url", audioStore.audioUrl(recipeId, name, text));
            return Result.success(data);
        } catch (Exception e) {
            log.error("TTS 合成失败, text={}", text, e);
            return Result.error("语音合成失败");
        }
    }

    /**
     * 预热一批播报（进入做菜模式时调用）：桶里已有的立刻按 name 返回 URL，缺失的交给后台线程合成。
     * 响应不等待合成，所以首次进入某道菜返回的 map 可能为空，属于正常结果。
     */
    @PostMapping("/prefetch")
    public Result<TtsPrefetchResult> prefetch(@RequestBody(required = false) TtsPrefetchRequest request) {
        List<TtsClip> clips = request == null ? null : request.getClips();
        if (clips == null || clips.isEmpty()) {
            return Result.error("播报内容不能为空");
        }
        try {
            List<TtsClip> batch = clips.size() > MAX_PREFETCH_CLIPS
                    ? clips.subList(0, MAX_PREFETCH_CLIPS)
                    : clips;
            return Result.success(new TtsPrefetchResult(audioStore.prefetch(request.getRecipeId(), batch)));
        } catch (Exception e) {
            log.error("TTS 预热失败, recipeId={}, count={}", request.getRecipeId(), clips.size(), e);
            return Result.error("语音预热失败");
        }
    }
}
