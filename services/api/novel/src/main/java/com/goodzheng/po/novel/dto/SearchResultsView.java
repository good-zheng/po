package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/**
 * 左栏统一检索的结果（§10.3「章题、正文、正典断言、人名别名一起搜」）。
 *
 * <p>分节返回而不是混排成一条全局序列：一期只有 MySQL {@code LIKE}，跨三张表没有可比的打分，
 * 硬凑全局序只会让「第 12 章那句」和「她的眼睛颜色」假装在同一尺度上排过。
 * 分页按 scope 各自偏移，各节自带 total。
 */
@Data
public class SearchResultsView {

    private Long bookId;

    /** 回显去空白后的查询词 */
    private String query;

    /** 实际参与检索的 scope，合法值 chapter/canon/alias */
    private List<String> scopes = new ArrayList<>();

    /** 查询词命中的称谓，展开后的实体键：断言检索额外按它们匹配 subject_key */
    private List<String> expandedEntityKeys = new ArrayList<>();

    private List<ChapterHit> chapters = new ArrayList<>();

    private List<CanonHit> canon = new ArrayList<>();

    private List<AliasHit> aliases = new ArrayList<>();

    private long chapterTotal;

    private long canonTotal;

    private long aliasTotal;

    @Data
    public static class ChapterHit {

        private Long chapterId;

        private Integer chapterIndex;

        private String title;

        /** draft/pending_review/committed */
        private String status;

        private Integer revision;

        /** 命中处前后各截一段；正文没命中而标题命中时给正文起头 */
        private String excerpt;
    }

    @Data
    public static class CanonHit {

        private Long canonId;

        private String kind;

        private String subjectKey;

        private String predicate;

        private String objectText;

        /** author/text/model：作者要能一眼看出这条是谁说了算的 */
        private String authority;

        /** confirmed/disputed/todo/rejected */
        private String status;

        private Integer validFromChapter;

        /** NULL 表示至今有效 */
        private Integer validUntilChapter;

        /** true 表示只因「这个称谓属于该实体」才被搜出来，文本本身不含查询词 */
        private boolean matchedViaAlias;
    }

    @Data
    public static class AliasHit {

        private Long aliasId;

        private String entityKey;

        private String aliasText;

        private Integer firstSeenChapter;

        private Boolean isPrimary;
    }
}
