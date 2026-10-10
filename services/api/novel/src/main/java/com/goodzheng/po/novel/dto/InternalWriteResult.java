package com.goodzheng.po.novel.dto;

import lombok.Data;

/**
 * 内部通道写入结果：把「重放被识别」与「真的写了」区分开。
 *
 * <p>调用方（LangGraph 节点在 interrupt 之后会整体重放）必须能分辨这两件事，
 * 否则重放成功会被记成「新写入」，幂等就失去意义。
 */
@Data
public class InternalWriteResult {

    /** 本次是否真正落库；false 表示幂等键已 committed，即重放 */
    private boolean applied;

    /** 落库的 canon_entry 行数 */
    private int assertionsInserted;

    private int foreshadowsWritten;

    private int aliasesWritten;

    private int stateChangesWritten;

    /**
     * 本次 upsert 落库的 chapter_summary 行数（scene/chapter/arc 三级同口径）。
     *
     * <p>只数「写了几行」，不区分新建与覆盖：摘要靠唯一键 upsert 收敛，重复写同一摘要
     * 是预期路径，不像别名冲突那样需要单独报给调用方。
     */
    private int summariesWritten;

    /** 跳过的条数（如别名撞唯一键且指向同一实体） */
    private int skipped;

    public static InternalWriteResult replayed() {
        InternalWriteResult result = new InternalWriteResult();
        result.setApplied(false);
        return result;
    }
}
