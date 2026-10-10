package com.goodzheng.po.talk.dto;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/** agent-talk 一轮产出的完整结果：四段洞察 + 三条建议 + 可追问。 */
@Data
public class SuggestionView {

    private Long id;
    private Long utteranceId;
    private String model;
    /** 对方真正想要的 */
    private String intent;
    /** 潜台词 */
    private String subtext;
    /** 情绪标签与强度描述 */
    private String emotion;
    /** 风险提示 */
    private String risk;
    private List<SuggestionItem> suggestions = new ArrayList<>();
    private List<String> followups = new ArrayList<>();
    private Integer latencyMs;
    private LocalDateTime createdAt;
}
