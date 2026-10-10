package com.goodzheng.po.talk.dto;

import lombok.Data;

/** 修改会话：标题、场景、状态。字段为 null 表示不修改。 */
@Data
public class UpdateSessionRequest {

    private String title;

    private String scene;

    /** recording进行中 / ended已结束 */
    private String status;

    /** 累计录音时长（毫秒），结束会话时上报 */
    private Long durationMs;
}
