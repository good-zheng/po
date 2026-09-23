import { useQuery } from '@tanstack/react-query';
import { useLocalSearchParams } from 'expo-router';
import { View } from 'react-native';

import { RecipeList } from '@/components/recipe-list';
import { ScreenHeader } from '@/components/screen-header';
import { fetchRecipeCategories, fetchRecipes } from '@/lib/api/recipes';
import { categoryKeys, recipeKeys } from '@/lib/query-keys';

export default function CategoryRecipesScreen() {
  const { id, name } = useLocalSearchParams<{ id: string; name?: string }>();
  const categoryId = Number(id);

  const { data: categories } = useQuery({
    queryFn: fetchRecipeCategories,
    queryKey: categoryKeys.list(),
  });
  const category = categories?.find((item) => item.id === categoryId);
  const title = name ?? category?.name ?? '分类菜谱';

  const filter = { categoryIds: [categoryId] };

  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <ScreenHeader
        subtitle={category?.description ?? undefined}
        title={title}
      />
      <RecipeList
        emptyDescription="这个分类下还没有菜谱，换一个看看。"
        fetchPage={(page, size) => fetchRecipes({ ...filter, page, size })}
        queryKey={recipeKeys.list(filter)}
      />
    </View>
  );
}
