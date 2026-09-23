import { View } from 'react-native';

import { RecipeList } from '@/components/recipe-list';
import { ScreenHeader } from '@/components/screen-header';
import { fetchHistory } from '@/lib/api/recipes';
import { recipeKeys } from '@/lib/query-keys';

export default function HistoryScreen() {
  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <ScreenHeader subtitle="最近看过的菜谱" title="浏览历史" />
      <RecipeList
        emptyDescription="去首页逛逛，看过的菜谱会出现在这里。"
        emptyTitle="还没有浏览记录"
        fetchPage={fetchHistory}
        queryKey={recipeKeys.history()}
      />
    </View>
  );
}
