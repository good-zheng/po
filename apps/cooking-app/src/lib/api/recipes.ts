import type {
  PageResponse,
  Recipe,
  RecipeCategory,
  RecipeLikeResult,
  RecipeRequest,
  RecipeSort,
} from '@po/types';

import { apiClient, unwrap } from '@/lib/api/client';

export type FetchRecipesParams = {
  page: number;
  size?: number;
  categoryIds?: number[];
  keyword?: string;
  difficulty?: number;
  sort?: RecipeSort;
};

export async function fetchRecipes({
  page,
  size = 20,
  categoryIds,
  keyword,
  difficulty,
  sort,
}: FetchRecipesParams): Promise<PageResponse<Recipe>> {
  const response = await apiClient.get('/recipes', {
    params: {
      categoryIdStr: categoryIds?.join(','),
      difficulty,
      keyword,
      page,
      size,
      sort,
    },
  });

  return unwrap<PageResponse<Recipe>>(response);
}

/** 详情接口返回完整食材与步骤（列表接口不带） */
export async function fetchRecipeDetail(id: number): Promise<Recipe> {
  const response = await apiClient.get(`/recipes/${id}`);

  return unwrap<Recipe>(response);
}

export async function fetchRecipeCategories(): Promise<RecipeCategory[]> {
  const response = await apiClient.get('/recipe-categories');

  return unwrap<RecipeCategory[]>(response);
}

/** 我的菜谱（全部审核状态） */
export async function fetchMyRecipes(
  page: number,
  size = 20,
): Promise<PageResponse<Recipe>> {
  const response = await apiClient.get('/recipes/mine', {
    params: { page, size },
  });

  return unwrap<PageResponse<Recipe>>(response);
}

/** 我的收藏（按收藏时间倒序） */
export async function fetchFavorites(
  page: number,
  size = 20,
): Promise<PageResponse<Recipe>> {
  const response = await apiClient.get('/recipes/favorites', {
    params: { page, size },
  });

  return unwrap<PageResponse<Recipe>>(response);
}

/** 我的浏览历史（按最近浏览倒序） */
export async function fetchHistory(
  page: number,
  size = 20,
): Promise<PageResponse<Recipe>> {
  const response = await apiClient.get('/recipes/history', {
    params: { page, size },
  });

  return unwrap<PageResponse<Recipe>>(response);
}

export async function favoriteRecipe(id: number): Promise<void> {
  const response = await apiClient.post(`/recipes/${id}/favorite`);

  unwrap<string>(response);
}

export async function unfavoriteRecipe(id: number): Promise<void> {
  const response = await apiClient.delete(`/recipes/${id}/favorite`);

  unwrap<string>(response);
}

/** 点赞切换，返回最新点赞状态与总数 */
export async function toggleLikeRecipe(id: number): Promise<RecipeLikeResult> {
  const response = await apiClient.post(`/recipes/${id}/like`);

  return unwrap<RecipeLikeResult>(response);
}

/** 创建菜谱（App 用户创建后进入待审核） */
export async function createRecipe(payload: RecipeRequest): Promise<Recipe> {
  const response = await apiClient.post('/recipes', payload);

  return unwrap<Recipe>(response);
}

/** 更新菜谱（作者本人，修改后重新进入待审核） */
export async function updateRecipe(
  id: number,
  payload: RecipeRequest,
): Promise<Recipe> {
  const response = await apiClient.put(`/recipes/${id}`, payload);

  return unwrap<Recipe>(response);
}

export async function deleteRecipe(id: number): Promise<void> {
  const response = await apiClient.delete(`/recipes/${id}`);

  unwrap<string>(response);
}
