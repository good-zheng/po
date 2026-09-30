import { useEffect, useState } from 'react';
import { View, Text, Image } from '@tarojs/components';
import Taro, { useLoad, useUnload } from '@tarojs/taro';
import type { Recipe } from '@po/types';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { fetchRecipeDetail } from '@/lib/api/recipes';
import { resolveAssetUrl } from '@/lib/api/client';
import { useCooking } from '@/lib/cooking/cooking-context';
import { useCookAlert } from '@/lib/cooking/use-cook-alert';
import {
  FINISH_CLIP,
  isAvailable as isTtsAvailable,
  prefetch as prefetchTts,
  speak,
  stepClip,
  stop as stopTts,
} from '@/lib/tts';
import { formatClock, sortSteps, stepDurationSeconds } from '@/lib/recipe-utils';
import './index.scss';

/** 计时结束的「叮叮」提示音：与 Expo 同一份 step-done.wav，由后端静态目录提供 */
const ALERT_SOUND_URL = resolveAssetUrl('/api/sounds/step-done.wav') || '';

type TimerState = {
  totalSeconds: number;
  remaining: number;
  running: boolean;
};

export default function CookEntry() {
  return (
    <AuthGuard>
      <CookPage />
    </AuthGuard>
  );
}

function CookPage() {
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [recipeId, setRecipeId] = useState(0);
  const [loading, setLoading] = useState(true);
  const [timer, setTimer] = useState<TimerState | null>(null);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [ttsAvailable, setTtsAvailable] = useState(false);
  const [finished, setFinished] = useState(false);

  const { session, beginCooking, goToStep, finishCooking } = useCooking();

  const { play: playAlert, ringing, stop: stopAlert } = useCookAlert({ loopUrl: ALERT_SOUND_URL });

  useLoad(() => {
    const pages = Taro.getCurrentPages();
    const currentPage = pages[pages.length - 1];
    const id = Number(currentPage.options?.id);
    if (!id) {
      Taro.showToast({ title: '菜谱不存在', icon: 'none' });
      return;
    }
    setRecipeId(id);
    setTtsAvailable(isTtsAvailable());
    Taro.setKeepScreenOn({ keepScreenOn: true, fail: () => {} });
    fetchRecipeDetail(id)
      .then((data) => {
        setRecipe(data);
        // 进页面就把整道菜的播报文案交给后端预热：命中桶缓存的立即到账，
        // 缺失的在后台合成，等用户看完第一步文案时基本都已就绪
        prefetchTts(id, sortSteps(data.steps).map(stepClip));
        // 完成播报所有菜谱共用，归入 tts/misc/ 只合成一次
        prefetchTts(0, [FINISH_CLIP]);
      })
      .catch(() => {
        Taro.showToast({ title: '加载失败', icon: 'none' });
      })
      .finally(() => setLoading(false));
  });

  const steps = sortSteps(recipe?.steps);
  const stepCount = steps.length;
  const stepIndex =
    session && session.recipeId === recipeId
      ? Math.min(session.stepIndex, Math.max(stepCount - 1, 0))
      : 0;
  const step = steps[stepIndex];
  const nextStep = steps[stepIndex + 1];
  const isLastStep = stepCount > 0 && stepIndex === stepCount - 1;
  const timeUp = Boolean(timer && timer.remaining === 0);

  // 数据就绪即登记/恢复会话
  useEffect(() => {
    if (recipe && stepCount > 0) {
      beginCooking({ id: recipe.id, title: recipe.title }, stepCount);
    }
  }, [recipe, stepCount, beginCooking]);

  // 换步骤重新计时：有时长的自动开表，无时长的不显示计时卡
  useEffect(() => {
    const seconds = stepDurationSeconds(step);
    setTimer(seconds > 0 ? { totalSeconds: seconds, remaining: seconds, running: true } : null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stepIndex, recipeId]);

  // 每秒递减
  useEffect(() => {
    if (!timer?.running) {
      return;
    }
    const handle = setInterval(() => {
      setTimer((prev) => {
        if (!prev?.running) {
          return prev;
        }
        const remaining = Math.max(0, prev.remaining - 1);
        return { ...prev, remaining, running: remaining > 0 };
      });
    }, 1000);
    return () => clearInterval(handle);
  }, [timer?.running]);

  // 换步骤播报当前做法（含首步：step 由 undefined 变为有值时也应触发）
  // finished 后不再播报：完成时清空会话会让 stepIndex 回落，若不拦截会误播第一步
  useEffect(() => {
    if (!ttsEnabled || !step || finished) {
      return;
    }
    const clip = stepClip(step);
    speak(clip.text, { recipeId, name: clip.name });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stepIndex, ttsEnabled, step?.content, finished]);

  // 计时归零触发提醒
  useEffect(() => {
    if (timeUp) {
      playAlert();
    }
  }, [timeUp, playAlert]);

  useUnload(() => {
    stopAlert();
    stopTts();
    Taro.setKeepScreenOn({ keepScreenOn: false, fail: () => {} });
  });

  const leaveCook = () => {
    stopAlert();
    stopTts();
    if (Taro.getCurrentPages().length > 1) {
      Taro.navigateBack();
    } else {
      Taro.switchTab({ url: '/pages/ai/chat' });
    }
  };

  const goPrev = () => {
    stopAlert();
    goToStep(stepIndex - 1);
  };

  const goNext = () => {
    stopAlert();
    if (isLastStep) {
      finishCooking();
      if (ttsEnabled) {
        speak(FINISH_CLIP.text, { name: FINISH_CLIP.name });
      }
      setFinished(true);
      return;
    }
    goToStep(stepIndex + 1);
  };

  const skipWait = () => {
    setTimer((prev) => (prev ? { ...prev, remaining: 0, running: false } : prev));
  };

  const dismissTimer = () => {
    stopAlert();
    setTimer(null);
  };

  const restartTimer = () => {
    const seconds = stepDurationSeconds(step);
    if (seconds > 0) {
      setTimer({ totalSeconds: seconds, remaining: seconds, running: true });
    }
  };

  const toggleTts = () => {
    const next = !ttsEnabled;
    setTtsEnabled(next);
    if (!next) {
      stopTts();
    }
  };

  if (loading) {
    return (
      <View className="cook-page">
        <Text className="cook-loading">正在准备灶台…</Text>
      </View>
    );
  }

  if (!recipe || !step) {
    return (
      <View className="cook-page">
        <Text className="cook-loading">这道菜还没有录入做法，先看看用料吧。</Text>
        <View className="cook-empty-back" onClick={leaveCook}>
          <Text className="cook-empty-back-text">返回</Text>
        </View>
      </View>
    );
  }

  if (finished) {
    return (
      <View className="cook-page">
        <View className="finish-card">
          <Text className="finish-emoji">{'\u{1F389}'}</Text>
          <Text className="finish-title">大功告成！</Text>
          <Text className="finish-text">
            {'你已经完成「'}
            {recipe.title}
            {'」，恭喜你！趁热享用这份用心烹制的美味吧。'}
          </Text>
          <View className="finish-btn" onClick={leaveCook}>
            <Text className="finish-btn-text">返回</Text>
          </View>
        </View>
      </View>
    );
  }

  const progress = ((stepIndex + 1) / stepCount) * 100;
  const timerProgress = timer ? (timer.remaining / timer.totalSeconds) * 100 : 0;

  return (
    <View className="cook-page">
      <View className="cook-header">
        <View className="cook-header-row">
          <View className="cook-exit" onClick={leaveCook}>
            <Text className="cook-exit-icon">{'\u2715'}</Text>
          </View>
          <View className="cook-header-info">
            <Text className="cook-title">{recipe.title}</Text>
            <Text className="cook-subtitle">第 {stepIndex + 1}/{stepCount} 步 · 退出后进度会保留</Text>
          </View>
          {ttsAvailable ? (
            <View className="tts-toggle" onClick={toggleTts}>
              <Text className={`tts-toggle-icon ${ttsEnabled ? 'tts-toggle-active' : ''}`}>
                {ttsEnabled ? '\u{1F50A}' : '\u{1F507}'}
              </Text>
            </View>
          ) : null}
        </View>
        <View className="progress-bar">
          <View className="progress-fill" style={{ width: `${progress}%` }} />
        </View>
      </View>

      <View className="cook-body">
        <View className="step-badge-row">
          <View className="step-badge">
            <Text className="step-badge-text">{step.stepNumber}</Text>
          </View>
          <Text className="step-count-text">共 {stepCount} 步</Text>
        </View>

        <Text className="step-content-text">{step.content}</Text>

        {step.imageUrl ? (
          <Image className="step-image" src={resolveAssetUrl(step.imageUrl) || ''} mode="aspectFill" />
        ) : null}

        {timer ? (
          <View className="timer-card">
            <View className="timer-header">
              <Text className="timer-label">{'\u23F1'} {timeUp ? '计时结束' : '这一步需要等待'}</Text>
              <Text className="timer-display">{formatClock(timer.remaining)}</Text>
            </View>
            <View className="timer-progress">
              <View className="timer-progress-fill" style={{ width: `${timerProgress}%` }} />
            </View>
            <View className="timer-actions">
              {timeUp ? null : (
                <View className="timer-btn" onClick={() => setTimer((p) => (p ? { ...p, running: !p.running } : p))}>
                  <Text className="timer-btn-text">{timer.running ? '暂停计时' : '继续计时'}</Text>
                </View>
              )}
              <View className="timer-btn" onClick={timeUp ? dismissTimer : skipWait}>
                <Text className="timer-btn-text">{timeUp ? '收起计时' : '跳过等待'}</Text>
              </View>
            </View>
          </View>
        ) : stepDurationSeconds(step) > 0 ? (
          <View className="timer-reopen" onClick={restartTimer}>
            <Text className="timer-reopen-text">{'\u23F1'} 开始 {step.duration} 分钟计时</Text>
          </View>
        ) : null}

        {timeUp ? (
          <View className="time-up-banner">
            <View className="time-up-head">
              <Text className="time-up-title">{'\u{1F514}'} 时间到，可以进行下一步了</Text>
              {ringing ? (
                <View className="ring-stop-chip" onClick={stopAlert}>
                  <Text className="ring-stop-text">停止响铃</Text>
                </View>
              ) : null}
            </View>
            <Text className="time-up-next">
              {nextStep ? `下一步：${nextStep.content}` : '最后一步完成了，盛盘上桌吧。'}
            </Text>
            <View className="time-up-btn" onClick={goNext}>
              <Text className="time-up-btn-text">{nextStep ? '进入下一步' : '完成做菜'}</Text>
            </View>
          </View>
        ) : null}
      </View>

      <View className="cook-footer">
        <View
          className={`nav-btn ${stepIndex === 0 ? 'nav-btn-disabled' : ''}`}
          onClick={stepIndex === 0 ? undefined : goPrev}
        >
          <Text className={`nav-btn-text ${stepIndex === 0 ? 'nav-btn-text-disabled' : ''}`}>上一步</Text>
        </View>
        <View className="nav-btn nav-btn-primary" onClick={goNext}>
          <Text className="nav-btn-text nav-btn-text-primary">{isLastStep ? '完成做菜' : '下一步'}</Text>
        </View>
      </View>
    </View>
  );
}
