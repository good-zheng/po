package com.goodzheng.po.talk.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import java.time.LocalDateTime;
import lombok.Data;

/** 言外-建议：agent-talk 对某条对方话语产出的一轮洞察与回复建议。 */
@Data
@TableName("talk_suggestion")
public class TalkSuggestion {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long sessionId;

    private Long utteranceId;

    private Long userId;

    private String model;

    /** 对方真正想要的 */
    private String intent;

    /** 潜台词 */
    private String subtext;

    /** 情绪标签，如「回避 · 略带不满」 */
    private String emotion;

    /** 风险提示 */
    private String risk;

    /** 完整结构化结果（含 suggestions / followups）的 JSON 文本 */
    private String payload;

    private Integer latencyMs;

    private LocalDateTime createdAt = LocalDateTime.now();
}
