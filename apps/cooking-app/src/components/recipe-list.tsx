import { useInfiniteQuery } from '@tanstack/react-query';
import { Link } from 'expo-router';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  RefreshControl,
  View,
} from 'react-native';

import { RecipeCard, RecipeGridCard } from '@/components/recipe-card';
import { EmptyState, ErrorState, LoadingState } from '@/components/state-views';
import type { fetchRecipes } from '@/lib/api/recipes';

const pageSize = 20;

type RecipeListProps = {
  queryKey: readonly unknown[];
  fetchPage: (page: number, size: number) => ReturnType<typeof fetchRecipes>;
  variant?: 'feed' | 'grid';
  emptyTitle?: string;
  emptyDescription?: string;
  contentContainerClassName?: string;
};

export function RecipeList({
  queryKey,
  fetchPage,
  variant = 'feed',
  emptyTitle = '还没有菜谱',
  emptyDescription = '换个条件看看，或者稍后再来。',
  contentContainerClassName,
}: RecipeListProps) {
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
    queryKey,
    queryFn: ({ pageParam }) => fetchPage(pageParam, pageSize),
    initialPageParam: 0,
    getNextPageParam: (lastPage) =>
      lastPage.number + 1 < lastPage.totalPages
        ? lastPage.number + 1
        : undefined,
  });

  const recipes = data?.pages.flatMap((page) => page.content) ?? [];

  const loadMore = () => {
    if (hasNextPage && !isFetchingNextPage) {
      void fetchNextPage();
    }
  };

  const isGrid = variant === 'grid';
  // 网格下补齐一行，避免最后一张卡片独占整行宽度
  const rows: Array<(typeof recipes)[number] | null> =
    isGrid && recipes.length % 2 === 1 ? [...recipes, null] : recipes;

  const renderRecipe = (item: (typeof recipes)[number]) => (
    <Link asChild href={{ pathname: '/recipe/[id]', params: { id: item.id } }}>
      <Pressable
        className={isGrid ? 'flex-1 active:opacity-90' : 'active:opacity-90'}
      >
        {isGrid ? (
          <RecipeGridCard recipe={item} />
        ) : (
          <RecipeCard recipe={item} />
        )}
      </Pressable>
    </Link>
  );

  return (
    <FlatList
      columnWrapperClassName={isGrid ? 'gap-3' : undefined}
      contentContainerClassName={
        contentContainerClassName ?? (isGrid ? 'gap-1 px-4 pb-8' : 'px-5 pb-8')
      }
      data={rows}
      keyExtractor={(row) => (row ? row.id.toString() : 'grid-spacer')}
      ListEmptyComponent={
        isLoading ? (
          <LoadingState />
        ) : error ? (
          <ErrorState error={error} onRetry={() => void refetch()} />
        ) : (
          <EmptyState description={emptyDescription} title={emptyTitle} />
        )
      }
      ListFooterComponent={
        isFetchingNextPage ? (
          <View className="py-3">
            <ActivityIndicator color="#ea580c" />
          </View>
        ) : null
      }
      numColumns={isGrid ? 2 : 1}
      onEndReached={loadMore}
      onEndReachedThreshold={0.6}
      refreshControl={
        <RefreshControl
          onRefresh={() => void refetch()}
          refreshing={isRefetching}
        />
      }
      renderItem={({ item }) =>
        item ? renderRecipe(item) : <View className="flex-1" />
      }
      showsVerticalScrollIndicator={false}
    />
  );
}
