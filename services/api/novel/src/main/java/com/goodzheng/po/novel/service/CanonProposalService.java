package com.goodzheng.po.novel.service;

import com.goodzheng.po.novel.dto.ProposalDecisionRequest;
import com.goodzheng.po.novel.dto.ProposalDecisionView;
import com.goodzheng.po.novel.dto.ProposalRequest;
import com.goodzheng.po.novel.entity.CanonProposal;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

/**
 * 提议卡队列（§10.3 约定 1「只谈，不写」的落库面）。
 *
 * <p>对话面板唯一能写进来的东西就是这张表，而它<b>不在注入路径上</b>：未采纳的卡
 * 既不进 Tier-0 也不进 Tier-1。从 proposal 到 {@code canon_entry} 只有 {@link #adopt} 一条路，
 * 且必须带管理端 JWT（§8-⑤）。卡片的入库由工作台前端代作者提交——右栏收到一张卡就入队，
 * Python 侧不直接写这张表：它拿不到管理端 JWT，而给内网令牌开这张表等于把「谁点的头」
 * 变成「哪个进程调的接口」。
 */
public interface CanonProposalService {

    Page<CanonProposal> page(Long bookId, String status, Pageable pageable);

    /** 新卡一律 {@code status=pending}，由服务端写死 */
    CanonProposal create(ProposalRequest req);

    /**
     * 采纳：写一条 {@code authority=author} 的断言 + 闭旧区间 + 标卡片，单事务。
     *
     * <p>撞车时必须显式指定覆盖哪几条（{@code closeAssertionIds}），否则整体不落库——
     * 「作者点头」要建立在作者看得见的冲突上，不然它就是污染拿到正名（§10.6）。
     */
    ProposalDecisionView adopt(Long proposalId, ProposalDecisionRequest req, Long userId);

    /** 驳回：必填依据。卡片内容留得住，「为什么不要它」不写就没有下一次 */
    ProposalDecisionView dismiss(Long proposalId, ProposalDecisionRequest req, Long userId);
}
