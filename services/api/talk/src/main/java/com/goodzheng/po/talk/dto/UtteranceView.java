package com.goodzheng.po.talk.dto;

import java.time.LocalDateTime;
import lombok.Data;

/** 会话详情里的一句话；只有「对方」的话才带 suggestion。 */
@Data
public class UtteranceView {

    private Long id;
    private Integer seq;
    private String speaker;
    private String source;
    private String content;
    private Boolean edited;
    private Double confidence;
    private Long startMs;
    private Long endMs;
    private LocalDateTime createdAt;
    /** 该句话触发的分析结果，speaker=me 或尚未分析时为 null */
    private SuggestionView suggestion;
}
