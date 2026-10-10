package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/**
 * 改一章会波及哪些后续章（§10.5-③ 的第④件事）。
 *
 * <p>长篇的连锁改错就发生在这里：作者改的是第 12 章的一句话，读到这条事实的却是第 30 章。
 * 保存后不给这份清单，等于让作者盲改——所以清单是接口的一部分，不是前端的推测。
 */
@Data
public class ChapterImpactView {

    private Long chapterId;

    private Integer chapterIndex;

    /** 当前版本号，配合 chapter_revision 定位任一历史正文 */
    private Integer revision;

    private String status;

    /** 仍会读到「出处在本章」的断言的后续章 */
    private List<AffectedChapter> affectedChapters = new ArrayList<>();

    /** 出处引文已不在当前正文里的断言（改稿后待作者处理，台账里对应 source_orphaned 行） */
    private List<OrphanedAssertion> orphanedAssertions = new ArrayList<>();

    /** 本章证据已被改写、状态转为 orphaned 的待裁定冲突数 */
    private long orphanedFindings;

    @Data
    public static class AffectedChapter {

        private Long chapterId;

        private Integer chapterIndex;

        private String title;

        /** draft/pending_review/committed */
        private String status;

        /** 该章为什么会看到本章的事实：命中的断言 id */
        private List<Long> canonIds = new ArrayList<>();

        /** 给作者看的一句话，列前几条断言的主-谓 */
        private String brief;
    }

    @Data
    public static class OrphanedAssertion {

        private Long canonId;

        private String subjectKey;

        private String predicate;

        private String objectText;

        /** 断言当初引的那句原文，现在正文里已经找不到了 */
        private String evidenceQuote;

        /** 台账里那条未裁定的 source_orphaned，便于作者从清单直接跳到裁定 */
        private Long findingId;
    }
}
