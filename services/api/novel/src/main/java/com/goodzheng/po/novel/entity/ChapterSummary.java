package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

/**
 * 层级摘要树的一节（scene / chapter / arc）。
 *
 * <p>{@code sourceVersion} 记来源正文版本：正文改了（revision 递增）即视为该摘要过期，
 * 由上下文编译器按版本比对决定重算，避免「摘要的摘要」把早期幻觉固化。
 */
@Data
@TableName("chapter_summary")
public class ChapterSummary {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    /** arc 级为 NULL */
    private Long chapterId;

    /** scene/chapter/arc */
    private String level;

    private Integer sceneNo;

    /**
     * 覆盖区间的起始章：scene/chapter 级由服务端按章节 chapterIndex 推导，arc 级取入参区间端点。
     *
     * <p>不采信调用方传值，理由与 sourceVersion 同源——虚报起点就能把尚未发生的剧情
     * 标成「已知」，as-of 过滤当场失效。
     */
    private Integer fromChapter;

    /** 覆盖区间的结束章；NULL 表示无终点（历史行未回填，读侧当作未知处理） */
    private Integer toChapter;

    private String content;

    /** 预算核算：注入超限要能看见 */
    private Integer tokens;

    private Integer sourceVersion;
}
