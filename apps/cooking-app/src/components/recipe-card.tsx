import { Ionicons } from '@expo/vector-icons';
import type { Recipe } from '@po/types';
import { Text, View } from 'react-native';

import { MetaItem } from '@/components/recipe-meta';
import { resolveAssetUrl } from '@/lib/api/client';
import { Image } from '@/lib/nativewind';
import { difficultyLabel, splitTags, totalMinutes } from '@/lib/recipe-utils';

type RecipeCardProps = {
  recipe: Recipe;
};

export function RecipeCard({ recipe }: RecipeCardProps) {
  const tags = splitTags(recipe.tags).slice(0, 3);
  const minutes = totalMinutes(recipe);

  return (
    <View className="mb-4 overflow-hidden rounded-3xl bg-white shadow-sm dark:bg-stone-900">
      {recipe.coverImageUrl ? (
        <Image
          accessibilityLabel={`${recipe.title}成品图`}
          className="h-48 w-full bg-stone-200 dark:bg-stone-800"
          contentFit="cover"
          source={resolveAssetUrl(recipe.coverImageUrl)}
          transition={150}
        />
      ) : (
        <View className="h-32 items-center justify-center bg-brand-50 dark:bg-stone-800">
          <Ionicons color="#ea580c" name="restaurant-outline" size={36} />
        </View>
      )}
      <View className="p-4">
        <View className="flex-row items-start justify-between gap-3">
          <Text
            className="flex-1 text-lg font-bold text-stone-900 dark:text-stone-50"
            numberOfLines={1}
          >
            {recipe.title}
          </Text>
          {recipe.category ? (
            <Text className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-medium text-brand-700">
              {recipe.category}
            </Text>
          ) : null}
        </View>
        {recipe.description ? (
          <Text
            className="mt-2 text-sm leading-5 text-stone-500 dark:text-stone-400"
            numberOfLines={2}
          >
            {recipe.description}
          </Text>
        ) : null}
        <View className="mt-3 flex-row flex-wrap items-center gap-x-4 gap-y-2">
          {minutes ? (
            <MetaItem icon="time-outline" label={`${minutes} 分钟`} />
          ) : null}
          {recipe.servings ? (
            <MetaItem icon="people-outline" label={`${recipe.servings} 人份`} />
          ) : null}
          {recipe.likesCount > 0 ? (
            <MetaItem icon="heart-outline" label={`${recipe.likesCount}`} />
          ) : null}
        </View>
        {tags.length ? (
          <View className="mt-3 flex-row flex-wrap gap-2">
            {tags.map((tag) => (
              <Text
                className="rounded-full bg-stone-100 px-2.5 py-1 text-xs text-stone-600 dark:bg-stone-800 dark:text-stone-300"
                key={tag}
              >
                {tag}
              </Text>
            ))}
          </View>
        ) : null}
      </View>
    </View>
  );
}

/** 双列网格卡片（首页瀑布流）：大图 + 标题 + 元信息 */
export function RecipeGridCard({ recipe }: RecipeCardProps) {
  const minutes = totalMinutes(recipe);

  return (
    <View className="mb-3 flex-1 overflow-hidden rounded-2xl bg-white shadow-sm dark:bg-stone-900">
      {recipe.coverImageUrl ? (
        <View>
          <Image
            accessibilityLabel={`${recipe.title}成品图`}
            className="h-40 w-full bg-stone-200 dark:bg-stone-800"
            contentFit="cover"
            source={resolveAssetUrl(recipe.coverImageUrl)}
            transition={150}
          />
          {recipe.category ? (
            <View className="absolute left-2 top-2 rounded-full bg-black/50 px-2 py-0.5">
              <Text className="text-[10px] font-medium text-white">
                {recipe.category}
              </Text>
            </View>
          ) : null}
        </View>
      ) : (
        <View className="h-28 items-center justify-center bg-brand-50 dark:bg-stone-800">
          <Ionicons color="#ea580c" name="restaurant-outline" size={30} />
        </View>
      )}
      <View className="gap-1.5 p-3">
        <Text
          className="text-sm font-semibold leading-5 text-stone-900 dark:text-stone-50"
          numberOfLines={2}
        >
          {recipe.title}
        </Text>
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-1">
            <Ionicons color="#a8a29e" name="barbell-outline" size={12} />
            <Text className="text-xs text-stone-500 dark:text-stone-400">
              {difficultyLabel(recipe.difficulty)}
            </Text>
          </View>
          {minutes ? (
            <View className="flex-row items-center gap-1">
              <Ionicons color="#a8a29e" name="time-outline" size={12} />
              <Text className="text-xs text-stone-500 dark:text-stone-400">
                {minutes} 分钟
              </Text>
            </View>
          ) : null}
        </View>
        <View className="flex-row items-center justify-between">
          <View className="flex-row items-center gap-1">
            <Ionicons
              color={recipe.isLiked ? '#ea580c' : '#a8a29e'}
              name={recipe.isLiked ? 'heart' : 'heart-outline'}
              size={12}
            />
            <Text className="text-xs text-stone-500 dark:text-stone-400">
              {recipe.likesCount}
            </Text>
          </View>
          {recipe.isFavorited ? (
            <Ionicons color="#ea580c" name="bookmark" size={12} />
          ) : null}
        </View>
      </View>
    </View>
  );
}
