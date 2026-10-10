package com.goodzheng.po.talk.dto;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/** 会话详情：会话元信息 + 按 seq 排序的完整对话流。 */
@Data
public class SessionDetail {

    private Long id;
    private String threadId;
    private String title;
    private String scene;
    private String status;
    private Integer turnCount;
    private Long durationMs;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private List<UtteranceView> utterances = new ArrayList<>();
}
