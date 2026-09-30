import { useMemo, useState } from 'react';
import { View, Text, Image, Input, Textarea, ScrollView } from '@tarojs/components';
import Taro, { useLoad } from '@tarojs/taro';
import type { RecipeCategory, RecipeRequest } from '@po/types';
import { AuthGuard } from '@/lib/auth/auth-guard';
import { resolveAssetUrl } from '@/lib/api/client';
import {
  createRecipe,
  fetchRecipeCategories,
  fetchRecipeDetail,
  updateRecipe,
  uploadRecipeCover,
} from '@/lib/api/recipes';
import './form.scss';

const DIFFICULTY_OPTIONS = [
  { label: '简单', value: 1 },
  { label: '中等', value: 2 },
  { label: '困难', value: 3 },
];

type IngredientDraft = {
  key: string;
  name: string;
  amount: string;
  unit: string;
  isEssential: boolean;
};

type StepDraft = {
  key: string;
  content: string;
  duration: string;
};

let draftSeq = 0;
const nextDraftKey = () => `draft-${++draftSeq}`;
const emptyIngredient = (): IngredientDraft => ({
  key: nextDraftKey(),
  name: '',
  amount: '',
  unit: '',
  isEssential: true,
});
const emptyStep = (): StepDraft => ({ key: nextDraftKey(), content: '', duration: '' });

export default function RecipeFormPage() {
  return (
    <AuthGuard>
      <RecipeFormView />
    </AuthGuard>
  );
}

function RecipeFormView() {
  const [recipeId, setRecipeId] = useState<number | undefined>();
  const [categories, setCategories] = useState<RecipeCategory[]>([]);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploadingCover, setUploadingCover] = useState(false);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState<string | undefined>();
  const [difficulty, setDifficulty] = useState(1);
  const [prepTime, setPrepTime] = useState('');
  const [cookTime, setCookTime] = useState('');
  const [servings, setServings] = useState('');
  const [tags, setTags] = useState('');
  const [coverImageUrl, setCoverImageUrl] = useState('');
  const [tips, setTips] = useState('');
  const [ingredients, setIngredients] = useState<IngredientDraft[]>([emptyIngredient()]);
  const [steps, setSteps] = useState<StepDraft[]>([emptyStep()]);

  const isEdit = Number.isFinite(recipeId);

  useLoad(() => {
    const pages = Taro.getCurrentPages();
    const raw = pages[pages.length - 1].options?.id;
    const id = raw ? Number(raw) : undefined;

    fetchRecipeCategories()
      .then(setCategories)
      .catch(() => undefined);

    if (!id) {
      return;
    }
    setRecipeId(id);
    Taro.setNavigationBarTitle({ title: '编辑菜谱' });
    setLoadingDetail(true);
    fetchRecipeDetail(id)
      .then((recipe) => {
        setTitle(recipe.title);
        setDescription(recipe.description ?? '');
        setCategory(recipe.category ?? undefined);
        setDifficulty(recipe.difficulty || 1);
        setPrepTime(recipe.prepTime ? String(recipe.prepTime) : '');
        setCookTime(recipe.cookTime ? String(recipe.cookTime) : '');
        setServings(recipe.servings ? String(recipe.servings) : '');
        setTags(recipe.tags ?? '');
        setCoverImageUrl(recipe.coverImageUrl ?? '');
        setTips(recipe.tips ?? '');
        const loadedIngredients = (recipe.ingredients ?? [])
          .slice()
          .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
          .map((item) => ({
            key: nextDraftKey(),
            name: item.name,
            amount: item.amount ?? '',
            unit: item.unit ?? '',
            isEssential: item.isEssential ?? true,
          }));
        setIngredients(loadedIngredients.length ? loadedIngredients : [emptyIngredient()]);
        const loadedSteps = (recipe.steps ?? [])
          .slice()
          .sort((a, b) => a.stepNumber - b.stepNumber)
          .map((step) => ({
            key: nextDraftKey(),
            content: step.content,
            duration: step.duration ? String(step.duration) : '',
          }));
        setSteps(loadedSteps.length ? loadedSteps : [emptyStep()]);
      })
      .catch(() => Taro.showToast({ title: '加载失败', icon: 'none' }))
      .finally(() => setLoadingDetail(false));
  });

  const categoryRows = useMemo(() => {
    const rows: RecipeCategory[][] = [];
    for (let i = 0; i < categories.length; i += 3) {
      rows.push(categories.slice(i, i + 3));
    }
    return rows;
  }, [categories]);

  const updateIngredient = (index: number, patch: Partial<IngredientDraft>) => {
    setIngredients((prev) => prev.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  };
  const updateStep = (index: number, patch: Partial<StepDraft>) => {
    setSteps((prev) => prev.map((item, i) => (i === index ? { ...item, ...patch } : item)));
  };

  const pickCover = () => {
    if (uploadingCover) return;
    Taro.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const filePath = res.tempFilePaths[0];
        if (!filePath) return;
        setUploadingCover(true);
        uploadRecipeCover(filePath)
          .then(setCoverImageUrl)
          .then(() => Taro.showToast({ title: '封面已上传', icon: 'success' }))
          .catch(() => Taro.showToast({ title: '封面上传失败', icon: 'none' }))
          .finally(() => setUploadingCover(false));
      },
    });
  };

  const parsePositiveInt = (value: string): number | undefined => {
    const trimmed = value.trim();
    if (!trimmed) return undefined;
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) && parsed > 0 ? Math.round(parsed) : undefined;
  };

  const handleSubmit = () => {
    if (saving) return;
    if (!title.trim()) {
      Taro.showToast({ title: '请填写菜谱名称', icon: 'none' });
      return;
    }

    const payload: RecipeRequest = {
      title: title.trim(),
      description: description.trim() || undefined,
      category,
      difficulty,
      prepTime: parsePositiveInt(prepTime),
      cookTime: parsePositiveInt(cookTime),
      servings: parsePositiveInt(servings),
      tags: tags.trim() || undefined,
      coverImageUrl: coverImageUrl.trim() || undefined,
      tips: tips.trim() || undefined,
      ingredients: ingredients
        .filter((item) => item.name.trim())
        .map((item, index) => ({
          name: item.name.trim(),
          amount: item.amount.trim() || undefined,
          unit: item.unit.trim() || undefined,
          isEssential: item.isEssential,
          sortOrder: index,
        })),
      steps: steps
        .filter((item) => item.content.trim())
        .map((item, index) => ({
          stepNumber: index + 1,
          content: item.content.trim(),
          duration: parsePositiveInt(item.duration),
        })),
    };

    setSaving(true);
    const request = isEdit
      ? updateRecipe(recipeId as number, payload)
      : createRecipe(payload);

    request
      .then(() => {
        Taro.showToast({ title: '提交成功，等待审核', icon: 'success' });
        setTimeout(() => Taro.navigateBack(), 1200);
      })
      .catch(() => Taro.showToast({ title: '保存失败，请稍后再试', icon: 'none' }))
      .finally(() => setSaving(false));
  };

  if (loadingDetail) {
    return (
      <View className="recipe-form">
        <View className="form-loading">
          <Text className="form-loading-text">正在加载菜谱…</Text>
        </View>
      </View>
    );
  }

  return (
    <View className="recipe-form">
      <ScrollView className="form-scroll" scrollY>
        <View className="form-section">
          <Text className="field-label">菜谱名称</Text>
          <Input
            className="field-input"
            placeholder="例如：辣椒炒肉"
            maxlength={60}
            value={title}
            onInput={(e) => setTitle(e.detail.value)}
          />
        </View>

        <View className="form-section">
          <Text className="field-label">简介</Text>
          <Textarea
            className="field-textarea"
            placeholder="简单介绍这道菜（选填）"
            maxlength={300}
            value={description}
            onInput={(e) => setDescription(e.detail.value)}
          />
        </View>

        <View className="form-section">
          <Text className="field-label">分类</Text>
          {categoryRows.map((row, rowIndex) => (
            <View key={`cat-row-${rowIndex}`} className="chip-row">
              {row.map((item) => {
                const active = category === item.name;
                return (
                  <View
                    key={item.id}
                    className={`chip ${active ? 'chip-active' : ''}`}
                    onClick={() => setCategory((prev) => (prev === item.name ? undefined : item.name))}
                  >
                    <Text className={`chip-text ${active ? 'chip-text-active' : ''}`}>{item.name}</Text>
                  </View>
                );
              })}
            </View>
          ))}
        </View>

        <View className="form-section">
          <Text className="field-label">难度</Text>
          <View className="diff-row">
            {DIFFICULTY_OPTIONS.map((option) => {
              const active = difficulty === option.value;
              return (
                <View
                  key={option.value}
                  className={`diff-btn ${active ? 'diff-btn-active' : ''}`}
                  onClick={() => setDifficulty(option.value)}
                >
                  <Text className={`diff-text ${active ? 'diff-text-active' : ''}`}>{option.label}</Text>
                </View>
              );
            })}
          </View>
        </View>

        <View className="form-section">
          <View className="num-row">
            <View className="num-cell">
              <Text className="field-label">准备（分钟）</Text>
              <Input
                className="field-input"
                type="number"
                value={prepTime}
                onInput={(e) => setPrepTime(e.detail.value)}
              />
            </View>
            <View className="num-cell">
              <Text className="field-label">烹饪（分钟）</Text>
              <Input
                className="field-input"
                type="number"
                value={cookTime}
                onInput={(e) => setCookTime(e.detail.value)}
              />
            </View>
            <View className="num-cell">
              <Text className="field-label">几人份</Text>
              <Input
                className="field-input"
                type="number"
                value={servings}
                onInput={(e) => setServings(e.detail.value)}
              />
            </View>
          </View>
        </View>

        <View className="form-section">
          <Text className="field-label">标签</Text>
          <Input
            className="field-input"
            placeholder="用逗号分隔，例如：下饭菜,家常,快手"
            value={tags}
            onInput={(e) => setTags(e.detail.value)}
          />
        </View>

        <View className="form-section">
          <Text className="field-label">封面图</Text>
          <View className="cover-row">
            <View className="cover-box" onClick={pickCover}>
              {coverImageUrl ? (
                <Image className="cover-img" src={resolveAssetUrl(coverImageUrl)} mode="aspectFill" />
              ) : (
                <View className="cover-placeholder">
                  <Text className="cover-placeholder-icon">{'\u{1F4F7}'}</Text>
                  <Text className="cover-placeholder-text">
                    {uploadingCover ? '上传中…' : '点击上传'}
                  </Text>
                </View>
              )}
            </View>
            {coverImageUrl ? (
              <View className="cover-clear" onClick={() => setCoverImageUrl('')}>
                <Text className="cover-clear-text">移除</Text>
              </View>
            ) : null}
          </View>
          <Input
            className="field-input"
            placeholder="或直接粘贴图片 URL（选填）"
            value={coverImageUrl}
            onInput={(e) => setCoverImageUrl(e.detail.value)}
          />
        </View>

        <View className="form-section">
          <Text className="field-label">小贴士</Text>
          <Textarea
            className="field-textarea"
            placeholder="做菜的小窍门（选填）"
            maxlength={300}
            value={tips}
            onInput={(e) => setTips(e.detail.value)}
          />
        </View>

        <View className="form-section">
          <View className="section-head">
            <Text className="section-title">用料</Text>
            <View
              className="add-btn"
              onClick={() => setIngredients((prev) => [...prev, emptyIngredient()])}
            >
              <Text className="add-text">+ 添加</Text>
            </View>
          </View>
          {ingredients.map((item, index) => (
            <View key={item.key} className="ing-row">
              <View className="ing-line">
                <Input
                  className="ing-name"
                  placeholder="食材名称"
                  value={item.name}
                  onInput={(e) => updateIngredient(index, { name: e.detail.value })}
                />
              </View>
              <View className="ing-line">
                <Input
                  className="ing-amount"
                  placeholder="用量"
                  value={item.amount}
                  onInput={(e) => updateIngredient(index, { amount: e.detail.value })}
                />
                <Input
                  className="ing-unit"
                  placeholder="单位"
                  value={item.unit}
                  onInput={(e) => updateIngredient(index, { unit: e.detail.value })}
                />
                <View
                  className={`essential-pill ${item.isEssential ? 'essential-on' : ''}`}
                  onClick={() => updateIngredient(index, { isEssential: !item.isEssential })}
                >
                  <Text className={`essential-text ${item.isEssential ? 'essential-text-on' : ''}`}>
                    {item.isEssential ? '必备' : '可选'}
                  </Text>
                </View>
                <View
                  className="row-del"
                  onClick={() =>
                    setIngredients((prev) =>
                      prev.length > 1 ? prev.filter((_, i) => i !== index) : prev,
                    )
                  }
                >
                  <Text className="row-del-text">{'\u2715'}</Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        <View className="form-section">
          <View className="section-head">
            <Text className="section-title">做法步骤</Text>
            <View className="add-btn" onClick={() => setSteps((prev) => [...prev, emptyStep()])}>
              <Text className="add-text">+ 添加</Text>
            </View>
          </View>
          {steps.map((item, index) => (
            <View key={item.key} className="step-row">
              <View className="step-head">
                <View className="step-num">
                  <Text className="step-num-text">{index + 1}</Text>
                </View>
                <View
                  className="row-del row-del-step"
                  onClick={() =>
                    setSteps((prev) =>
                      prev.length > 1 ? prev.filter((_, i) => i !== index) : prev,
                    )
                  }
                >
                  <Text className="row-del-text">{'\u2715'}</Text>
                </View>
              </View>
              <Textarea
                className="step-content"
                placeholder="这一步要做什么？"
                value={item.content}
                onInput={(e) => updateStep(index, { content: e.detail.value })}
              />
              <View className="step-duration-line">
                <Text className="step-duration-label">计时（分钟）</Text>
                <Input
                  className="step-duration"
                  type="number"
                  placeholder="选填"
                  value={item.duration}
                  onInput={(e) => updateStep(index, { duration: e.detail.value })}
                />
              </View>
            </View>
          ))}
        </View>

        <View
          className={`submit-btn ${saving ? 'submit-btn-disabled' : ''}`}
          onClick={handleSubmit}
        >
          <Text className="submit-text">
            {saving ? '提交中…' : isEdit ? '保存并重新提交审核' : '提交审核'}
          </Text>
        </View>
        <View className="submit-spacer" />
      </ScrollView>
    </View>
  );
}
