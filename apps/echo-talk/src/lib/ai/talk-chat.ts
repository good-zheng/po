import Taro from '@tarojs/taro';

import { CHAT_WS_URL } from '@/config/env';

/**
 * 与 chat 服务（FastAPI）的 /ws/chat 通信：把「对方的一句话」交给 talk Agent。
 *
 * 复用既有帧协议，只多带两个向后兼容的字段：
 * - ``agent: "talk"`` —— 显式指定插槽，跳过意图路由（客户端已经知道要哪个 Agent）；
 * - ``context`` —— 场景 / 说话人 / utteranceId，其中 utteranceId 只用于结果回写定位，
 *   不会拼进提示词（服务端会把保留键剔除）。
 *
 * 返回值是模型输出的完整文本（纯 JSON），由调用方解析成卡片数据。
 */

type OutFrame = {
  type: 'message' | 'ping';
  content: string;
  conversation_id: string;
  agent?: string;
  context?: Record<string, unknown>;
};

type InFrame = {
  type: string;
  content?: string;
  payload?: Record<string, unknown>;
};

export type AnalyzeParams = {
  /** 会话 threadId，多轮记忆的 key */
  conversationId: string;
  /** 对方刚说的话 */
  text: string;
  /** 话语 id：服务端据此把建议回写到正确的那条记录 */
  utteranceId: number;
  scene: string;
  speaker: string;
  /** 流式回调：Agent 还没出完时可用于展示「正在理解」 */
  onToken?: (partial: string) => void;
};

const TIMEOUT_MS = 30000;

export function analyzeUtterance(params: AnalyzeParams): Promise<string> {
  const { conversationId, text, utteranceId, scene, speaker, onToken } = params;

  return new Promise<string>((resolve, reject) => {
    let settled = false;
    let chunks = '';
    let task: Taro.SocketTask | null = null;

    const finish = (error: Error | null, value = '') => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      try {
        task?.close({ code: 1000, reason: 'done' });
      } catch {
        // 已断开时忽略
      }
      if (error) reject(error);
      else resolve(value);
    };

    const timer = setTimeout(() => finish(new Error('分析超时，请稍后重试')), TIMEOUT_MS);

    // Taro 4 破坏性变更：connectSocket 返回 Promise<SocketTask>，先 await 拿到 task 再注册回调，
    // 直接拿返回值当 SocketTask 用会报 "task.onOpen is not a function"。
    Taro.connectSocket({ url: CHAT_WS_URL })
      .then((t) => {
        task = t;
        t.onOpen(() => {
          const frame: OutFrame = {
            type: 'message',
            content: text,
            conversation_id: conversationId,
            agent: 'talk',
            context: { utteranceId, scene, speaker },
          };
          t.send({ data: JSON.stringify(frame) });
        });

        t.onMessage((res) => {
          let frame: InFrame;
          try {
            frame = JSON.parse(String(res.data)) as InFrame;
          } catch {
            return;
          }
          if (frame.type === 'token') {
            chunks += frame.content ?? '';
            onToken?.(chunks);
            return;
          }
          if (frame.type === 'done') {
            finish(null, chunks);
            return;
          }
          if (frame.type === 'error') {
            finish(new Error(frame.content || '分析失败'));
          }
        });

        t.onError((err) => finish(new Error(err.errMsg || '无法连接分析服务')));
        t.onClose(() => finish(new Error('分析服务连接已关闭')));
      })
      .catch((err) => finish(err instanceof Error ? err : new Error('无法连接分析服务')));
  });
}

/** 把 Agent 输出解析成卡片数据；解析失败返回 null（调用方降级为纯文本） */
export function parseAnalysis<T>(raw: string): T | null {
  if (!raw) return null;
  try {
    const start = raw.indexOf('{');
    const end = raw.lastIndexOf('}');
    if (start < 0 || end <= start) return null;
    return JSON.parse(raw.slice(start, end + 1)) as T;
  } catch {
    return null;
  }
}
