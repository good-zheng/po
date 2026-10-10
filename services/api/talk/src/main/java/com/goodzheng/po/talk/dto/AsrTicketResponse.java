package com.goodzheng.po.talk.dto;

import lombok.Data;

/**
 * ASR 一次性票据。
 *
 * <p>微信小程序 WebSocket 不能带自定义请求头，JWT 只能拼在 query 里，会被访问日志记录。
 * 故用短期一次性 ticket 换取连接：换取后 60 秒内有效，建立连接即失效。
 */
@Data
public class AsrTicketResponse {

    private String ticket;

    /** 有效期（秒） */
    private int expiresIn;
}
