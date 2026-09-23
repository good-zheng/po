import type { RecipeSort } from '@po/types';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';
import { Text, View } from 'react-native';

import { RecipeFilterBar } from '@/components/recipe-filter-bar';
import { RecipeList } from '@/components/recipe-list';
import { fetchRecipeCategories, fetchRecipes } from '@/lib/api/recipes';
import { categoryKeys, recipeKeys } from '@/lib/query-keys';

export default function HomeScreen() {
  const [draftKeyword, setDraftKeyword] = useState('');
  const [keyword, setKeyword] = useState('');
  const [categoryId, setCategoryId] = useState<number | undefined>();
  const [difficulty, setDifficulty] = useState<number | undefined>();
  const [sort, setSort] = useState<RecipeSort>('recommend');

  const categoriesQuery = useQuery({
    queryFn: fetchRecipeCategories,
    queryKey: categoryKeys.list(),
  });

  const filter = useMemo(
    () => ({
      categoryIds: categoryId ? [categoryId] : undefined,
      difficulty,
      keyword,
      sort,
    }),
    [categoryId, difficulty, keyword, sort],
  );

  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <View className="px-5 pb-1 pt-5">
        <Text className="text-2xl font-bold text-stone-900 dark:text-stone-50">
          今天吃什么
        </Text>
        <Text className="mt-1 text-sm text-stone-500 dark:text-stone-400">
          从一顿好饭开始
        </Text>
      </View>
      <View className="px-5">
        <RecipeFilterBar
          categories={categoriesQuery.data ?? []}
          categoryId={categoryId}
          difficulty={difficulty}
          keyword={draftKeyword}
          onCategoryChange={setCategoryId}
          onDifficultyChange={setDifficulty}
          onKeywordChange={setDraftKeyword}
          onSearch={() => setKeyword(draftKeyword.trim())}
          onSortChange={setSort}
          sort={sort}
        />
      </View>
      <RecipeList
        emptyDescription="没有符合条件的菜谱，换个筛选条件试试。"
        emptyTitle="没有找到相关菜谱"
        fetchPage={(page, size) => fetchRecipes({ ...filter, page, size })}
        queryKey={recipeKeys.list(filter)}
        variant="grid"
      />
    </View>
  );
}
