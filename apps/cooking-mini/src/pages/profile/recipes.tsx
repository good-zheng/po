import { useCallback, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro, { useDidShow, usePullDownRefresh, useReachBottom } from '@tarojs/taro';
import type { Recipe } from '@po/types';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { deleteRecipe, fetchMyRecipes } from '@/lib/api/recipes';
import { RecipeFeedCard } from '@/components/recipe-card';
import { RecipeStatusBadge } from '@/components/recipe-status-badge';
import './recipes.scss';

const PAGE_SIZE = 20;

export default function MyRecipesPage() {
  return (
    <AuthGuard>
      <MyRecipesView />
    </AuthGuard>
  );
}

function MyRecipesView() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(
    async (pageNum: number, reset = false) => {
      if (loading) return;
      setLoading(true);
      try {
        const res = await fetchMyRecipes(pageNum, PAGE_SIZE);
        const items = res.content || [];
        setRecipes((prev) => (reset ? items : [...prev, ...items]));
        setHasMore(pageNum < res.totalPages - 1);
        setPage(pageNum);
      } catch {
        Taro.showToast({ title: '加载失败', icon: 'none' });
      } finally {
        setLoading(false);
        setLoaded(true);
      }
    },
    [loading],
  );

  // 从新建/编辑页返回时刷新，确保审核状态与新增项即时可见
  useDidShow(() => {
    load(0, true);
  });

  useReachBottom(() => {
    if (hasMore && !loading) {
      load(page + 1);
    }
  });

  usePullDownRefresh(() => {
    load(0, true).finally(() => Taro.stopPullDownRefresh());
  });

  const handleDelete = (recipe: Recipe) => {
    Taro.showModal({
      title: '删除菜谱',
      content: `确定删除「${recipe.title}」吗？删除后不可恢复。`,
      confirmText: '删除',
      confirmColor: '#dc2626',
      success: (res) => {
        if (!res.confirm) return;
        deleteRecipe(recipe.id)
          .then(() => {
            Taro.showToast({ title: '已删除', icon: 'success' });
            load(0, true);
          })
          .catch(() => Taro.showToast({ title: '删除失败', icon: 'none' }));
      },
    });
  };

  const openForm = (id?: number) => {
    Taro.navigateTo({
      url: id ? `/pages/recipe/form?id=${id}` : '/pages/recipe/form',
    });
  };

  return (
    <View className="my-recipes">
      <View className="my-recipes-header">
        <Text className="my-recipes-title">我的菜谱</Text>
        <Text className="my-recipes-sub">创建后需管理员审核通过才会公开</Text>
      </View>

      <ScrollView className="my-recipes-scroll" scrollY>
        {recipes.map((recipe) => (
          <View key={recipe.id} className="my-recipe-item">
            <View
              className="my-recipe-card"
              onClick={() =>
                Taro.navigateTo({ url: `/pages/recipe/detail?id=${recipe.id}` })
              }
            >
              <RecipeFeedCard recipe={recipe} />
            </View>
            <View className="my-recipe-foot">
              <RecipeStatusBadge status={recipe.status} rejectReason={recipe.rejectReason} />
              <View className="my-recipe-actions">
                <View className="action-btn" onClick={() => openForm(recipe.id)}>
                  <Text className="action-icon">{'\u270E'}</Text>
                  <Text className="action-text">编辑</Text>
                </View>
                <View className="action-btn action-btn-danger" onClick={() => handleDelete(recipe)}>
                  <Text className="action-icon action-icon-danger">{'\u{1F5D1}'}</Text>
                  <Text className="action-text action-text-danger">删除</Text>
                </View>
              </View>
            </View>
          </View>
        ))}

        {loaded && recipes.length === 0 && !loading ? (
          <View className="empty-view">
            <Text className="empty-icon">{'\u{1F373}'}</Text>
            <Text className="empty-title">还没有创建菜谱</Text>
            <Text className="empty-desc">点击右下角按钮，分享你的拿手菜。</Text>
          </View>
        ) : null}

        {loading ? (
          <View className="tip">
            <Text className="tip-text">加载中…</Text>
          </View>
        ) : null}

        {!hasMore && recipes.length > 0 ? (
          <View className="tip">
            <Text className="tip-text">没有更多了</Text>
          </View>
        ) : null}
      </ScrollView>

      <View className="fab" onClick={() => openForm()}>
        <Text className="fab-icon">{'+'}</Text>
      </View>
    </View>
  );
}
