package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/**
 * 层级摘要入库载荷（POST /novel/internal/summaries），scene / chapter / arc 三级共用一条通道。
 *
 * <p>sourceVersion 由服务端取章节当前 revision，不接受调用方传值：摘要与正文版本
 * 一旦错位，上下文编译器就会拿旧摘要去约束新正文。
 *
 * <p>同理，{@code fromChapter}/{@code toChapter} 只在 arc 级被采信——scene/chapter 级的区间
 * 端点等于该章自己的 chapterIndex，让调用方报就是让它自己声明「这段区间我已看完」。
 */
@Data
public class InternalSummaryRequest {

    /** level=scene/chapter 时必填；arc 级可空（弧不挂在单章上） */
    private Long chapterId;

    /** 摘要层级：scene/chapter/arc。缺省或空按 scene 处理，旧载荷因此无需改动 */
    private String level;

    /** 仅 arc 级使用的弧序号（1 基），落到 scene_no 列充当该层级的排序位 */
    private Integer arcNo;

    /** 仅 arc 级：覆盖区间起始章 */
    private Integer fromChapter;

    /** 仅 arc 级：覆盖区间结束章，需满足 1 &lt;= fromChapter &lt;= toChapter */
    private Integer toChapter;

    /** arc 级缺 chapterId 时用它定位书籍；scene/chapter 级忽略（以章节反查为准） */
    private Long bookId;

    private List<SceneItem> scenes = new ArrayList<>();

    @Data
    public static class SceneItem {
        private Integer sceneNo;
        private String content;
        /** 预算核算用；缺省按内容长度估算 */
        private Integer tokens;
    }
}
