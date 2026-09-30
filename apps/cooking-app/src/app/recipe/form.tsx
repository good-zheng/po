import { Ionicons } from '@expo/vector-icons';
import type { Ingredient, RecipeRequest, Step } from '@po/types';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as ImagePicker from 'expo-image-picker';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import {
  Alert,
  Image,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from 'react-native';
import { FormError, SubmitButton, TextField } from '@/components/form';
import { ScreenHeader } from '@/components/screen-header';
import { LoadingState } from '@/components/state-views';
import { ApiError, resolveAssetUrl } from '@/lib/api/client';
import {
  createRecipe,
  fetchRecipeCategories,
  fetchRecipeDetail,
  updateRecipe,
  uploadRecipeCover,
} from '@/lib/api/recipes';
import { categoryKeys, recipeKeys } from '@/lib/query-keys';
import { cn } from '@/lib/utils';

const difficultyOptions = [
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

const emptyStep = (): StepDraft => ({
  key: nextDraftKey(),
  content: '',
  duration: '',
});

export default function RecipeFormScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const recipeId = id ? Number(id) : undefined;
  const isEdit = Number.isFinite(recipeId);
  const router = useRouter();
  const queryClient = useQueryClient();

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
  const [ingredients, setIngredients] = useState<IngredientDraft[]>([
    emptyIngredient(),
  ]);
  const [steps, setSteps] = useState<StepDraft[]>([emptyStep()]);
  const [formError, setFormError] = useState<string | null>(null);
  const [uploadingCover, setUploadingCover] = useState(false);

  const categoriesQuery = useQuery({
    queryFn: fetchRecipeCategories,
    queryKey: categoryKeys.list(),
  });

  const detailQuery = useQuery({
    enabled: isEdit,
    queryFn: () => fetchRecipeDetail(recipeId as number),
    queryKey: recipeKeys.detail(recipeId ?? 0),
  });

  // 编辑模式：详情加载完成后回填表单（仅一次）
  useEffect(() => {
    const recipe = detailQuery.data;
    if (!recipe) {
      return;
    }
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
      .sort((a, b) => (a.sortOrder ?? 0) - (b.sortOrder ?? 0))
      .map((ingredient: Ingredient) => ({
        key: nextDraftKey(),
        name: ingredient.name,
        amount: ingredient.amount ?? '',
        unit: ingredient.unit ?? '',
        isEssential: ingredient.isEssential ?? true,
      }));
    setIngredients(
      loadedIngredients.length ? loadedIngredients : [emptyIngredient()],
    );
    const loadedSteps = (recipe.steps ?? [])
      .sort((a, b) => a.stepNumber - b.stepNumber)
      .map((step: Step) => ({
        key: nextDraftKey(),
        content: step.content,
        duration: step.duration ? String(step.duration) : '',
      }));
    setSteps(loadedSteps.length ? loadedSteps : [emptyStep()]);
  }, [detailQuery.data]);

  const mutation = useMutation({
    mutationFn: (payload: RecipeRequest) =>
      isEdit
        ? updateRecipe(recipeId as number, payload)
        : createRecipe(payload),
    onError: (error) => {
      setFormError(
        error instanceof ApiError ? error.message : '保存失败，请稍后再试。',
      );
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: recipeKeys.mine() });
      await queryClient.invalidateQueries({ queryKey: recipeKeys.all });
      Alert.alert('提交成功', '菜谱已提交审核，管理员通过后会公开展示。', [
        { onPress: () => router.back(), text: '知道了' },
      ]);
    },
  });

  const parsePositiveInt = (value: string): number | undefined => {
    const trimmed = value.trim();
    if (!trimmed) {
      return undefined;
    }
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) && parsed > 0
      ? Math.round(parsed)
      : undefined;
  };

  const handleSubmit = () => {
    setFormError(null);
    if (!title.trim()) {
      setFormError('请填写菜谱名称');
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
        .filter((ingredient) => ingredient.name.trim())
        .map((ingredient, index) => ({
          name: ingredient.name.trim(),
          amount: ingredient.amount.trim() || undefined,
          unit: ingredient.unit.trim() || undefined,
          isEssential: ingredient.isEssential,
          sortOrder: index,
        })),
      steps: steps
        .filter((step) => step.content.trim())
        .map((step, index) => ({
          stepNumber: index + 1,
          content: step.content.trim(),
          duration: parsePositiveInt(step.duration),
        })),
    };
    mutation.mutate(payload);
  };

  const updateIngredient = (index: number, patch: Partial<IngredientDraft>) => {
    setIngredients((prev) =>
      prev.map((item, i) => (i === index ? { ...item, ...patch } : item)),
    );
  };

  const updateStep = (index: number, patch: Partial<StepDraft>) => {
    setSteps((prev) =>
      prev.map((item, i) => (i === index ? { ...item, ...patch } : item)),
    );
  };

  const pickCover = async () => {
    if (uploadingCover) {
      return;
    }
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setFormError('需要相册权限才能选择封面图');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.8,
    });
    if (result.canceled) {
      return;
    }
    const asset = result.assets[0];
    if (!asset) {
      return;
    }
    setUploadingCover(true);
    setFormError(null);
    try {
      setCoverImageUrl(await uploadRecipeCover(asset.uri));
    } catch {
      setFormError('封面上传失败，请稍后再试。');
    } finally {
      setUploadingCover(false);
    }
  };

  if (isEdit && detailQuery.isLoading) {
    return (
      <View className="flex-1 bg-stone-50 dark:bg-stone-950">
        <ScreenHeader title="编辑菜谱" />
        <LoadingState message="正在加载菜谱…" />
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      className="flex-1 bg-stone-50 dark:bg-stone-950"
    >
      <ScreenHeader
        subtitle="提交后需管理员审核通过才会公开"
        title={isEdit ? '编辑菜谱' : '新建菜谱'}
      />
      <ScrollView
        contentContainerClassName="gap-4 px-5 pb-10"
        keyboardShouldPersistTaps="handled"
      >
        <FormError message={formError} />

        <TextField
          label="菜谱名称"
          maxLength={60}
          onChangeText={setTitle}
          placeholder="例如：辣椒炒肉"
          value={title}
        />
        <TextField
          label="简介"
          multiline
          numberOfLines={3}
          onChangeText={setDescription}
          placeholder="简单介绍这道菜（选填）"
          value={description}
        />

        <View className="gap-1.5">
          <Text className="text-sm font-medium text-stone-700 dark:text-stone-300">
            分类
          </Text>
          <View className="flex-row flex-wrap gap-2">
            {(categoriesQuery.data ?? []).map((item) => (
              <Pressable
                className={cn(
                  'rounded-full border px-3.5 py-1.5',
                  category === item.name
                    ? 'border-brand-600 bg-brand-600'
                    : 'border-stone-200 bg-white dark:border-stone-700 dark:bg-stone-800',
                )}
                key={item.id}
                onPress={() =>
                  setCategory((prev) =>
                    prev === item.name ? undefined : item.name,
                  )
                }
              >
                <Text
                  className={cn(
                    'text-sm',
                    category === item.name
                      ? 'font-medium text-white'
                      : 'text-stone-700 dark:text-stone-300',
                  )}
                >
                  {item.name}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        <View className="gap-1.5">
          <Text className="text-sm font-medium text-stone-700 dark:text-stone-300">
            难度
          </Text>
          <View className="flex-row gap-2">
            {difficultyOptions.map((option) => (
              <Pressable
                className={cn(
                  'flex-1 rounded-2xl border py-2.5',
                  difficulty === option.value
                    ? 'border-brand-600 bg-brand-600'
                    : 'border-stone-200 bg-white dark:border-stone-700 dark:bg-stone-800',
                )}
                key={option.value}
                onPress={() => setDifficulty(option.value)}
              >
                <Text
                  className={cn(
                    'text-center text-sm',
                    difficulty === option.value
                      ? 'font-medium text-white'
                      : 'text-stone-700 dark:text-stone-300',
                  )}
                >
                  {option.label}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        <View className="flex-row gap-3">
          <View className="flex-1">
            <TextField
              keyboardType="number-pad"
              label="准备（分钟）"
              onChangeText={setPrepTime}
              value={prepTime}
            />
          </View>
          <View className="flex-1">
            <TextField
              keyboardType="number-pad"
              label="烹饪（分钟）"
              onChangeText={setCookTime}
              value={cookTime}
            />
          </View>
          <View className="flex-1">
            <TextField
              keyboardType="number-pad"
              label="几人份"
              onChangeText={setServings}
              value={servings}
            />
          </View>
        </View>

        <TextField
          label="标签"
          onChangeText={setTags}
          placeholder="用逗号分隔，例如：下饭菜,家常,快手"
          value={tags}
        />
        <View className="gap-1.5">
          <Text className="text-sm font-medium text-stone-700 dark:text-stone-300">
            封面图
          </Text>
          <View className="flex-row items-center gap-3">
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="上传封面图"
              onPress={pickCover}
              className="h-28 w-40 items-center justify-center overflow-hidden rounded-2xl border border-stone-200 bg-stone-50 dark:border-stone-700 dark:bg-stone-800"
            >
              {coverImageUrl.trim() ? (
                <Image
                  className="h-full w-full"
                  source={{ uri: resolveAssetUrl(coverImageUrl) }}
                  resizeMode="cover"
                />
              ) : (
                <View className="items-center">
                  <Ionicons color="#a8a29e" name="camera-outline" size={28} />
                  <Text className="mt-1 text-xs text-stone-400">
                    {uploadingCover ? '上传中…' : '点击上传'}
                  </Text>
                </View>
              )}
            </Pressable>
            {coverImageUrl.trim() ? (
              <Pressable
                accessibilityRole="button"
                onPress={() => setCoverImageUrl('')}
                className="flex-row items-center gap-1 rounded-full border border-stone-200 px-3 py-1.5 dark:border-stone-700"
              >
                <Ionicons color="#78716c" name="close" size={16} />
                <Text className="text-sm text-stone-500 dark:text-stone-400">
                  移除
                </Text>
              </Pressable>
            ) : null}
          </View>
          <TextField
            autoCapitalize="none"
            label="图片 URL（选填）"
            onChangeText={setCoverImageUrl}
            placeholder="或直接粘贴图片 URL"
            value={coverImageUrl}
          />
        </View>
        <TextField
          label="小贴士"
          multiline
          numberOfLines={2}
          onChangeText={setTips}
          placeholder="做菜的小窍门（选填）"
          value={tips}
        />

        <View className="gap-2">
          <View className="flex-row items-center justify-between">
            <Text className="text-sm font-medium text-stone-700 dark:text-stone-300">
              用料
            </Text>
            <Pressable
              accessibilityRole="button"
              className="flex-row items-center gap-1"
              onPress={() =>
                setIngredients((prev) => [...prev, emptyIngredient()])
              }
            >
              <Ionicons color="#ea580c" name="add-circle-outline" size={18} />
              <Text className="text-sm text-brand-600">添加</Text>
            </Pressable>
          </View>
          {ingredients.map((ingredient, index) => (
            <View className="flex-row items-center gap-2" key={ingredient.key}>
              <TextInput
                className="flex-[2] rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-50"
                onChangeText={(value) =>
                  updateIngredient(index, { name: value })
                }
                placeholder="食材名称"
                placeholderTextColor="#a8a29e"
                value={ingredient.name}
              />
              <TextInput
                className="flex-1 rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-50"
                onChangeText={(value) =>
                  updateIngredient(index, { amount: value })
                }
                placeholder="用量"
                placeholderTextColor="#a8a29e"
                value={ingredient.amount}
              />
              <TextInput
                className="flex-1 rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-50"
                onChangeText={(value) =>
                  updateIngredient(index, { unit: value })
                }
                placeholder="单位"
                placeholderTextColor="#a8a29e"
                value={ingredient.unit}
              />
              <Pressable
                accessibilityLabel={ingredient.isEssential ? '必备' : '可选'}
                accessibilityRole="button"
                className={cn(
                  'rounded-full px-2.5 py-1.5',
                  ingredient.isEssential
                    ? 'bg-brand-50 dark:bg-stone-800'
                    : 'bg-stone-100 dark:bg-stone-800',
                )}
                onPress={() =>
                  updateIngredient(index, {
                    isEssential: !ingredient.isEssential,
                  })
                }
              >
                <Text
                  className={cn(
                    'text-xs',
                    ingredient.isEssential
                      ? 'text-brand-700 dark:text-brand-500'
                      : 'text-stone-500 dark:text-stone-400',
                  )}
                >
                  {ingredient.isEssential ? '必备' : '可选'}
                </Text>
              </Pressable>
              <Pressable
                accessibilityLabel="删除该行"
                accessibilityRole="button"
                hitSlop={6}
                onPress={() =>
                  setIngredients((prev) =>
                    prev.length > 1 ? prev.filter((_, i) => i !== index) : prev,
                  )
                }
              >
                <Ionicons
                  color="#a8a29e"
                  name="close-circle-outline"
                  size={18}
                />
              </Pressable>
            </View>
          ))}
        </View>

        <View className="gap-2">
          <View className="flex-row items-center justify-between">
            <Text className="text-sm font-medium text-stone-700 dark:text-stone-300">
              做法步骤
            </Text>
            <Pressable
              accessibilityRole="button"
              className="flex-row items-center gap-1"
              onPress={() => setSteps((prev) => [...prev, emptyStep()])}
            >
              <Ionicons color="#ea580c" name="add-circle-outline" size={18} />
              <Text className="text-sm text-brand-600">添加</Text>
            </Pressable>
          </View>
          {steps.map((step, index) => (
            <View className="flex-row items-start gap-2" key={step.key}>
              <View className="mt-2 h-6 w-6 items-center justify-center rounded-full bg-brand-600">
                <Text className="text-xs font-bold text-white">
                  {index + 1}
                </Text>
              </View>
              <TextInput
                className="flex-1 min-h-16 rounded-2xl border border-stone-200 bg-stone-50 px-3 py-2.5 text-sm leading-5 text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-50"
                multiline
                onChangeText={(value) => updateStep(index, { content: value })}
                placeholder="这一步要做什么？"
                placeholderTextColor="#a8a29e"
                value={step.content}
              />
              <TextInput
                className="mt-0.5 w-16 rounded-2xl border border-stone-200 bg-stone-50 px-2 py-2.5 text-center text-sm text-stone-900 dark:border-stone-700 dark:bg-stone-800 dark:text-stone-50"
                keyboardType="number-pad"
                onChangeText={(value) => updateStep(index, { duration: value })}
                placeholder="分钟"
                placeholderTextColor="#a8a29e"
                value={step.duration}
              />
              <Pressable
                accessibilityLabel="删除该步骤"
                accessibilityRole="button"
                className="mt-2"
                hitSlop={6}
                onPress={() =>
                  setSteps((prev) =>
                    prev.length > 1 ? prev.filter((_, i) => i !== index) : prev,
                  )
                }
              >
                <Ionicons
                  color="#a8a29e"
                  name="close-circle-outline"
                  size={18}
                />
              </Pressable>
            </View>
          ))}
        </View>

        <View className="mt-2">
          <SubmitButton
            label={isEdit ? '保存并重新提交审核' : '提交审核'}
            loading={mutation.isPending}
            onPress={handleSubmit}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}
