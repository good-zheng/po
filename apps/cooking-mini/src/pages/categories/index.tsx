import { useEffect, useState } from 'react';
import { View, Text, ScrollView } from '@tarojs/components';
import Taro, { usePullDownRefresh } from '@tarojs/taro';
import type { RecipeCategory } from '@po/types';
import { fetchRecipeCategories } from '@/lib/api/recipes';
import './index.scss';

type CategorySection = {
  key: string;
  title: string;
  items: RecipeCategory[];
};

const SECTIONS = [
  { key: 'dish', min: 0, max: 100, title: '按做法' },
  { key: 'cuisine', min: 100, max: 200, title: '按菜系' },
  { key: 'diet', min: 200, max: Infinity, title: '按需求' },
];

export default function CategoriesPage() {
  const [categories, setCategories] = useState<RecipeCategory[]>([]);
  const [loading, setLoading] = useState(true);

  const loadCategories = async (force = false) => {
    try {
      const data = await fetchRecipeCategories(force);
      setCategories(data);
    } catch {
      Taro.showToast({ title: '分类加载失败', icon: 'none' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  // 分类结果被模块级缓存复用，下拉刷新要显式绕过缓存
  usePullDownRefresh(() => {
    loadCategories(true).then(() => Taro.stopPullDownRefresh());
  });

  const sections: CategorySection[] = SECTIONS.map((s) => ({
    key: s.key,
    title: s.title,
    items: categories
      .filter((c) => c.sortOrder >= s.min && c.sortOrder < s.max)
      .sort((a, b) => a.sortOrder - b.sortOrder),
  })).filter((s) => s.items.length > 0);

  const goToCategory = (id: number, name: string) => {
    Taro.navigateTo({ url: `/pages/category/detail?id=${id}&name=${encodeURIComponent(name)}` });
  };

  if (loading) {
    return (
      <View className="categories-page">
        <Text className="loading-text">正在整理分类…</Text>
      </View>
    );
  }

  if (sections.length === 0) {
    return (
      <View className="categories-page">
        <Text className="empty-text">暂无分类</Text>
      </View>
    );
  }

  return (
    <ScrollView className="categories-page" scrollY>
      <View className="page-header">
        <Text className="page-subtitle">按做法、菜系或需求挑一道</Text>
      </View>

      {sections.map((section) => (
        <View key={section.key} className="category-section">
          <Text className="section-title">{section.title}</Text>
          <View className="category-grid">
            {Array.from({ length: Math.ceil(section.items.length / 2) }, (_, i) => {
              const rowItems = section.items.slice(i * 2, i * 2 + 2);
              return (
                <View key={`row-${i}`} className="category-row">
                  {rowItems.map((cat) => (
                    <View
                      key={cat.id}
                      className="category-card"
                      onClick={() => goToCategory(cat.id, cat.name)}
                    >
                      <Text className="card-icon">{cat.icon || '\u{1F37D}\uFE0F'}</Text>
                      <Text className="card-name">{cat.name}</Text>
                      {cat.description ? (
                        <Text className="card-desc">{cat.description}</Text>
                      ) : null}
                    </View>
                  ))}
                </View>
              );
            })}
          </View>
        </View>
      ))}
    </ScrollView>
  );
}
