import { Text, View } from '@tarojs/components';
import Taro, { usePullDownRefresh, useReachBottom } from '@tarojs/taro';
import { useCallback, useEffect, useRef, useState } from 'react';

import { sceneLabel } from '@/config/env';
import { talkApi, type SessionDetail, type SessionSummary } from '@/lib/api/talk';
import { useAuth } from '@/lib/auth/auth-context';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { GuestPlaceholder } from '@/lib/auth/guest-placeholder';
import './index.scss';

const CURRENT_SESSION_KEY = 'echo.currentSessionId';
const PAGE_SIZE = 20;

function formatDuration(ms: number): string {
  const total = Math.round((ms || 0) / 1000);
  if (total < 60) return `${total} 秒`;
  const minutes = Math.floor(total / 60);
  if (minutes < 60) return `${minutes} 分`;
  return `${Math.floor(minutes / 60)} 小时 ${minutes % 60} 分`;
}

/** 后端给的是 LocalDateTime 的 ISO 串，列表里只取「月-日 时:分」 */
function formatWhen(value?: string): string {
  const text = String(value ?? '').replace('T', ' ');
  return text.length >= 16 ? text.slice(5, 16) : text;
}

/** 「结束并保存」之后的落点：回看、继续、删除已保存的对话 */
export default function HistoryPage() {
  const { status } = useAuth();
  if (status === 'unauthenticated') {
    return <GuestPlaceholder title='会话记录' hint='登录后查看已保存的对话' />;
  }
  return (
    <AuthGuard>
      <HistoryView />
    </AuthGuard>
  );
}

function HistoryView() {
  const [items, setItems] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [openId, setOpenId] = useState(0);
  const [details, setDetails] = useState<Record<number, SessionDetail>>({});
  // 触底翻页与下拉刷新可能几乎同时触发，用 ref 而不是 state 拦：state 更新是异步的，拦不住
  const busyRef = useRef(false);
  const finishedRef = useRef(false);
  const pageRef = useRef(0);

  const load = useCallback(async (next: number, reset: boolean) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setLoading(true);
    try {
      let page = next;
      let replace = reset;
      // 每场录音都会先建会话，没说过话的（turnCount 0）不该出现在记录里。
      // 滤完可能整页皆空：列表不增长就不会再触发触底，所以这里自己往后翻，直到有内容或到底。
      for (;;) {
        const res = await talkApi.listSessions({ page, size: PAGE_SIZE });
        const fresh = res.content.filter((item: SessionSummary) => item.turnCount > 0);
        setItems((prev) => (replace ? fresh : prev.concat(fresh)));
        pageRef.current = page;
        finishedRef.current = page + 1 >= res.totalPages;
        if (fresh.length > 0 || res.content.length < PAGE_SIZE || finishedRef.current) break;
        page += 1;
        replace = false;
      }
    } catch (error) {
      Taro.showToast({ title: error instanceof Error ? error.message : '记录载入失败', icon: 'none' });
    } finally {
      busyRef.current = false;
      setLoading(false);
      Taro.stopPullDownRefresh();
    }
  }, []);

  useEffect(() => {
    void load(0, true);
  }, [load]);

  usePullDownRefresh(() => void load(0, true));
  useReachBottom(() => {
    if (finishedRef.current) return;
    void load(pageRef.current + 1, false);
  });

  const toggle = (id: number) => {
    if (openId === id) {
      setOpenId(0);
      return;
    }
    setOpenId(id);
    if (details[id]) return;
    void talkApi
      .getSession(id)
      .then((detail) => setDetails((prev) => ({ ...prev, [id]: detail })))
      .catch(() => Taro.showToast({ title: '对话内容载入失败', icon: 'none' }));
  };

  /** 继续这场：只改 storage 里的会话号，由会话页 useDidShow 按号重载 */
  const resume = (id: number) => {
    Taro.setStorageSync(CURRENT_SESSION_KEY, id);
    Taro.switchTab({ url: '/pages/session/index' });
  };

  const remove = (item: SessionSummary) => {
    Taro.showModal({
      title: '删除这场对话',
      content: '转写文字与 AI 建议一并删除，不可恢复',
      confirmText: '删除',
      confirmColor: '#dc2626',
      success: (res) => {
        if (!res.confirm) return;
        void talkApi
          .deleteSession(item.id)
          .then(() => {
            setItems((prev) => prev.filter((x) => x.id !== item.id));
            if (Number(Taro.getStorageSync(CURRENT_SESSION_KEY) || 0) === item.id) {
              Taro.removeStorageSync(CURRENT_SESSION_KEY);
            }
            Taro.showToast({ title: '已删除', icon: 'success' });
          })
          .catch(() => Taro.showToast({ title: '删除失败', icon: 'none' }));
      },
    });
  };

  const openDetail = openId ? details[openId] : undefined;

  return (
    <View className='history'>
      {items.length === 0 && !loading ? <View className='h-empty'>还没有保存的对话</View> : null}

      {items.map((item) => (
        <View key={item.id} className='h-item'>
          <View className='h-item__head' onClick={() => toggle(item.id)}>
            <View className='h-item__title'>{item.title || `${sceneLabel(item.scene)}对话`}</View>
            <Text className={`h-item__status ${item.status === 'recording' ? 'is-live' : ''}`}>
              {item.status === 'recording' ? '进行中' : '已结束'}
            </Text>
          </View>

          <View className='h-item__preview'>{item.preview || '（没有对方的话）'}</View>

          <View className='h-item__meta'>
            <Text className='h-item__time'>{formatWhen(item.updatedAt)}</Text>
            <Text className='h-item__dot'>·</Text>
            <Text className='h-item__num'>{item.turnCount} 轮</Text>
            <Text className='h-item__dot'>·</Text>
            <Text className='h-item__num'>{formatDuration(item.durationMs)}</Text>
          </View>

          <View className='h-item__acts'>
            <Text className='h-act' onClick={() => toggle(item.id)}>
              {openId === item.id ? '收起' : '看全文'}
            </Text>
            {item.status === 'recording' ? (
              <Text className='h-act h-act--primary' onClick={() => resume(item.id)}>
                继续这场
              </Text>
            ) : null}
            <Text className='h-act h-act--danger' onClick={() => remove(item)}>
              删除
            </Text>
          </View>

          {openId === item.id ? (
            <View className='h-body'>
              {openDetail ? (
                openDetail.utterances.map((utterance) => (
                  <View
                    key={utterance.id}
                    className={`h-turn ${utterance.speaker === 'me' ? 'h-turn--me' : ''}`}
                  >
                    <Text className='h-turn__who'>{utterance.speaker === 'me' ? '我' : '对方'}</Text>
                    <View className='h-turn__text'>{utterance.content}</View>
                    {utterance.suggestion?.intent ? (
                      <Text className='h-turn__note'>真正想要的：{utterance.suggestion.intent}</Text>
                    ) : null}
                    {utterance.suggestion?.suggestions?.[0]?.text ? (
                      <Text className='h-turn__note'>可以这样回：{utterance.suggestion.suggestions[0].text}</Text>
                    ) : null}
                  </View>
                ))
              ) : (
                <View className='h-loading'>正在载入…</View>
              )}
            </View>
          ) : null}
        </View>
      ))}

      <Text className='h-footnote'>
        转写文字与 AI 建议保存在服务端{'\n'}原始音频不落盘，仅用于实时转写
      </Text>
    </View>
  );
}
