import Taro from '@tarojs/taro';
import { apiClient, resolveAssetUrl } from '@/lib/api/client';

let audioContext: Taro.InnerAudioContext | null = null;

/** 已拿到音频地址的文案 → 地址：命中即同步起播，省掉一次 /tts 往返 */
const audioUrls = new Map<string, string>();

/** 播报文案是即兴的，地址缓存只留最近这些条（Map 保序，按插入顺序淘汰最旧的） */
const AUDIO_URL_LIMIT = 60;

function remember(text: string, url: string) {
  if (audioUrls.size >= AUDIO_URL_LIMIT) {
    const oldest = audioUrls.keys().next().value;
    if (oldest !== undefined) {
      audioUrls.delete(oldest);
    }
  }
  audioUrls.set(text, url);
}

function release(audio: Taro.InnerAudioContext) {
  if (audioContext === audio) {
    audioContext = null;
  }
  audio.destroy();
}

/** 播报是否已被后续的 speak/stop 取代：被取代的那条已由对方 destroy，不能再播 */
function superseded(audio: Taro.InnerAudioContext) {
  return audioContext !== audio;
}

function play(audio: Taro.InnerAudioContext, fullUrl: string) {
  audio.onEnded(() => release(audio));
  audio.onError(() => release(audio));
  audio.src = fullUrl;
  audio.play();
}

/**
 * 播报一条文案（把分析结论念给用户听）。
 *
 * 自由文本谈不上预热，落 tts/misc/ 由后端按需合成；同一句再播时命中本地地址直接起播。
 */
export function speak(text: string) {
  stop();
  if (!text) return;

  const audio = Taro.createInnerAudioContext();
  audioContext = audio;

  const cached = audioUrls.get(text);
  if (cached) {
    play(audio, cached);
    return;
  }

  apiClient
    .get<{ url: string }>('/tts', { text })
    .then((res) => {
      if (superseded(audio)) {
        return;
      }
      const fullUrl = resolveAssetUrl(res.url);
      if (!fullUrl) {
        release(audio);
        return;
      }
      remember(text, fullUrl);
      play(audio, fullUrl);
    })
    .catch(() => {
      if (!superseded(audio)) {
        release(audio);
      }
    });
}

export function stop() {
  if (audioContext) {
    audioContext.stop();
    audioContext.destroy();
    audioContext = null;
  }
}
