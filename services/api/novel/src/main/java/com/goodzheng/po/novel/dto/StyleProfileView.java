package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.List;

/**
 * 文风契约（§5.5）的对外形状。
 *
 * <p>三个词表在这里是字符串数组而不是库里的 JSON 文本：注入侧（L1 编译器的 Tier-0）与
 * 闸门侧（{@code GateRules.forbidden_words}）要的都是数组，让调用方各自再解一次 JSON
 * 只会把「谁写的这份契约」变成三份解析实现。
 */
@Data
public class StyleProfileView {

    private Long id;

    private Long bookId;

    /** 第几人称，如「第三人称限知」 */
    private String person;

    private String tense;

    private Integer sentenceLenMin;

    private Integer sentenceLenMax;

    private Integer chapterWordsMin;

    private Integer chapterWordsMax;

    private List<String> forbiddenWords = List.of();

    private List<String> tics = List.of();

    private List<String> taboo = List.of();
}
