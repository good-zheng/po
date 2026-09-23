import { setAudioModeAsync, useAudioPlayer } from 'expo-audio';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Platform, Vibration } from 'react-native';

// 三声上菜铃 + 一锅气（2 秒），参数与合成方式见 tools/cook-alert-sound.py
const ALERT_SOURCE = require('../../../assets/sounds/step-done.wav');

/** 单遍铃只有 2 秒，循环播放到这么久还没人处理就自动安静 */
const RING_DURATION_MS = 30_000;

/**
 * 计时结束的提醒：循环响铃，非 Web 端同时震动。
 * 默认持续 30 秒，期间调用 stop() 立即停止。
 */
export function useCookAlert() {
  const player = useAudioPlayer(ALERT_SOURCE);
  const [ringing, setRinging] = useState(false);
  const ringTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // 灶台边手机常静音或放着音乐：静音键下也要响，响的时候把背景音压下去
    void setAudioModeAsync({
      interruptionMode: 'duckOthers',
      playsInSilentMode: true,
    });
  }, []);

  const stop = useCallback(() => {
    if (ringTimer.current) {
      clearTimeout(ringTimer.current);
      ringTimer.current = null;
    }

    player.loop = false;
    player.pause();
    // 停下的位置留在末尾的话，下次响铃会没声音
    void player.seekTo(0);
    setRinging(false);
  }, [player]);

  const play = useCallback(() => {
    // 开着循环，靠用户操作或超时收尾
    player.loop = true;
    // 播到结尾后 currentTime 停在末尾，直接 play() 不会再出声，先回到开头
    void player.seekTo(0).then(() => player.play());
    setRinging(true);

    if (ringTimer.current) {
      clearTimeout(ringTimer.current);
    }
    ringTimer.current = setTimeout(stop, RING_DURATION_MS);

    if (Platform.OS !== 'web') {
      Vibration.vibrate(400);
    }
  }, [player, stop]);

  // 卸载时 expo-audio 会释放播放器并顺带停掉声音，这里只要别让定时器再去碰已释放的对象
  useEffect(
    () => () => {
      if (ringTimer.current) {
        clearTimeout(ringTimer.current);
        ringTimer.current = null;
      }
    },
    [],
  );

  return { play, ringing, stop };
}
