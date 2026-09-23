import { Ionicons } from '@expo/vector-icons';
import type { RecipeCategory, RecipeSort } from '@po/types';
import { useState } from 'react';
import { Pressable, ScrollView, Text, TextInput, View } from 'react-native';

import { cn } from '@/lib/utils';

const sortOptions: Array<{ label: string; value: RecipeSort }> = [
  { label: '推荐', value: 'recommend' },
  { label: '最多点赞', value: 'likes' },
  { label: '最新发布', value: 'newest' },
];

const difficultyOptions: Array<{ label: string; value?: number }> = [
  { label: '不限', value: undefined },
  { label: '简单', value: 1 },
  { label: '中等', value: 2 },
  { label: '困难', value: 3 },
];

type RecipeFilterBarProps = {
  keyword: string;
  onKeywordChange: (value: string) => void;
  onSearch: () => void;
  sort: RecipeSort;
  onSortChange: (value: RecipeSort) => void;
  categoryId?: number;
  onCategoryChange: (value?: number) => void;
  difficulty?: number;
  onDifficultyChange: (value?: number) => void;
  categories: RecipeCategory[];
};

function Chip({
  active,
  label,
  onPress,
}: {
  active: boolean;
  label: string;
  onPress: () => void;
}) {
  return (
    <Pressable
      className={cn(
        'rounded-full border px-3.5 py-1.5',
        active
          ? 'border-brand-600 bg-brand-600'
          : 'border-stone-200 bg-white dark:border-stone-700 dark:bg-stone-900',
      )}
      onPress={onPress}
    >
      <Text
        className={cn(
          'text-sm',
          active
            ? 'font-medium text-white'
            : 'text-stone-700 dark:text-stone-300',
        )}
      >
        {label}
      </Text>
    </Pressable>
  );
}

export function RecipeFilterBar({
  keyword,
  onKeywordChange,
  onSearch,
  sort,
  onSortChange,
  categoryId,
  onCategoryChange,
  difficulty,
  onDifficultyChange,
  categories,
}: RecipeFilterBarProps) {
  const [focused, setFocused] = useState(false);

  return (
    <View className="gap-2.5 pb-3">
      <View
        className={cn(
          'flex-row items-center gap-2 rounded-full border bg-white px-4 py-2.5 dark:bg-stone-900',
          focused
            ? 'border-brand-600 dark:border-brand-500'
            : 'border-stone-200 dark:border-stone-700',
        )}
      >
        <Ionicons color="#a8a29e" name="search" size={16} />
        <TextInput
          className="flex-1 text-sm text-stone-900 dark:text-stone-50"
          onBlur={() => setFocused(false)}
          onChangeText={onKeywordChange}
          onFocus={() => setFocused(true)}
          onSubmitEditing={onSearch}
          placeholder="搜索菜谱名称"
          placeholderTextColor="#a8a29e"
          returnKeyType="search"
          submitBehavior="submit"
          value={keyword}
        />
        {keyword ? (
          <Pressable
            accessibilityLabel="清空"
            hitSlop={8}
            onPress={() => onKeywordChange('')}
          >
            <Ionicons color="#a8a29e" name="close-circle" size={16} />
          </Pressable>
        ) : null}
      </View>

      <ScrollView
        className="grow-0"
        contentContainerClassName="gap-2 pr-4"
        horizontal
        showsHorizontalScrollIndicator={false}
      >
        {sortOptions.map((option) => (
          <Chip
            active={sort === option.value}
            key={option.value}
            label={option.label}
            onPress={() => onSortChange(option.value)}
          />
        ))}
        <View className="mx-1 w-px bg-stone-200 dark:bg-stone-700" />
        {difficultyOptions.map((option) => (
          <Chip
            active={difficulty === option.value}
            key={option.label}
            label={`难度·${option.label}`}
            onPress={() => onDifficultyChange(option.value)}
          />
        ))}
      </ScrollView>

      <ScrollView
        className="grow-0"
        contentContainerClassName="gap-2 pr-4"
        horizontal
        showsHorizontalScrollIndicator={false}
      >
        <Chip
          active={categoryId === undefined}
          label="全部"
          onPress={() => onCategoryChange(undefined)}
        />
        {categories.map((category) => (
          <Chip
            active={categoryId === category.id}
            key={category.id}
            label={category.name}
            onPress={() =>
              onCategoryChange(
                categoryId === category.id ? undefined : category.id,
              )
            }
          />
        ))}
      </ScrollView>
    </View>
  );
}
