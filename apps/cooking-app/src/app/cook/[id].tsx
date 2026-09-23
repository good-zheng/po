import { Ionicons } from '@expo/vector-icons';
import { useQuery } from '@tanstack/react-query';
import { useKeepAwake } from 'expo-keep-awake';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import {
  Pressable,
  ScrollView,
  Text,
  useColorScheme,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { EmptyState, ErrorState, LoadingState } from '@/components/state-views';
import { resolveAssetUrl } from '@/lib/api/client';
import { fetchRecipeDetail } from '@/lib/api/recipes';
import { useCooking } from '@/lib/cooking/cooking-context';
import { useCookAlert } from '@/lib/cooking/use-cook-alert';
import { Image } from '@/lib/nativewind';
import { recipeKeys } from '@/lib/query-keys';
import {
  formatClock,
  sortSteps,
  stepDurationSeconds,
} from '@/lib/recipe-utils';
import { cn } from '@/lib/utils';

type TimerState = {
  totalSeconds: number;
  remaining: number;
  running: boolean;
};

export default function CookModeScreen() {
  useKeepAwake();
  const { id } = useLocalSearchParams<{ id: string }>();
  const recipeId = Number(id);
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const isDark = useColorScheme() === 'dark';
  const { beginCooking, finishCooking, goToStep, session } = useCooking();
  const { play: playAlert, ringing, stop: stopAlert } = useCookAlert();
  const [timer, setTimer] = useState<TimerState | null>(null);

  const { data, error, isLoading, refetch } = useQuery({
    enabled: Number.isFinite(recipeId),
    queryFn: () => fetchRecipeDetail(recipeId),
    queryKey: recipeKeys.detail(recipeId),
  });

  const steps = sortSteps(data?.steps);
  const stepCount = steps.length;
  const stepIndex =
    session?.recipeId === recipeId
      ? Math.min(session.stepIndex, stepCount - 1)
      : 0;
  const step = steps[stepIndex];
  const nextStep = steps[stepIndex + 1];
  const isLastStep = stepCount > 0 && stepIndex === stepCount - 1;

  useEffect(() => {
    if (data && stepCount > 0) {
      beginCooking({ id: data.id, title: data.title }, stepCount);
    }
  }, [beginCooking, data, stepCount]);

  // 换步骤就重新计时：有时长的步骤自动开表，没时长的步骤不显示计时卡
  useEffect(() => {
    const seconds = stepDurationSeconds(step);
    setTimer(
      seconds > 0
        ? { remaining: seconds, running: true, totalSeconds: seconds }
        : null,
    );
  }, [step, stepIndex]);

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

  const timeUp = Boolean(timer && timer.remaining === 0);

  // 计时归零就是这一步的停顿点：响铃提醒，用户决定要不要进下一步
  useEffect(() => {
    if (timeUp) {
      playAlert();
    }
  }, [playAlert, timeUp]);

  // 直接以链接进入做菜页时没有上一页可退，回落到 AI 指导页
  const leaveCook = () => {
    stopAlert();

    if (router.canGoBack()) {
      router.back();
      return;
    }

    router.replace('/ai');
  };

  const goPrev = () => {
    stopAlert();
    goToStep(stepIndex - 1);
  };

  const goNext = () => {
    stopAlert();

    if (isLastStep) {
      finishCooking();
      leaveCook();
      return;
    }

    goToStep(stepIndex + 1);
  };

  // 跳过等待也算「时间到」：归零触发提示音与震动，而不是直接收起计时
  const skipWait = () => {
    setTimer((prev) =>
      prev ? { ...prev, remaining: 0, running: false } : prev,
    );
  };

  const dismissTimer = () => {
    stopAlert();
    setTimer(null);
  };

  if (isLoading) {
    return (
      <View className="flex-1 bg-stone-50 dark:bg-stone-950">
        <LoadingState message="正在准备灶台…" />
      </View>
    );
  }

  if (error || !data) {
    return (
      <View className="flex-1 bg-stone-50 dark:bg-stone-950">
        <ErrorState error={error} onRetry={() => void refetch()} />
      </View>
    );
  }

  if (!step) {
    return (
      <View className="flex-1 bg-stone-50 dark:bg-stone-950">
        <EmptyState
          description="这道菜还没有录入做法，先看看用料吧。"
          title="没有可执行的步骤"
        />
        <View className="px-5" style={{ paddingBottom: insets.bottom + 12 }}>
          <Pressable
            accessibilityRole="button"
            className="items-center rounded-full bg-brand-600 py-3.5 active:opacity-90"
            onPress={leaveCook}
          >
            <Text className="font-semibold text-white">返回</Text>
          </Pressable>
        </View>
      </View>
    );
  }

  const progress = ((stepIndex + 1) / stepCount) * 100;
  const timerProgress = timer
    ? (timer.remaining / timer.totalSeconds) * 100
    : 0;

  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <View
        className="flex-row items-center gap-3 px-4 pb-3"
        style={{ paddingTop: insets.top + 8 }}
      >
        <Pressable
          accessibilityLabel="退出做菜模式"
          accessibilityRole="button"
          className="h-9 w-9 items-center justify-center rounded-full bg-white shadow-sm active:opacity-70 dark:bg-stone-900"
          hitSlop={8}
          onPress={leaveCook}
        >
          <Ionicons
            color={isDark ? '#fafaf9' : '#1c1917'}
            name="chevron-down"
            size={20}
          />
        </Pressable>
        <View className="flex-1">
          <Text
            className="text-base font-bold text-stone-900 dark:text-stone-50"
            numberOfLines={1}
          >
            {data.title}
          </Text>
          <Text className="mt-0.5 text-xs text-stone-500 dark:text-stone-400">
            第 {stepIndex + 1}/{stepCount} 步 · 退出后进度会保留
          </Text>
        </View>
      </View>

      <View className="h-1.5 bg-stone-200 dark:bg-stone-800">
        <View
          className="h-full bg-brand-600"
          style={{ width: `${progress}%` }}
        />
      </View>

      <ScrollView
        contentContainerClassName="px-5 pb-6 pt-6"
        showsVerticalScrollIndicator={false}
      >
        <View className="flex-row items-center gap-3">
          <View className="h-10 w-10 items-center justify-center rounded-full bg-brand-600">
            <Text className="text-base font-bold text-white">
              {step.stepNumber}
            </Text>
          </View>
          <Text className="text-xs text-stone-500 dark:text-stone-400">
            共 {stepCount} 步
          </Text>
        </View>

        <Text className="mt-4 text-xl font-semibold leading-9 text-stone-900 dark:text-stone-50">
          {step.content}
        </Text>

        {step.imageUrl ? (
          <Image
            accessibilityLabel={`第 ${step.stepNumber} 步`}
            className="mt-4 h-44 w-full rounded-2xl bg-stone-200 dark:bg-stone-800"
            contentFit="cover"
            source={resolveAssetUrl(step.imageUrl)}
            transition={150}
          />
        ) : null}

        {timer ? (
          <View className="mt-6 rounded-3xl bg-white p-5 shadow-sm dark:bg-stone-900">
            <View className="flex-row items-center justify-between">
              <View className="flex-row items-center gap-2">
                <Ionicons color="#ea580c" name="timer-outline" size={18} />
                <Text className="text-sm font-medium text-stone-600 dark:text-stone-300">
                  {timeUp ? '计时结束' : '这一步需要等待'}
                </Text>
              </View>
              <Text className="text-3xl font-bold tabular-nums text-stone-900 dark:text-stone-50">
                {formatClock(timer.remaining)}
              </Text>
            </View>
            <View className="mt-3 h-1.5 overflow-hidden rounded-full bg-stone-100 dark:bg-stone-800">
              <View
                className="h-full rounded-full bg-brand-600"
                style={{ width: `${timerProgress}%` }}
              />
            </View>
            <View className="mt-4 flex-row gap-3">
              {timeUp ? null : (
                <Pressable
                  accessibilityRole="button"
                  className="flex-1 items-center rounded-full border border-stone-200 py-2.5 active:opacity-70 dark:border-stone-700"
                  onPress={() =>
                    setTimer((prev) =>
                      prev ? { ...prev, running: !prev.running } : prev,
                    )
                  }
                >
                  <Text className="text-sm font-semibold text-stone-600 dark:text-stone-300">
                    {timer.running ? '暂停计时' : '继续计时'}
                  </Text>
                </Pressable>
              )}
              <Pressable
                accessibilityRole="button"
                className="flex-1 items-center rounded-full border border-stone-200 py-2.5 active:opacity-70 dark:border-stone-700"
                onPress={timeUp ? dismissTimer : skipWait}
              >
                <Text className="text-sm font-semibold text-stone-600 dark:text-stone-300">
                  {timeUp ? '收起计时' : '跳过等待'}
                </Text>
              </Pressable>
            </View>
          </View>
        ) : stepDurationSeconds(step) > 0 ? (
          <Pressable
            accessibilityRole="button"
            className="mt-6 flex-row items-center justify-center gap-2 rounded-full bg-white py-3 shadow-sm active:opacity-80 dark:bg-stone-900"
            onPress={() =>
              setTimer({
                remaining: stepDurationSeconds(step),
                running: true,
                totalSeconds: stepDurationSeconds(step),
              })
            }
          >
            <Ionicons color="#ea580c" name="timer-outline" size={18} />
            <Text className="text-sm font-semibold text-brand-700 dark:text-brand-500">
              开始 {step.duration} 分钟计时
            </Text>
          </Pressable>
        ) : null}

        {timeUp ? (
          <View className="mt-4 rounded-3xl bg-brand-50 p-5 dark:bg-stone-900">
            <View className="flex-row items-center gap-2">
              <Ionicons color="#ea580c" name="alarm-outline" size={18} />
              <Text className="flex-1 text-sm font-bold text-brand-700 dark:text-brand-500">
                时间到，可以进行下一步了
              </Text>
              {ringing ? (
                <Pressable
                  accessibilityRole="button"
                  className="rounded-full border border-brand-200 px-3 py-1.5 active:opacity-70 dark:border-stone-700"
                  hitSlop={6}
                  onPress={stopAlert}
                >
                  <Text className="text-xs font-semibold text-brand-700 dark:text-brand-500">
                    停止响铃
                  </Text>
                </Pressable>
              ) : null}
            </View>
            <Text className="mt-2 text-sm leading-6 text-stone-600 dark:text-stone-300">
              {nextStep
                ? `下一步：${nextStep.content}`
                : '最后一步完成了，盛盘上桌吧。'}
            </Text>
            <Pressable
              accessibilityRole="button"
              className="mt-4 items-center rounded-full bg-brand-600 py-3 active:opacity-90"
              onPress={goNext}
            >
              <Text className="text-sm font-semibold text-white">
                {nextStep ? '进入下一步' : '完成做菜'}
              </Text>
            </Pressable>
          </View>
        ) : null}
      </ScrollView>

      <View
        className="border-t border-stone-200 bg-white px-5 pt-3 dark:border-stone-800 dark:bg-stone-950"
        style={{ paddingBottom: insets.bottom + 12 }}
      >
        <View className="flex-row gap-3">
          <Pressable
            accessibilityRole="button"
            className={cn(
              'items-center justify-center rounded-full border px-5 py-3.5',
              stepIndex === 0
                ? 'border-stone-200 dark:border-stone-800'
                : 'border-stone-300 active:opacity-70 dark:border-stone-700',
            )}
            disabled={stepIndex === 0}
            onPress={goPrev}
          >
            <Text
              className={cn(
                'text-sm font-semibold',
                stepIndex === 0
                  ? 'text-stone-300 dark:text-stone-700'
                  : 'text-stone-600 dark:text-stone-300',
              )}
            >
              上一步
            </Text>
          </Pressable>
          <Pressable
            accessibilityRole="button"
            className="flex-1 flex-row items-center justify-center gap-2 rounded-full bg-brand-600 py-3.5 active:opacity-90"
            onPress={goNext}
          >
            <Text className="text-base font-semibold text-white">
              {isLastStep ? '完成做菜' : '下一步'}
            </Text>
            <Ionicons color="#ffffff" name="chevron-forward" size={16} />
          </Pressable>
        </View>
      </View>
    </View>
  );
}
