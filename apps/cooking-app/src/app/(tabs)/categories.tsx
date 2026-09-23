import { useQuery } from '@tanstack/react-query';
import { Link } from 'expo-router';
import {
  Pressable,
  RefreshControl,
  ScrollView,
  Text,
  View,
} from 'react-native';

import { EmptyState, ErrorState, LoadingState } from '@/components/state-views';
import { fetchRecipeCategories } from '@/lib/api/recipes';
import { categoryKeys } from '@/lib/query-keys';

const sections = [
  { key: 'dish', max: 100, min: 0, title: '按做法' },
  { key: 'cuisine', max: 200, min: 100, title: '按菜系' },
  { key: 'diet', max: Number.POSITIVE_INFINITY, min: 200, title: '按需求' },
];

export default function CategoriesScreen() {
  const { data, error, isLoading, isRefetching, refetch } = useQuery({
    queryFn: fetchRecipeCategories,
    queryKey: categoryKeys.list(),
  });

  const categories = data ?? [];
  const visibleSections = sections
    .map((section) => ({
      ...section,
      items: categories
        .filter(
          (category) =>
            category.sortOrder >= section.min &&
            category.sortOrder < section.max,
        )
        .sort((a, b) => a.sortOrder - b.sortOrder),
    }))
    .filter((section) => section.items.length > 0);

  return (
    <ScrollView
      className="flex-1 bg-stone-50 dark:bg-stone-950"
      contentContainerClassName="px-5 pb-8 pt-5"
      refreshControl={
        <RefreshControl
          onRefresh={() => void refetch()}
          refreshing={isRefetching}
        />
      }
      showsVerticalScrollIndicator={false}
    >
      <Text className="text-2xl font-bold text-stone-900 dark:text-stone-50">
        菜谱分类
      </Text>
      <Text className="mt-1 text-sm text-stone-500 dark:text-stone-400">
        按做法、菜系或需求挑一道
      </Text>

      {isLoading ? (
        <LoadingState message="正在整理分类…" />
      ) : error ? (
        <ErrorState error={error} onRetry={() => void refetch()} />
      ) : visibleSections.length === 0 ? (
        <EmptyState
          description="分类还在整理中，稍后再来看看。"
          title="暂无分类"
        />
      ) : (
        visibleSections.map((section) => (
          <View className="mt-6" key={section.key}>
            <Text className="mb-3 text-base font-bold text-stone-900 dark:text-stone-50">
              {section.title}
            </Text>
            <View className="flex-row flex-wrap justify-between">
              {section.items.map((category) => (
                <Link
                  asChild
                  href={{
                    pathname: '/category/[id]',
                    params: { id: category.id, name: category.name },
                  }}
                  key={category.id}
                >
                  <Pressable className="mb-3 w-[48%] rounded-2xl bg-white p-4 active:opacity-80 dark:bg-stone-900">
                    <Text className="text-2xl">{category.icon ?? '🍽️'}</Text>
                    <Text
                      className="mt-2 text-sm font-bold text-stone-900 dark:text-stone-50"
                      numberOfLines={1}
                    >
                      {category.name}
                    </Text>
                    {category.description ? (
                      <Text
                        className="mt-1 text-xs leading-4 text-stone-500 dark:text-stone-400"
                        numberOfLines={2}
                      >
                        {category.description}
                      </Text>
                    ) : null}
                  </Pressable>
                </Link>
              ))}
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );
}
