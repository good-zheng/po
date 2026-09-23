import { Ionicons } from '@expo/vector-icons';
import type { Recipe } from '@po/types';
import { Text, View } from 'react-native';

import { difficultyLabel, totalMinutes } from '@/lib/recipe-utils';
import { cn } from '@/lib/utils';

export function MetaItem({
  icon,
  label,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
}) {
  return (
    <View className="flex-row items-center gap-1">
      <Ionicons color="#78716c" name={icon} size={15} />
      <Text className="text-xs text-stone-500 dark:text-stone-400">
        {label}
      </Text>
    </View>
  );
}

export function RecipeMeta({
  recipe,
  className,
}: {
  recipe: Recipe;
  className?: string;
}) {
  const minutes = totalMinutes(recipe);

  return (
    <View
      className={cn(
        'flex-row flex-wrap items-center gap-x-4 gap-y-2',
        className,
      )}
    >
      {minutes ? (
        <MetaItem icon="time-outline" label={`${minutes} 分钟`} />
      ) : null}
      <MetaItem
        icon="speedometer-outline"
        label={difficultyLabel(recipe.difficulty)}
      />
      {recipe.servings ? (
        <MetaItem icon="people-outline" label={`${recipe.servings} 人份`} />
      ) : null}
      {recipe.calories ? (
        <MetaItem icon="flame-outline" label={`${recipe.calories} 千卡`} />
      ) : null}
    </View>
  );
}
