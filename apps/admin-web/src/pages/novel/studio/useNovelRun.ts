import type { ChatInFrame, ChatWSFrame } from '@po/types';
import { useCallback, useEffect, useRef, useState } from 'react';
import { getChatTicket } from '@/services/novel';
import { CHAT_WS_URL } from '../../chatbot/service';

const HEARTBEAT_INTERVAL = 30_000;

/**
 * 两处人工口的载荷（`graph.py` 的 `gate_plan` 与 `archive`）。
 *
 * 判别键是 `stage`：计划闸门带 `stage: "plan_approval"`，归档确认**没有**这个键——
 * 服务端把 `interrupt(...)` 的入参原样放进 `payload.value`，两处载荷字段集不同，
 * 所以卡片要按 stage 分流，不能靠「有没有 title」这类巧合。
 */
export type NovelInterruptValue = {
  stage?: string;
  question?: string;
  hint?: string;
  title?: string;
  genre?: string;
  chapter?: number;
  chapter_count?: number;
  card_text?: string;
  blockers?: unknown[];
  unreviewed?: boolean;
  reason?: string;
  frozen?: unknown[];
  frozen_note?: string;
  plan_unreviewed?: unknown[];
  unreviewed_note?: string;
  halted_at?: number;
  halted_note?: string;
  open_questions?: string[];
};

/**
 * connecting/running/awaiting/finished/failed 的五态。
 *
 * `awaiting` 是「interrupt 已到但 run 还没收尾」——服务端在 interrupt 之后仍会把本轮
 * 帧发到 `done` 才停（`ws.py:269-277` 逐条 await 发送），此时发 resume 会让两轮的
 * 收尾帧交错，所以这一态下按钮点下去只是排队。
 */
export type RunPhase =
  | 'idle'
  | 'connecting'
  | 'running'
  | 'awaiting'
  | 'finished'
  | 'failed';

type RunState = {
  phase: RunPhase;
  notes: string[];
  text: string;
  interrupt: NovelInterruptValue | null;
  errorText: string | null;
  archivedBookId: number | null;
};

const initialState: RunState = {
  phase: 'idle',
  notes: [],
  text: '',
  interrupt: null,
  errorText: null,
  archivedBookId: null,
};

/**
 * 生成链路（`agent: 'novel'`）的浏览器侧通道：一句话想法 → 整本新书 → 两处人工拍板。
 *
 * 不复用 `chatbot/service.ts` 的 `ChatWSRequest`：它对 `interrupt` 是「信息性透传」，
 * 而这条链路的两个卡点必须由人作答才会往下走（归档侧不作答=正文照回但永不入库；
 * 计划侧不作答=图挂在 checkpoint，后续一章都不会写）。也不复用右栏的 `useNovelChat`：
 * 那条连接绑定 `bookId`/参照章、只读不写，和这条「会建新书的长任务」共用一条连接会让
 * 两边的会话历史混进同一个 thread。
 *
 * 帧时序（服务端硬约束，见 `services/chat/app/routers/ws.py` 顶部注释与链路图 §4.2）：
 * `interrupt` 之后必须先把本轮消费到 `done`，`resume` 才发得出去；`resume` 必须带
 * `conversation_id`，缺了服务端回 `error` 而不是新建线程。这一轮的 id 由服务端在
 * `run_started.payload.thread_id` 里给出——首帧故意不带 id，好让每轮都是新线程。
 */
export function useNovelRun(onArchived?: (bookId: number) => void) {
  const [state, setState] = useState<RunState>(initialState);

  const wsRef = useRef<WebSocket | null>(null);
  const pingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const conversationRef = useRef<string>('');
  // 本轮是否还在发帧（发出 message/resume 起、收到 done/error 止）。
  // 不能用 ws.readyState 判：连接在整个 run 期间都是 OPEN，interrupt 之后到 done
  // 之间服务端还在收尾，此时插一条 resume 会让两轮的帧交错。
  const streamingRef = useRef(false);
  // interrupt 之后、done 之前点「确认」：先存下来，done 到达时补发（见上面的时序约束）
  const pendingResumeRef = useRef<string | null>(null);
  const awaitingRef = useRef<NovelInterruptValue | null>(null);
  const onArchivedRef = useRef(onArchived);
  onArchivedRef.current = onArchived;

  const stopHeartbeat = () => {
    if (pingRef.current) {
      clearInterval(pingRef.current);
      pingRef.current = null;
    }
  };

  const sendFrame = (frame: ChatInFrame) => {
    const ws = wsRef.current;
    if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(frame));
  };

  const writeResume = (value: string) => {
    pendingResumeRef.current = null;
    awaitingRef.current = null;
    streamingRef.current = true;
    setState((prev) => ({
      ...prev,
      phase: 'running',
      interrupt: null,
      notes: [...prev.notes, `已回复：${value}`],
    }));
    sendFrame({
      type: 'resume',
      content: value,
      conversation_id: conversationRef.current,
    });
  };

  const handleFrame = useCallback((frame: ChatWSFrame) => {
    if (frame.type === 'pong') return;

    if (frame.type === 'run_started') {
      // thread_id 是 resume 的唯一凭据：本轮不带 conversation_id 出去，id 就从这里回来。
      const threadId = frame.payload?.thread_id;
      if (typeof threadId === 'string' && threadId) {
        conversationRef.current = threadId;
      }
      return;
    }

    if (frame.type === 'token') {
      setState((prev) => ({
        ...prev,
        text: prev.text + (frame.content ?? ''),
      }));
      return;
    }

    if (
      frame.type === 'thinking' ||
      frame.type === 'plan' ||
      frame.type === 'step'
    ) {
      // route 是 supervisor 的编排节点名，不是创作步骤：点名插槽后每一轮都会多一条
      // 「route」，作者只会读成故障，所以过程行只收领域节点。
      if (frame.type === 'step' && frame.payload?.node === 'route') return;
      const note = frame.content || String(frame.payload?.node ?? '');
      const stage = frame.payload?.stage;
      if (stage === 'archived') {
        const bookId = Number(frame.payload?.book_id);
        if (Number.isFinite(bookId) && bookId > 0) {
          setState((prev) => ({ ...prev, archivedBookId: bookId }));
          onArchivedRef.current?.(bookId);
        }
      }
      if (note)
        setState((prev) => ({
          ...prev,
          notes: [
            ...prev.notes,
            stage === 'archived' ? `${note}（书已入库）` : note,
          ],
        }));
      return;
    }

    if (frame.type === 'interrupt') {
      const value = (frame.payload?.value ?? {}) as NovelInterruptValue;
      awaitingRef.current = value;
      setState((prev) => ({
        ...prev,
        phase: 'awaiting',
        interrupt: value,
        notes: [
          ...prev.notes,
          value.question || frame.content || '等待你的拍板',
        ],
      }));
      return;
    }

    if (frame.type === 'done') {
      streamingRef.current = false;
      const queued = pendingResumeRef.current;
      if (queued) {
        writeResume(queued);
        return;
      }
      setState((prev) => ({
        ...prev,
        phase: prev.interrupt ? 'awaiting' : 'finished',
      }));
      return;
    }

    if (frame.type === 'error') {
      streamingRef.current = false;
      pendingResumeRef.current = null;
      setState((prev) => ({
        ...prev,
        phase: 'failed',
        errorText: frame.content || '服务返回错误',
      }));
      return;
    }

    // tool_call_* / proposal：本面板不消费（生成链路没有提议卡）
  }, []);

  const ensureConnection = useCallback(async (): Promise<WebSocket> => {
    const live = wsRef.current;
    if (live && live.readyState <= WebSocket.CONNECTING) return live;

    // 票据对 novel 插槽不是硬要求（帧级闸门只拦 novel-chat），但换得到就带上：
    // 一旦服务端把 novel 也纳入需要身份的插槽，没票的连接会在每一帧上收到 error，
    // 而那种报错读起来像「模型出问题」，比握手期就关掉连接更难查。
    let ticket = '';
    try {
      const res = await getChatTicket();
      ticket = res?.data?.ticket ?? '';
    } catch {
      ticket = '';
    }
    const url = ticket
      ? `${CHAT_WS_URL}?ticket=${encodeURIComponent(ticket)}`
      : CHAT_WS_URL;

    const ws = new WebSocket(url);
    wsRef.current = ws;
    ws.onopen = () => {
      stopHeartbeat();
      pingRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) sendFrame({ type: 'ping' });
      }, HEARTBEAT_INTERVAL);
    };
    ws.onmessage = (event) => {
      let frame: ChatWSFrame;
      try {
        frame = JSON.parse(String(event.data));
      } catch {
        return;
      }
      handleFrame(frame);
    };
    ws.onclose = () => {
      stopHeartbeat();
      if (wsRef.current === ws) wsRef.current = null;
      // 长任务最常见的中断形态是「服务端实例被回收」而不是收到 error 帧：
      // 不收尾的话按钮会永远停在「生成中」，人只能刷新页面。
      if (streamingRef.current) {
        streamingRef.current = false;
        pendingResumeRef.current = null;
        setState((prev) => ({
          ...prev,
          phase: 'failed',
          errorText:
            '生成连接已断开：这一轮停在了中断处，重发一次想法会另起一条线程',
        }));
      }
    };
    ws.onerror = () => {
      streamingRef.current = false;
      pendingResumeRef.current = null;
      setState((prev) => ({
        ...prev,
        phase: 'failed',
        errorText:
          '生成连接出错：长任务中断后同一条会话仍可续跑，重发一次会走 checkpoint',
      }));
    };
    return ws;
  }, [handleFrame]);

  useEffect(
    () => () => {
      stopHeartbeat();
      const ws = wsRef.current;
      wsRef.current = null;
      ws?.close();
    },
    [],
  );

  /** 起一轮生成：`content` 是一句话想法，服务端从这里推出构思 → 大纲 → 逐章 → 归档确认。 */
  const start = useCallback(
    async (idea: string) => {
      const content = idea.trim();
      // awaiting 也在拦截之列：图挂在 interrupt 的 checkpoint 上，此时再发 message
      // 不是「新开一本」，是同一条线程上撞开两段执行。要先答上面的拍板卡。
      if (
        !content ||
        state.phase === 'connecting' ||
        state.phase === 'running' ||
        state.phase === 'awaiting'
      )
        return;
      // 故意不带 conversation_id：服务端为这条 message 新建 thread，并把 id 随
      // run_started 的 payload.thread_id 回吐（见 ws.py 的该分支注释）。这样每一轮
      // 生成都是一条全新线程——上一轮已归档的书不该和这一轮的构思共享 checkpoint。
      conversationRef.current = '';
      streamingRef.current = true;
      setState({
        ...initialState,
        phase: 'connecting',
        notes: [`发起生成：${content}`],
      });
      const ws = await ensureConnection();
      const frame: ChatInFrame = {
        type: 'message',
        content,
        agent: 'novel',
      };
      const write = () => ws.send(JSON.stringify(frame));
      if (ws.readyState === WebSocket.OPEN) write();
      else ws.addEventListener('open', write, { once: true });
      setState((prev) => ({ ...prev, phase: 'running' }));
    },
    [ensureConnection, state.phase],
  );

  /**
   * 回答当前的人工口。词表在服务端（`_APPROVE_WORDS`）：`yes/true/1/ok/确认/同意/是`，
   * 其余都算「否」——归档侧=暂不落库，计划侧=停笔转归档。
   */
  const answer = useCallback((value: string) => {
    if (!awaitingRef.current) return;
    if (!streamingRef.current) {
      writeResume(value);
      return;
    }
    // 本轮还没收尾（interrupt 之后服务端仍把这轮的帧发到 done）：排队给 done 补发
    pendingResumeRef.current = value;
    setState((prev) => ({
      ...prev,
      notes: [...prev.notes, `已记录回复（${value}），等本轮收尾后发出`],
    }));
  }, []);

  const reset = useCallback(() => {
    streamingRef.current = false;
    pendingResumeRef.current = null;
    awaitingRef.current = null;
    conversationRef.current = '';
    setState(initialState);
  }, []);

  return { ...state, start, answer, reset };
}
