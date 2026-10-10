package com.goodzheng.po.talk.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.goodzheng.po.talk.constant.TalkConstants;
import java.time.LocalDateTime;
import lombok.Data;

/** 言外-话语：对方或我说的一句话（语音转写定稿，或手动输入）。 */
@Data
@TableName("talk_utterance")
public class TalkUtterance {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long sessionId;

    private Long userId;

    /** 段内序号，从 1 开始 */
    private Integer seq;

    /** 说话人: other对方, me我, unknown未知 */
    private String speaker = TalkConstants.SPEAKER_OTHER;

    /** 来源: voice语音, text文字 */
    private String source = TalkConstants.SOURCE_VOICE;

    private String content;

    /** 是否被用户手工纠错 */
    private Boolean edited = false;

    /** ASR 置信度，文本输入为 null */
    private Double confidence;

    /** 相对会话开始的毫秒偏移，用于时间轴定位 */
    private Long startMs;

    private Long endMs;

    private LocalDateTime createdAt = LocalDateTime.now();
}
