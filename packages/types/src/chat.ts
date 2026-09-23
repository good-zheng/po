export type ChatMessage = {
  role: string;
  content: string;
};

export type ChatRequestParams = {
  messages: ChatMessage[];
  /** 会话标识：映射后端 LangGraph thread_id，实现多轮记忆 */
  conversationId?: string;
};

export type ChatInFrame = {
  type: 'message' | 'ping' | 'resume';
  content?: string;
  /** interrupt 挂起后续传（resume 帧必填） */
  conversation_id?: string;
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
  | 'interrupt';

export type ChatWSFrame = {
  type: ChatWSFrameType;
  content?: string;
  /** 结构化载荷：run_started.thread_id / step.node / tool_call.name 等 */
  payload?: Record<string, unknown>;
};
