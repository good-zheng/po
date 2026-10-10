package com.goodzheng.po.talk.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.goodzheng.po.shared.mybatis.MyBatisPages;
import com.goodzheng.po.talk.constant.TalkConstants;
import com.goodzheng.po.talk.dto.CreateSessionRequest;
import com.goodzheng.po.talk.dto.InternalSuggestionRequest;
import com.goodzheng.po.talk.dto.SessionDetail;
import com.goodzheng.po.talk.dto.SessionSummary;
import com.goodzheng.po.talk.dto.SuggestionItem;
import com.goodzheng.po.talk.dto.SuggestionView;
import com.goodzheng.po.talk.dto.UpdateSessionRequest;
import com.goodzheng.po.talk.dto.UpdateUtteranceRequest;
import com.goodzheng.po.talk.dto.UtteranceRequest;
import com.goodzheng.po.talk.dto.UtteranceView;
import com.goodzheng.po.talk.entity.TalkSession;
import com.goodzheng.po.talk.entity.TalkSuggestion;
import com.goodzheng.po.talk.entity.TalkUtterance;
import com.goodzheng.po.talk.repository.TalkSessionMapper;
import com.goodzheng.po.talk.repository.TalkSuggestionMapper;
import com.goodzheng.po.talk.repository.TalkUtteranceMapper;
import com.goodzheng.po.talk.service.TalkService;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Slf4j
@Service
@RequiredArgsConstructor
public class TalkServiceImpl implements TalkService {

    /** 列表预览的截断长度 */
    private static final int PREVIEW_LENGTH = 40;

    private final TalkSessionMapper sessionMapper;
    private final TalkUtteranceMapper utteranceMapper;
    private final TalkSuggestionMapper suggestionMapper;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public SessionDetail createSession(Long userId, CreateSessionRequest request) {
        TalkSession session = new TalkSession();
        session.setUserId(userId);
        // LangGraph thread_id：chat 服务用它做会话记忆的 key，一会话一线程
        session.setThreadId("talk-" + UUID.randomUUID().toString().replace("-", ""));
        session.setScene(normalize(request == null ? null : request.getScene(),
                TalkConstants.SCENE_GENERAL, ALLOWED_SCENE));
        sessionMapper.insert(session);
        return toDetail(session, List.of());
    }

    @Override
    public Page<SessionSummary> listSessions(Long userId, String keyword, int page, int size) {
        LambdaQueryWrapper<TalkSession> wrapper = new LambdaQueryWrapper<TalkSession>()
                .eq(TalkSession::getUserId, userId);
        if (keyword != null && !keyword.isBlank()) {
            wrapper.like(TalkSession::getTitle, keyword.trim());
        }
        wrapper.orderByDesc(TalkSession::getUpdatedAt);

        com.baomidou.mybatisplus.extension.plugins.pagination.Page<TalkSession> mpPage =
                sessionMapper.selectPage(
                        MyBatisPages.toMpPage(PageRequest.of(Math.max(page, 0), Math.min(Math.max(size, 1), 50))),
                        wrapper);

        List<TalkSession> records = mpPage.getRecords();
        Map<Long, String> previews = loadPreviews(records);
        List<SessionSummary> summaries = new ArrayList<>();
        for (TalkSession s : records) {
            SessionSummary summary = new SessionSummary();
            summary.setId(s.getId());
            summary.setThreadId(s.getThreadId());
            summary.setTitle(s.getTitle());
            summary.setScene(s.getScene());
            summary.setStatus(s.getStatus());
            summary.setTurnCount(s.getTurnCount());
            summary.setDurationMs(s.getDurationMs());
            summary.setPreview(previews.get(s.getId()));
            summary.setCreatedAt(s.getCreatedAt());
            summary.setUpdatedAt(s.getUpdatedAt());
            summaries.add(summary);
        }
        return new PageImpl<>(summaries,
                PageRequest.of(Math.max(page, 0), Math.min(Math.max(size, 1), 50)), mpPage.getTotal());
    }

    @Override
    public SessionDetail getSession(Long userId, Long sessionId) {
        TalkSession session = requireSession(userId, sessionId);
        return toDetail(session, loadUtterances(sessionId));
    }

    @Override
    @Transactional
    public SessionDetail updateSession(Long userId, Long sessionId, UpdateSessionRequest request) {
        TalkSession session = requireSession(userId, sessionId);
        if (request == null) {
            return toDetail(session, loadUtterances(sessionId));
        }
        // 全局 update-strategy=always 会把实体每个字段都写进 SET 子句，
        // 稀疏 patch 因此把 session_id/user_id/seq 这些 NOT NULL 列刷成 NULL 直接报错，
        // 所以这里只能用 UpdateWrapper 逐列 set（与 addUtterance 里的自增同一套写法）。
        LambdaUpdateWrapper<TalkSession> patch = new LambdaUpdateWrapper<TalkSession>()
                .eq(TalkSession::getId, sessionId);
        boolean dirty = false;
        if (request.getTitle() != null && !request.getTitle().isBlank()) {
            patch.set(TalkSession::getTitle, request.getTitle().trim());
            dirty = true;
        }
        if (request.getScene() != null && !request.getScene().isBlank()) {
            patch.set(TalkSession::getScene, normalize(request.getScene(), session.getScene(), ALLOWED_SCENE));
            dirty = true;
        }
        if (request.getStatus() != null && !request.getStatus().isBlank()) {
            patch.set(TalkSession::getStatus, normalize(request.getStatus(), session.getStatus(), ALLOWED_STATUS));
            dirty = true;
        }
        if (request.getDurationMs() != null) {
            patch.set(TalkSession::getDurationMs, request.getDurationMs());
            dirty = true;
        }
        if (dirty) {
            patch.set(TalkSession::getUpdatedAt, LocalDateTime.now());
            sessionMapper.update(null, patch);
        }
        return toDetail(requireSession(userId, sessionId), loadUtterances(sessionId));
    }

    @Override
    @Transactional
    public void deleteSession(Long userId, Long sessionId) {
        requireSession(userId, sessionId);
        suggestionMapper.delete(new LambdaQueryWrapper<TalkSuggestion>()
                .eq(TalkSuggestion::getSessionId, sessionId));
        utteranceMapper.delete(new LambdaQueryWrapper<TalkUtterance>()
                .eq(TalkUtterance::getSessionId, sessionId));
        sessionMapper.deleteById(sessionId);
    }

    @Override
    @Transactional
    public UtteranceView addUtterance(Long userId, Long sessionId, UtteranceRequest request) {
        TalkSession session = requireSession(userId, sessionId);
        if (request == null || request.getContent() == null || request.getContent().isBlank()) {
            throw new IllegalArgumentException("内容不能为空");
        }
        String speaker = normalize(request.getSpeaker(), TalkConstants.SPEAKER_OTHER, ALLOWED_SPEAKER);
        String source = normalize(request.getSource(), TalkConstants.SOURCE_VOICE, ALLOWED_SOURCE);

        TalkUtterance entity = new TalkUtterance();
        entity.setSessionId(sessionId);
        entity.setUserId(userId);
        entity.setSeq(nextSeq(sessionId));
        entity.setSpeaker(speaker);
        entity.setSource(source);
        entity.setContent(truncate(request.getContent().trim()));
        entity.setConfidence(request.getConfidence());
        entity.setStartMs(request.getStartMs());
        entity.setEndMs(request.getEndMs());
        utteranceMapper.insert(entity);

        // 只有「对方」的话才是分析对象，才计入轮次
        if (TalkConstants.SPEAKER_OTHER.equals(speaker)) {
            sessionMapper.update(null, new LambdaUpdateWrapper<TalkSession>()
                    .eq(TalkSession::getId, sessionId)
                    .setSql("turn_count = turn_count + 1"));
        }
        return toView(entity, null);
    }

    @Override
    @Transactional
    public UtteranceView updateUtterance(Long userId, Long utteranceId, UpdateUtteranceRequest request) {
        TalkUtterance entity = requireUtterance(userId, utteranceId);
        if (request == null) {
            return toView(entity, latestSuggestion(utteranceId));
        }
        LambdaUpdateWrapper<TalkUtterance> patch = new LambdaUpdateWrapper<TalkUtterance>()
                .eq(TalkUtterance::getId, utteranceId);
        boolean dirty = false;
        if (request.getContent() != null && !request.getContent().isBlank()) {
            patch.set(TalkUtterance::getContent, truncate(request.getContent().trim()));
            patch.set(TalkUtterance::getEdited, true);
            dirty = true;
        }
        if (request.getSpeaker() != null && !request.getSpeaker().isBlank()) {
            patch.set(TalkUtterance::getSpeaker, normalize(request.getSpeaker(), entity.getSpeaker(), ALLOWED_SPEAKER));
            dirty = true;
        }
        if (dirty) {
            utteranceMapper.update(null, patch);
        }
        return toView(requireUtterance(userId, utteranceId), latestSuggestion(utteranceId));
    }

    @Override
    @Transactional
    public void saveSuggestion(InternalSuggestionRequest request) {
        if (request == null) {
            return;
        }
        TalkUtterance utterance = null;
        if (request.getUtteranceId() != null) {
            utterance = utteranceMapper.selectById(request.getUtteranceId());
        }
        if (utterance == null && request.getThreadId() != null) {
            TalkSession session = sessionMapper.selectOne(new LambdaQueryWrapper<TalkSession>()
                    .eq(TalkSession::getThreadId, request.getThreadId()));
            if (session != null) {
                List<TalkUtterance> latest = utteranceMapper.selectList(new LambdaQueryWrapper<TalkUtterance>()
                        .eq(TalkUtterance::getSessionId, session.getId())
                        .eq(TalkUtterance::getSpeaker, TalkConstants.SPEAKER_OTHER)
                        .orderByDesc(TalkUtterance::getSeq)
                        .last("limit 1"));
                utterance = latest.isEmpty() ? null : latest.get(0);
            }
        }
        if (utterance == null) {
            log.warn("建议落库失败：找不到对应话语 utteranceId={} threadId={}",
                    request.getUtteranceId(), request.getThreadId());
            return;
        }

        TalkSuggestion entity = new TalkSuggestion();
        entity.setSessionId(utterance.getSessionId());
        entity.setUtteranceId(utterance.getId());
        entity.setUserId(utterance.getUserId());
        entity.setModel(request.getModel());
        entity.setIntent(request.getIntent());
        entity.setSubtext(request.getSubtext());
        entity.setEmotion(request.getEmotion());
        entity.setRisk(request.getRisk());
        entity.setLatencyMs(request.getLatencyMs());
        entity.setPayload(toJson(request));
        suggestionMapper.insert(entity);
    }

    // ── 内部工具 ──────────────────────────────────────────

    private TalkSession requireSession(Long userId, Long sessionId) {
        TalkSession session = sessionMapper.selectById(sessionId);
        if (session == null || !userId.equals(session.getUserId())) {
            throw new IllegalArgumentException("会话不存在或无权访问");
        }
        return session;
    }

    private TalkUtterance requireUtterance(Long userId, Long utteranceId) {
        TalkUtterance entity = utteranceMapper.selectById(utteranceId);
        if (entity == null || !userId.equals(entity.getUserId())) {
            throw new IllegalArgumentException("话语不存在或无权访问");
        }
        return entity;
    }

    private int nextSeq(Long sessionId) {
        List<TalkUtterance> latest = utteranceMapper.selectList(new LambdaQueryWrapper<TalkUtterance>()
                .eq(TalkUtterance::getSessionId, sessionId)
                .orderByDesc(TalkUtterance::getSeq)
                .last("limit 1"));
        return latest.isEmpty() ? 1 : latest.get(0).getSeq() + 1;
    }

    private List<TalkUtterance> loadUtterances(Long sessionId) {
        return utteranceMapper.selectList(new LambdaQueryWrapper<TalkUtterance>()
                .eq(TalkUtterance::getSessionId, sessionId)
                .orderByAsc(TalkUtterance::getSeq));
    }

    /** 列表预览：批量取每个会话的首条「对方」话语，避免逐条查询 */
    private Map<Long, String> loadPreviews(List<TalkSession> sessions) {
        if (sessions.isEmpty()) {
            return Collections.emptyMap();
        }
        Set<Long> ids = new HashSet<>();
        for (TalkSession s : sessions) {
            ids.add(s.getId());
        }
        List<TalkUtterance> all = utteranceMapper.selectList(new LambdaQueryWrapper<TalkUtterance>()
                .in(TalkUtterance::getSessionId, ids)
                .eq(TalkUtterance::getSpeaker, TalkConstants.SPEAKER_OTHER)
                .orderByAsc(TalkUtterance::getSeq));
        Map<Long, String> previews = new LinkedHashMap<>();
        for (TalkUtterance u : all) {
            previews.putIfAbsent(u.getSessionId(), truncate(u.getContent()));
        }
        for (TalkSession s : sessions) {
            previews.putIfAbsent(s.getId(), null);
        }
        return previews;
    }

    private SuggestionView latestSuggestion(Long utteranceId) {
        List<TalkSuggestion> list = suggestionMapper.selectList(new LambdaQueryWrapper<TalkSuggestion>()
                .eq(TalkSuggestion::getUtteranceId, utteranceId)
                .orderByDesc(TalkSuggestion::getId)
                .last("limit 1"));
        return list.isEmpty() ? null : toSuggestionView(list.get(0));
    }

    private SessionDetail toDetail(TalkSession session, List<TalkUtterance> utterances) {
        Map<Long, SuggestionView> suggestions = new LinkedHashMap<>();
        if (!utterances.isEmpty()) {
            Set<Long> ids = new HashSet<>();
            for (TalkUtterance u : utterances) {
                ids.add(u.getId());
            }
            List<TalkSuggestion> list = suggestionMapper.selectList(new LambdaQueryWrapper<TalkSuggestion>()
                    .in(TalkSuggestion::getUtteranceId, ids)
                    .orderByAsc(TalkSuggestion::getId));
            for (TalkSuggestion s : list) {
                // 同一句话换过一批时保留最后一次
                suggestions.put(s.getUtteranceId(), toSuggestionView(s));
            }
        }

        SessionDetail detail = new SessionDetail();
        detail.setId(session.getId());
        detail.setThreadId(session.getThreadId());
        detail.setTitle(session.getTitle());
        detail.setScene(session.getScene());
        detail.setStatus(session.getStatus());
        detail.setTurnCount(session.getTurnCount());
        detail.setDurationMs(session.getDurationMs());
        detail.setCreatedAt(session.getCreatedAt());
        detail.setUpdatedAt(session.getUpdatedAt());
        for (TalkUtterance u : utterances) {
            detail.getUtterances().add(toView(u, suggestions.get(u.getId())));
        }
        return detail;
    }

    private static UtteranceView toView(TalkUtterance u, SuggestionView suggestion) {
        UtteranceView view = new UtteranceView();
        view.setId(u.getId());
        view.setSeq(u.getSeq());
        view.setSpeaker(u.getSpeaker());
        view.setSource(u.getSource());
        view.setContent(u.getContent());
        view.setEdited(u.getEdited());
        view.setConfidence(u.getConfidence());
        view.setStartMs(u.getStartMs());
        view.setEndMs(u.getEndMs());
        view.setCreatedAt(u.getCreatedAt());
        view.setSuggestion(suggestion);
        return view;
    }

    private SuggestionView toSuggestionView(TalkSuggestion s) {
        SuggestionView view = new SuggestionView();
        view.setId(s.getId());
        view.setUtteranceId(s.getUtteranceId());
        view.setModel(s.getModel());
        view.setIntent(s.getIntent());
        view.setSubtext(s.getSubtext());
        view.setEmotion(s.getEmotion());
        view.setRisk(s.getRisk());
        view.setLatencyMs(s.getLatencyMs());
        view.setCreatedAt(s.getCreatedAt());
        if (s.getPayload() != null && !s.getPayload().isBlank()) {
            try {
                InternalSuggestionRequest payload =
                        objectMapper.readValue(s.getPayload(), InternalSuggestionRequest.class);
                if (payload.getSuggestions() != null) {
                    for (SuggestionItem item : payload.getSuggestions()) {
                        view.getSuggestions().add(item);
                    }
                }
                if (payload.getFollowups() != null) {
                    view.getFollowups().addAll(payload.getFollowups());
                }
            } catch (Exception e) {
                log.warn("建议 payload 解析失败, suggestionId={}", s.getId());
            }
        }
        return view;
    }

    private String toJson(InternalSuggestionRequest request) {
        try {
            return objectMapper.writeValueAsString(request);
        } catch (Exception e) {
            log.warn("建议 payload 序列化失败: {}", e.getMessage());
            return "{}";
        }
    }

    private static String truncate(String text) {
        if (text == null) {
            return null;
        }
        return text.length() <= PREVIEW_LENGTH ? text : text.substring(0, PREVIEW_LENGTH) + "…";
    }

    /** 枚举取值白名单：非法值一律回退，避免脏数据落库 */
    private static final Set<String> ALLOWED_SPEAKER =
            Set.of(TalkConstants.SPEAKER_OTHER, TalkConstants.SPEAKER_ME, TalkConstants.SPEAKER_UNKNOWN);
    private static final Set<String> ALLOWED_SOURCE =
            Set.of(TalkConstants.SOURCE_VOICE, TalkConstants.SOURCE_TEXT);
    private static final Set<String> ALLOWED_SCENE =
            Set.of(TalkConstants.SCENE_GENERAL, TalkConstants.SCENE_WORK,
                    TalkConstants.SCENE_SALES, TalkConstants.SCENE_ROMANCE);
    private static final Set<String> ALLOWED_STATUS =
            Set.of(TalkConstants.STATUS_RECORDING, TalkConstants.STATUS_ENDED);

    private static String normalize(String value, String fallback, Set<String> allowed) {
        if (value == null || value.isBlank()) {
            return fallback;
        }
        String v = value.trim();
        return allowed.contains(v) ? v : fallback;
    }
}
