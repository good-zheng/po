import { Ionicons } from '@expo/vector-icons';
import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useRouter } from 'expo-router';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  RefreshControl,
  Text,
  View,
} from 'react-native';

import { RecipeCard } from '@/components/recipe-card';
import { RecipeStatusBadge } from '@/components/recipe-status-badge';
import { ScreenHeader } from '@/components/screen-header';
import { EmptyState, ErrorState, LoadingState } from '@/components/state-views';
import { deleteRecipe, fetchMyRecipes } from '@/lib/api/recipes';
import { recipeKeys } from '@/lib/query-keys';

const pageSize = 20;

export default function MyRecipesScreen() {
  const router = useRouter();
  const queryClient = useQueryClient();

  const {
    data,
    error,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    isRefetching,
    refetch,
  } = useInfiniteQuery({
    queryFn: ({ pageParam }) => fetchMyRecipes(pageParam, pageSize),
    initialPageParam: 0,
    queryKey: recipeKeys.mine(),
    getNextPageParam: (lastPage) =>
      lastPage.number + 1 < lastPage.totalPages
        ? lastPage.number + 1
        : undefined,
  });

  const recipes = data?.pages.flatMap((page) => page.content) ?? [];

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: recipeKeys.mine() });
    void queryClient.invalidateQueries({ queryKey: recipeKeys.all });
  };

  const handleDelete = (id: number, title: string) => {
    Alert.alert('删除菜谱', `确定删除「${title}」吗？删除后不可恢复。`, [
      { style: 'cancel', text: '取消' },
      {
        onPress: () => {
          void (async () => {
            try {
              await deleteRecipe(id);
              invalidate();
            } catch {
              Alert.alert('删除失败', '请稍后再试。');
            }
          })();
        },
        style: 'destructive',
        text: '删除',
      },
    ]);
  };

  const loadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      void fetchNextPage();
    }
  };

  return (
    <View className="flex-1 bg-stone-50 dark:bg-stone-950">
      <ScreenHeader
        subtitle="创建后需管理员审核通过才会公开"
        title="我的菜谱"
      />

      <FlatList
        contentContainerClassName="px-5 pb-28"
        data={recipes}
        keyExtractor={(recipe) => recipe.id.toString()}
        ListEmptyComponent={
          isLoading ? (
            <LoadingState />
          ) : error ? (
            <ErrorState error={error} onRetry={() => void refetch()} />
          ) : (
            <EmptyState
              description="点击右下角按钮，分享你的拿手菜。"
              title="还没有创建菜谱"
            />
          )
        }
        ListFooterComponent={
          isFetchingNextPage ? (
            <View className="py-3">
              <ActivityIndicator color="#ea580c" />
            </View>
          ) : null
        }
        onEndReached={loadMore}
        onEndReachedThreshold={0.6}
        refreshControl={
          <RefreshControl
            onRefresh={() => void refetch()}
            refreshing={isRefetching}
          />
        }
        renderItem={({ item }) => (
          <View className="mb-4 gap-2">
            <Link
              asChild
              href={{ pathname: '/recipe/[id]', params: { id: item.id } }}
            >
              <Pressable className="active:opacity-90">
                <RecipeCard recipe={item} />
              </Pressable>
            </Link>
            <View className="flex-row items-center justify-between">
              <RecipeStatusBadge
                rejectReason={item.rejectReason}
                status={item.status}
              />
              <View className="flex-row gap-4">
                <Pressable
                  accessibilityRole="button"
                  className="flex-row items-center gap-1"
                  onPress={() =>
                    router.push({
                      pathname: '/recipe/form',
                      params: { id: item.id },
                    })
                  }
                >
                  <Ionicons color="#78716c" name="pencil-outline" size={15} />
                  <Text className="text-sm text-stone-600 dark:text-stone-300">
                    编辑
                  </Text>
                </Pressable>
                <Pressable
                  accessibilityRole="button"
                  className="flex-row items-center gap-1"
                  onPress={() => handleDelete(item.id, item.title)}
                >
                  <Ionicons color="#dc2626" name="trash-outline" size={15} />
                  <Text className="text-sm text-red-600 dark:text-red-400">
                    删除
                  </Text>
                </Pressable>
              </View>
            </View>
          </View>
        )}
        showsVerticalScrollIndicator={false}
      />

      <Link asChild href="/recipe/form">
        <Pressable className="absolute bottom-6 right-5 h-14 w-14 items-center justify-center rounded-full bg-brand-600 shadow-lg active:opacity-90">
          <Ionicons color="#ffffff" name="add" size={28} />
        </Pressable>
      </Link>
    </View>
  );
}
