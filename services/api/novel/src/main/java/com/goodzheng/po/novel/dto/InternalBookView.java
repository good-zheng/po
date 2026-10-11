package com.goodzheng.po.novel.dto;

import lombok.Data;

/**
 * 书本读回端点（GET /novel/internal/books/detail）交给对话装配的形状。
 *
 * <p>为什么只带一章：L1 编译器对「已定稿章节」的全部需求就是参照章的标题与末尾原文
 * （近因层的原文尾段），其余章在这条链路上一个字段都不读。回整本正文会让一次对话
 * 的固定开销随书长线性增长，而那正是 §1.2 里 long-context 硬塞全文的失败模式。
 */
@Data
public class InternalBookView {

    private Long bookId;

    private String title;

    /** 题材；对话侧据此构造默认文风契约 */
    private String genre;

    /** 主线梗概（Tier-0 的「世界观与主线」行） */
    private String summary;

    /**
     * 有正文的章数：对话据此判断参照章号是否越界，续写据此定本轮起点。
     *
     * <p>不含正文留空的占位章——那一行是「排给下一轮的位子」，把它算进游标会让续写跳过它
     * 往后写，于是它永久空着，而衔接用的「上一章结尾」读成空串。
     */
    private Integer chapterCount;

    /** 参照章；请求没带 chapterId 或那一章不属于这本书时为 null */
    private Chapter chapter;

    @Data
    public static class Chapter {

        private Long chapterId;

        /** 1 基章号，即对话侧的 as-of */
        private Integer chapterIndex;

        private String title;

        /** 全文：裁剪与估算是编译器的事，这里不做截断，否则两处口径会分叉 */
        private String content;
    }
}
