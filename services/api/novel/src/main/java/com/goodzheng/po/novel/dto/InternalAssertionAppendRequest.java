package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

/**
 * Agent 抽取结果入库载荷（POST /novel/internal/assertions:append）。
 *
 * <p>一次调用对应「一章的全部抽取产物」，四类产物同事务写入：断言之间互相引用
 * （别名归一要先于断言落库、伏笔收束要闭旧区间），拆成四个端点就得由调用方保证跨请求顺序，
 * 而调用方是会被 interrupt 重放的 LangGraph 节点，不值得信任。
 *
 * <p>注意这里<b>没有</b> authority 字段：{@code author/text/model} 由服务端判定（本通道只写 model），
 * 调用方多传的同名字段会被 Jackson 当未知属性忽略——「模型自证为作者设定」这条路必须在契约层就不存在。
 */
@Data
public class InternalAssertionAppendRequest {

    private Long bookId;

    /** 抽取发生时正在写的章号，as-of 过滤与 valid_from 缺省值都用它 */
    private Integer asOfChapter;

    /** 幂等键：chapterId + contentHash + promptVersion + model；服务端唯一索引兜底 */
    private String idempotencyKey;

    /** 归属章的 book_chapter.id，供 gen_job 与断言溯源 */
    private Long chapterId;

    private List<AssertionItem> assertions = new ArrayList<>();

    private List<ForeshadowOpItem> foreshadows = new ArrayList<>();

    private List<AliasItem> aliases = new ArrayList<>();

    private List<StateChangeItem> stateChanges = new ArrayList<>();

    @Data
    public static class AssertionItem {
        private String kind;
        private String subjectKey;
        private String predicate;
        private String objectText;
        private String restatement;
        private BigDecimal confidence;
        private Integer establishedChapter;
        /** 缺省取请求的 asOfChapter */
        private Integer validFromChapter;
        private Integer validUntilChapter;
        private Long supersedesId;
        /** 缺省取请求的 chapterId */
        private Long sourceChapterId;
        private Integer sourceStart;
        private Integer sourceEnd;
        private String evidenceQuote;
        private String promptVersion;
        private String model;
        /** confirmed / todo（缺口）；其余值一律按 confirmed 入库 */
        private String status;
    }

    @Data
    public static class ForeshadowOpItem {
        /** open 埋设 / pay 收回 / abandon 作废 */
        private String op;
        /** pay/abandon 时定位既有伏笔 */
        private Long foreshadowId;
        private Integer plantedChapter;
        private String content;
        private Integer dueByArc;
    }

    @Data
    public static class AliasItem {
        private String entityKey;
        private String aliasText;
        private Integer firstSeenChapter;
        private Boolean isPrimary;
    }

    @Data
    public static class StateChangeItem {
        private String charKey;
        /** 缺省取请求的 asOfChapter */
        private Integer asOfChapter;
        private Boolean isAlive;
        private String locationKey;
        private List<String> knows;
        private List<String> holds;
        private String mood;
        private Integer lastSeenChapter;
    }
}
