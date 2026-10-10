package com.goodzheng.po.talk.constant;

/** 言外（EchoTalk）领域常量。取值落库，改动需同步历史数据与小程序端。 */
public final class TalkConstants {

    private TalkConstants() {
    }

    // ── 说话人 ────────────────────────────────────────────
    /** 对方：AI 的分析对象，只有这类话语会触发洞察与建议 */
    public static final String SPEAKER_OTHER = "other";
    /** 我：仅记录，不触发分析 */
    public static final String SPEAKER_ME = "me";
    public static final String SPEAKER_UNKNOWN = "unknown";

    // ── 话语来源 ──────────────────────────────────────────
    public static final String SOURCE_VOICE = "voice";
    public static final String SOURCE_TEXT = "text";

    // ── 会话状态 ──────────────────────────────────────────
    public static final String STATUS_RECORDING = "recording";
    public static final String STATUS_ENDED = "ended";

    // ── 场景 ─────────────────────────────────────────────
    public static final String SCENE_GENERAL = "general";
    public static final String SCENE_WORK = "work";
    public static final String SCENE_SALES = "sales";
    public static final String SCENE_ROMANCE = "romance";

    /** 单条话语文本长度上限：超长段（如对方长篇独白）截断，避免撑爆上下文与存储 */
    public static final int MAX_UTTERANCE_LENGTH = 2000;
}
