package com.goodzheng.po.novel.dto;

import lombok.Data;

/** 对话面板握手票据：客户端拿到后拼在 {@code /ws/chat?ticket=} 上 */
@Data
public class ChatTicketView {

    private String ticket;

    /** 有效期（秒）。只在「拿到票据后建立连接」这段时间内有用 */
    private int expiresIn;
}
