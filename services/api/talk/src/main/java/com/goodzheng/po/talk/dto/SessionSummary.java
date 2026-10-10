package com.goodzheng.po.talk.dto;

import java.time.LocalDateTime;
import lombok.Data;

/** 历史列表项：标题 + 首句摘要 + 轮次 + 时长。 */
@Data
public class SessionSummary {

    private Long id;
    private String threadId;
    private String title;
    private String scene;
    private String status;
    private Integer turnCount;
    private Long durationMs;
    /** 首条对方话语的截断文本，用于列表预览 */
    private String preview;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
