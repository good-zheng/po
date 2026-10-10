package com.goodzheng.po.novel.dto;

import lombok.Data;

import java.util.ArrayList;
import java.util.List;

/**
 * 闸门产物的冲突台账入库载荷（POST /novel/internal/findings）。
 *
 * <p>bookId 与 revision 由服务端从章节反查，不接受调用方传值：Finding 必须挂在
 * 它当时检视的那一版正文上，否则作者改完正文，已录样本与裁定记录就对不上原文。
 */
@Data
public class InternalFindingRequest {

    private Long chapterId;

    private String idempotencyKey;

    private List<FindingItem> findings = new ArrayList<>();

    @Data
    public static class FindingItem {
        /** 冲突编码，对应 C1-C6 */
        private String code;
        /** blocker/major/minor */
        private String severity;
        /** rule / judge */
        private String checker;
        private List<Long> canonRefs;
        private Integer textStart;
        private Integer textEnd;
        private String evidenceQuote;
        private String explanation;
        private String fixInstruction;
    }
}
