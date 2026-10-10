package com.goodzheng.po.novel.dto;

import lombok.Data;

/** 正典停用入参（POST /novel/canon/{id}/retire）。 */
@Data
public class CanonRetireRequest {

    /**
     * 最后一个仍然成立的章号。缺省取该书当前最大章号——「停用」的语义是「从现在起不再成立」，
     * 而不是「从来就不成立」，写 0 会把历史章节的 as-of 视图一起改掉，那是伪造记忆。
     */
    private Integer untilChapter;

    /** 停用理由，只进日志：断言行本身没有 reason 列，为一次停用扩列不值 */
    private String reason;
}
