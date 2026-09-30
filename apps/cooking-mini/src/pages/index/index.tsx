import { useCallback, useEffect, useMemo, useState } from 'react';
import { View, Text, Input, ScrollView } from '@tarojs/components';
import Taro, { useReachBottom, usePullDownRefresh } from '@tarojs/taro';
import type { Recipe, RecipeCategory, RecipeSort } from '@po/types';
import { fetchRecipes, fetchRecipeCategories } from '@/lib/api/recipes';
import { RecipeGrid } from '@/components/recipe-card';
import './index.scss';

const PAGE_SIZE = 20;
const HISTORY_KEY = 'search_history';
const MAX_HISTORY = 10;

const DIFFICULTY_OPTIONS: { label: string; value: number | undefined }[] = [
  { label: '难度-不限', value: undefined },
  { label: '简单', value: 1 },
  { label: '中等', value: 2 },
  { label: '困难', value: 3 },
];

const SORT_OPTIONS: { label: string; value: RecipeSort }[] = [
  { label: '推荐', value: 'recommend' },
  { label: '最多点赞', value: 'likes' },
  { label: '最新发布', value: 'newest' },
];

function getHistory(): string[] {
  try {
    const raw = Taro.getStorageSync(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveHistory(list: string[]) {
  Taro.setStorageSync(HISTORY_KEY, JSON.stringify(list));
}

export default function Index() {
  return <RecipeList />;
}

function RecipeList() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [categories, setCategories] = useState<RecipeCategory[]>([]);
  const [keyword, setKeyword] = useState('');
  const [categoryId, setCategoryId] = useState<number | undefined>();
  const [difficulty, setDifficulty] = useState<number | undefined>();
  const [sort, setSort] = useState<RecipeSort>('recommend');
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    setHistory(getHistory());
    fetchRecipeCategories()
      .then(setCategories)
      .catch(() => {
        Taro.showToast({ title: '分类加载失败', icon: 'none' });
      });
  }, []);

  const filter = useMemo(
    () => ({
      categoryIds: categoryId ? [categoryId] : undefined,
      difficulty,
      keyword,
      sort,
    }),
    [categoryId, difficulty, keyword, sort],
  );

  const loadRecipes = useCallback(
    async (pageNum: number, reset = false) => {
      if (loading) return;
      setLoading(true);
      try {
        const res = await fetchRecipes({
          ...filter,
          page: pageNum,
          size: PAGE_SIZE,
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
    [filter, loading],
  );

  useEffect(() => {
    loadRecipes(0, true);
  }, [filter]);

  useReachBottom(() => {
    if (hasMore && !loading) {
      loadRecipes(page + 1);
    }
  });

  usePullDownRefresh(() => {
    loadRecipes(0, true).then(() => Taro.stopPullDownRefresh());
  });

  const addHistory = (term: string) => {
    const trimmed = term.trim();
    if (!trimmed) return;
    const next = [trimmed, ...history.filter((h) => h !== trimmed)].slice(0, MAX_HISTORY);
    setHistory(next);
    saveHistory(next);
  };

  const clearHistory = () => {
    setHistory([]);
    saveHistory([]);
  };

  const handleSearch = (term?: string) => {
    const searchTerm = term ?? keyword;
    if (searchTerm.trim()) {
      setKeyword(searchTerm.trim());
      addHistory(searchTerm.trim());
    } else {
      setKeyword('');
    }
    setShowHistory(false);
  };

  const selectHistory = (term: string) => {
    setKeyword(term);
    handleSearch(term);
  };

  const goToRecipe = (id: number) => {
    Taro.navigateTo({ url: `/pages/recipe/detail?id=${id}` });
  };

  return (
    <View className="index">
      <View className="header">
        <Text className="title">今天吃什么</Text>
        <Text className="subtitle">从一顿好饭开始</Text>
      </View>

      <View className="search-section">
        <View className="search-bar">
          <Text className="search-icon">{'\u{1F50D}'}</Text>
          <Input
            className="search-input"
            placeholder="搜索菜谱名称"
            value={keyword}
            onInput={(e) => {
              setKeyword(e.detail.value);
              setShowHistory(true);
            }}
            onConfirm={() => handleSearch()}
            onFocus={() => setShowHistory(true)}
          />
        </View>
        {showHistory && history.length > 0 ? (
          <View className="history-panel">
            <View className="history-header">
              <Text className="history-title">搜索历史</Text>
              <Text className="history-clear" onClick={clearHistory}>
                清空
              </Text>
            </View>
            <View className="history-tags">
              {history.map((h) => (
                <View key={h} className="history-tag" onClick={() => selectHistory(h)}>
                  <Text className="history-tag-text">{h}</Text>
                </View>
              ))}
            </View>
          </View>
        ) : null}
      </View>

      <ScrollView className="sort-row" scrollX>
        <View className="sort-row-inner">
          {SORT_OPTIONS.map((opt) => (
            <View
              key={opt.label}
              className={`sort-chip ${sort === opt.value ? 'sort-chip-active' : ''}`}
              onClick={() => setSort(opt.value)}
            >
              <Text className={`sort-chip-text ${sort === opt.value ? 'sort-chip-text-active' : ''}`}>
                {opt.label}
              </Text>
            </View>
          ))}
          <View className="sort-divider" />
          {DIFFICULTY_OPTIONS.map((opt) => (
            <View
              key={opt.label}
              className={`difficulty-chip ${difficulty === opt.value ? 'difficulty-chip-active' : ''}`}
              onClick={() => setDifficulty(opt.value)}
            >
              <Text className={`difficulty-chip-text ${difficulty === opt.value ? 'difficulty-chip-text-active' : ''}`}>
                {opt.label}
              </Text>
            </View>
          ))}
        </View>
      </ScrollView>

      {categories.length > 0 ? (
        <ScrollView className="category-bar" scrollX>
          <View className="category-bar-inner">
            <View
              className={`category-chip ${!categoryId ? 'category-chip-active' : ''}`}
              onClick={() => setCategoryId(undefined)}
            >
              <Text className={`category-chip-text ${!categoryId ? 'category-chip-text-active' : ''}`}>
                全部
              </Text>
            </View>
            {categories.map((cat) => (
              <View
                key={cat.id}
                className={`category-chip ${categoryId === cat.id ? 'category-chip-active' : ''}`}
                onClick={() => setCategoryId(categoryId === cat.id ? undefined : cat.id)}
              >
                <Text className={`category-chip-text ${categoryId === cat.id ? 'category-chip-text-active' : ''}`}>
                  {cat.name}
                </Text>
              </View>
            ))}
          </View>
        </ScrollView>
      ) : null}

      <RecipeGrid recipes={recipes} onSelect={goToRecipe} />

      {loading ? (
        <View className="loading-tip">
          <Text className="loading-text">加载中...</Text>
        </View>
      ) : null}

      {!hasMore && recipes.length > 0 ? (
        <View className="loading-tip">
          <Text className="loading-text">没有更多了</Text>
        </View>
      ) : null}

      {recipes.length === 0 && !loading ? (
        <View className="empty-tip">
          <Text className="empty-title">没有找到相关菜谱</Text>
          <Text className="empty-desc">换个筛选条件试试</Text>
        </View>
      ) : null}
    </View>
  );
}
