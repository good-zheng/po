package com.goodzheng.po.novel.dto;

import lombok.Data;

@Data
public class ChapterRequest {

    /**
     * 章节标题。允许留空：空标题在本服务里统一写成「第 N 章」，落库的 title 列永不为空。
     *
     * <p>留空且正文也为空的那一章是「待写占位」——管理端据此排期，续写链路按章号把它填掉
     * （见 {@code BookChapterService#putByIndex}）。
     */
    private String title;

    private String content;

    /** 章节索引（可选，为空时自动取当前最大序号+1） */
    private Integer chapterIndex;
}
