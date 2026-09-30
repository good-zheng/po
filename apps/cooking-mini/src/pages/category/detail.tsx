import { useCallback, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro, { useLoad, useReachBottom, usePullDownRefresh } from '@tarojs/taro';
import type { Recipe } from '@po/types';
import { fetchRecipes, fetchRecipeCategories } from '@/lib/api/recipes';
import { RecipeGrid } from '@/components/recipe-card';
import './detail.scss';

const PAGE_SIZE = 20;

export default function CategoryDetail() {
  const [categoryId, setCategoryId] = useState<number>(0);
  const [categoryName, setCategoryName] = useState('');
  const [categoryDesc, setCategoryDesc] = useState<string | null>(null);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(true);

  useLoad(() => {
    const pages = Taro.getCurrentPages();
    const currentPage = pages[pages.length - 1];
    const id = Number(currentPage.options?.id);
    const name = currentPage.options?.name ? decodeURIComponent(currentPage.options.name) : '';
    if (!id) {
      Taro.showToast({ title: '分类不存在', icon: 'none' });
      return;
    }
    setCategoryId(id);
    setCategoryName(name);
    loadCategoryInfo(id, name);
    loadRecipes(id, 0, true);
  });

  const loadCategoryInfo = async (id: number, fallbackName: string) => {
    try {
      const cats = await fetchRecipeCategories();
      const cat = cats.find((c) => c.id === id);
      if (cat) {
        setCategoryName(cat.name);
        setCategoryDesc(cat.description);
        Taro.setNavigationBarTitle({ title: cat.name });
      } else if (fallbackName) {
        Taro.setNavigationBarTitle({ title: fallbackName });
      }
    } catch {
      if (fallbackName) {
        Taro.setNavigationBarTitle({ title: fallbackName });
      }
    }
  };

  const loadRecipes = useCallback(
    async (catId: number, pageNum: number, reset = false) => {
      if (loading && !reset) return;
      setLoading(true);
      try {
        const res = await fetchRecipes({
          categoryIds: [catId],
          page: pageNum,
          size: PAGE_SIZE,
          sort: 'recommend',
        });
        const newRecipes = res.content || [];
        if (reset) {
          setRecipes(newRecipes);
        } else {
          setRecipes((prev) => [...prev, ...newRecipes]);
        }
        setHasMore(pageNum < res.totalPages - 1);
        setPage(pageNum);
      } catch {
        Taro.showToast({ title: '加载失败', icon: 'none' });
      } finally {
        setLoading(false);
      }
    },
    [loading],
  );

  useReachBottom(() => {
    if (hasMore && !loading) {
      loadRecipes(categoryId, page + 1);
    }
  });

  usePullDownRefresh(() => {
    loadRecipes(categoryId, 0, true).then(() => Taro.stopPullDownRefresh());
  });

  const goToRecipe = (id: number) => {
    Taro.navigateTo({ url: `/pages/recipe/detail?id=${id}` });
  };

  if (loading && recipes.length === 0) {
    return (
      <View className="category-detail">
        <Text className="loading-text">加载中...</Text>
      </View>
    );
  }

  return (
    <ScrollView className="category-detail" scrollY>
      {categoryDesc ? (
        <View className="category-header">
          <Text className="category-name">{categoryName}</Text>
          <Text className="category-desc">{categoryDesc}</Text>
        </View>
      ) : (
        <View className="category-header">
          <Text className="category-name">{categoryName}</Text>
        </View>
      )}

      <RecipeGrid recipes={recipes} onSelect={goToRecipe} />

      {loading ? (
        <View className="loading-tip">
          <Text className="loading-text-small">加载中...</Text>
        </View>
      ) : null}

      {!hasMore && recipes.length > 0 ? (
        <View className="loading-tip">
          <Text className="loading-text-small">没有更多了</Text>
        </View>
      ) : null}

      {recipes.length === 0 && !loading ? (
        <View className="empty-tip">
          <Text className="empty-title">这个分类下还没有菜谱</Text>
          <Text className="empty-desc">换一个看看</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}
