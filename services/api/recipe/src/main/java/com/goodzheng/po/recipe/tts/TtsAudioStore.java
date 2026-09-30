package com.goodzheng.po.recipe.tts;

import com.goodzheng.po.recipe.dto.TtsClip;
import com.goodzheng.po.shared.storage.ObjectStorage;
import jakarta.annotation.PreDestroy;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * 合成音频的对象存储仓库：同一菜谱、同一步骤、同一份文案 + 同一发音人只合成一次。
 *
 * 目录按菜谱分开，在控制台里一眼能看出某个对象属于哪道菜的哪一步：
 * <pre>
 *   {cos.key-prefix}/tts/recipes/{菜谱ID}/{发音人}/step-3-1a2b3c4d.mp3   第 3 步
 *   {cos.key-prefix}/tts/recipes/{菜谱ID}/{发音人}/finish-5e6f7a8b.mp3   完成播报
 *   {cos.key-prefix}/tts/misc/{发音人}/{哈希前2位}/{哈希}.mp3            无菜谱上下文的自由文本
 * </pre>
 * 文件名 = 调用方给的语义名 + 文案哈希前 8 位：改了步骤文案哈希就变，新文案落到新对象，
 * 不会播出旧内容；旧对象留在原地不影响正确性，要清理按 {@code tts/recipes/{ID}/} 前缀列举即可。
 * misc 没有菜谱可归属，用全哈希并按前两位分片，避免单前缀堆积到百万级后列举变慢。
 * 发音人参与哈希与目录，换音色后旧音频自然失效（不会串味），也便于按前缀配生命周期规则。
 * 取单条（{@link #audioUrl}）与批量预热（{@link #prefetch}）共用同一套 {@link #objectPath}，缓存不会各说各话。
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class TtsAudioStore {

    /** 发音人只允许出现在对象 key 里的安全字符，异常配置退回占位名 */
    private static final Pattern SAFE_VCN = Pattern.compile("[A-Za-z0-9_-]{1,32}");

    /** 音频文件名的语义部分（step-3、finish 之类），同样限制在安全字符内 */
    private static final Pattern SAFE_NAME = Pattern.compile("[A-Za-z0-9_-]{1,32}");

    private static final String RECIPE_DIR = "tts/recipes/";
    private static final String MISC_DIR = "tts/misc/";

    private final XfyunTtsService ttsService;
    private final ObjectStorage storage;
    private final XfyunTtsProperties props;

    /** 同 key 的并发请求合并：一次合成，其余等待同一结果，避免同一文本被打成多份 */
    private final Map<String, CompletableFuture<String>> inFlight = new ConcurrentHashMap<>();

    /** 已排进预热队列的对象 key：反复进出做菜页时不再重复排队 */
    private final Set<String> queued = ConcurrentHashMap.newKeySet();

    /**
     * 预热专用线程池。讯飞并发路数有限，2 路串行合成即可：用户看第一步文案的几十秒里，
     * 后面十几步基本都能合成完。队列满时直接拒绝，退化成播放时再同步合成，不拖慢接口。
     */
    private final ExecutorService prefetchPool = new ThreadPoolExecutor(
            2,
            2,
            0L,
            TimeUnit.MILLISECONDS,
            new LinkedBlockingQueue<>(200),
            runnable -> {
                Thread thread = new Thread(runnable, "tts-prefetch");
                thread.setDaemon(true);
                return thread;
            });

    /**
     * 返回该文案的公网音频 URL；桶里已有对象时直接复用，不重复合成。
     *
     * @param recipeId 所属菜谱 ID，null 或非正数时归入 misc 目录
     * @param name     期望的文件名语义部分（如 step-3、finish），不安全时退化为纯哈希
     * @throws IllegalStateException 合成结果为空音频
     */
    public String audioUrl(Long recipeId, String name, String text) {
        String path = objectPath(recipeId, name, text);
        CompletableFuture<String> mine = new CompletableFuture<>();
        CompletableFuture<String> running = inFlight.putIfAbsent(path, mine);
        if (running != null) {
            return running.join();
        }
        try {
            String url = synthesizeOnce(path, text);
            mine.complete(url);
            return url;
        } catch (RuntimeException e) {
            mine.completeExceptionally(e);
            throw e;
        } finally {
            inFlight.remove(path, mine);
        }
    }

    /**
     * 预热一批音频：桶里已有的立即返回，缺失的排入后台线程合成，本次响应不等待。
     *
     * @return 「clip.name → URL」，只含已就绪的条目；首次预热某道菜返回空 map 是正常结果
     */
    public Map<String, String> prefetch(Long recipeId, List<TtsClip> clips) {
        Map<String, String> ready = new LinkedHashMap<>();
        for (TtsClip clip : clips) {
            String text = clip.getText();
            if (text == null || text.isBlank()) {
                continue;
            }
            String path = objectPath(recipeId, clip.getName(), text);
            if (storage.exists(path)) {
                ready.put(clipId(clip), storage.urlFor(path));
                continue;
            }
            enqueue(recipeId, clip, path);
        }
        return ready;
    }

    private void enqueue(Long recipeId, TtsClip clip, String path) {
        if (!queued.add(path)) {
            return;
        }
        String text = clip.getText();
        try {
            prefetchPool.execute(() -> {
                try {
                    audioUrl(recipeId, clip.getName(), text);
                } catch (RuntimeException e) {
                    log.warn("TTS 预热合成失败, path={}", path, e);
                } finally {
                    queued.remove(path);
                }
            });
        } catch (RejectedExecutionException e) {
            queued.remove(path);
            log.warn("TTS 预热队列已满，改为播放时再合成, path={}", path);
        }
    }

    @PreDestroy
    public void shutdownPrefetchPool() {
        prefetchPool.shutdownNow();
    }

    private String synthesizeOnce(String path, String text) {
        if (storage.exists(path)) {
            return storage.urlFor(path);
        }
        byte[] audio = ttsService.synthesize(text);
        if (audio == null || audio.length == 0) {
            log.warn("TTS 合成返回空音频, text={}", text);
            throw new IllegalStateException("语音合成返回空音频");
        }
        storage.upload(path, audio, "audio/mpeg");
        return storage.urlFor(path);
    }

    /** 回给调用方的标识：优先用它自己给的 name，缺失或不安全时用原文兜底 */
    private static String clipId(TtsClip clip) {
        String name = clip.getName();
        return name != null && SAFE_NAME.matcher(name).matches() ? name : clip.getText();
    }

    private String objectPath(Long recipeId, String name, String text) {
        String vcn = SAFE_VCN.matcher(String.valueOf(props.getVcn())).matches()
                ? props.getVcn()
                : "default";
        // 发音人参与哈希：换 vcn 后同一段文本落到不同对象，不会命中旧音色的音频
        String hash = md5(vcn + "\n" + text);
        if (recipeId == null || recipeId <= 0) {
            return MISC_DIR + vcn + "/" + hash.substring(0, 2) + "/" + hash + ".mp3";
        }
        String fileName = name != null && SAFE_NAME.matcher(name).matches()
                ? name + "-" + hash.substring(0, 8)
                : hash;
        return RECIPE_DIR + recipeId + "/" + vcn + "/" + fileName + ".mp3";
    }

    private static String md5(String value) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(value.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder(digest.length * 2);
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            // MD5 是 JDK 必备算法，走到这里说明环境异常；退化成 hashCode 也要保证 key 稳定
            return Integer.toHexString(value.hashCode());
        }
    }
}
