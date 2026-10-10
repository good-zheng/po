package com.goodzheng.po.talk.dto;

import lombok.Data;

/** 一条回复建议。style 为 稳妥 / 共情 / 推进，why 是给用户的策略说明。 */
@Data
public class SuggestionItem {

    private String style;

    private String text;

    private String why;
}
