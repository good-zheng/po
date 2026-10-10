package com.goodzheng.po.talk.dto;

import lombok.Data;

/** 纠错某条话语：改文本（重新分析的输入）或改说话人（分析报告对象）。 */
@Data
public class UpdateUtteranceRequest {

    private String content;

    /** 说话人: other对方, me我 */
    private String speaker;
}
