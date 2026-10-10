import { act, renderHook } from '@testing-library/react';
import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  type Mock,
  vi,
} from 'vitest';
import { useNovelRun } from './useNovelRun';

const mocks = vi.hoisted(() => ({
  getChatTicket: vi.fn(),
}));

vi.mock('@/services/novel', () => ({
  getChatTicket: mocks.getChatTicket,
}));

vi.mock('../../chatbot/service', () => ({
  CHAT_WS_URL: 'ws://localhost:5090/ws/chat',
}));

type Frame = {
  type: string;
  content?: string;
  payload?: Record<string, unknown>;
};

/** 只记录发出的帧、由测试决定何时回帧的 WS 桩 */
class FakeWebSocket {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  url: string;
  readyState = FakeWebSocket.CONNECTING;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  openListeners: (() => void)[] = [];

  constructor(url: string) {
    this.url = url;
    sockets.push(this);
  }

  send(raw: string) {
    this.sent.push(raw);
  }

  addEventListener(type: string, cb: () => void) {
    if (type === 'open') this.openListeners.push(cb);
  }

  close() {
    this.readyState = FakeWebSocket.CLOSED;
    this.onclose?.();
  }

  open() {
    this.readyState = FakeWebSocket.OPEN;
    this.onopen?.();
    for (const cb of this.openListeners) cb();
  }

  emit(frame: Frame) {
    this.onmessage?.({ data: JSON.stringify(frame) });
  }

  sentFrames() {
    return this.sent.map((raw) => JSON.parse(raw) as Record<string, unknown>);
  }
}

let sockets: FakeWebSocket[] = [];
let onArchived: Mock<(bookId: number) => void>;

const latest = () => sockets[sockets.length - 1];

async function startRun() {
  const view = renderHook(() => useNovelRun(onArchived));
  await act(async () => {
    await view.result.current.start('一句话想法');
  });
  latest().open();
  return view;
}

describe('useNovelRun · 生成链路帧归并与时序', () => {
  beforeEach(() => {
    sockets = [];
    onArchived = vi.fn<(bookId: number) => void>();
    mocks.getChatTicket.mockResolvedValue({
      data: { ticket: 'tk-1', expiresIn: 60 },
    });
    vi.stubGlobal('WebSocket', FakeWebSocket);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('起一轮时不带 conversation_id：新线程由服务端开', async () => {
    const view = await startRun();
    expect(latest().url).toBe('ws://localhost:5090/ws/chat?ticket=tk-1');
    expect(latest().sentFrames()).toEqual([
      { type: 'message', content: '一句话想法', agent: 'novel' },
    ]);
    expect(view.result.current.phase).toBe('running');
  });

  it('resume 用的 id 取自 run_started 的 payload.thread_id', async () => {
    const view = await startRun();
    const ws = latest();
    act(() => {
      ws.emit({ type: 'run_started', payload: { thread_id: 'thread-abc' } });
      ws.emit({
        type: 'interrupt',
        content: '摘要文本',
        payload: { value: { question: '要归档吗？' } },
      });
      ws.emit({ type: 'done' });
    });
    act(() => view.result.current.answer('yes'));
    expect(ws.sentFrames()[1]).toEqual({
      type: 'resume',
      content: 'yes',
      conversation_id: 'thread-abc',
    });
  });

  it('拍板载荷读 payload.value，content 只是给人看的摘要', async () => {
    const view = await startRun();
    act(() => {
      latest().emit({
        type: 'interrupt',
        content: '等待人工确认',
        payload: {
          value: {
            question: '这张场景卡照写吗？',
            stage: 'plan_approval',
            chapter: 2,
            card_text: '场景卡正文',
            blockers: [1, 2],
          },
        },
      });
    });
    expect(view.result.current.phase).toBe('awaiting');
    expect(view.result.current.interrupt?.stage).toBe('plan_approval');
    expect(view.result.current.interrupt?.chapter).toBe(2);
    // 过程行取的是卡片自己的 question，而不是服务端那句摘要
    expect(view.result.current.notes).toContain('这张场景卡照写吗？');
  });

  it('interrupt 之后、done 之前点确认只排队，done 到达才补发', async () => {
    const view = await startRun();
    const ws = latest();
    act(() => {
      ws.emit({ type: 'run_started', payload: { thread_id: 'thread-abc' } });
      ws.emit({
        type: 'interrupt',
        payload: { value: { question: '要归档吗？' } },
      });
    });
    act(() => view.result.current.answer('no'));
    expect(ws.sent).toHaveLength(1); // 只有 message 帧
    expect(
      view.result.current.notes.some((n) => n.includes('等本轮收尾后发出')),
    ).toBe(true);

    act(() => ws.emit({ type: 'done' }));
    expect(ws.sentFrames()[1]).toEqual({
      type: 'resume',
      content: 'no',
      conversation_id: 'thread-abc',
    });
    expect(view.result.current.phase).toBe('running');
    expect(view.result.current.interrupt).toBeNull();
  });

  it('本轮已收尾时确认立即发出', async () => {
    const view = await startRun();
    const ws = latest();
    act(() => {
      ws.emit({ type: 'run_started', payload: { thread_id: 'thread-abc' } });
      ws.emit({
        type: 'interrupt',
        payload: { value: { question: '要归档吗？' } },
      });
      ws.emit({ type: 'done' });
    });
    expect(view.result.current.phase).toBe('awaiting');
    act(() => view.result.current.answer('yes'));
    expect(ws.sentFrames()[1]).toEqual({
      type: 'resume',
      content: 'yes',
      conversation_id: 'thread-abc',
    });
  });

  it('归档帧记下新书 id 并回调宿主', async () => {
    const view = await startRun();
    act(() => {
      latest().emit({
        type: 'thinking',
        content: '已归档：book-77',
        payload: { stage: 'archived', book_id: 77 },
      });
    });
    expect(view.result.current.archivedBookId).toBe(77);
    expect(onArchived).toHaveBeenCalledWith(77);
    expect(view.result.current.notes.some((n) => n.includes('书已入库'))).toBe(
      true,
    );
  });

  it('token 累加成正文，thinking/step 进过程', async () => {
    const view = await startRun();
    const ws = latest();
    act(() => {
      ws.emit({ type: 'token', content: '第一章 ' });
      ws.emit({ type: 'token', content: '开头' });
      ws.emit({ type: 'step', payload: { node: 'write' } });
    });
    expect(view.result.current.text).toBe('第一章 开头');
    expect(view.result.current.notes).toContain('write');
  });

  it('supervisor 的 route 节点不进过程行，领域节点照常收', async () => {
    const view = await startRun();
    act(() => {
      latest().emit({ type: 'step', payload: { node: 'route' } });
      latest().emit({ type: 'step', payload: { node: 'conceive' } });
    });
    // 直连插槽改成走父图后，每轮都会多一条 node=route 的编排帧；它对作者没有意义
    expect(view.result.current.notes).toEqual([
      '发起生成：一句话想法',
      'conceive',
    ]);
  });

  it('error 帧解锁界面并丢掉排队的回复', async () => {
    const view = await startRun();
    const ws = latest();
    act(() => {
      ws.emit({ type: 'run_started', payload: { thread_id: 'thread-abc' } });
      ws.emit({
        type: 'interrupt',
        payload: { value: { question: '要归档吗？' } },
      });
    });
    act(() => view.result.current.answer('yes'));
    act(() => {
      ws.emit({ type: 'error', content: '运行超时' });
    });
    expect(view.result.current.phase).toBe('failed');
    expect(view.result.current.errorText).toBe('运行超时');
    // done 之后不再补发那条已经不该再发的 resume
    act(() => ws.emit({ type: 'done' }));
    expect(ws.sent).toHaveLength(1);
  });

  it('连接中断时在流式状态下收尾，不会永远停在生成中', async () => {
    const view = await startRun();
    act(() => latest().close());
    expect(view.result.current.phase).toBe('failed');
    expect(view.result.current.errorText).toContain('连接已断开');
  });

  it('挂起拍板时不允许再起新一轮', async () => {
    const view = await startRun();
    const ws = latest();
    act(() => {
      ws.emit({
        type: 'interrupt',
        payload: { value: { question: '要归档吗？' } },
      });
    });
    await act(async () => {
      await view.result.current.start('另一个想法');
    });
    expect(sockets).toHaveLength(1);
    expect(ws.sent).toHaveLength(1);
  });
});
