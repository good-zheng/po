package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.List;

/**
 * 文风契约的写入口（{@code PUT /novel/books/{bookId}/style}）。
 *
 * <p>字段全部可选：契约是逐条收紧的过程，作者一次只定人称与字数带是常态，
 * 未提供的字段保留库里的原值而不是被清空——「没填」不等于「填了空」。
 */
@Data
public class StyleProfileRequest {

    private String person;

    private String tense;

    private Integer sentenceLenMin;

    private Integer sentenceLenMax;

    private Integer chapterWordsMin;

    private Integer chapterWordsMax;

    private List<String> forbiddenWords;

    private List<String> tics;

    private List<String> taboo;
}
