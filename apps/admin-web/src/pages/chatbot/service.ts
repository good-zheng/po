// src/pages/chatbot/service.ts

import type {
  ChatProviderConfig,
  TransformMessage,
  XRequestOptions,
} from '@ant-design/x-sdk';
import { AbstractChatProvider, AbstractXRequestClass } from '@ant-design/x-sdk';
import type {
  ChatInFrame,
  ChatMessage,
  ChatRequestParams,
  ChatWSFrame,
} from '@po/types';

export type { ChatMessage, ChatRequestParams, ChatWSFrame } from '@po/types';

export const CHAT_WS_URL = `${
  window.location.protocol === 'https:' ? 'wss' : 'ws'
}://${window.location.host}/ws/chat`;

const HEARTBEAT_INTERVAL = 30_000;

/**
 * WebSocket 版 XRequest：持有长连接，run() 发送最后一条用户消息，
 * 将 token 帧推给 onUpdate，done 触发 onSuccess，error/断连触发 onError。
 */
class ChatWSRequest extends AbstractXRequestClass<
  ChatRequestParams,
  ChatWSFrame,
  ChatMessage
> {
  private ws: WebSocket | null = null;

  private chunks: ChatWSFrame[] = [];

  private requesting = false;

  private pendingContent: string | null = null;

  private pendingConversationId: string | null = null;

  private pingTimer: ReturnType<typeof setInterval> | null = null;

  get asyncHandler() {
    return Promise.resolve();
  }

  get isTimeout() {
    return false;
  }

  get isStreamTimeout() {
    return false;
  }

  get isRequesting() {
    return this.requesting;
  }

  get manual() {
    return true;
  }

  run(params?: ChatRequestParams): void {
    const message = params?.messages?.[params.messages.length - 1];
    if (!message) return;

    this.chunks = [];
    this.requesting = true;
    this.pendingContent = message.content;
    this.pendingConversationId = params?.conversationId || null;

    if (!this.ws) {
      this.connect();
    } else if (this.ws.readyState === WebSocket.OPEN) {
      this.flush();
    }
    // CONNECTING 状态下由 onopen 统一 flush
  }

  abort(): void {
    this.requesting = false;
    const error = new Error('aborted');
    error.name = 'AbortError';
    this.options.callbacks?.onError?.(error, undefined, new Headers());
    this.close();
  }

  private connect() {
    const ws = new WebSocket(this.baseURL);
    this.ws = ws;

    ws.onopen = () => {
      this.startHeartbeat();
      this.flush();
    };
    ws.onmessage = (event) => this.handleFrame(event);
    ws.onerror = () => {
      if (this.requesting) {
        this.requesting = false;
        this.options.callbacks?.onError?.(
          new Error('WebSocket 连接出错'),
          undefined,
          new Headers(),
        );
      }
    };
    ws.onclose = () => {
      this.stopHeartbeat();
      if (this.ws === ws) this.ws = null;
      if (this.requesting) {
        this.requesting = false;
        this.options.callbacks?.onError?.(
          new Error('WebSocket 连接已断开'),
          undefined,
          new Headers(),
        );
      }
    };
  }

  private close() {
    this.stopHeartbeat();
    const ws = this.ws;
    this.ws = null;
    ws?.close();
  }

  private flush() {
    if (this.pendingContent == null || !this.ws) return;
    const frame: ChatInFrame = {
      type: 'message',
      content: this.pendingContent,
      conversation_id: this.pendingConversationId ?? undefined,
    };
    this.ws.send(JSON.stringify(frame));
    this.pendingContent = null;
    this.pendingConversationId = null;
  }

  private handleFrame(event: MessageEvent) {
    let frame: ChatWSFrame;
    try {
      frame = JSON.parse(String(event.data));
    } catch {
      return;
    }
    const { callbacks } = this.options;

    if (frame.type === 'pong') return;

    if (frame.type === 'token') {
      this.chunks.push(frame);
      callbacks?.onUpdate?.(frame, new Headers());
      return;
    }

    if (frame.type === 'done') {
      this.requesting = false;
      callbacks?.onSuccess?.(this.chunks, new Headers());
      return;
    }

    if (frame.type === 'error') {
      this.requesting = false;
      callbacks?.onError?.(
        new Error(frame.content || '服务返回错误'),
        undefined,
        new Headers(),
      );
      return;
    }

    // run_started/step/thinking/plan/proposal/tool_call_*/interrupt 为编排过程帧：
    // 信息性透传，不结束请求、不触发回调
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.pingTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        const frame: ChatInFrame = { type: 'ping' };
        this.ws.send(JSON.stringify(frame));
      }
    }, HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat() {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }
}

class ChatWSProvider extends AbstractChatProvider<
  ChatMessage,
  ChatRequestParams,
  ChatWSFrame
> {
  transformParams(
    requestParams: Partial<ChatRequestParams>,
    options: XRequestOptions<ChatRequestParams, ChatWSFrame, ChatMessage>,
  ): ChatRequestParams {
    return {
      ...(options?.params || {}),
      ...requestParams,
    } as ChatRequestParams;
  }

  transformLocalMessage(
    requestParams: Partial<ChatRequestParams>,
  ): ChatMessage | ChatMessage[] {
    return requestParams?.messages || [];
  }

  transformMessage(
    info: TransformMessage<ChatMessage, ChatWSFrame>,
  ): ChatMessage {
    const { originMessage, chunk } = info;
    const delta = chunk && chunk.type === 'token' ? chunk.content || '' : '';
    return {
      role: 'assistant',
      content: `${originMessage?.content || ''}${delta}`,
    };
  }
}

export const createChatProvider = () =>
  new ChatWSProvider({
    request: () => new ChatWSRequest(CHAT_WS_URL, { manual: true }),
  } as ChatProviderConfig<ChatRequestParams, ChatWSFrame, ChatMessage>);
