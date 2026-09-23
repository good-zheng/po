package com.goodzheng.po.recipe.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/** 管理端审核请求 */
@Data
public class AuditRequest {

    /** approve=通过，reject=驳回 */
    @NotBlank(message = "审核动作不能为空")
    private String action;

    /** 驳回原因（action=reject 时必填，由 Controller 校验） */
    private String reason;
}
