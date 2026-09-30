import { useMemo, useState } from 'react';
import { View, Text, Image } from '@tarojs/components';
import Taro, { useLoad } from '@tarojs/taro';
import type { Recipe } from '@po/types';
import { useAuth } from '@/lib/auth/auth-context';
import { saveReturnTo } from '@/lib/auth/return-path';
import { fetchRecipeDetail, favoriteRecipe, unfavoriteRecipe, likeRecipe } from '@/lib/api/recipes';
import { resolveAssetUrl } from '@/lib/api/client';
import { RecipeStatusBadge } from '@/components/recipe-status-badge';
import {
  FINISH_CLIP,
  prefetch as prefetchTts,
  stepClip,
} from '@/lib/tts';
import {
  difficultyLabel,
  formatIngredientAmount,
  sortSteps,
  splitTags,
  totalMinutes,
} from '@/lib/recipe-utils';
import './detail.scss';

export default function RecipeDetail() {
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [loading, setLoading] = useState(true);
  const [isFavorited, setIsFavorited] = useState(false);
  const [isLiked, setIsLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [servingsOverride, setServingsOverride] = useState<number | null>(null);
  const { status } = useAuth();

  const goCook = (recipeId: number) => {
    const url = `/pages/cook/index?id=${recipeId}`;
    if (status !== 'authenticated') {
      saveReturnTo(url);
      Taro.navigateTo({ url: '/pages/login/index' });
      return;
    }
    Taro.navigateTo({ url });
  };

  useLoad(() => {
    const pages = Taro.getCurrentPages();
    const currentPage = pages[pages.length - 1];
    const id = Number(currentPage.options?.id);
    if (!id) {
      Taro.showToast({ title: '菜谱不存在', icon: 'none' });
      return;
    }
    loadRecipe(id);
  });

  const loadRecipe = async (id: number) => {
    try {
      const data = await fetchRecipeDetail(id);
      setRecipe(data);
      setIsFavorited(!!data.isFavorited || !!data.favoritedAt);
      setIsLiked(!!data.isLiked);
      setLikesCount(data.likesCount || 0);
      // 进详情页就预热播报音频：用户看完详情点「开始做菜」时基本都已就绪
      const steps = sortSteps(data.steps);
      if (steps.length > 0) {
        prefetchTts(id, steps.map(stepClip));
        prefetchTts(0, [FINISH_CLIP]);
      }
    } catch {
      Taro.showToast({ title: '加载失败', icon: 'none' });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async () => {
    if (!recipe) return;
    try {
      if (isFavorited) {
        await unfavoriteRecipe(recipe.id);
        setIsFavorited(false);
        Taro.showToast({ title: '已取消收藏', icon: 'none' });
      } else {
        await favoriteRecipe(recipe.id);
        setIsFavorited(true);
        Taro.showToast({ title: '收藏成功', icon: 'success' });
      }
    } catch {
      Taro.showToast({ title: '操作失败', icon: 'none' });
    }
  };

  const handleToggleLike = async () => {
    if (!recipe) return;
    try {
      const result = await likeRecipe(recipe.id);
      setIsLiked(result.liked);
      setLikesCount(result.likesCount);
    } catch {
      Taro.showToast({ title: '操作失败', icon: 'none' });
    }
  };

  const derived = useMemo(() => {
    if (!recipe) return null;
    const baseServings = recipe.servings && recipe.servings > 0 ? recipe.servings : 1;
    const effectiveServings = servingsOverride ?? baseServings;
    const amountScale = effectiveServings / baseServings;
    const ingredients = [...(recipe.ingredients ?? [])].sort(
      (a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0),
    );
    const steps = sortSteps(recipe.steps);
    const tags = splitTags(recipe.tags);
    const minutes = totalMinutes(recipe);
    const nutrition = [
      { label: '热量', unit: '千卡', value: recipe.calories },
      { label: '蛋白质', unit: 'g', value: recipe.protein },
      { label: '脂肪', unit: 'g', value: recipe.fat },
      { label: '碳水', unit: 'g', value: recipe.carbs },
    ].filter((item) => item.value);
    return { baseServings, effectiveServings, amountScale, ingredients, steps, tags, minutes, nutrition };
  }, [recipe, servingsOverride]);

  if (loading) {
    return (
      <View className="recipe-detail">
        <Text className="loading-text">正在翻开菜谱…</Text>
      </View>
    );
  }

  if (!recipe || !derived) {
    return (
      <View className="recipe-detail">
        <Text className="loading-text">菜谱不存在</Text>
      </View>
    );
  }

  const { effectiveServings, amountScale, ingredients, steps, tags, minutes, nutrition } = derived;
  const hasSteps = steps.length > 0;

  return (
    <View className="recipe-detail">
      {recipe.coverImageUrl ? (
        <Image className="recipe-cover" src={resolveAssetUrl(recipe.coverImageUrl)} mode="aspectFill" />
      ) : (
        <View className="recipe-cover-placeholder">
          <Text className="cover-emoji">{'\u{1F37D}\uFE0F'}</Text>
        </View>
      )}

      <View className="detail-content">
        <Text className="recipe-title">{recipe.title}</Text>

        {recipe.status && recipe.status !== 'approved' ? (
          <View className="detail-status">
            <RecipeStatusBadge status={recipe.status} rejectReason={recipe.rejectReason} />
          </View>
        ) : null}

        {recipe.description ? <Text className="recipe-desc">{recipe.description}</Text> : null}

        {tags.length > 0 ? (
          <View className="tag-row">
            {tags.map((tag) => (
              <Text key={tag} className="tag-pill">{tag}</Text>
            ))}
          </View>
        ) : null}

        <View className="meta-row">
          {minutes ? <Text className="meta-item">{'\u{1F551}'} {minutes} 分钟</Text> : null}
          <Text className="meta-item">{'\u21D4'} {difficultyLabel(recipe.difficulty)}</Text>
          {recipe.servings ? <Text className="meta-item">{recipe.servings} 人份</Text> : null}
          {recipe.calories ? <Text className="meta-item">{'\u{1F525}'} {recipe.calories} 千卡</Text> : null}
        </View>

        {ingredients.length > 0 ? (
          <View className="section">
            <View className="section-head">
              <Text className="section-title">用料</Text>
              <View className="servings-stepper">
                <View
                  className={`step-btn ${effectiveServings <= 1 ? 'step-btn-disabled' : ''}`}
                  onClick={() => effectiveServings > 1 && setServingsOverride(Math.max(1, effectiveServings - 1))}
                >
                  <Text className="step-btn-text">{'\uFF0D'}</Text>
                </View>
                <Text className="servings-label">{effectiveServings} 人份</Text>
                <View
                  className={`step-btn ${effectiveServings >= 20 ? 'step-btn-disabled' : ''}`}
                  onClick={() => effectiveServings < 20 && setServingsOverride(Math.min(20, effectiveServings + 1))}
                >
                  <Text className="step-btn-text">{'+'}</Text>
                </View>
              </View>
            </View>
            <View className="ingredient-card">
              {ingredients.map((ing, idx) => (
                <View key={ing.id ?? ing.name} className={`ingredient ${idx > 0 ? 'ingredient-divided' : ''}`}>
                  <View className="ingredient-name-wrap">
                    <Text className="ingredient-name">{ing.name}</Text>
                    {ing.isEssential ? <Text className="essential-pill">必备</Text> : null}
                  </View>
                  <Text className="ingredient-amount">{formatIngredientAmount(ing, amountScale)}</Text>
                </View>
              ))}
            </View>
          </View>
        ) : null}

        {hasSteps ? (
          <View className="section">
            <Text className="section-title">做法 · {steps.length} 步</Text>
            {steps.map((step) => (
              <View key={step.stepNumber} className="step-card">
                <Text className="step-num">{step.stepNumber}</Text>
                <View className="step-body">
                  <Text className="step-text">{step.content}</Text>
                  {step.duration ? (
                    <View className="step-duration-chip">
                      <Text className="step-duration-text">{'\u23F1'} 约 {step.duration} 分钟</Text>
                    </View>
                  ) : null}
                  {step.imageUrl ? (
                    <Image className="step-image" src={resolveAssetUrl(step.imageUrl)} mode="aspectFill" />
                  ) : null}
                </View>
              </View>
            ))}
          </View>
        ) : null}

        {recipe.tips ? (
          <View className="section">
            <Text className="section-title">小贴士</Text>
            <View className="tips-card">
              <Text className="tips-icon">{'\u{1F4A1}'}</Text>
              <Text className="tips-text">{recipe.tips}</Text>
            </View>
          </View>
        ) : null}

        {nutrition.length > 0 ? (
          <View className="section">
            <Text className="section-title">{recipe.servings ? '营养 · 每份' : '营养'}</Text>
            <View className="nutrition-row">
              {nutrition.map((item) => (
                <View key={item.label} className="nutrition-cell">
                  <Text className="nutrition-value">{item.value}</Text>
                  <Text className="nutrition-label">{item.label}{item.unit}</Text>
                </View>
              ))}
            </View>
          </View>
        ) : null}
      </View>

      <View className="action-bar">
        <View className="action-btn" onClick={handleToggleFavorite}>
          <Text className={`action-icon ${isFavorited ? 'action-icon-active' : ''}`}>
            {isFavorited ? '\u2605' : '\u2606'}
          </Text>
          <Text className={`action-label ${isFavorited ? 'action-label-active' : ''}`}>
            {isFavorited ? '已收藏' : '收藏'}
          </Text>
        </View>
        <View className="action-btn" onClick={handleToggleLike}>
          <Text className={`action-icon ${isLiked ? 'action-icon-active' : ''}`}>
            {isLiked ? '\u2665' : '\u2661'}
          </Text>
          <Text className={`action-label ${isLiked ? 'action-label-active' : ''}`}>
            {likesCount > 0 ? likesCount : '点赞'}
          </Text>
        </View>
        {hasSteps ? (
          <View
            className="cook-btn"
            onClick={() => goCook(recipe.id)}
          >
            <Text className="cook-btn-text">{'\u{1F525}'} 开始做菜</Text>
          </View>
        ) : (
          <View className="cook-btn cook-btn-disabled">
            <Text className="cook-btn-hint">这道菜还没有录入步骤</Text>
          </View>
        )}
      </View>
    </View>
  );
}
