package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.InternalAssertionAppendRequest;
import com.goodzheng.po.novel.dto.InternalAssertionCloseRequest;
import com.goodzheng.po.novel.dto.InternalFindingRequest;
import com.goodzheng.po.novel.dto.InternalSummaryRequest;
import com.goodzheng.po.novel.dto.InternalSummaryView;
import com.goodzheng.po.novel.dto.InternalWriteResult;
import com.goodzheng.po.novel.entity.CanonEntry;
import com.goodzheng.po.novel.entity.Foreshadow;

import java.util.List;

/**
 * 正典层的内部通道服务（供 agent-novel 经 X-Internal-Token 调用）。
 */
public interface CanonInternalService {

    InternalWriteResult append(InternalAssertionAppendRequest request);

    InternalWriteResult close(InternalAssertionCloseRequest request);

    InternalWriteResult saveFindings(InternalFindingRequest request);

    InternalWriteResult saveSummaries(InternalSummaryRequest request);

    /**
     * as-of 快照：只返回截至 {@code asOf} 章仍然有效的已确认断言。
     *
     * <p>asOf 必填：缺省等于「取全书」，会让重写第 12 章时把第 30 章的事实写进正文。
     * disputed 与 todo 不参与注入——前者等人裁定，后者是缺口，都不是既有设定。
     */
    List<CanonEntry> snapshot(Long bookId, Integer asOf, List<String> entities, List<String> kinds);

    List<Foreshadow> openForeshadows(Long bookId, Integer asOf);

    /**
     * 层级摘要读取（L1 上下文编译器的摘要入口）。
     *
     * <p><b>这里的 as-of 与 {@link #snapshot} 不同侧，不是笔误：</b>断言是原子事实，有效期
     * 区间与 as-of 相交就说明「此刻它仍然成立」，所以 snapshot 用 {@code valid_until >= asOf}；
     * 摘要是一段有损总结，一条覆盖 11..20 章的弧摘要里写着第 20 章发生了什么，相交即剧透。
     * 故这里要求<b>整段区间都已知</b>：{@code from_chapter <= upto AND (to_chapter IS NULL OR
     * to_chapter <= upto)}。宁可少注入一段摘要，也不能把后文端进当前章的上下文。
     *
     * <p>{@code from_chapter} 为 NULL 的历史行（加列前写的 scene 摘要）因此一律查不出来：
     * 区间起点未知就无法证明它不含后文，只能等重算回填。
     *
     * @param upto   已定稿的最新章号，即编译器所站的 as-of 位置
     * @param levels 需要的层级，合法值 scene/chapter/arc；空则取 scene,chapter
     * @param limit  返回条数上限，缺省 24，硬上限 200
     */
    List<InternalSummaryView> summaries(Long bookId, Integer upto, List<String> levels, Integer limit);
}
