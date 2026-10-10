import Taro from '@tarojs/taro';

/**
 * 录音采集：拿 RecorderManager 的 PCM 分片，切成讯飞要求的 1280 字节帧。
 *
 * 上行声明是 ``encoding=raw`` + ``audio/L16;rate=16000``，所以采集端必须真的产出 PCM：
 * ``format`` 传 ``mp3`` 时部分平台 ``frameBuffer`` 会随落盘格式一起变成压缩数据，
 * 讯飞按 16k PCM 解出来就是静音 —— 表现是帧数在涨、一个字第个都出不来。这里让
 * 声明与实际编码对齐，不做任何转码。
 *
 * 两个硬限制在这里兜住：
 * - 微信单次录音最长 10 分钟 → ``onStop`` 里若仍在录音态则自动重开，业务层无感；
 * - 讯飞要求 40ms / 1280 字节的发包节奏 → 由 :meth:`_push` 做字节级缓冲切片，
 *   与录音回调频率解耦（frameSize 只影响回调频率，不影响最终帧大小）。
 */

/** 采样率：讯飞要求 16k */
const SAMPLE_RATE = 16000;
/** 单帧字节数：1280 字节 = 16bit × 16000Hz × 40ms */
const FRAME_BYTES = 1280;
/** 微信单次录音上限（毫秒） */
const MAX_DURATION_MS = 600000;
/**
 * 暂停后隔多久才允许再开录（毫秒）。
 *
 * ``getRecorderManager()`` 拿到的是全局单例：``stop()`` 只是发指令，原生侧真正落到
 * 「已停止」还要几十到几百毫秒。快速「暂停→继续」时 start 会撞上还在收尾的上一次录音，
 * 表现是 onError 报 "recorder still starting" 或直接静默不出帧 —— 点继续没反应就是这么来的。
 */
const RESTART_COOLDOWN_MS = 300;

/** 单例 manager 的最近一次 stop 时刻：跨 PcmRecorder 实例共享 */
let lastStoppedAt = 0;

/**
 * 全局单例 manager 与「当前正在录音的那个实例」。
 *
 * ``onXxx`` 是往 manager 的监听列表里追加，注册一次就得管到底：
 * 每次 ``start()`` 再注册一遍的话，第 N 次录音时每一帧都要把 N 个历史闭包跑一遍
 * （原生侧按注册数线性分发），而那些闭包各自扣着上一轮的 AsrClient 与 WebSocket，
 * GC 也回收不掉。更糟的是 ``onError`` 没有录音态守卫，一次报错会弹 N 个 toast。
 * 所以这里只注册一次，靠 ``active`` 把事件交给当前实例。
 */
const manager = Taro.getRecorderManager();
let active: PcmRecorder | null = null;
let listenersBound = false;

function bindManagerListeners(): void {
  if (listenersBound) {
    return;
  }
  listenersBound = true;
  manager.onFrameRecorded((res) => {
    active?.handleFrame(res.frameBuffer);
  });
  manager.onStop(() => {
    active?.handleStop();
  });
  manager.onError((err) => {
    active?.handleError(err.errMsg || '录音失败');
  });
  manager.onInterruptionBegin(() => {
    active?.handleInterruption();
  });
}

export type RecorderHandlers = {
  /** 已按 FRAME_BYTES 切好的一帧，可直接 base64 后上行 */
  onChunk: (chunk: ArrayBuffer) => void;
  onAutoRestart?: () => void;
  onError?: (message: string) => void;
  onInterruption?: () => void;
};

function concatBytes(left: Uint8Array, right: Uint8Array): Uint8Array {
  const merged = new Uint8Array(left.length + right.length);
  merged.set(left, 0);
  merged.set(right, left.length);
  return merged;
}

export class PcmRecorder {
  private handlers: RecorderHandlers | null = null;
  private pending: Uint8Array | null = null;
  private running = false;
  private restartTimer: ReturnType<typeof setTimeout> | null = null;

  get isRecording(): boolean {
    return this.running;
  }

  start(handlers: RecorderHandlers): void {
    if (this.running) return;
    this.handlers = handlers;
    this.pending = null;
    this.running = true;

    bindManagerListeners();
    active = this;

    this.startRecord();
  }

  /** 停止录音：残留不足一帧的字节直接发出（讯飞接受小于 1280 的帧） */
  stop(): void {
    if (!this.running) return;
    this.running = false;
    if (this.restartTimer) {
      clearTimeout(this.restartTimer);
      this.restartTimer = null;
    }
    if (active === this) {
      active = null;
    }
    this.flush();
    lastStoppedAt = Date.now();
    try {
      manager.stop();
    } catch {
      // 未处于录音态时 stop 会抛错，忽略即可
    }
  }

  handleFrame(buffer: ArrayBuffer): void {
    if (!this.running) return;
    this.push(buffer);
  }

  handleStop(): void {
    // 10 分钟到了微信会自己停：仍在录音态就立即重开，时间轴继续走
    if (!this.running) return;
    this.flush();
    this.startRecord();
    this.handlers?.onAutoRestart?.();
  }

  handleError(message: string): void {
    this.running = false;
    if (active === this) {
      active = null;
    }
    this.handlers?.onError?.(message);
  }

  handleInterruption(): void {
    // 来电、其他应用抢占麦克风：暂停而非静默失败
    this.handlers?.onInterruption?.();
  }

  private startRecord(): void {
    const wait = RESTART_COOLDOWN_MS - (Date.now() - lastStoppedAt);
    if (lastStoppedAt > 0 && wait > 0 && !this.restartTimer) {
      // 冷却只在「刚停过」时起效：10 分钟自动重开走 onStop，那时 lastStoppedAt 不会被刷新
      this.restartTimer = setTimeout(() => {
        this.restartTimer = null;
        if (this.running) this.startRecord();
      }, wait);
      return;
    }
    manager.start({
      duration: MAX_DURATION_MS,
      sampleRate: SAMPLE_RATE,
      numberOfChannels: 1,
      encodeBitRate: 48000,
      // 必须是裸 PCM，且微信侧这个取值就是大写字面量 'PCM'（见官方 RecorderManager.start 的
      // 可选值 mp3/aac/wav/PCM）。写成小写 'pcm' 不是文档取值，会被回落到默认 mp3 ——
      // 上行按 raw/L16 声明，帧内容却是压缩数据，讯飞整段当静音：表现为「帧在涨、一个字都不出」
      format: 'PCM',
      // 每攒够约 2KB 回调一次。帧的切分由 push() 按 1280 字节做，与回调频率无关，
      // 所以调大它只减少「原生 → JS 桥」的穿越次数（约 32 次/秒 → 16 次/秒），不改变上行节奏
      frameSize: 2,
    });
  }

  private push(buffer: ArrayBuffer): void {
    const incoming = new Uint8Array(buffer);
    const merged = this.pending ? concatBytes(this.pending, incoming) : incoming;
    let offset = 0;
    while (merged.length - offset >= FRAME_BYTES) {
      const slice = merged.slice(offset, offset + FRAME_BYTES);
      this.handlers?.onChunk(slice.buffer);
      offset += FRAME_BYTES;
    }
    this.pending = offset < merged.length ? merged.slice(offset) : null;
  }

  private flush(): void {
    if (this.pending && this.pending.length > 0) {
      const slice = this.pending.slice();
      this.handlers?.onChunk(slice.buffer);
    }
    this.pending = null;
  }
}
