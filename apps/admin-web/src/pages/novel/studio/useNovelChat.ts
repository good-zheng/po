import type { ChatInFrame, ChatWSFrame } from '@po/types';
import { useCallback, useEffect, useRef, useState } from 'react';
import { getChatTicket } from '@/services/novel';
import { CHAT_WS_URL } from '../../chatbot/service';

/** 提议卡帧的 payload 形状：与 Java `ProposalRequest` 同名字段，前端只转发不拼装。 */
export type ProposalPayload = {
  bookId?: number | string;
  sessionId?: string;
  asOfChapter?: number;
  kind?: string;
  subjectKey?: string;
  predicate?: string;
  objectText?: string;
  validFromChapter?: number;
  basisQuote?: string;
};

export type ChatTurn = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  /** thinking / plan 过程行：装配失败、出卡数这类断链痕迹要在界面上看得见（§12.2） */
  notes: string[];
  cards: ProposalCardItem[];
};

/** 一张出卡带一个本地序号：会话内不重复，供 React key 用（采纳后落库的 id 走台账那条路） */
export type ProposalCardItem = {
  id: string;
  payload: ProposalPayload;
};

const HEARTBEAT_INTERVAL = 30_000;

let seq = 0;
const nextId = (scope: string) => {
  seq += 1;
  return `${scope}-${seq}`;
};

/**
 * 创作工作台右栏的对话通道：复用 `/ws/chat` 的帧协议，直连 `novel-chat` 插槽。
 *
 * 没有复用 chatbot 页的 x-sdk 客户端：`ChatWSRequest` 对 thinking/proposal 刻意忽略、
 * 且 `useXChat` 不给出旁听帧的出口，而右栏必须把提议卡和断链痕迹分开渲染。
 *
 * 握手带一次性票据（`?ticket=`）：novel-chat 会按 `context.bookId` 读某本书的正典，
 * 服务端只有在认得出「哪位作者」时才允许这次读（§15.13-12）。票据换不到就当作未登录处理
 * 直接停在发送前，不建匿名连接——那条连接上每一帧都会被回 error，看不出真实原因。
 */
export function useNovelChat(bookId: number, chapterId: number | null) {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [requesting, setRequesting] = useState(false);
  const [connected, setConnected] = useState(false);
  const [errorText, setErrorText] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const pingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  // 取票是异步的，而这期间 `requesting` 状态还没落到下一次渲染——用 ref 做同步守门，
  // 否则连按两次发送会开两个会话轮次。
  const busyRef = useRef(false);
  // 参照章在发送那一刻才读，改了参照章不必重连
  const chapterRef = useRef<number | null>(chapterId);
  const conversationRef = useRef<string>('');
  const assistantRef = useRef<string | null>(null);

  chapterRef.current = chapterId;

  const stopHeartbeat = () => {
    if (pingRef.current) {
      clearInterval(pingRef.current);
      pingRef.current = null;
    }
  };

  const patchAssistant = (patch: (turn: ChatTurn) => ChatTurn) => {
    const id = assistantRef.current;
    if (!id) return;
    setTurns((prev) =>
      prev.map((turn) =>
        turn.id === id && turn.role === 'assistant' ? patch(turn) : turn,
      ),
    );
  };

  const handleFrame = useCallback((frame: ChatWSFrame) => {
    if (frame.type === 'pong') return;
    if (frame.type === 'token') {
      patchAssistant((turn) => ({
        ...turn,
        content: turn.content + (frame.content ?? ''),
      }));
      return;
    }
    if (frame.type === 'thinking' || frame.type === 'plan') {
      const note = frame.content ?? '';
      if (note)
        patchAssistant((turn) => ({ ...turn, notes: [...turn.notes, note] }));
      return;
    }
    if (frame.type === 'proposal') {
      patchAssistant((turn) => ({
        ...turn,
        cards: [
          ...turn.cards,
          {
            id: nextId('card'),
            payload: (frame.payload ?? {}) as ProposalPayload,
          },
        ],
      }));
      return;
    }
    if (frame.type === 'done') {
      assistantRef.current = null;
      busyRef.current = false;
      setRequesting(false);
      return;
    }
    if (frame.type === 'error') {
      assistantRef.current = null;
      busyRef.current = false;
      setRequesting(false);
      setErrorText(frame.content || '服务返回错误');
      return;
    }
    // run_started / step / tool_call_* / interrupt：一期右栏不消费（只谈不写，无审批流）
  }, []);

  /**
   * 建立（或复用）这条连接。返回 null 表示没连上且原因已写进 errorText。
   *
   * 票据在这里现取，不缓存：它 60 秒过期、服务端校验一次即失效，而重连是新的一次握手，
   * 复用旧票等于必拒。
   */
  const ensureConnection = useCallback(async (): Promise<WebSocket | null> => {
    const live = wsRef.current;
    if (live && live.readyState <= WebSocket.CONNECTING) return live;

    let ticket = '';
    try {
      const res = await getChatTicket();
      ticket = res?.data?.ticket ?? '';
    } catch {
      ticket = '';
    }
    if (!ticket) {
      setErrorText('对话握手凭据获取失败：请确认仍登录管理端，再重发一次');
      return null;
    }

    const ws = new WebSocket(
      `${CHAT_WS_URL}?ticket=${encodeURIComponent(ticket)}`,
    );
    wsRef.current = ws;
    ws.onopen = () => {
      setConnected(true);
      stopHeartbeat();
      pingRef.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          const frame: ChatInFrame = { type: 'ping' };
          ws.send(JSON.stringify(frame));
        }
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
      setConnected(false);
      if (wsRef.current === ws) wsRef.current = null;
    };
    ws.onerror = () => {
      // 一并解锁 requesting：握手被拒（票据被服务端判无效）时不会有 done 帧，
      // 不解锁就是发送按钮永久 loading。下一次发送会重新取票重连。
      busyRef.current = false;
      setRequesting(false);
      setErrorText('对话连接出错，稍后重发即可（重发会重新换票建连）');
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

  const send = useCallback(
    async (text: string) => {
      const content = text.trim();
      if (!content || requesting || busyRef.current) return;
      if (!conversationRef.current)
        conversationRef.current = crypto.randomUUID();
      busyRef.current = true;
      setErrorText(null);
      setRequesting(true);
      // 先建连（含取票）再上屏：取票失败时不该留下一条永远等不到回复的空气泡
      const ws = await ensureConnection();
      if (!ws) {
        busyRef.current = false;
        setRequesting(false);
        return;
      }
      const assistantId = nextId('turn');
      assistantRef.current = assistantId;
      setTurns((prev) => [
        ...prev,
        { id: nextId('turn'), role: 'user', content, notes: [], cards: [] },
        {
          id: assistantId,
          role: 'assistant',
          content: '',
          notes: [],
          cards: [],
        },
      ]);
      const frame: ChatInFrame = {
        type: 'message',
        content,
        conversation_id: conversationRef.current,
        agent: 'novel-chat',
        // 定位键走 context：服务端只认 bookId / chapterId，其余键会被拼进提示词
        context: {
          bookId,
          ...(chapterRef.current != null
            ? { chapterId: chapterRef.current }
            : {}),
        },
      };
      const write = () => ws.send(JSON.stringify(frame));
      if (ws.readyState === WebSocket.OPEN) write();
      else ws.addEventListener('open', write, { once: true });
    },
    [bookId, ensureConnection, requesting],
  );

  return { turns, requesting, connected, errorText, send };
}
