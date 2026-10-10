import { apiClient } from '@/lib/api/client';
import type { PageResponse } from '@po/types';

// ── 领域类型（字段名与后端 dto 一一对应）────────────────────

export type SuggestionItem = {
  style: string;
  text: string;
  why: string;
};

export type SuggestionView = {
  id: number;
  utteranceId: number;
  model?: string | null;
  /** 对方真正想要的 */
  intent?: string | null;
  /** 潜台词 */
  subtext?: string | null;
  /** 情绪标签，如「回避 · 略带不满」 */
  emotion?: string | null;
  /** 风险提示 */
  risk?: string | null;
  suggestions: SuggestionItem[];
  followups: string[];
  latencyMs?: number | null;
  createdAt?: string;
};

export type UtteranceView = {
  id: number;
  seq: number;
  /** other对方 / me我 */
  speaker: string;
  /** voice语音 / text文字 */
  source: string;
  content: string;
  edited: boolean;
  confidence?: number | null;
  startMs?: number | null;
  endMs?: number | null;
  createdAt: string;
  /** 只有「对方」的话才有 */
  suggestion?: SuggestionView | null;
};

export type SessionDetail = {
  id: number;
  threadId: string;
  title?: string | null;
  scene: string;
  status: string;
  turnCount: number;
  durationMs: number;
  createdAt: string;
  updatedAt: string;
  utterances: UtteranceView[];
};

/** 历史列表项：标题 + 首句摘要 + 轮次 + 时长 */
export type SessionSummary = {
  id: number;
  threadId: string;
  title?: string | null;
  scene: string;
  /** recording 进行中 / ended 已结束 */
  status: string;
  turnCount: number;
  durationMs: number;
  preview?: string | null;
  createdAt: string;
  updatedAt: string;
};

// ── 接口 ────────────────────────────────────────────────

export const talkApi = {
  /** 新建会话：返回 threadId，后续 /ws/chat 用它做多轮记忆的 key */
  createSession(scene = 'general') {
    return apiClient.post<SessionDetail>('/talk/sessions', { scene });
  },

  getSession(id: number) {
    return apiClient.get<SessionDetail>(`/talk/sessions/${id}`);
  },

  /** 会话列表：按最近更新倒序，keyword 命中标题（「结束并保存」之后回看这里） */
  listSessions(params?: { keyword?: string; page?: number; size?: number }) {
    return apiClient.get<PageResponse<SessionSummary>>('/talk/sessions', {
      keyword: params?.keyword,
      page: params?.page ?? 0,
      size: params?.size ?? 20,
    });
  },

  deleteSession(id: number) {
    return apiClient.delete<boolean>(`/talk/sessions/${id}`);
  },

  /** 改标题 / 场景 / 状态 / 时长；未出现的字段保持原值 */
  updateSession(
    id: number,
    patch: { title?: string; scene?: string; status?: string; durationMs?: number },
  ) {
    return apiClient.patch<SessionDetail>(`/talk/sessions/${id}`, patch);
  },

  /** 追加一句话：语音定稿或手动输入，两种来源同一条路径 */
  addUtterance(
    sessionId: number,
    payload: {
      speaker: string;
      source: 'voice' | 'text';
      content: string;
      startMs?: number;
      endMs?: number;
    },
  ) {
    return apiClient.post<UtteranceView>(`/talk/sessions/${sessionId}/utterances`, payload);
  },

  /**
   * 纠正已落库的那句话。
   *
   * 松手即发之后，讯飞的定稿（wpgs 收敛后的整句）会在几百毫秒后才到，
   * 这时用整句覆盖发出去的半成品，其余字段（轮次、说话人）保持原值。
   */
  updateUtterance(id: number, patch: { content?: string; speaker?: string }) {
    return apiClient.patch<UtteranceView>(`/talk/utterances/${id}`, patch);
  },

  /** 换取 ASR 一次性票据：60 秒内有效，建连即失效 */
  asrTicket(sessionId?: number) {
    return apiClient.get<{ ticket: string; expiresIn: number }>('/talk/asr/ticket', {
      ...(sessionId ? { sessionId } : {}),
    });
  },
};
