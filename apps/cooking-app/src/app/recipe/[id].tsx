import { Ionicons } from '@expo/vector-icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useLocalSearchParams, useRouter } from 'expo-router';
import type { ReactNode } from 'react';
import { useState } from 'react';
import {
  Pressable,
  ScrollView,
  Text,
  useColorScheme,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { RecipeMeta } from '@/components/recipe-meta';
import { RecipeStatusBadge } from '@/components/recipe-status-badge';
import { ErrorState, LoadingState } from '@/components/state-views';
import { resolveAssetUrl } from '@/lib/api/client';
import {
  favoriteRecipe,
  fetchRecipeDetail,
  toggleLikeRecipe,
  unfavoriteRecipe,
} from '@/lib/api/recipes';
import { Image } from '@/lib/nativewind';
import { recipeKeys } from '@/lib/query-keys';
import {
  formatIngredientAmount,
  sortSteps,
  splitTags,
} from '@/lib/recipe-utils';
import { cn } from '@/lib/utils';

export default function RecipeDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const recipeId = Number(id);
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const isDark = useColorScheme() === 'dark';
  const queryClient = useQueryClient();
  const [servings, setServings] = useState<number | null>(null);

  const { data, error, isLoading, refetch } = useQuery({
    enabled: Number.isFinite(recipeId),
    queryFn: () => fetchRecipeDetail(recipeId),
    queryKey: recipeKeys.detail(recipeId),
  });

  const favoriteMutation = useMutation({
    mutationFn: (favorited: boolean) =>
      favorited ? unfavoriteRecipe(recipeId) : favoriteRecipe(recipeId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: recipeKeys.detail(recipeId),
      });
      await queryClient.invalidateQueries({
        queryKey: recipeKeys.favorites(),
      });
      await queryClient.invalidateQueries({ queryKey: recipeKeys.all });
    },
  });

  const likeMutation = useMutation({
    mutationFn: () => toggleLikeRecipe(recipeId),
    onSuccess: async (result) => {
      queryClient.setQueryData(recipeKeys.detail(recipeId), (prev: unknown) =>
        prev && typeof prev === 'object'
          ? {
              ...prev,
              isLiked: result.liked,
              likesCount: result.likesCount,
            }
          : prev,
      );
      await queryClient.invalidateQueries({ queryKey: recipeKeys.all });
    },
  });

  const backButton = (
    <Pressable
      accessibilityLabel="返回"
      accessibilityRole="button"
      className="absolute left-4 h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm active:opacity-70 dark:bg-stone-900"
      hitSlop={8}
      onPress={() => router.back()}
      style={{ top: insets.top + 8 }}
    >
      <Ionicons
        color={isDark ? '#fafaf9' : '#1c1917'}
        name="chevron-back"
        size={22}
      />
    </Pressable>
  );

  if (isLoading) {
    return (
      <View className="flex-1 bg-stone-50 dark:bg-stone-950">
        <LoadingState message="正在翻开菜谱…" />
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

  const baseServings = data.servings && data.servings > 0 ? data.servings : 1;
  const effectiveServings = servings ?? baseServings;
  const amountScale = effectiveServings / baseServings;

  const ingredients = [...(data.ingredients ?? [])].sort(
    (a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0),
  );
  const steps = sortSteps(data.steps);
  const tags = splitTags(data.tags);
  const nutrition = [
    { label: '热量', unit: '千卡', value: data.calories },
    { label: '蛋白质', unit: 'g', value: data.protein },
    { label: '脂肪', unit: 'g', value: data.fat },
    { label: '碳水', unit: 'g', value: data.carbs },
  ].filter((item) => item.value);

  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <ScrollView
        contentContainerClassName="pb-32"
        showsVerticalScrollIndicator={false}
      >
        {data.coverImageUrl ? (
          <Image
            accessibilityLabel={`${data.title}成品图`}
            className="h-60 w-full bg-stone-200 dark:bg-stone-800"
            contentFit="cover"
            source={resolveAssetUrl(data.coverImageUrl)}
            transition={150}
          />
        ) : (
          <View className="h-44 items-center justify-center bg-brand-50 dark:bg-stone-900">
            <Ionicons color="#ea580c" name="restaurant-outline" size={44} />
          </View>
        )}

        <View className="px-5 pt-5">
          <Text className="text-2xl font-bold text-stone-900 dark:text-stone-50">
            {data.title}
          </Text>
          {data.status && data.status !== 'approved' ? (
            <View className="mt-2">
              <RecipeStatusBadge
                rejectReason={data.rejectReason}
                status={data.status}
              />
            </View>
          ) : null}
          {data.description ? (
            <Text className="mt-2 text-sm leading-6 text-stone-500 dark:text-stone-400">
              {data.description}
            </Text>
          ) : null}
          {tags.length > 0 ? (
            <View className="mt-3 flex-row flex-wrap gap-2">
              {tags.map((tag) => (
                <Text
                  className="rounded-full bg-white px-2.5 py-1 text-xs text-stone-600 dark:bg-stone-900 dark:text-stone-300"
                  key={tag}
                >
                  {tag}
                </Text>
              ))}
            </View>
          ) : null}
          <RecipeMeta className="mt-4" recipe={data} />

          {ingredients.length > 0 ? (
            <Section
              extra={
                <View className="flex-row items-center gap-3">
                  <Pressable
                    accessibilityLabel="减少份量"
                    accessibilityRole="button"
                    className={cn(
                      'h-7 w-7 items-center justify-center rounded-full border',
                      effectiveServings <= 1
                        ? 'border-stone-200 dark:border-stone-800'
                        : 'border-stone-300 active:opacity-70 dark:border-stone-700',
                    )}
                    disabled={effectiveServings <= 1}
                    hitSlop={6}
                    onPress={() =>
                      setServings(Math.max(1, effectiveServings - 1))
                    }
                  >
                    <Ionicons
                      color={
                        effectiveServings <= 1
                          ? isDark
                            ? '#44403c'
                            : '#d6d3d1'
                          : isDark
                            ? '#d6d3d1'
                            : '#57534e'
                      }
                      name="remove"
                      size={16}
                    />
                  </Pressable>
                  <Text className="text-sm font-semibold text-stone-900 dark:text-stone-50">
                    {effectiveServings} 人份
                  </Text>
                  <Pressable
                    accessibilityLabel="增加份量"
                    accessibilityRole="button"
                    className={cn(
                      'h-7 w-7 items-center justify-center rounded-full border',
                      effectiveServings >= 20
                        ? 'border-stone-200 dark:border-stone-800'
                        : 'border-stone-300 active:opacity-70 dark:border-stone-700',
                    )}
                    disabled={effectiveServings >= 20}
                    hitSlop={6}
                    onPress={() =>
                      setServings(Math.min(20, effectiveServings + 1))
                    }
                  >
                    <Ionicons
                      color={
                        effectiveServings >= 20
                          ? isDark
                            ? '#44403c'
                            : '#d6d3d1'
                          : isDark
                            ? '#d6d3d1'
                            : '#57534e'
                      }
                      name="add"
                      size={16}
                    />
                  </Pressable>
                </View>
              }
              title="用料"
            >
              <View className="overflow-hidden rounded-2xl bg-white dark:bg-stone-900">
                {ingredients.map((ingredient, index) => (
                  <View
                    className={cn(
                      'flex-row items-center justify-between gap-3 px-4 py-3',
                      index > 0 &&
                        'border-t border-stone-100 dark:border-stone-800',
                    )}
                    key={ingredient.id ?? ingredient.name}
                  >
                    <View className="flex-1 flex-row items-center gap-2">
                      <Text className="text-sm text-stone-800 dark:text-stone-100">
                        {ingredient.name}
                      </Text>
                      {ingredient.isEssential ? (
                        <Text className="rounded bg-brand-50 px-1.5 py-0.5 text-[10px] font-medium text-brand-700 dark:bg-stone-800 dark:text-brand-500">
                          必备
                        </Text>
                      ) : null}
                    </View>
                    <Text className="text-sm text-stone-500 dark:text-stone-400">
                      {formatIngredientAmount(ingredient, amountScale)}
                    </Text>
                  </View>
                ))}
              </View>
            </Section>
          ) : null}

          {steps.length > 0 ? (
            <Section title={`做法 · ${steps.length} 步`}>
              {steps.map((step) => (
                <View
                  className="mb-3 flex-row gap-3 rounded-2xl bg-white p-4 dark:bg-stone-900"
                  key={step.stepNumber}
                >
                  <View className="h-7 w-7 items-center justify-center rounded-full bg-brand-600">
                    <Text className="text-xs font-bold text-white">
                      {step.stepNumber}
                    </Text>
                  </View>
                  <View className="flex-1">
                    <Text className="text-sm leading-6 text-stone-800 dark:text-stone-100">
                      {step.content}
                    </Text>
                    {step.duration ? (
                      <View className="mt-2 flex-row items-center gap-1 self-start rounded-full bg-stone-100 px-2.5 py-1 dark:bg-stone-800">
                        <Ionicons
                          color="#78716c"
                          name="timer-outline"
                          size={13}
                        />
                        <Text className="text-xs text-stone-500 dark:text-stone-400">
                          约 {step.duration} 分钟
                        </Text>
                      </View>
                    ) : null}
                    {step.imageUrl ? (
                      <Image
                        accessibilityLabel={`第 ${step.stepNumber} 步`}
                        className="mt-3 h-40 w-full rounded-xl bg-stone-200 dark:bg-stone-800"
                        contentFit="cover"
                        source={resolveAssetUrl(step.imageUrl)}
                        transition={150}
                      />
                    ) : null}
                  </View>
                </View>
              ))}
            </Section>
          ) : null}

          {data.tips ? (
            <Section title="小贴士">
              <View className="flex-row gap-3 rounded-2xl bg-brand-50 p-4 dark:bg-stone-900">
                <Ionicons color="#ea580c" name="bulb-outline" size={18} />
                <Text className="flex-1 text-sm leading-6 text-stone-700 dark:text-stone-300">
                  {data.tips}
                </Text>
              </View>
            </Section>
          ) : null}

          {nutrition.length > 0 ? (
            <Section title={data.servings ? '营养 · 每份' : '营养'}>
              <View className="flex-row gap-3">
                {nutrition.map((item) => (
                  <View
                    className="flex-1 items-center rounded-2xl bg-white py-3 dark:bg-stone-900"
                    key={item.label}
                  >
                    <Text className="text-base font-bold text-stone-900 dark:text-stone-50">
                      {item.value}
                    </Text>
                    <Text className="mt-1 text-xs text-stone-500 dark:text-stone-400">
                      {item.label}
                      {item.unit}
                    </Text>
                  </View>
                ))}
              </View>
            </Section>
          ) : null}
        </View>
      </ScrollView>

      {backButton}

      <View
        className="absolute bottom-0 left-0 right-0 border-t border-stone-200 bg-white px-5 pt-3 dark:border-stone-800 dark:bg-stone-950"
        style={{ paddingBottom: insets.bottom + 12 }}
      >
        <View className="flex-row items-center gap-3">
          <Pressable
            accessibilityLabel={data.isFavorited ? '取消收藏' : '收藏'}
            accessibilityRole="button"
            className="items-center gap-0.5"
            disabled={favoriteMutation.isPending}
            hitSlop={6}
            onPress={() => favoriteMutation.mutate(Boolean(data.isFavorited))}
          >
            <Ionicons
              color={
                data.isFavorited ? '#ea580c' : isDark ? '#a8a29e' : '#78716c'
              }
              name={data.isFavorited ? 'bookmark' : 'bookmark-outline'}
              size={22}
            />
            <Text className="text-[10px] text-stone-500 dark:text-stone-400">
              {data.isFavorited ? '已收藏' : '收藏'}
            </Text>
          </Pressable>
          <Pressable
            accessibilityLabel="点赞"
            accessibilityRole="button"
            className="items-center gap-0.5"
            disabled={likeMutation.isPending}
            hitSlop={6}
            onPress={() => likeMutation.mutate()}
          >
            <Ionicons
              color={data.isLiked ? '#ea580c' : isDark ? '#a8a29e' : '#78716c'}
              name={data.isLiked ? 'heart' : 'heart-outline'}
              size={22}
            />
            <Text className="text-[10px] text-stone-500 dark:text-stone-400">
              {data.likesCount}
            </Text>
          </Pressable>
          {steps.length > 0 ? (
            <Link
              asChild
              href={{ pathname: '/cook/[id]', params: { id: recipeId } }}
            >
              <Pressable className="flex-1 flex-row items-center justify-center gap-2 rounded-full bg-brand-600 py-3.5 active:opacity-90">
                <Ionicons color="#ffffff" name="flame" size={18} />
                <Text className="text-base font-semibold text-white">
                  开始做菜
                </Text>
              </Pressable>
            </Link>
          ) : (
            <View className="flex-1 items-center rounded-full bg-stone-100 py-3.5 dark:bg-stone-900">
              <Text className="text-sm text-stone-500 dark:text-stone-400">
                这道菜还没有录入步骤
              </Text>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}

function Section({
  title,
  extra,
  children,
}: {
  title: string;
  extra?: ReactNode;
  children: ReactNode;
}) {
  return (
    <View className="mt-6">
      <View className="mb-3 flex-row items-center justify-between">
        <Text className="text-base font-bold text-stone-900 dark:text-stone-50">
          {title}
        </Text>
        {extra}
      </View>
      {children}
    </View>
  );
}
