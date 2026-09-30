import { useCallback, useEffect, useRef, useState } from 'react';
import { View, Text, Input, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import type { RecipeBrief } from '@po/types';
import { useAuth } from '@/lib/auth/auth-context';
import { currentPageUrl, saveReturnTo } from '@/lib/auth/return-path';
import { askAssistant } from '@/lib/ai/chat';
import { useCooking } from '@/lib/cooking/cooking-context';
import { CHAT_WS_URL } from '@/config/env';
import './chat.scss';

type ChatMessage = {
  id: number;
  role: 'user' | 'assistant';
  text: string;
  recipes?: RecipeBrief[];
  suggestions?: string[];
};

const SUGGESTIONS = ['今晚吃什么', '推荐几道快手菜', '剁椒鱼头怎么做'];
const CONNECT_TIMEOUT = 8000;
const RUN_TIMEOUT = 90000;
const PING_INTERVAL = 30000;

let messageSeq = 0;
function nextId() {
  return ++messageSeq;
}

function welcomeMessage(): ChatMessage {
  return {
    id: nextId(),
    role: 'assistant',
    suggestions: SUGGESTIONS,
    text: '我是你的做菜助手。报个菜名，我给你讲清用料和步骤！',
  };
}

let conversationId: string | null = null;

export function resetConversation() {
  conversationId = null;
}

// 游客可完整浏览聊天界面；只有在真正发消息时才要求登录（跳转由用户触发，不自动重定向）
export default function AIChat() {
  return <ChatView />;
}

function ChatView() {
  const { status } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>(() => [welcomeMessage()]);
  const [input, setInput] = useState('');
  const [pending, setPending] = useState(false);
  const socketRef = useRef<Taro.SocketTask | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { cancelCooking, clearNote, note, session } = useCooking();

  useEffect(() => {
    if (!note) {
      return;
    }

    clearNote();
    const minutes = Math.max(1, Math.round((Date.now() - note.startedAt) / 60_000));
    setMessages((prev) => [
      ...prev,
      {
        id: nextId(),
        role: 'assistant',
        suggestions: ['今晚吃什么', '推荐几道快手菜'],
        text: `「${note.title}」做好了，一共 ${note.stepCount} 步，用时约 ${minutes} 分钟，趁热吃。还想再做一道吗？`,
      },
    ]);
  }, [clearNote, note]);

  useEffect(() => {
    return () => {
      cleanup();
    };
  }, []);

  const cleanup = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (pingRef.current) {
      clearInterval(pingRef.current);
      pingRef.current = null;
    }
    if (socketRef.current) {
      try {
        socketRef.current.close({});
      } catch {
        // ignore
      }
      socketRef.current = null;
    }
  };

  const patchMessage = useCallback((id: number, patch: (msg: ChatMessage) => ChatMessage) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? patch(m) : m)));
  }, []);

  const send = useCallback(
    (raw: string) => {
      const text = raw.trim();
      if (!text || pending) return;

      if (status !== 'authenticated') {
        saveReturnTo(currentPageUrl());
        Taro.navigateTo({ url: '/pages/login/index' });
        return;
      }

      setInput('');
      const replyId = nextId();
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role: 'user', text },
        { id: replyId, role: 'assistant', text: '', suggestions: SUGGESTIONS },
      ]);
      setPending(true);

      cleanup();

      let streamed = false;
      let fellBack = false;

      // 大模型这条链路一个字都没给（服务没起、离线、超时）：退回本地菜谱规则，
      // 保证没有模型可用时聊天框依然能查菜、给推荐。
      const finish = () => {
        cleanup();
        setPending(false);
        if (streamed || fellBack) return;
        fellBack = true;
        void askAssistant(text).then((reply) => {
          patchMessage(replyId, (m) => ({
            ...m,
            recipes: reply.recipes?.length
              ? reply.recipes.map((r) => ({ id: r.id, title: r.title }))
              : m.recipes,
            suggestions: reply.suggestions ?? SUGGESTIONS,
            text: reply.text,
          }));
        });
      };

      const connectTimer = setTimeout(finish, CONNECT_TIMEOUT);

      Taro.connectSocket({
        url: CHAT_WS_URL,
      })
        .then((socket) => {
          socketRef.current = socket;

          socket.onOpen(() => {
            clearTimeout(connectTimer);

            timerRef.current = setTimeout(finish, RUN_TIMEOUT);

            pingRef.current = setInterval(() => {
              try {
                socket.send({ data: JSON.stringify({ type: 'ping', content: 'ping' }) });
              } catch {
                // ignore
              }
            }, PING_INTERVAL);

            const frame: Record<string, unknown> = {
              type: 'message',
              content: text,
            };
            if (conversationId) {
              frame.conversation_id = conversationId;
            }
            socket.send({ data: JSON.stringify(frame) });
          });

          socket.onMessage((res) => {
            try {
              const frame = JSON.parse(res.data as string) as {
                type: string;
                content?: string;
                payload?: Record<string, unknown>;
              };

              switch (frame.type) {
                case 'run_started':
                  if (frame.payload?.thread_id) {
                    conversationId = frame.payload.thread_id as string;
                  }
                  break;

                case 'token':
                  if (frame.content) {
                    streamed = true;
                    patchMessage(replyId, (m) => ({
                      ...m,
                      text: m.text + frame.content,
                    }));
                  }
                  break;

                case 'tool_call_result':
                  if (
                    frame.payload?.name === 'search_recipes' ||
                    frame.payload?.name === 'get_recipe_detail'
                  ) {
                    try {
                      const data = JSON.parse(frame.content || '[]');
                      const items: Array<{ id: number; title: string }> = Array.isArray(data)
                        ? data
                        : data.recipes
                          ? data.recipes
                          : data.recipe
                            ? [data.recipe]
                            : [];
                      if (items.length > 0) {
                        streamed = true;
                        const recipes: RecipeBrief[] = items.map((r) => ({
                          id: r.id,
                          title: r.title,
                        }));
                        patchMessage(replyId, (m) => {
                          const existing = m.recipes ?? [];
                          const seen = new Set(existing.map((r) => r.id));
                          const deduped = recipes.filter((r) => !seen.has(r.id));
                          return { ...m, recipes: [...existing, ...deduped] };
                        });
                      }
                    } catch {
                      // ignore parse errors
                    }
                  }
                  break;

                case 'error':
                  streamed = true;
                  patchMessage(replyId, (m) => ({
                    ...m,
                    text: `${m.text}\n\n${frame.content || '出错了'}`,
                  }));
                  break;

                case 'done':
                  finish();
                  break;
              }
            } catch {
              // ignore non-JSON frames
            }
          });

          socket.onError(finish);

          socket.onClose(finish);
        })
        .catch(() => {
          clearTimeout(connectTimer);
          finish();
        });
    },
    [patchMessage, pending, status],
  );

  const resetChat = () => {
    cleanup();
    resetConversation();
    setMessages([welcomeMessage()]);
    setPending(false);
    setInput('');
  };

  const scrollToMessage = messages.length > 0 ? messages[messages.length - 1].id : 0;
  const lastAssistantId = [...messages].reverse().find((m) => m.role === 'assistant')?.id;

  return (
    <View className="chat">
      <View className="chat-header">
        <View className="header-left">
          <View className="avatar-icon">
            <Text className="avatar-text">AI</Text>
          </View>
          <View>
            <Text className="header-title">AI 指导</Text>
            <Text className="header-sub">做菜的事都可以问我</Text>
          </View>
        </View>
        <View className="reset-btn" onClick={resetChat}>
          <Text className="reset-text">清空</Text>
        </View>
      </View>

      <ScrollView
        className="message-list"
        scrollY
        scrollIntoView={`msg-${scrollToMessage}`}
        scrollWithAnimation
      >
        {messages.map((msg) => {
          const isEmpty = !msg.text && !msg.recipes?.length;
          const isLastAssistant = msg.role === 'assistant' && msg.id === lastAssistantId;

          if (msg.role === 'assistant' && isEmpty) {
            return (
              <View key={msg.id} id={`msg-${msg.id}`} className="message assistant">
                <View className="msg-avatar assistant-avatar">
                  <Text className="msg-avatar-text">AI</Text>
                </View>
                <View className="bubble assistant-bubble typing-bubble">
                  <Text className="typing-text">正在翻菜谱…</Text>
                </View>
              </View>
            );
          }

          return (
            <View key={msg.id} id={`msg-${msg.id}`}>
              <View className={`message ${msg.role}`}>
                {msg.role === 'assistant' ? (
                  <View className="msg-avatar assistant-avatar">
                    <Text className="msg-avatar-text">AI</Text>
                  </View>
                ) : null}
                <View className={`bubble ${msg.role}-bubble`}>
                  <Text className="bubble-text">{msg.text}</Text>
                </View>
              </View>

              {msg.recipes && msg.recipes.length > 0 ? (
                <View className="recipe-cards">
                  {msg.recipes.map((r) => (
                    <View
                      key={r.id}
                      className="recipe-card"
                      onClick={() =>
                        Taro.navigateTo({ url: `/pages/recipe/detail?id=${r.id}` })
                      }
                    >
                      <Text className="card-title">{r.title}</Text>
                      <Text className="card-action">查看菜谱 →</Text>
                    </View>
                  ))}
                </View>
              ) : null}

              {msg.suggestions && msg.suggestions.length > 0 && msg.role === 'assistant' && !pending && isLastAssistant ? (
                <View className="suggestions">
                  {msg.suggestions.map((s) => (
                    <View key={s} className="suggestion-chip" onClick={() => send(s)}>
                      <Text className="chip-text">{s}</Text>
                    </View>
                  ))}
                </View>
              ) : null}
            </View>
          );
        })}
      </ScrollView>

      {session ? (
        <View className="cooking-banner">
          <View
            className="banner-main"
            onClick={() =>
              Taro.navigateTo({ url: `/pages/cook/index?id=${session.recipeId}` })
            }
          >
            <View className="banner-icon">
              <Text className="banner-icon-text">{'\u{1F525}'}</Text>
            </View>
            <View className="banner-text-wrap">
              <Text className="banner-title">正在做「{session.title}」</Text>
              <Text className="banner-sub">
                第 {session.stepIndex + 1}/{session.stepCount} 步 · 点这里继续
              </Text>
            </View>
            <Text className="banner-arrow">{'>'}</Text>
          </View>
          <View
            className="banner-close"
            onClick={() => {
              cancelCooking();
            }}
          >
            <Text className="banner-close-text">{'✕'}</Text>
          </View>
        </View>
      ) : null}

      {status !== 'authenticated' ? (
        <View
          className="guest-hint"
          onClick={() => {
            saveReturnTo(currentPageUrl());
            Taro.navigateTo({ url: '/pages/login/index' });
          }}
        >
          <Text className="guest-hint-text">登录后即可发送消息，点我去登录</Text>
        </View>
      ) : null}

      <View className="input-bar">
        <Input
          className="input"
          placeholder="问问今天做什么菜"
          value={input}
          onInput={(e) => setInput(e.detail.value)}
          onConfirm={() => send(input)}
          disabled={pending}
        />
        <View
          className={`send-btn ${input.trim() && !pending ? 'send-btn-active' : ''}`}
          onClick={() => send(input)}
        >
          <Text className="send-text">发送</Text>
        </View>
      </View>
    </View>
  );
}
