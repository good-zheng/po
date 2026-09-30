import Taro from '@tarojs/taro';
import { useCallback, useEffect, useRef, useState } from 'react';

/** 无人处理则自动安静，避免一直循环响 */
const RING_DURATION_MS = 30_000;

type Options = {
  /** 计时结束时循环播放的提示音 URL（与 Expo 的 step-done.wav 对齐） */
  loopUrl: string;
};

/**
 * 计时结束提醒：循环播放内置「叮叮」提示音 + 起始一次震动，30s 自动安静。
 * 与 cooking-app 的 Expo 行为对齐——只响铃、不播语音、不受播报开关影响。
 */
export function useCookAlert({ loopUrl }: Options) {
  const [ringing, setRinging] = useState(false);
  const ringTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const audioRef = useRef<Taro.InnerAudioContext | null>(null);

  const stop = useCallback(() => {
    if (ringTimer.current) {
      clearTimeout(ringTimer.current);
      ringTimer.current = null;
    }
    const audio = audioRef.current;
    if (audio) {
      audio.stop();
      audio.destroy();
      audioRef.current = null;
    }
    setRinging(false);
  }, []);

  const play = useCallback(() => {
    if (ringTimer.current) {
      clearTimeout(ringTimer.current);
    }
    if (!loopUrl) {
      return;
    }
    if (!audioRef.current) {
      const audio = Taro.createInnerAudioContext();
      audio.src = loopUrl;
      audio.loop = true;
      audio.onError(() => {});
      audioRef.current = audio;
    }
    audioRef.current.play();
    setRinging(true);
    Taro.vibrateLong({ fail: () => {} });
    ringTimer.current = setTimeout(stop, RING_DURATION_MS);
  }, [loopUrl, stop]);

  useEffect(
    () => () => {
      if (ringTimer.current) {
        clearTimeout(ringTimer.current);
      }
      if (audioRef.current) {
        audioRef.current.destroy();
        audioRef.current = null;
      }
    },
    [],
  );

  return { play, ringing, stop };
}
