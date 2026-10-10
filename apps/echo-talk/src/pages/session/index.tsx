import { ScrollView, Text, Textarea, View } from '@tarojs/components';
import Taro, { useDidHide, useDidShow, useUnload } from '@tarojs/taro';
import { memo, useCallback, useEffect, useRef, useState } from 'react';

import { sceneLabel } from '@/config/env';
import { analyzeUtterance, parseAnalysis } from '@/lib/ai/talk-chat';
import { talkApi, type SessionDetail, type SuggestionView } from '@/lib/api/talk';
import { AsrClient, toBase64, type AsrDownEvent } from '@/lib/asr/asr-client';
import { PcmRecorder } from '@/lib/asr/recorder';
import { useAuth } from '@/lib/auth/auth-context';
import { currentPageUrl, saveReturnTo } from '@/lib/auth/return-path';
import { getSessionToken } from '@/lib/auth/session';
import { speak, stop as stopTts } from '@/lib/tts';
import './index.scss';

const CURRENT_SESSION_KEY = 'echo.currentSessionId';
const SCENE_KEY = 'echo.scene';

/**
 * 松手后保留连接、等讯飞定稿的最长时间。
 *
 * 这句是先发出去的（松手即发），晚到的 final 只用来纠正它，所以这段时间不是「卡住等定稿」
 * 而是「留着连接等修正」。网关收到 stop 会等讯飞收尾确认（它自己最多等 2 秒）再回 segment_end，
 * 实测 final 距松手约 100ms，因此这个上限只在 segment_end 死活不来时兜底：到点就用已发的文本收尾。
 */
const LATE_FINAL_GRACE_MS = 3000;

type Turn = {
  key: string;
  id?: number;
  speaker: 'other' | 'me';
  source: 'voice' | 'text';
  text: string;
  analyzing?: boolean;
  suggestion?: SuggestionView | null;
};

type AnalysisPayload = {
  intent?: string;
  subtext?: string;
  emotion?: string;
  risk?: string;
  suggestions?: { style: string; text: string; why: string }[];
  followups?: string[];
};

/**
 * 松手时已经发出去的那一句。
 *
 * 讯飞的定稿（wpgs 收敛后的整句）会在它之后几百毫秒才到，用这个定位回写同一条话语，
 * 并作为分析的输入——落库文本以定稿为准，AI 不会拿着半成品去猜弦外之音。
 */
type SentTurn = {
  key: string;
  utteranceId: number;
  text: string;
  speaker: 'other' | 'me';
};

function formatClock(seconds: number): string {
  const mm = String(Math.floor(seconds / 60)).padStart(2, '0');
  const ss = String(seconds % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

/**
 * 一条话语。
 *
 * 单独拆出来是为了 memo：按住说话期间，输入框每几百毫秒就被讯飞的中间结果改写一次，
 * 整页跟着重渲染，会话攒到几十条时每一帧都在重排所有气泡和「可以这样回」卡片。
 * 某一行的数据只在「这句定稿」或「分析回来」时才换引用，其余行被这里挡住。
 */
const TurnRow = memo(function TurnRow({ turn, onPlay }: { turn: Turn; onPlay: (text: string) => void }) {
  return (
    <View className={`turn ${turn.speaker === 'me' ? 'turn--me' : ''}`}>
      <Text className='turn__who'>{turn.speaker === 'me' ? '我' : '对方'}</Text>
      <View className='bubble'>{turn.text}</View>
      {turn.analyzing ? <View className='thinking'>正在理解这句话…</View> : null}
      {turn.suggestion ? (
        <View className='insight'>
          {turn.suggestion.intent ? (
            <View className='kv'>
              <Text className='kv__k'>真正想要</Text>
              <Text className='kv__v'>{turn.suggestion.intent}</Text>
            </View>
          ) : null}
          {turn.suggestion.subtext ? (
            <View className='kv'>
              <Text className='kv__k'>潜台词</Text>
              <Text className='kv__v'>{turn.suggestion.subtext}</Text>
            </View>
          ) : null}
          {turn.suggestion.emotion ? (
            <View className='kv'>
              <Text className='kv__k'>情绪</Text>
              <Text className='kv__v'>{turn.suggestion.emotion}</Text>
            </View>
          ) : null}
          {turn.suggestion.risk ? (
            <View className='kv'>
              <Text className='kv__k'>风险</Text>
              <Text className='kv__v kv__v--risk'>{turn.suggestion.risk}</Text>
            </View>
          ) : null}
        </View>
      ) : null}
      {turn.suggestion?.suggestions?.length ? (
        <View className='sugg'>
          <View className='sugg__hd'>可以这样回</View>
          {turn.suggestion.suggestions.map((item, index) => (
            <View key={`${item.style}-${index}`} className='card'>
              <Text className={`tag tag--${index}`}>{item.style}</Text>
              <View className='card__body'>
                <Text className='card__text'>{item.text}</Text>
                {item.why ? <Text className='card__why'>{item.why}</Text> : null}
              </View>
              <View className='card__play' onClick={() => onPlay(item.text)}>
                朗读
              </View>
            </View>
          ))}
        </View>
      ) : null}
    </View>
  );
});

export default function SessionPage() {
  const { status } = useAuth();
  const [session, setSession] = useState<SessionDetail | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [speaker, setSpeaker] = useState<'other' | 'me'>('other');
  const [recording, setRecording] = useState(false);
  const [pausing, setPausing] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [scene, setScene] = useState<string>(Taro.getStorageSync(SCENE_KEY) || 'general');
  const [input, setInput] = useState('');
  const [asrError, setAsrError] = useState('');
  /** 对话流的滚动锚点：在底部两个探针之间交替，值一变 ScrollView 才会重新滚 */
  const [anchor, setAnchor] = useState('');

  // 回调里要读到最新值（ASR 回调发生在录音线程回抛的时刻），故用 ref 镜像
  const sessionRef = useRef<SessionDetail | null>(null);
  const speakerRef = useRef<'other' | 'me'>('other');
  const sceneRef = useRef(scene);
  const recorderRef = useRef<PcmRecorder | null>(null);
  const asrRef = useRef<AsrClient | null>(null);
  const inputRef = useRef('');
  /** 输入框里「正在说、还没定稿」的那一句；partial 是整句替换（讯飞 wpgs 语义），不是追加 */
  const asrTailRef = useRef('');
  // 本轮录音有没有真的收到过转写：一句都没收到时要明确告诉用户，别让「松手后框里空着」变成哑谜
  const asrDeliveredRef = useRef(false);
  // 上行帧计数 + 是否收到 ready：松手后「没识别到语音」要能区分是采集没出帧，还是网关/讯飞没出字
  const frameCountRef = useRef(0);
  const readyRef = useRef(false);
  const fromVoiceRef = useRef(false);
  // 服务端已宣告这一段结束：再等 final 也等不来了
  const segmentEndedRef = useRef(false);
  /** 在途的建会话请求：登录态就绪与页面显示可能同时触发 */
  const pendingRef = useRef<Promise<void> | null>(null);
  /** 手指是否还按在麦克风上：开录是异步的，建连期间可能已经松手 */
  const holdRef = useRef(false);
  /**
   * 麦克风授权是否已在手。false 时第一次按下只用来弹授权框（见 startRecording），
   * 免得授权点完「允许」才发现手指早抬起来了，像按坏了一样。
   */
  const recordReadyRef = useRef(false);
  /** 在途的开录流程：松手要等它走完，否则停的是还没建好的连接，刚说的半句被丢 */
  const holdTaskRef = useRef<Promise<void> | null>(null);
  /** 按住开录前输入框里已有的草稿：松手只发送这一次说出的部分，草稿留在框里 */
  const draftBeforeRef = useRef('');
  /** 滚动锚点轮换计数：同一个 id 不会触发第二次滚动，所以两个底部探针轮流用 */
  const anchorSeqRef = useRef(0);
  /** 已发出、正等讯飞定稿来纠正的那一句 */
  const sentRef = useRef<SentTurn | null>(null);
  /** 松手之后、连接关掉之前：这期间来的转写只用于纠正那一条，不再回写输入框 */
  const settlingRef = useRef(false);
  /** 宽限期兜底计时：segment_end 不来也要收摊，否则连接和「收尾中」一起挂死 */
  const graceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  /** 松手后才到达的整句定稿 */
  const lateFinalRef = useRef('');
  /** 讯飞当前段号（ready/partial/final 都带）：松手时快照下来，用来排除跨段的定稿 */
  const segmentRef = useRef(1);
  const sentSegmentRef = useRef(1);

  const setInputValue = useCallback((value: string) => {
    inputRef.current = value;
    setInput(value);
  }, []);

  /** 把识别结果写进输入框：只动尾部那一句在说的话，前面的正文（含手改内容）保持不动 */
  const writeAsrText = useCallback(
    (text: string, committed: boolean) => {
      if (text) asrDeliveredRef.current = true;
      const box = inputRef.current;
      const base = box.slice(0, Math.max(0, box.length - asrTailRef.current.length));
      asrTailRef.current = committed ? '' : text;
      fromVoiceRef.current = true;
      setInputValue(base + text);
    },
    [setInputValue],
  );

  const applySession = useCallback((next: SessionDetail) => {
    sessionRef.current = next;
    setSession(next);
    Taro.setStorageSync(CURRENT_SESSION_KEY, next.id);
  }, []);

  /** 会话详情 → 界面：续用进行中的会话与从「会话记录」载入走同一条路 */
  const hydrate = useCallback(
    (detail: SessionDetail) => {
      applySession(detail);
      setTurns(
        detail.utterances.map((item) => ({
          key: String(item.id),
          id: item.id,
          speaker: item.speaker === 'me' ? 'me' : 'other',
          source: item.source === 'text' ? 'text' : 'voice',
          text: item.content,
          suggestion: item.suggestion ?? null,
        })),
      );
      setSpeaker('other');
      setElapsed(Math.round((detail.durationMs ?? 0) / 1000));
    },
    [applySession],
  );

  /** 游客点录音/发送时先去登录，来路记下；跳转只由用户点击触发，页面本身不自动跳 */
  const goLogin = useCallback(() => {
    saveReturnTo(currentPageUrl());
    Taro.navigateTo({ url: '/pages/login/index' });
  }, []);

  const ensureSession = useCallback(async () => {
    if (sessionRef.current) return;
    // 冷启动回填登录态与页面显示都会触发这里，在途请求必须合并，否则会建出两场会话
    if (pendingRef.current) {
      await pendingRef.current;
      return;
    }
    const task = (async () => {
      const cachedId = Number(Taro.getStorageSync(CURRENT_SESSION_KEY) || 0);
      if (cachedId) {
        try {
          const existing = await talkApi.getSession(cachedId);
          if (existing.status === 'recording') {
            // 续用未结束的会话：切 tab 回来、或从「会话记录」点「继续这场」都不该重开一场
            hydrate(existing);
            return;
          }
        } catch {
          // 会话已被删除或不属于当前用户：静默新建
        }
      }
      const created = await talkApi.createSession(sceneRef.current);
      applySession(created);
      setTurns([]);
    })();
    pendingRef.current = task;
    try {
      await task;
    } finally {
      pendingRef.current = null;
    }
  }, [applySession, hydrate]);

  const runAnalysis = useCallback(
    async (utteranceId: number, text: string, key: string) => {
      const current = sessionRef.current;
      if (!current) return;
      try {
        const raw = await analyzeUtterance({
          conversationId: current.threadId,
          text,
          utteranceId,
          scene: sceneRef.current,
          speaker: 'other',
        });
        const parsed = parseAnalysis<AnalysisPayload>(raw);
        const suggestion: SuggestionView | null = parsed
          ? {
              id: 0,
              utteranceId,
              intent: parsed.intent ?? '',
              subtext: parsed.subtext ?? '',
              emotion: parsed.emotion ?? '',
              risk: parsed.risk ?? '',
              suggestions: parsed.suggestions ?? [],
              followups: parsed.followups ?? [],
            }
          : null;
        setTurns((prev) => prev.map((t) => (t.key === key ? { ...t, analyzing: false, suggestion } : t)));
      } catch (error) {
        setTurns((prev) => prev.map((t) => (t.key === key ? { ...t, analyzing: false } : t)));
        Taro.showToast({ title: error instanceof Error ? error.message : '分析失败', icon: 'none' });
      }
    },
    [],
  );

  /**
   * 一句话落库、入列，并回传「刚发出去的这一句」供后续纠正定位。
   *
   * `analyze: false` 用于语音松手即发：此刻文本还是讯飞的中间结果，分析要等整句定稿回写之后再跑，
   * 否则会拿半成品猜一次弦外之音、再拿准确文本猜第二次（多烧一次模型，还给用户看一版错的）。
   */
  const commitUtterance = useCallback(
    async (
      text: string,
      source: 'voice' | 'text',
      who: 'other' | 'me',
      options?: { analyze?: boolean },
    ): Promise<SentTurn | null> => {
      const current = sessionRef.current;
      const content = text.trim();
      if (!current || !content) return null;
      const key = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
      try {
        const saved = await talkApi.addUtterance(current.id, {
          speaker: who,
          source,
          content,
        });
        setTurns((prev) => [
          ...prev,
          { key, id: saved.id, speaker: who, source, text: content, analyzing: who === 'other' },
        ]);
        if (who === 'other' && saved.id && options?.analyze !== false) {
          // 不等分析：落库入列后立刻恢复录音节奏，建议回来再填
          void runAnalysis(saved.id, content, key);
        }
        return saved.id ? { key, utteranceId: saved.id, text: content, speaker: who } : null;
      } catch (error) {
        Taro.showToast({ title: '保存失败', icon: 'none' });
        return null;
      }
    },
    [runAnalysis],
  );

  /** 收尾：没等到 final 也把当前这句「还在说」的文本转成正文，否则下一段的 partial 会把它覆盖掉 */
  const settleTail = useCallback(() => {
    asrTailRef.current = '';
  }, []);

  /**
   * 结束松手后的宽限期：收摊连接与计时，用已知最准确的文本回写刚发出的那句，然后才让它去分析。
   *
   * 三个入口都走这里——segment_end（讯飞确认收尾）、error、以及 LATE_FINAL_GRACE_MS 兜底计时。
   * 它必须能被安全地调用两次：addUtterance 的往返比 WS 帧慢，定稿可能在 sentRef 填上之前就到了，
   * 那一次只关掉连接，第二次（发送路径补调）才真正把纠正用上。
   */
  const endGrace = useCallback(
    async (corrected: string) => {
      if (graceTimerRef.current) {
        clearTimeout(graceTimerRef.current);
        graceTimerRef.current = null;
      }
      const client = asrRef.current;
      asrRef.current = null;
      client?.close();
      settlingRef.current = false;
      setPausing(false);

      const sent = sentRef.current;
      if (!sent) return;
      sentRef.current = null;
      const best = corrected.trim() || sent.text;
      if (best !== sent.text) {
        try {
          await talkApi.updateUtterance(sent.utteranceId, { content: best });
        } catch {
          // 回写失败就留着已发的那句：宁可少一次修正，不能让这句话从对话流里消失
        }
        setTurns((prev) => prev.map((t) => (t.key === sent.key ? { ...t, text: best } : t)));
      }
      if (sent.speaker === 'other') void runAnalysis(sent.utteranceId, best, sent.key);
    },
    [runAnalysis],
  );

  const handleAsrEvent = useCallback(
    (event: AsrDownEvent) => {
      if (event.type === 'ready') {
        readyRef.current = true;
        segmentRef.current = event.segment;
        // 55s 轮换时网关先说 segment_end 再开新段：这里必须清掉「本段已结束」的标记，
        // 否则录过一次轮换后松手就不再等 final，最后一句被直接丢掉
        segmentEndedRef.current = false;
        return;
      }
      if (event.type === 'partial') {
        segmentRef.current = event.segment;
        // 松手后这句已经发出去了：中间结果不再回写输入框，否则同一句会重新出现在框里等着被发第二遍
        if (!settlingRef.current) writeAsrText(event.text, false);
        return;
      }
      if (event.type === 'final') {
        segmentRef.current = event.segment;
        if (settlingRef.current) {
          // 只要同一段的定稿：跨 55s 轮换后 final 只带新段文本，拿它覆盖已发的整句会把前半句截掉
          lateFinalRef.current = event.segment === sentSegmentRef.current ? event.text : '';
          return;
        }
        writeAsrText(event.text, true);
        return;
      }
      if (event.type === 'segment_end') {
        segmentEndedRef.current = true;
        if (settlingRef.current) void endGrace(lateFinalRef.current);
        return;
      }
      if (event.type === 'error') {
        // 出错就不会再有定稿了：先用手上的文本把那句收尾，别让它一直挂在「收尾中」
        if (settlingRef.current) void endGrace(lateFinalRef.current);
        setAsrError(event.message || '转写服务异常');
        Taro.showToast({ title: event.message || '转写服务异常', icon: 'none' });
      }
    },
    [endGrace, writeAsrText],
  );

  const startRecording = useCallback(async () => {
    // 游客按麦克风：先去登录。麦克风只在登录后由用户按住，登录后回跳也不会自动开录
    if (!getSessionToken()) {
      goLogin();
      return;
    }
    // 会话没就绪就按住（上一场刚结束、或冷启动还没建好）：按需建会话，
    // 不能静默 return —— 表现是按住没反应，真因被吞掉
    if (!sessionRef.current) {
      try {
        await ensureSession();
      } catch (error) {
        Taro.showToast({
          title: error instanceof Error ? error.message : '会话未就绪，请稍候再按',
          icon: 'none',
        });
        return;
      }
    }
    if (!sessionRef.current) {
      Taro.showToast({ title: '会话尚未就绪，请稍候重试', icon: 'none' });
      return;
    }
    if (recorderRef.current) return;
    try {
      await Taro.authorize({ scope: 'scope.record' });
    } catch {
      Taro.showModal({
        title: '需要麦克风权限',
        content: '录音是本产品的核心能力。也可以在下方输入框直接打字。',
        showCancel: false,
      });
      return;
    }
    if (!recordReadyRef.current) {
      // 第一次按下多半就是弹授权框：等用户点「允许」时手指早抬起来了，这时接着开录会「按下即停」，
      // 看起来像按坏了。所以首次只拿授权并说明要再按一次；第二次 authorize 直接成功，链路是顺的。
      recordReadyRef.current = true;
      Taro.showToast({ title: '已开启麦克风，再按住说话', icon: 'none' });
      return;
    }
    // 上一句还在等定稿就又被按住（pausing 的 state 还没回到这次点击）：先让它就地结算。
    // 顶掉 asrRef 的话，endGrace 会去关刚建的这条连接，上一句的纠正与分析双双丢失。
    if (settlingRef.current) await endGrace(lateFinalRef.current);
    try {
      // 必须在建连前记下草稿：松开发送时按这个长度切出「这一次说的话」
      draftBeforeRef.current = inputRef.current;
      const { ticket } = await talkApi.asrTicket(sessionRef.current.id);
      const client = new AsrClient();
      // 连接被服务端掐断（网关重启、讯飞断线、票据失效）要立刻收摊：继续采只是把帧丢进
      // 死管子，用户看到的是「说了半天没反应」，而且不知道断在哪
      const onGatewayClosed = () => {
        if (asrRef.current !== client) return;
        if (!recorderRef.current) {
          // 松手后的宽限期内被服务端关闭（网关回完 segment_end 就断）：连接已无用，立刻收摊
          if (settlingRef.current) void endGrace(lateFinalRef.current);
          return;
        }
        recorderRef.current.stop();
        recorderRef.current = null;
        asrRef.current = null;
        setRecording(false);
        settleTail();
        Taro.showToast({ title: '转写连接中断，已识别的文字仍在输入框', icon: 'none', duration: 3000 });
      };
      await client.connect(ticket, handleAsrEvent, onGatewayClosed);
      client.start();
      asrRef.current = client;
      segmentEndedRef.current = false;
      asrDeliveredRef.current = false;
      frameCountRef.current = 0;
      readyRef.current = false;
      segmentRef.current = 1;
      settlingRef.current = false;
      lateFinalRef.current = '';
      setAsrError('');

      const recorder = new PcmRecorder();
      recorderRef.current = recorder;
      recorder.start({
        onChunk: (chunk) => {
          frameCountRef.current += 1;
          client.sendFrame(toBase64(chunk));
        },
        onError: (message) => Taro.showToast({ title: message, icon: 'none' }),
      });
      setRecording(true);
    } catch (error) {
      Taro.showToast({ title: error instanceof Error ? error.message : '无法开始录音', icon: 'none' });
    }
  }, [endGrace, ensureSession, goLogin, handleAsrEvent, settleTail]);

  const teardown = useCallback(() => {
    // 松手时的收尾状态一并清掉：否则页面隐藏/登出后回来，按住麦克风会被这里拦掉
    holdRef.current = false;
    // 宽限期内离开页面：连接即将关闭，最后那句不可能再等到来。就地结算 ——
    // 已发出去的话宁可只按当前文本分析一次，也不能留下一条永不分析的记录。
    void endGrace(lateFinalRef.current);
    recorderRef.current?.stop();
    recorderRef.current = null;
    asrRef.current?.close();
    asrRef.current = null;
    // 播报是 InnerAudioContext，页面切走/卸载不会自己停：不主动停就是「人走了声音还在念」
    stopTts();
    setRecording(false);
  }, [endGrace]);

  /**
   * 松手：停止上行、发收尾帧，但**不关连接**——讯飞的整句定稿就在这之后几百毫秒到，
   * 它用来纠正刚发出去的那一句（见 endGrace）。
   *
   * 这里不再原地等定稿：等的时候用户看到的是一句已经说到一半的话被卡住，而松开发送要的就是即时。
   */
  const stopRecording = useCallback(() => {
    // 已经在等定稿（「结束保存」也会走这里）：别重复发 stop 帧，别再另起一份宽限期计时
    if (settlingRef.current) return;
    const client = asrRef.current;
    setRecording(false);
    recorderRef.current?.stop();
    recorderRef.current = null;
    // 输入框里的「正在说」转正：这句接下来要被切出去发送，不再属于尾部
    settleTail();
    if (!client?.isOpen) {
      client?.close();
      if (asrRef.current === client) asrRef.current = null;
      return;
    }
    setPausing(true);
    client.stop();
    settlingRef.current = true;
    sentSegmentRef.current = segmentRef.current;
    lateFinalRef.current = '';
    graceTimerRef.current = setTimeout(() => void endGrace(lateFinalRef.current), LATE_FINAL_GRACE_MS);
    // 一段录音下来一个字都没转出来：没有「刚发出的那句」要纠正，直接收摊并把断点说清楚
    // （0 帧 = 采集没出声；有帧但没 ready = 网关没建起讯飞会话；都有帧 = 讯飞没出字）
    if (!asrDeliveredRef.current && !asrError) {
      void endGrace('');
      const frames = frameCountRef.current;
      const detail =
        frames === 0
          ? '未采到音，请检查麦克风或改用文字输入'
          : `已上行 ${frames} 帧${readyRef.current ? '' : '，网关未就绪'}`;
      Taro.showToast({ title: `没识别到语音：${detail}`, icon: 'none', duration: 3000 });
    }
  }, [asrError, endGrace, settleTail]);

  /**
   * 松开发送：立刻把这次按住说出的那一句发出去，按住前已有的草稿留在框里。
   *
   * 发的是当时输入框里的文本（讯飞中间结果），定稿随后由 endGrace 回写覆盖。
   * 按住期间手不可能同时编辑输入框，partial 又始终只替换尾部那一句，
   * 所以按「按住前的长度」切分是可靠的。
   */
  const sendHeldVoice = useCallback(async () => {
    const draft = draftBeforeRef.current;
    const spoken = inputRef.current.slice(draft.length).trim();
    if (!spoken) return;
    fromVoiceRef.current = false;
    setInputValue(draft);
    const sent = await commitUtterance(spoken, 'voice', speakerRef.current, { analyze: false });
    if (!sent) return;
    sentRef.current = sent;
    // addUtterance 的往返比 WS 帧慢：定稿和 segment_end 可能已经先到，那一次 endGrace 无句可纠、
    // 只关掉了连接；这里补一次，把已经拿到手的纠正用上
    if (!settlingRef.current) void endGrace(lateFinalRef.current);
  }, [commitUtterance, endGrace, setInputValue]);

  /** 按住：开始录音。重复的 touchstart（多指、抖动）只认第一次 */
  const beginHold = () => {
    if (holdRef.current || pausing) return;
    if (!getSessionToken()) {
      goLogin();
      return;
    }
    holdRef.current = true;
    const task = (async () => {
      await startRecording();
    })().finally(() => {
      if (holdTaskRef.current === task) holdTaskRef.current = null;
    });
    holdTaskRef.current = task;
  };

  /** 松手：等开录流程走完再收尾发送，否则会停掉一条还没建好的连接，刚说的那半句被丢 */
  const endHold = () => {
    if (!holdRef.current) return;
    holdRef.current = false;
    void (async () => {
      if (holdTaskRef.current) await holdTaskRef.current;
      // 开录本身没成功（权限被拒、会话没就绪、建连失败）时不收尾：
      // 否则再补一条「没识别到语音」，把上面那条真因提示盖掉
      if (!recorderRef.current && !asrRef.current) return;
      stopRecording();
      await sendHeldVoice();
    })();
  };

  useDidShow(() => {
    // 「我的」里改的场景要在这里生效：tab 页常驻不重新挂载，只读 storage 不读 state
    const nextScene = Taro.getStorageSync(SCENE_KEY) || 'general';
    sceneRef.current = nextScene;
    setScene(nextScene);
    // 从「会话记录」点「继续这场」切回本 tab：tab 页常驻不重新挂载，按 storage 里的会话号重载，
    // 否则界面显示的仍是手上这一场，用户以为继续了、实际说的还是落到旧会话里
    const storedId = Number(Taro.getStorageSync(CURRENT_SESSION_KEY) || 0);
    const currentId = sessionRef.current?.id ?? 0;
    if (!storedId || storedId === currentId || pendingRef.current || !getSessionToken()) {
      return;
    }
    teardown();
    setInputValue('');
    void talkApi
      .getSession(storedId)
      .then(hydrate)
      .catch(() => Taro.showToast({ title: '会话载入失败', icon: 'none' }));
  });

  useEffect(() => {
    if (status === 'authenticated') {
      // 补 catch：否则 createSession 失败（如登录态过期）会变成未捕获的 Promise 拒绝，
      // 表现为「按了没反应」，真因完全不可见。录音一律由用户按住开启（隐私边界）
      void ensureSession().catch((error: unknown) => {
        Taro.showToast({
          title: error instanceof Error ? error.message : '会话初始化失败',
          icon: 'none',
        });
      });
      // 以前授权过就不必浪费一次按下：getSetting 只读状态，不弹窗
      void Taro.getSetting()
        .then((setting) => {
          if (setting.authSetting?.['scope.record']) recordReadyRef.current = true;
        })
        .catch(() => undefined);
      return;
    }
    if (status === 'unauthenticated') {
      // 退出/登录失效：清掉上一位用户的会话与转写，界面回落到游客态
      teardown();
      recordReadyRef.current = false;
      sessionRef.current = null;
      setSession(null);
      setTurns([]);
      setElapsed(0);
      Taro.removeStorageSync(CURRENT_SESSION_KEY);
    }
  }, [ensureSession, status, teardown]);

  useDidHide(teardown);
  useUnload(teardown);

  /**
   * 对话流始终跟到底部：新句入列、以及异步回来的洞察/建议把这条撑高时都要拉一次。
   * 少了这一步，刚发出去的那句会落在屏幕外，看起来像「点了没反应」。
   */
  useEffect(() => {
    anchorSeqRef.current += 1;
    setAnchor(anchorSeqRef.current % 2 === 0 ? 'stream-bottom-b' : 'stream-bottom-a');
  }, [turns]);

  // 计时：只在录音中累加，松手即停（与真实录音时长保持一致）
  useEffect(() => {
    if (!recording) return;
    const timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, [recording]);

  const switchSpeaker = (next: 'other' | 'me') => {
    speakerRef.current = next;
    setSpeaker(next);
  };

  /**
   * 发送输入框里的话（手动点「发送」）：来源按「这句是不是转写出来的」记，转写文本被编辑过也算语音。
   * 按住说话期间不走这里：那时输入框尾部还是半成品，且松手路径已经负责发送。
   */
  const sendPending = useCallback(async () => {
    if (recorderRef.current || asrRef.current) return;
    const content = inputRef.current.trim();
    if (!content) return;
    // 游客打的字不清空：登录回来这句话还留在输入框里
    if (!getSessionToken()) {
      goLogin();
      return;
    }
    const source = fromVoiceRef.current ? 'voice' : 'text';
    fromVoiceRef.current = false;
    setInputValue('');
    await commitUtterance(content, source, speakerRef.current);
  }, [commitUtterance, goLogin, setInputValue]);

  const goHistory = () => Taro.navigateTo({ url: '/pages/history/index' });

  /**
   * 结束并保存：停录音 → 把输入框里没说出去的话落库 → 会话置为 ended → 本地清场。
   * 不再原地自动开下一场：下一场由「下一次按住录音」或「继续这场」按需创建，
   * 免得每次点保存都留下一场空会话。
   */
  const endSession = async () => {
    const current = sessionRef.current;
    if (!current) {
      Taro.showToast({ title: '当前没有进行中的会话', icon: 'none' });
      return;
    }
    stopRecording();
    // 上一句可能还在等定稿：先把它的纠正与分析起跑做完，再清场。
    // 顺序反了的话 runAnalysis 读到的是已经置空的会话，最后一句会永远停在「正在理解…」
    await endGrace(lateFinalRef.current);
    await sendPending();
    try {
      await talkApi.updateSession(current.id, {
        status: 'ended',
        durationMs: elapsed * 1000,
        title: current.title ?? undefined,
      });
    } catch {
      // 结束失败不阻断：本地已停录音，会话仍可稍后在「会话记录」里处理
    }
    Taro.removeStorageSync(CURRENT_SESSION_KEY);
    sessionRef.current = null;
    setSession(null);
    setTurns([]);
    setElapsed(0);
    setInputValue('');
    Taro.showModal({
      title: '已保存',
      content: '这场对话已存进「会话记录」，可随时回看；直接按住麦克风就说下一场。',
      confirmText: '看记录',
      cancelText: '知道了',
      success: (res) => {
        if (res.confirm) goHistory();
      },
    });
  };

  // speak 自己吞掉合成失败（返回 void）：这里不能再 .catch，否则点击即 TypeError
  // useCallback 是为了 TurnRow 的 memo 有意义——行内函数的话每一帧都算「props 变了」
  const playSuggestion = useCallback((text: string) => {
    speak(text);
  }, []);

  const sendable = !recording && !pausing && Boolean(input.trim());

  return (
    <View className='session'>
      <View className='recbar'>
        <View className={`dot ${recording ? 'live' : ''}`} />
        <Text className='recbar__text'>
          {recording ? '录音中' : pausing ? '收尾中' : elapsed > 0 ? '已停止' : '未录音'}
        </Text>
        <Text className='recbar__time'>{formatClock(elapsed)}</Text>
        <View className='speaker'>
          <View
            className={`speaker__item ${speaker === 'other' ? 'on' : ''}`}
            onClick={() => switchSpeaker('other')}
          >
            对方
          </View>
          <View
            className={`speaker__item ${speaker === 'me' ? 'on' : ''}`}
            onClick={() => switchSpeaker('me')}
          >
            我
          </View>
        </View>
      </View>

      <View className='meta'>
        <Text className='meta__chip'>场景：{sceneLabel(scene)}</Text>
        {asrError ? <Text className='meta__warn'>{asrError} · 可改用文字输入</Text> : null}
        <View className='meta__link' onClick={goHistory}>
          会话记录{'\u203A'}
        </View>
      </View>

      <ScrollView className='stream' scrollY scrollWithAnimation scrollIntoView={anchor}>
        {turns.length === 0 && !input ? (
          <View className='empty'>按住下方麦克风说话，松手自动发送；也可在输入框直接打字</View>
        ) : null}

        {turns.map((turn) => (
          <TurnRow key={turn.key} turn={turn} onPlay={playSuggestion} />
        ))}

        {/* 底部两个探针：scroll-into-view 只在 id 变化时才动作，交替指这两个才能反复滚到底 */}
        <View id='stream-bottom-a' className='stream__anchor' />
        <View id='stream-bottom-b' className='stream__anchor' />

      </ScrollView>

      {status !== 'authenticated' ? (
        <View className='guest-hint' onClick={goLogin}>
          <Text className='guest-hint__text'>
            {status === 'loading' ? '正在恢复登录态…' : '登录后才能录音并保存对话，点我去登录'}
          </Text>
        </View>
      ) : null}

      <View className='dock'>
        {!recording && input ? <Text className='dock__hint'>核对后点「发送」，AI 才开始分析这句</Text> : null}
        <Textarea
          className='dock__input'
          placeholder='对方说的话（按住麦克风转写会填在这里，可修改）'
          value={input}
          maxlength={500}
          showConfirmBar={false}
          disableDefaultPadding
          onInput={(event) => setInputValue(event.detail.value ?? '')}
        />
        <View className='dock__ctl'>
          <View className='dock__side' onClick={() => void endSession()}>
            结束保存
          </View>
          <View
            className={`mic ${recording ? 'mic--on' : ''}`}
            onTouchStart={beginHold}
            onTouchEnd={endHold}
            onTouchCancel={endHold}
          >
            {recording ? <View className='mic__ring' /> : null}
            {recording ? <View className='mic__ring mic__ring--b' /> : null}
            <View className='mic__capsule' />
            <View className='mic__arc' />
            <View className='mic__stem' />
            <View className='mic__base' />
          </View>
          <View
            className={`dock__side dock__side--send ${sendable ? '' : 'is-off'}`}
            onClick={() => void sendPending()}
          >
            发送
          </View>
        </View>
        <Text className='dock__tip'>
          {recording ? '松开发送' : pausing ? '这句已发出，正在定稿…' : '按住麦克风说话，松手自动发送'}
        </Text>
      </View>
    </View>
  );
}
