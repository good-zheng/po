import Taro from '@tarojs/taro';
import { apiClient, resolveAssetUrl } from '@/lib/api/client';

/** 与后端 /tts/prefetch 的截断值保持一致 */
const PREFETCH_LIMIT = 50;

/** 一条播报：name 决定音频在桶里的文件名（step-3、finish），text 是要合成的文案 */
export type SpeechClip = {
  name: string;
  text: string;
};

/** 完成整道菜时的祝贺播报：所有菜谱共用同一段文案，归入 tts/misc/ 只合成一次 */
export const FINISH_CLIP: SpeechClip = {
  name: 'finish',
  text: '恭喜你，这道菜已经完成啦！用心烹制的美味，趁热享用吧。',
};

/** 步骤播报的音频名与文案：预热与播放必须用同一份，才会命中桶里同一个对象 */
export function stepClip(step: { stepNumber: number; content: string }): SpeechClip {
  return { name: `step-${step.stepNumber}`, text: `第 ${step.stepNumber} 步，${step.content}` };
}

let audioContext: Taro.InnerAudioContext | null = null;
let speaking = false;

/** 已拿到音频地址的文案 → 地址：命中即同步起播，省掉一次 /tts 往返 */
const audioUrls = new Map<string, string>();

function release(audio: Taro.InnerAudioContext) {
  speaking = false;
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
 * 预热整道菜的播报：桶里已有的立刻写进本地缓存，缺失的由后端后台合成。
 * 不等待、失败静默——真正 speak 时仍会走单条合成兜底。
 */
export function prefetch(recipeId: number, clips: SpeechClip[]) {
  // 一道菜内 name 唯一（step-N / finish），按 name 去重即可；本地已有地址的不再问后端
  const byName = new Map(clips.map((clip) => [clip.name, clip]));
  const pending = Array.from(byName.values())
    .filter((clip) => clip.text && !audioUrls.has(clip.text))
    .slice(0, PREFETCH_LIMIT);
  if (!pending.length) {
    return;
  }
  apiClient
    .post<{ urls?: Record<string, string> }>('/tts/prefetch', { recipeId, clips: pending })
    .then((res) => {
      pending.forEach((clip) => {
        const fullUrl = resolveAssetUrl(res?.urls?.[clip.name]);
        if (fullUrl) {
          audioUrls.set(clip.text, fullUrl);
        }
      });
    })
    .catch(() => {});
}

/**
 * 播报一条文案。带上所属菜谱与 name 时，后端会把音频存进 tts/recipes/{recipeId}/ 并与预热命中同一份对象；
 * 不带时落 tts/misc/，只适合聊天一类的自由文本。
 */
export function speak(text: string, clip?: { recipeId?: number; name?: string }) {
  stop();
  if (!text) return;

  speaking = true;
  const audio = Taro.createInnerAudioContext();
  audioContext = audio;

  const cached = audioUrls.get(text);
  if (cached) {
    play(audio, cached);
    return;
  }

  apiClient
    .get<{ url: string }>('/tts', { text, recipeId: clip?.recipeId, name: clip?.name })
    .then((res) => {
      if (superseded(audio)) {
        return;
      }
      const fullUrl = resolveAssetUrl(res.url);
      if (!fullUrl) {
        release(audio);
        return;
      }
      audioUrls.set(text, fullUrl);
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
  speaking = false;
}

export function isSpeaking() {
  return speaking;
}

export function isAvailable() {
  return true;
}
