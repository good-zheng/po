import {
  act,
  fireEvent,
  render,
  screen,
  waitFor,
} from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
  getChatTicket: vi.fn(),
  historyPush: vi.fn(),
}));

vi.mock('@/services/novel', () => ({ getChatTicket: mocks.getChatTicket }));
vi.mock('../../chatbot/service', () => ({
  CHAT_WS_URL: 'ws://localhost:5090/ws/chat',
}));
// 抽屉里的跳转按钮走 Umi 的 history，测试只关心它被点没点
vi.mock('@umijs/max', () => ({ history: { push: mocks.historyPush } }));

import RunPanel from './RunPanel';

type Frame = {
  type: string;
  content?: string;
  payload?: Record<string, unknown>;
};

let sockets: FakeSocket[] = [];

class FakeSocket {
  static readonly CONNECTING = 0;
  static readonly OPEN = 1;
  static readonly CLOSING = 2;
  static readonly CLOSED = 3;

  readyState = 0;
  sent: string[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((e: { data: string }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  openListeners: (() => void)[] = [];

  url: string;
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
  open() {
    this.readyState = FakeSocket.OPEN;
    this.onopen?.();
    for (const cb of this.openListeners) cb();
  }
  close() {
    this.readyState = FakeSocket.CLOSED;
    this.onclose?.();
  }
  emit(frame: Frame) {
    this.onmessage?.({ data: JSON.stringify(frame) });
  }
  frames() {
    return this.sent.map((raw) => JSON.parse(raw) as Record<string, unknown>);
  }
}

/** 填想法 → 点开始 → 连上并收到 run_started，返回这一轮的连接桩 */
async function startRound() {
  fireEvent.change(screen.getByRole('textbox'), {
    target: { value: '一个程序员能改写物理法则' },
  });
  fireEvent.click(screen.getByRole('button', { name: /开始生成/ }));
  await waitFor(() => expect(sockets.length).toBeGreaterThan(0));
  const ws = sockets[sockets.length - 1];
  act(() => {
    ws.open();
    ws.emit({ type: 'run_started', payload: { thread_id: 'thread-1' } });
  });
  return ws;
}

const send = (ws: FakeSocket, frame: Frame) => act(() => ws.emit(frame));

// 外层卡片与内层文本同 textContent，getByText 会撞上「多个元素」，
// 这里只断言「这一支确实渲染了」，按钮一律按 role 查。
const expectText = (re: RegExp) => {
  expect(screen.getAllByText(re).length).toBeGreaterThan(0);
};

describe('RunPanel · 两处人工口的渲染与作答', () => {
  beforeEach(() => {
    sockets = [];
    mocks.getChatTicket.mockResolvedValue({
      data: { ticket: 'tk-1', expiresIn: 60 },
    });
    mocks.historyPush.mockReset();
    vi.stubGlobal('WebSocket', FakeSocket);
    render(<RunPanel onArchived={vi.fn()} />);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('计划闸门卡：按 stage 走计划那套措辞，展示场景卡与未平冲突', async () => {
    const ws = await startRound();
    send(ws, {
      type: 'interrupt',
      content: '等待人工确认',
      payload: {
        value: {
          stage: 'plan_approval',
          question: '这张场景卡照写吗？',
          chapter: 2,
          card_text: '第2章 场景1：天台对峙',
          blockers: ['major 一处'],
          reason: '裁判判定与正典冲突',
          unreviewed: true,
        },
      },
    });
    expectText(/计划闸门 · 第 2 章/);
    expectText(/这张场景卡照写吗？/);
    expectText(/天台对峙/);
    expectText(/未平的冲突 1 条/);
    expectText(/批准后本章会标注为/);
    expect(
      screen.getByRole('button', { name: '照这张卡继续写' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: '停笔并转归档' }),
    ).toBeInTheDocument();
    // 归档那套按钮不该出现在计划卡上
    expect(
      screen.queryByRole('button', { name: '确认归档入库' }),
    ).not.toBeInTheDocument();
  });

  it('归档确认卡：没有 stage 键走归档措辞，列出书名章数与冻结章', async () => {
    const ws = await startRound();
    send(ws, {
      type: 'interrupt',
      content: '等待人工确认',
      payload: {
        value: {
          question: '确认把这本书归档入库吗？',
          title: '代码之隙',
          chapter_count: 3,
          frozen: [1],
          open_questions: ['陈默的师承是谁？'],
        },
      },
    });
    expectText(/《代码之隙》 共 3 章/);
    expectText(/1 章待人工裁定/);
    expectText(/陈默的师承是谁？/);
    expect(
      screen.getByRole('button', { name: '确认归档入库' }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: '暂不归档' }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: '照这张卡继续写' }),
    ).not.toBeInTheDocument();
  });

  it('按钮只发 yes / no 两个字面值，且等本轮收尾后才发 resume', async () => {
    const ws = await startRound();
    send(ws, {
      type: 'interrupt',
      payload: { value: { question: '确认归档吗？' } },
    });
    fireEvent.click(screen.getByRole('button', { name: '确认归档入库' }));
    // interrupt 之后服务端还在收尾：此刻不该有第二帧
    expect(ws.sent).toHaveLength(1);
    expectText(/已回复「确认归档入库」/);

    send(ws, { type: 'done' });
    expect(ws.frames()[1]).toEqual({
      type: 'resume',
      content: 'yes',
      conversation_id: 'thread-1',
    });
  });

  it('停笔按钮发的是 no（计划侧的非同意即停笔）', async () => {
    const ws = await startRound();
    send(ws, {
      type: 'interrupt',
      payload: {
        value: { stage: 'plan_approval', question: '照卡写吗？', chapter: 1 },
      },
    });
    fireEvent.click(screen.getByRole('button', { name: '停笔并转归档' }));
    send(ws, { type: 'done' });
    expect(ws.frames()[1]).toEqual({
      type: 'resume',
      content: 'no',
      conversation_id: 'thread-1',
    });
  });

  it('拍板挂起时不允许另起一轮，作答后按钮回到生成中', async () => {
    const ws = await startRound();
    send(ws, {
      type: 'interrupt',
      payload: { value: { question: '归档吗？' } },
    });
    expect(screen.getByRole('button', { name: /生成$/ })).toBeDisabled();
    expectText(/上方有等你拍板的卡片/);
    fireEvent.click(screen.getByRole('button', { name: '确认归档入库' }));
    send(ws, { type: 'done' });
    // resume 已发出，这一轮重新变成「生成中」
    expectText(/生成中/);
    // 生成中再点「重新生成」不该开出第二条连接、也不该再发帧
    // （antd 的 loading 按钮只加类不置 disabled，所以按行为断言）
    fireEvent.click(screen.getByRole('button', { name: /生成$/ }));
    expect(sockets).toHaveLength(1);
    expect(ws.sent).toHaveLength(2);
  });

  it('归档成功后给出新书的两个出口', async () => {
    const ws = await startRound();
    send(ws, {
      type: 'thinking',
      content: '已归档：book-77',
      payload: { stage: 'archived', book_id: 77 },
    });
    fireEvent.click(screen.getByRole('button', { name: '打开这本书的工作台' }));
    expect(mocks.historyPush).toHaveBeenCalledWith('/novel/book/77/studio');
  });
});
