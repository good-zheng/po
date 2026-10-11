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
  drawerClose: vi.fn(),
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

const BOOK = { id: 7, title: '代码之隙' };
const CHAPTERS = [
  { id: 71, chapterIndex: 1, wordCount: 1200 },
  { id: 72, chapterIndex: 2, wordCount: 1300 },
  { id: 73, chapterIndex: 3, wordCount: 1400 },
];
/** 作者在第 4 章排了一个待写占位（标题正文都空）：它不进游标，也不该被当成衔接尾段 */
const WITH_PLACEHOLDER = [
  ...CHAPTERS,
  { id: 74, chapterIndex: 4, wordCount: 0 },
];
/** 空位夹在已写章之间：游标（有正文的章数=2）会撞上第 3 章的已有正文 */
const WITH_HOLE = [
  { id: 71, chapterIndex: 1, wordCount: 1200 },
  { id: 72, chapterIndex: 2, wordCount: 0 },
  { id: 73, chapterIndex: 3, wordCount: 1400 },
];

/** 在工作台里打开抽屉（带当前书与章树）→ 填一句 → 点开始 → 连上并收到 run_started */
async function startContinueRound(idea: string) {
  fireEvent.change(screen.getByRole('textbox'), { target: { value: idea } });
  fireEvent.click(screen.getByRole('button', { name: /开始续写|开始生成/ }));
  await waitFor(() => expect(sockets.length).toBeGreaterThan(0));
  const ws = sockets[sockets.length - 1];
  act(() => {
    ws.open();
    ws.emit({ type: 'run_started', payload: { thread_id: 'thread-9' } });
  });
  return ws;
}

const frame0 = (ws: FakeSocket) => ws.frames()[0] as Record<string, unknown>;

describe('RunPanel · 续写本书（一句话直接出章，默认不问）', () => {
  beforeEach(() => {
    sockets = [];
    mocks.getChatTicket.mockResolvedValue({
      data: { ticket: 'tk-1', expiresIn: 60 },
    });
    mocks.historyPush.mockReset();
    mocks.drawerClose.mockReset();
    vi.stubGlobal('WebSocket', FakeSocket);
    render(
      <RunPanel
        onArchived={vi.fn()}
        onClose={mocks.drawerClose}
        book={BOOK}
        chapters={CHAPTERS}
      />,
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('默认就落在续写模式，并按库里章数预告往后追加的范围', () => {
    expect(
      screen.getByRole('button', { name: '开始续写' }),
    ).toBeInTheDocument();
    expectText(/已写 3 章/);
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: '接着往下写' },
    });
    expectText(/第 4 至 6 章共 3 章/);
  });

  it('句子里的中文章号会被读成范围，走保留键而不是拼进正文', async () => {
    const ws = await startContinueRound('开始创作第三至第十章的内容');
    expect(frame0(ws)).toEqual({
      type: 'message',
      content: '开始创作第三至第十章的内容',
      agent: 'novel',
      context: {
        auto: true,
        bookId: '7',
        fromChapter: 3,
        chapterCount: 8,
        tailChapterId: '73',
      },
    });
  });

  it('勾上「写之前先问我」才保留两处人工口', async () => {
    fireEvent.click(screen.getByRole('checkbox', { name: '写之前先问我' }));
    const ws = await startContinueRound('再写两章');
    const context = frame0(ws).context as Record<string, unknown>;
    expect(context.auto).toBe(false);
    expect(context.bookId).toBe('7');
    expect(context.chapterCount).toBe(2);
  });

  it('切到「写本新书」：不带 bookId，也不带章号范围', async () => {
    fireEvent.click(screen.getByText('写本新书'));
    const ws = await startContinueRound('一个程序员能改写物理法则');
    expect(frame0(ws)).toEqual({
      type: 'message',
      content: '一个程序员能改写物理法则',
      agent: 'novel',
      context: { auto: true },
    });
  });

  it('续写入库后的出口是回中栏看新章，不去另一本书', async () => {
    const ws = await startContinueRound('写两章');
    send(ws, {
      type: 'thinking',
      content: '已续写入库（书 7 新增第 4-5 章）',
      payload: {
        stage: 'archived',
        book_id: 7,
        mode: 'continue',
        from_chapter: 4,
        to_chapter: 5,
      },
    });
    expectText(/已续写入库/);
    expect(
      screen.queryByRole('button', { name: '打开这本书的工作台' }),
    ).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: '关掉抽屉看中栏' }));
    expect(mocks.drawerClose).toHaveBeenCalled();
  });

  it('连接层的失败把服务端/客户端的原因原样摊开，不只是一句「出错了」', async () => {
    const ws = await startContinueRound('写两章');
    send(ws, {
      type: 'error',
      content: '续写这本书需要作者身份：先在管理端登录，再重开创作面板',
    });
    expect(screen.getByText('这一轮没跑成')).toBeInTheDocument();
    expect(screen.getByText(/先在管理端登录/)).toBeInTheDocument();
    // 闸门只拦这一帧、不关连接，所以界面要能立刻重试
    // （名字用正则：antd 的按钮图标会把 aria-label 拼进可及名）
    expect(
      screen.getByRole('button', { name: /重新生成/ }),
    ).toBeInTheDocument();
  });
});

describe('RunPanel · 游标只数有正文的章（待写占位不算已写）', () => {
  beforeEach(() => {
    sockets = [];
    mocks.getChatTicket.mockResolvedValue({
      data: { ticket: 'tk-1', expiresIn: 60 },
    });
    mocks.historyPush.mockReset();
    mocks.drawerClose.mockReset();
    vi.stubGlobal('WebSocket', FakeSocket);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('第 4 章是空位：游标仍是 3，尾段取第 3 章，预告点明这一轮会填掉它', async () => {
    render(
      <RunPanel
        onArchived={vi.fn()}
        onClose={mocks.drawerClose}
        book={BOOK}
        chapters={WITH_PLACEHOLDER}
      />,
    );
    // 按章节行数算会报「已写 4 章」并从第 5 章起写，第 4 章就此永久空着
    expectText(/这本书已写 3 章，本轮往后追加第 4 至 6 章/);
    const ws = await startContinueRound('接着往下写三章');
    expect(frame0(ws)).toEqual({
      type: 'message',
      content: '接着往下写三章',
      agent: 'novel',
      context: {
        auto: true,
        bookId: '7',
        chapterCount: 3,
        tailChapterId: '73',
      },
    });
    expectText(/第 4 章是你留的待写占位/);
  });

  it('空位夹在已写章之间时先报撞号，不让人发起一轮注定失败的续写', () => {
    render(
      <RunPanel
        onArchived={vi.fn()}
        onClose={mocks.drawerClose}
        book={BOOK}
        chapters={WITH_HOLE}
      />,
    );
    expectText(/第 2 章正文为空却排在已写章之前/);
  });
});
