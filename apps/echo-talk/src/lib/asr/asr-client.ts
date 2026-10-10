import Taro from '@tarojs/taro';

import { ASR_WS_URL } from '@/config/env';

/**
 * ASR 网关客户端：PCM 帧上行、转写文本下行。
 *
 * 为什么走服务端代理而不是小程序直连讯飞：APIKey/APISecret 绝不能下发到端上。
 * 连接地址带一次性 ticket（见 ``/talk/asr/ticket``），因为微信小程序 WebSocket
 * 不支持自定义请求头，JWT 只能拼在 query 里会被网关日志留存。
 *
 * 帧协议（与后端 AsrSocketHandler 对应）：
 *   上行 start / frame / stop
 *   下行 ready / partial / final / segment_end / error
 */

export type AsrDownEvent =
  | { type: 'ready'; segment: number }
  | { type: 'partial'; text: string; segment: number }
  | { type: 'final'; text: string; segment: number }
  | { type: 'segment_end'; reason: string; segment: number }
  | { type: 'error'; code: string; message: string };

/**
 * 建连超时（毫秒）。
 *
 * 真机上 WebSocket 握手经常「既不 open 也不 error」（弱网、域名未加白名单、TLS 握手卡住），
 * 少了这一层保护就会一直 await：点录音没反应、也没提示，只能杀掉小程序重进。
 * 取 8s 是给服务端留出讯飞握手的时间，别在网关还没失败时先自己掐断。
 */
const OPEN_TIMEOUT_MS = 8000;

export class AsrClient {
  private task: Taro.SocketTask | null = null;
  private opened = false;

  get isOpen(): boolean {
    return this.opened;
  }

  /** 建立连接；ticket 无效或服务端没建起讯飞会话时 reject，调用方据此回落到文字输入 */
  async connect(
    ticket: string,
    onEvent: (event: AsrDownEvent) => void,
    onClosed?: () => void,
  ): Promise<void> {
    // Taro 4 破坏性变更：connectSocket 返回 Promise<SocketTask>，必须先 await 再注册回调，
    // 直接拿返回值当 SocketTask 用会报 "task.onOpen is not a function"。
    const task = await Taro.connectSocket({ url: `${ASR_WS_URL}?ticket=${encodeURIComponent(ticket)}` });
    this.task = task;

    return new Promise<void>((resolve, reject) => {
      let settled = false;
      const fail = (message: string) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        this.opened = false;
        this.task = null;
        try {
          task.close({ code: 1000, reason: 'timeout' });
        } catch {
          // 压根没连上时 close 也会抛，忽略
        }
        reject(new Error(message));
      };
      const timer = setTimeout(() => fail('转写服务连接超时，请改用文字输入'), OPEN_TIMEOUT_MS);

      task.onOpen(() => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        this.opened = true;
        resolve();
      });
      task.onError((err) => fail(err.errMsg || '转写服务连接失败'));
      task.onClose(() => {
        if (!settled) {
          fail('转写服务已断开，请改用文字输入');
          return;
        }
        const wasOpen = this.opened;
        this.opened = false;
        this.task = null;
        // 录音途中被服务端掐断也要有下文：不通知的话端上会一直采、一直发，全丢在路上
        if (wasOpen) onClosed?.();
      });
      task.onMessage((res) => {
        // 关闭后仍可能收到在途帧：本端已把这句话说完并提交了，再吃一条 final 会重复入列
        if (!this.opened) return;
        try {
          const payload = JSON.parse(String(res.data)) as AsrDownEvent;
          onEvent(payload);
        } catch {
          // 非 JSON 帧直接忽略：协议外的数据不该让录音中断
        }
      });
    });
  }

  /** 告知服务端开始一段（服务端据此开讯飞会话） */
  start(): void {
    this.send({ type: 'start' });
  }

  /** 上行一帧 PCM（base64）；由 PcmRecorder 保证是 1280 字节 */
  sendFrame(base64Audio: string): void {
    this.send({ type: 'frame', audio: base64Audio });
  }

  stop(): void {
    this.send({ type: 'stop' });
  }

  close(): void {
    try {
      if (this.opened) this.task?.close({ code: 1000, reason: 'done' });
    } catch {
      // 连接已断开时 close 可能抛错，忽略
    }
    this.opened = false;
    this.task = null;
  }

  private send(payload: Record<string, unknown>): void {
    if (!this.opened || !this.task) return;
    try {
      this.task.send({ data: JSON.stringify(payload) });
    } catch {
      // 单帧发送失败不阻断后续帧：丢一帧只影响 40ms 音频
    }
  }
}

/** ArrayBuffer → base64（小程序端没有 Buffer） */
export function toBase64(buffer: ArrayBuffer): string {
  return Taro.arrayBufferToBase64(buffer);
}
