package com.goodzheng.po.talk.dto;

import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/**
 * chat 服务（agent-talk）产出建议后回调落库的载荷。
 *
 * <p>与 agent-cooking 调用菜谱接口同属「Python 侧回调 Java 侧」的内网链路，
 * 由 {@code X-Internal-Token} 保护，不对外暴露（见 SecurityConfig 的 /talk/internal/** 规则）。
 */
@Data
public class InternalSuggestionRequest {

    /** 目标话语 id；缺省时按 threadId 定位会话并追加到最后一条对方话语 */
    private Long utteranceId;

    private String threadId;

    private String model;

    private Integer latencyMs;

    private String intent;

    private String subtext;

    private String emotion;

    private String risk;

    private List<SuggestionItem> suggestions = new ArrayList<>();

    private List<String> followups = new ArrayList<>();
}
