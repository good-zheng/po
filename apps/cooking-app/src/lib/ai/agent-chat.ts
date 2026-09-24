import type { ChatInFrame, ChatWSFrame, RecipeBrief } from '@po/types';
import { Platform } from 'react-native';

/** 固定端点：不带 /api 前缀，nginx 与测试注入都按此路径挂载 */
const CHAT_PATH = '/ws/chat';
/** chat 服务独立监听 5090，与 Spring Boot 的 8080 分开 */
const CHAT_PORT = '5090';
const DEFAULT_API_URL = 'http://localhost:8080/api';
const CONNECT_TIMEOUT_MS = 8_000;
const RUN_TIMEOUT_MS = 90_000;
const PING_INTERVAL_MS = 30_000;
const FALLBACK_ERROR = '聊天服务暂时用不了。';

/** 只有这两个工具的结果能带出菜谱卡片，list_categories 只给分类名 */
const RECIPE_TOOLS = new Set(['search_recipes', 'get_recipe_detail']);

export type AgentStreamOptions = {
  /** 打字机增量：回调参数是本次回复截至目前累计的完整文本 */
  onText?: (text: string) => void;
  /** 工具结果里解析到的菜谱卡片（按 id 去重，可能分多次回调） */
  onRecipes?: (recipes: RecipeBrief[]) => void;
  /** 离开页面或清空对话时中断本轮，否则连接要挂到超时才释放 */
  signal?: AbortSignal;
};

export type AgentStreamResult = {
  /** 本轮是否拿到可见回复；false 表示调用方该走本地规则兜底 */
  answered: boolean;
  /** 失败原因：连不上 / 超时 / 服务端 error 帧 */
  error?: string;
};

/** 会话 id：服务端映射为 LangGraph thread_id，多轮记忆靠它跨轮保留 */
let conversationId: string | undefined;

/** 清空对话时一并重置，否则新一轮会带着旧上下文继续聊 */
export function resetAgentConversation() {
  conversationId = undefined;
}

/**
 * 聊天 WS 地址：优先 EXPO_PUBLIC_CHAT_URL 覆盖，否则按运行目标推导。
 *
 * 生产 web 与后端同源（网关转发 /ws/chat）；开发期 Metro 只代理 HTTP /api、
 * 不处理 WS upgrade，所以按 EXPO_PUBLIC_API_URL 的主机换到 5090 端口直连。
 */
export function resolveChatUrl(): string {
  const override = process.env.EXPO_PUBLIC_CHAT_URL?.trim();
  if (override) {
    return override;
  }

  if (Platform.OS === 'web' && !__DEV__) {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws';

    return `${scheme}://${window.location.host}${CHAT_PATH}`;
  }

  const apiUrl = process.env.EXPO_PUBLIC_API_URL ?? DEFAULT_API_URL;
  const host = apiUrl
    .replace(/^[a-z][a-z0-9+.-]*:\/\//i, '')
    .replace(/\/.*$/, '')
    .replace(/:\d+$/, '');

  return `${/^https:/i.test(apiUrl) ? 'wss' : 'ws'}://${host}:${CHAT_PORT}${CHAT_PATH}`;
}

/**
 * 跑一轮对话：连一次 WS、发一条 message 帧、把 token 与工具结果流式回吐，
 * 收到 done 帧即结束（连接用完即关，不做长连接复用）。
 *
 * 任何失败都不抛异常：回答「本轮有没有拿到回复」，由调用方决定是否降级到
 * 本地规则（见 @/lib/ai/chat），因此断网时聊天框仍可用。
 */
export function streamAgentReply(
  message: string,
  options: AgentStreamOptions = {},
): Promise<AgentStreamResult> {
  const recipes = new Map<number, RecipeBrief>();
  let socket: WebSocket | undefined;
  let connectTimer: ReturnType<typeof setTimeout> | undefined;
  let runTimer: ReturnType<typeof setTimeout> | undefined;
  let heartbeat: ReturnType<typeof setInterval> | undefined;
  let text = '';
  let error: string | undefined;

  return new Promise<AgentStreamResult>((resolve) => {
    let settled = false;

    function abort() {
      settle();
    }

    const settle = () => {
      if (settled) {
        return;
      }
      settled = true;
      clearTimeout(connectTimer);
      clearTimeout(runTimer);
      clearInterval(heartbeat);
      options.signal?.removeEventListener('abort', abort);
      if (socket) {
        // 先摘掉回调再关闭：主动 close 也会触发 onclose，否则会二次收尾
        socket.onopen = null;
        socket.onmessage = null;
        socket.onerror = null;
        socket.onclose = null;
        socket.close();
      }
      resolve({
        answered: text.length > 0 || recipes.size > 0,
        ...(error === undefined ? {} : { error }),
      });
    };

    if (options.signal?.aborted) {
      resolve({ answered: false });
      return;
    }
    options.signal?.addEventListener('abort', abort);

    const onFrame = (frame: ChatWSFrame) => {
      if (frame.type === 'token') {
        text += frame.content ?? '';
        options.onText?.(text);
        return;
      }

      if (frame.type === 'tool_call_result') {
        const name = frame.payload?.name;
        if (typeof name !== 'string' || !RECIPE_TOOLS.has(name)) {
          return;
        }
        const found = recipesFromResult(frame.content);
        if (found.length === 0) {
          return;
        }
        for (const recipe of found) {
          recipes.set(recipe.id, recipe);
        }
        options.onRecipes?.([...recipes.values()]);
        return;
      }

      if (frame.type === 'run_started') {
        // 首轮的 thread_id 由服务端生成，存下来在下一轮回传才能续上记忆
        const threadId = frame.payload?.thread_id;
        if (typeof threadId === 'string' && threadId) {
          conversationId = threadId;
        }
        return;
      }

      if (frame.type === 'error') {
        error = frame.content?.trim() || FALLBACK_ERROR;
        settle();
        return;
      }

      if (frame.type === 'done') {
        settle();
        return;
      }

      // thinking / plan / step / tool_call_* / interrupt 目前不参与渲染：
      // interrupt 需等服务端 done 收尾后再发 resume，待接入工具审批流时再补确认 UI。
    };

    try {
      socket = new WebSocket(resolveChatUrl());
    } catch {
      error = FALLBACK_ERROR;
      settle();
      return;
    }

    connectTimer = setTimeout(() => {
      error = '连接聊天服务超时，请确认 chat 服务已启动。';
      settle();
    }, CONNECT_TIMEOUT_MS);

    socket.onopen = () => {
      clearTimeout(connectTimer);
      runTimer = setTimeout(() => {
        error = '等回复等太久了，先按本轮结束处理。';
        settle();
      }, RUN_TIMEOUT_MS);
      heartbeat = setInterval(() => {
        socket?.send(JSON.stringify({ type: 'ping' } satisfies ChatInFrame));
      }, PING_INTERVAL_MS);

      const outbound: ChatInFrame = { content: message, type: 'message' };
      if (conversationId) {
        outbound.conversation_id = conversationId;
      }
      socket?.send(JSON.stringify(outbound));
    };

    socket.onmessage = (event) => {
      const frame = parseFrame(event.data);
      if (frame) {
        onFrame(frame);
      }
    };

    socket.onerror = () => {
      error = '连不上聊天服务，请确认 chat 服务已启动。';
      settle();
    };

    // 服务端在 done 之前断开（进程退出、网关超时）：按失败收尾，
    // 已流出的文本由 answered 决定是否保留。
    socket.onclose = () => {
      error ??= FALLBACK_ERROR;
      settle();
    };
  });
}

function parseFrame(data: unknown): ChatWSFrame | undefined {
  if (typeof data !== 'string') {
    return undefined;
  }

  try {
    const frame = JSON.parse(data) as Partial<ChatWSFrame>;

    return typeof frame?.type === 'string' ? (frame as ChatWSFrame) : undefined;
  } catch {
    return undefined;
  }
}

/** 工具结果 content 是 JSON 字符串；解析失败或结构不符当「没有卡片」，不影响文本回复 */
function recipesFromResult(content?: string): RecipeBrief[] {
  if (!content) {
    return [];
  }

  let payload: unknown;
  try {
    payload = JSON.parse(content);
  } catch {
    return [];
  }
  if (!isRecord(payload)) {
    return [];
  }

  const candidates = [
    ...(Array.isArray(payload.recipes) ? payload.recipes : []),
    ...(isRecord(payload.recipe) ? [payload.recipe] : []),
  ];

  return candidates.filter(isRecipeBrief);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** 渲染卡片只依赖 id 与 title，缺这两个字段的结果直接丢弃 */
function isRecipeBrief(value: unknown): value is RecipeBrief {
  return (
    isRecord(value) &&
    typeof value.id === 'number' &&
    typeof value.title === 'string'
  );
}
