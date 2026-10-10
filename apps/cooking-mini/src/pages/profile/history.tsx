import { useCallback, useEffect, useState } from 'react';
import { View, Text, ScrollView, Image } from '@tarojs/components';
import Taro, { useReachBottom } from '@tarojs/taro';
import type { Recipe } from '@po/types';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { fetchHistory } from '@/lib/api/recipes';
import { resolveAssetUrl } from '@/lib/api/client';
import './list.scss';

const PAGE_SIZE = 20;

export default function HistoryPage() {
  return (
    <AuthGuard>
      <RecipeList title="浏览历史" fetcher={fetchHistory} />
    </AuthGuard>
  );
}

function RecipeList({
  title,
  fetcher,
}: {
  title: string;
  fetcher: (page: number, size: number) => Promise<{ content: Recipe[]; totalPages: number }>;
}) {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  const load = useCallback(
    async (pageNum: number, reset = false) => {
      if (loading) return;
      setLoading(true);
      try {
        const res = await fetcher(pageNum, PAGE_SIZE);
        const items = res.content || [];
        setRecipes((prev) => (reset ? items : [...prev, ...items]));
        setHasMore(pageNum < res.totalPages - 1);
        setPage(pageNum);
      } catch {
        Taro.showToast({ title: '加载失败', icon: 'none' });
      } finally {
        setLoading(false);
      }
    },
    [fetcher, loading],
  );

  useEffect(() => {
    load(0, true);
  }, []);

  useReachBottom(() => {
    if (hasMore && !loading) {
      load(page + 1);
    }
  });

  return (
    <View className="list-page">
      <Text className="list-title">{title}</Text>

      <ScrollView className="list-scroll" scrollY>
        {recipes.map((recipe) => (
          <View
            key={recipe.id}
            className="recipe-card"
            onClick={() => Taro.navigateTo({ url: `/pages/recipe/detail?id=${recipe.id}` })}
          >
            {recipe.coverImageUrl ? (
              <Image
                className="card-cover"
                src={resolveAssetUrl(recipe.coverImageUrl)}
                mode="aspectFill"
                lazyLoad
              />
            ) : (
              <View className="card-cover-placeholder">
                <Text className="placeholder-icon">🍽️</Text>
              </View>
            )}
            <View className="card-info">
              <Text className="card-name">{recipe.title}</Text>
              <Text className="card-desc">{recipe.description || '暂无描述'}</Text>
            </View>
          </View>
        ))}

        {loading ? (
          <View className="tip">
            <Text className="tip-text">加载中...</Text>
          </View>
        ) : null}

        {!hasMore && recipes.length > 0 ? (
          <View className="tip">
            <Text className="tip-text">没有更多了</Text>
          </View>
        ) : null}

        {recipes.length === 0 && !loading ? (
          <View className="tip">
            <Text className="tip-text">暂无内容</Text>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}
