package com.goodzheng.po.novel.dto;

import lombok.Data;

/**
 * 提议卡入参（{@code POST /novel/proposals}）。
 *
 * <p>这里<b>没有</b> status，也没有 authority：一张卡的初始状态只能是 pending，由服务端写死；
 * 调用方若能自报 {@code adopted}，「未采纳的设定不得被注入」（§10.3 约定 3）这条就从接口层漏了。
 * 同理，提议卡永远带着 {@code authority} 缺失的事实——它连一条断言都还不是。
 */
@Data
public class ProposalRequest {

    /** 提议卡挂在哪本书上；服务端验它存在 */
    private Long bookId;

    /** 哪一次对话会话产出的卡，仅作回溯 */
    private String sessionId;

    /** 出卡时的参照章；采纳时按它判「作者点头时看得见哪些断言」 */
    private Integer asOfChapter;

    /** world_rule/character/relation/location/item/theme/style */
    private String kind;

    /** 别名归一后的实体键，如 char:shenqing */
    private String subjectKey;

    private String predicate;

    private String objectText;

    /** 从第几章起成立；留空由服务端取参照章 */
    private Integer validFromChapter;

    /** 依据：对话里引用的那一句原话 */
    private String basisQuote;
}
