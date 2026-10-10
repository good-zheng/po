package com.goodzheng.po.talk.controller;

import com.goodzheng.po.identity.security.AuthUser;
import com.goodzheng.po.shared.dto.Result;
import com.goodzheng.po.talk.asr.AsrTicketService;
import com.goodzheng.po.talk.dto.AsrTicketResponse;
import com.goodzheng.po.talk.dto.CreateSessionRequest;
import com.goodzheng.po.talk.dto.InternalSuggestionRequest;
import com.goodzheng.po.talk.dto.SessionDetail;
import com.goodzheng.po.talk.dto.SessionSummary;
import com.goodzheng.po.talk.dto.UpdateSessionRequest;
import com.goodzheng.po.talk.dto.UpdateUtteranceRequest;
import com.goodzheng.po.talk.dto.UtteranceRequest;
import com.goodzheng.po.talk.dto.UtteranceView;
import com.goodzheng.po.talk.service.TalkService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 言外（EchoTalk）会话接口。
 *
 * <p>{@code /talk/internal/**} 是给 chat 服务回调落库建议用的内网端点，
 * 由 {@code X-Internal-Token} 保护；该端点在 SecurityConfig 里放行交由本类自行校验，
 * 因为 Python 侧拿不到 JWT。
 */
@Slf4j
@RestController
@RequestMapping("/talk")
@RequiredArgsConstructor
public class TalkController {

    private static final String INTERNAL_HEADER = "X-Internal-Token";

    private final TalkService talkService;
    private final AsrTicketService asrTicketService;

    /** 内部回调令牌；未配置时一律拒绝（安全默认值） */
    @Value("${app.internal-token:}")
    private String internalToken;

    /** 新建会话，返回 threadId 供 /ws/chat 使用 */
    @PostMapping("/sessions")
    public Result<SessionDetail> createSession(@AuthenticationPrincipal AuthUser principal,
                                               @RequestBody(required = false) CreateSessionRequest request) {
        return Result.success(talkService.createSession(principal.id(), request));
    }

    /** 会话列表：按最近更新倒序，keyword 命中标题 */
    @GetMapping("/sessions")
    public Result<Page<SessionSummary>> listSessions(
            @AuthenticationPrincipal AuthUser principal,
            @RequestParam(required = false) String keyword,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return Result.success(talkService.listSessions(principal.id(), keyword, page, size));
    }

    /** 会话详情：会话元信息 + 完整对话流（含建议） */
    @GetMapping("/sessions/{id}")
    public Result<SessionDetail> getSession(@AuthenticationPrincipal AuthUser principal,
                                            @PathVariable Long id) {
        return Result.success(talkService.getSession(principal.id(), id));
    }

    /** 改标题 / 场景 / 状态 / 时长 */
    @PatchMapping("/sessions/{id}")
    public Result<SessionDetail> updateSession(@AuthenticationPrincipal AuthUser principal,
                                               @PathVariable Long id,
                                               @RequestBody(required = false) UpdateSessionRequest request) {
        return Result.success(talkService.updateSession(principal.id(), id, request));
    }

    /** 删除会话及其下话语与建议 */
    @DeleteMapping("/sessions/{id}")
    public Result<Boolean> deleteSession(@AuthenticationPrincipal AuthUser principal,
                                         @PathVariable Long id) {
        talkService.deleteSession(principal.id(), id);
        return Result.success(true);
    }

    /** 追加一句话：语音定稿或手动输入，两种来源同一条路径 */
    @PostMapping("/sessions/{id}/utterances")
    public Result<UtteranceView> addUtterance(@AuthenticationPrincipal AuthUser principal,
                                              @PathVariable Long id,
                                              @RequestBody UtteranceRequest request) {
        try {
            return Result.success(talkService.addUtterance(principal.id(), id, request));
        } catch (IllegalArgumentException e) {
            return Result.error(e.getMessage());
        }
    }

    /** 纠错文本或改说话人（改完由小程序决定是否重新分析） */
    @PatchMapping("/utterances/{id}")
    public Result<UtteranceView> updateUtterance(@AuthenticationPrincipal AuthUser principal,
                                                 @PathVariable Long id,
                                                 @RequestBody(required = false) UpdateUtteranceRequest request) {
        try {
            return Result.success(talkService.updateUtterance(principal.id(), id, request));
        } catch (IllegalArgumentException e) {
            return Result.error(e.getMessage());
        }
    }

    /**
     * 换取 ASR 一次性票据。
     * 微信小程序 WebSocket 不能带自定义头，JWT 只能拼在 query 上会被网关日志留存，
     * 故用一次性 ticket 换取连接，60 秒内有效、建连即失效。
     */
    @GetMapping("/asr/ticket")
    public Result<AsrTicketResponse> asrTicket(@AuthenticationPrincipal AuthUser principal,
                                               @RequestParam(required = false) Long sessionId) {
        AsrTicketService.AsrTicket ticket = asrTicketService.issue(principal.id(), sessionId);
        AsrTicketResponse response = new AsrTicketResponse();
        response.setTicket(ticket.ticket());
        response.setExpiresIn(ticket.expiresIn());
        return Result.success(response);
    }

    /** chat 服务（agent-talk）产出建议后回调落库 */
    @PostMapping("/internal/suggestions")
    public Result<Boolean> saveSuggestion(HttpServletRequest httpRequest,
                                          @RequestBody(required = false) InternalSuggestionRequest request) {
        String token = httpRequest.getHeader(INTERNAL_HEADER);
        if (internalToken.isBlank() || !internalToken.equals(token)) {
            return Result.error(403, "内部令牌无效");
        }
        talkService.saveSuggestion(request);
        return Result.success(true);
    }
}
