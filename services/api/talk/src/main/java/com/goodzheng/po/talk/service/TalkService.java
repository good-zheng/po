package com.goodzheng.po.talk.service;

import com.goodzheng.po.talk.dto.CreateSessionRequest;
import com.goodzheng.po.talk.dto.InternalSuggestionRequest;
import com.goodzheng.po.talk.dto.SessionDetail;
import com.goodzheng.po.talk.dto.SessionSummary;
import com.goodzheng.po.talk.dto.UpdateSessionRequest;
import com.goodzheng.po.talk.dto.UpdateUtteranceRequest;
import com.goodzheng.po.talk.dto.UtteranceRequest;
import com.goodzheng.po.talk.dto.UtteranceView;
import org.springframework.data.domain.Page;

/** 言外会话的读写入口：会话、话语、建议三层，归属校验一律在 Service 内完成。 */
public interface TalkService {

    /** 新建会话；threadId 与 LangGraph 的会话记忆一一对应 */
    SessionDetail createSession(Long userId, CreateSessionRequest request);

    /** 会话列表：按最近更新倒序，keyword 命中标题 */
    Page<SessionSummary> listSessions(Long userId, String keyword, int page, int size);

    SessionDetail getSession(Long userId, Long sessionId);

    SessionDetail updateSession(Long userId, Long sessionId, UpdateSessionRequest request);

    /** 删除会话及其下所有话语与建议 */
    void deleteSession(Long userId, Long sessionId);

    /** 追加一句话（语音定稿或手动输入）；对方的话会计入 turnCount */
    UtteranceView addUtterance(Long userId, Long sessionId, UtteranceRequest request);

    /** 纠错文本或改说话人 */
    UtteranceView updateUtterance(Long userId, Long utteranceId, UpdateUtteranceRequest request);

    /** chat 服务（agent-talk）产出结果后回调落库 */
    void saveSuggestion(InternalSuggestionRequest request);
}
