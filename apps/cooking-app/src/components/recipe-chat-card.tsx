import { Ionicons } from '@expo/vector-icons';
import type { Recipe } from '@po/types';
import { Link } from 'expo-router';
import { Pressable, Text, View } from 'react-native';

import { resolveAssetUrl } from '@/lib/api/client';
import { Image } from '@/lib/nativewind';
import { difficultyLabel, totalMinutes } from '@/lib/recipe-utils';

/** 聊天回复里的菜谱卡片，带「查看详情」和「开始做菜」两个入口 */
export function RecipeChatCard({ recipe }: { recipe: Recipe }) {
  const minutes = totalMinutes(recipe);
  const meta = [
    minutes ? `${minutes} 分钟` : undefined,
    difficultyLabel(recipe.difficulty),
    recipe.servings ? `${recipe.servings} 人份` : undefined,
  ]
    .filter(Boolean)
    .join(' · ');

  return (
    <View className="w-60 overflow-hidden rounded-2xl bg-white shadow-sm dark:bg-stone-900">
      {recipe.coverImageUrl ? (
        <Image
          accessibilityLabel={`${recipe.title}成品图`}
          className="h-24 w-full bg-stone-200 dark:bg-stone-800"
          contentFit="cover"
          source={resolveAssetUrl(recipe.coverImageUrl)}
          transition={150}
        />
      ) : (
        <View className="h-16 items-center justify-center bg-brand-50 dark:bg-stone-800">
          <Ionicons color="#ea580c" name="restaurant-outline" size={24} />
        </View>
      )}
      <View className="p-3">
        <Text
          className="text-sm font-bold text-stone-900 dark:text-stone-50"
          numberOfLines={1}
        >
          {recipe.title}
        </Text>
        <Text
          className="mt-1 text-xs text-stone-500 dark:text-stone-400"
          numberOfLines={1}
        >
          {meta}
        </Text>
        <View className="mt-3 flex-row gap-2">
          <Link
            asChild
            href={{ pathname: '/recipe/[id]', params: { id: recipe.id } }}
          >
            <Pressable className="flex-1 items-center rounded-full border border-stone-200 py-2 active:opacity-70 dark:border-stone-700">
              <Text className="text-xs font-semibold text-stone-600 dark:text-stone-300">
                查看详情
              </Text>
            </Pressable>
          </Link>
          <Link
            asChild
            href={{ pathname: '/cook/[id]', params: { id: recipe.id } }}
          >
            <Pressable className="flex-1 flex-row items-center justify-center gap-1 rounded-full bg-brand-600 py-2 active:opacity-80">
              <Ionicons color="#ffffff" name="flame" size={13} />
              <Text className="text-xs font-semibold text-white">开始做菜</Text>
            </Pressable>
          </Link>
        </View>
      </View>
    </View>
  );
}
