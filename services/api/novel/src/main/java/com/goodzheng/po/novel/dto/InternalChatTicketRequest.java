package com.goodzheng.po.novel.dto;

import lombok.Data;

/** chat 服务提交给后端校验的握手票据 */
@Data
public class InternalChatTicketRequest {

    private String ticket;
}
