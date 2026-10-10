package com.goodzheng.po.novel.entity;

import com.baomidou.mybatisplus.annotation.FieldStrategy;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

/**
 * 对话面板的提议卡（§10.3 约定 1/3）。
 *
 * <p><b>这张表不在注入路径上</b>：未采纳的卡永不被 L1 编译器读到，所以右栏再怎么聊都污染不了正典
 * （§12.4 要求为这条补 {@code test_chat_cannot_write_canon}，落在 N5c-3 的 Python 侧）。
 * 唯一的升级通道是 {@code PUT /novel/proposals/{id}/adopt}，它写一条
 * {@code authority=author} 的 {@link CanonEntry} 并把本行标成 adopted。
 */
@Data
@TableName("canon_proposal")
public class CanonProposal {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long bookId;

    /** 哪一次对话会话聊出来的，仅作回溯 */
    private String sessionId;

    /** 出卡时工作台的参照章：采纳时按它判「当时看得见哪些断言」 */
    private Integer asOfChapter;

    private String kind;

    private String subjectKey;

    private String predicate;

    private String objectText;

    private Integer validFromChapter;

    /** 依据：引哪一章哪一句。原话留在本行，采纳后不会变成断言的逐字出处 */
    private String basisQuote;

    /** pending/adopted/dismissed/expired */
    private String status;

    private Long adoptedEntryId;

    private Long decidedBy;

    private LocalDateTime decidedAt;

    /** 驳回依据；与 {@code basisQuote} 分开——那是卡片的证据，这是作者对卡片的裁定 */
    private String decidedBasis;

    @TableField(updateStrategy = FieldStrategy.NEVER)
    private LocalDateTime createdAt;
}
