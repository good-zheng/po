import { View } from 'react-native';

import { RecipeList } from '@/components/recipe-list';
import { ScreenHeader } from '@/components/screen-header';
import { fetchFavorites } from '@/lib/api/recipes';
import { recipeKeys } from '@/lib/query-keys';

export default function FavoritesScreen() {
  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <ScreenHeader subtitle="收藏过的菜谱" title="我的收藏" />
      <RecipeList
        emptyDescription="看到喜欢的菜谱，点右下角收藏就能在这里找到。"
        emptyTitle="还没有收藏"
        fetchPage={fetchFavorites}
        queryKey={recipeKeys.favorites()}
      />
    </View>
  );
}
