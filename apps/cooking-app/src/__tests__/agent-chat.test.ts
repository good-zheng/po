import type { ChatWSFrame } from '@po/types';

import {
  resetAgentConversation,
  resolveChatUrl,
  streamAgentReply,
} from '@/lib/ai/agent-chat';

/** 最小 WebSocket 替身：记录上行帧，测试用 open/emit/fail 驱动下行 */
class FakeSocket {
  static instances: FakeSocket[] = [];

  static get latest() {
    const socket = FakeSocket.instances.at(-1);

    if (!socket) {
      throw new Error('还没有创建 WebSocket');
    }

    return socket;
  }

  onopen: (() => void) | null = null;
  onmessage: ((event: { data: unknown }) => void) | null = null;
  onerror: (() => void) | null = null;
  onclose: (() => void) | null = null;
  sent: string[] = [];
  closed = false;

  constructor(readonly url: string) {
    FakeSocket.instances.push(this);
  }

  send(data: string) {
    this.sent.push(data);
  }

  close() {
    this.closed = true;
  }

  open() {
    this.onopen?.();
  }

  emit(frame: ChatWSFrame) {
    this.onmessage?.({ data: JSON.stringify(frame) });
  }

  fail() {
    this.onerror?.();
  }
}

const RECIPE = {
  id: 7,
  title: '剁椒鱼头',
  difficulty: 2,
  totalTime: 40,
  servings: 2,
  coverImageUrl: null,
};

function toolResultFrame(
  name: string,
  payload: Record<string, unknown>,
): ChatWSFrame {
  return {
    content: JSON.stringify(payload),
    payload: { name, status: 'success', tool_call_id: 'call-1' },
    type: 'tool_call_result',
  };
}

describe('resolveChatUrl', () => {
  const nativeApiUrl = process.env.EXPO_PUBLIC_API_URL;

  afterEach(() => {
    process.env.EXPO_PUBLIC_API_URL = nativeApiUrl;
    delete process.env.EXPO_PUBLIC_CHAT_URL;
  });

  it('derives the chat host from EXPO_PUBLIC_API_URL', () => {
    process.env.EXPO_PUBLIC_API_URL = 'http://10.0.2.2:8080/api';

    expect(resolveChatUrl()).toBe('ws://10.0.2.2:5090/ws/chat');
  });

  it('honours the EXPO_PUBLIC_CHAT_URL override', () => {
    process.env.EXPO_PUBLIC_API_URL = 'http://10.0.2.2:8080/api';
    process.env.EXPO_PUBLIC_CHAT_URL = 'wss://chat.example.com/ws/chat';

    expect(resolveChatUrl()).toBe('wss://chat.example.com/ws/chat');
  });
});

describe('streamAgentReply', () => {
  beforeEach(() => {
    FakeSocket.instances = [];
    resetAgentConversation();
    globalThis.WebSocket = FakeSocket as unknown as typeof WebSocket;
  });

  it('streams tokens and collects recipe cards until done', async () => {
    const onText = jest.fn();
    const onRecipes = jest.fn();
    const result = streamAgentReply('剁椒鱼头怎么做', { onRecipes, onText });
    const socket = FakeSocket.latest;

    socket.open();
    socket.emit({
      payload: { thread_id: 'thread-1' },
      type: 'run_started',
    });
    socket.emit(
      toolResultFrame('search_recipes', { count: 1, recipes: [RECIPE] }),
    );
    socket.emit({ content: '剁椒鱼头', type: 'token' });
    socket.emit({ content: '要蒸 40 分钟。', type: 'token' });
    socket.emit({ type: 'done' });

    await expect(result).resolves.toEqual({ answered: true });
    expect(JSON.parse(socket.sent[0])).toEqual({
      content: '剁椒鱼头怎么做',
      type: 'message',
    });
    expect(onText).toHaveBeenLastCalledWith('剁椒鱼头要蒸 40 分钟。');
    expect(onRecipes).toHaveBeenLastCalledWith([RECIPE]);
    expect(socket.closed).toBe(true);
  });

  it('reuses the server thread id on the next run', async () => {
    const first = streamAgentReply('今晚吃什么');
    FakeSocket.latest.open();
    FakeSocket.latest.emit({
      payload: { thread_id: 'thread-1' },
      type: 'run_started',
    });
    FakeSocket.latest.emit({ content: '来道鱼', type: 'token' });
    FakeSocket.latest.emit({ type: 'done' });
    await first;

    const second = streamAgentReply('换个素菜');
    const socket = FakeSocket.latest;

    socket.open();
    expect(JSON.parse(socket.sent[0])).toEqual({
      content: '换个素菜',
      conversation_id: 'thread-1',
      type: 'message',
    });
    socket.emit({ content: '炒青菜', type: 'token' });
    socket.emit({ type: 'done' });
    await second;
  });

  it('reports no answer when the chat service errors out', async () => {
    const result = streamAgentReply('你好');
    const socket = FakeSocket.latest;

    socket.open();
    socket.emit({ content: '服务端出错', type: 'error' });

    await expect(result).resolves.toEqual({
      answered: false,
      error: '服务端出错',
    });
  });

  it('treats a dropped connection as no answer', async () => {
    const result = streamAgentReply('你好');

    FakeSocket.latest.fail();

    await expect(result).resolves.toEqual({
      answered: false,
      error: '连不上聊天服务，请确认 chat 服务已启动。',
    });
  });

  it('keeps streamed text when the connection drops midway', async () => {
    const result = streamAgentReply('你好');
    const socket = FakeSocket.latest;

    socket.open();
    socket.emit({ content: '先说到这', type: 'token' });
    socket.onclose?.();

    await expect(result).resolves.toEqual({
      answered: true,
      error: '聊天服务暂时用不了。',
    });
  });

  it('ignores recipe payloads that do not carry an id and title', async () => {
    const onRecipes = jest.fn();
    const result = streamAgentReply('找点吃的', { onRecipes });
    const socket = FakeSocket.latest;

    socket.open();
    socket.emit(toolResultFrame('search_recipes', { recipes: [{ id: 1 }] }));
    socket.emit(
      toolResultFrame('list_categories', { count: 1, categories: ['川菜'] }),
    );
    socket.emit({ type: 'done' });

    await expect(result).resolves.toEqual({ answered: false });
    expect(onRecipes).not.toHaveBeenCalled();
  });

  it('finishes immediately when the caller already aborted', async () => {
    const controller = new AbortController();
    controller.abort();

    await expect(
      streamAgentReply('你好', { signal: controller.signal }),
    ).resolves.toEqual({ answered: false });
    expect(FakeSocket.instances).toHaveLength(0);
  });
});
