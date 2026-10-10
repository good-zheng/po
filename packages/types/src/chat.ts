export type ChatMessage = {
  role: string;
  content: string;
};

export type ChatRequestParams = {
  messages: ChatMessage[];
  /** 会话标识：映射后端 LangGraph thread_id，实现多轮记忆 */
  conversationId?: string;
  /** 显式指定垂直 Agent 插槽名（如 "novel-chat"）：命中即绕过意图路由直连该子图 */
  agent?: string;
  /** 随消息携带的上下文元信息；novel-chat 认 bookId / chapterId 两个定位键 */
  context?: Record<string, unknown>;
};

export type ChatTicket = {
  /** 一次性握手票据：由 GET /api/novel/chat-ticket 签发，拼在 WS URL 的 ?ticket= 上 */
  ticket: string;
  /** 有效期（秒）。它守的是「能不能建立这条连接」，连接建立后中途过期不重验 */
  expiresIn: number;
};

export type ChatInFrame = {
  type: 'message' | 'ping' | 'resume';
  content?: string;
  /** interrupt 挂起后续传（resume 帧必填） */
  conversation_id?: string;
  /** 缺省不发：老客户端不发它，行为与历史上线一致 */
  agent?: string;
  context?: Record<string, unknown>;
};

export type ChatWSFrameType =
  | 'token'
  | 'done'
  | 'pong'
  | 'error'
  | 'run_started'
  | 'step'
  | 'thinking'
  | 'plan'
  | 'tool_call_start'
  | 'tool_call_args'
  | 'tool_call_end'
  | 'tool_call_result'
  | 'interrupt'
  /** 设定提议卡（novel-chat 专属）：payload 即 ProposalRequest 的字段，前端只转发不拼装 */
  | 'proposal';

export type ChatWSFrame = {
  type: ChatWSFrameType;
  content?: string;
  /** 结构化载荷：run_started.thread_id / step.node / tool_call.name 等 */
  payload?: Record<string, unknown>;
};
