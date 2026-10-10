import type { PageResponse, Recipe, RecipeCategory, RecipeLikeResult, RecipeListParams, RecipeRequest } from '@po/types';
import { apiClient, uploadFile } from '@/lib/api/client';

type FetchRecipesParams = RecipeListParams & {
  page?: number;
  size?: number;
  categoryIds?: number[];
};

export async function fetchRecipes(params?: FetchRecipesParams): Promise<PageResponse<Recipe>> {
  const query: Record<string, string | number | boolean | undefined> = {};
  if (params?.keyword) query.keyword = params.keyword;
  const pageNum = params?.page ?? params?.current;
  const pageSize = params?.size ?? params?.pageSize;
  if (pageNum !== undefined) query.page = pageNum;
  if (pageSize !== undefined) query.size = pageSize;
  if (params?.sort) query.sort = params.sort;
  if (params?.difficulty !== undefined) query.difficulty = params.difficulty;
  const catIds = params?.categoryIds ?? params?.categoryId;
  if (catIds && catIds.length > 0) {
    query.categoryIdStr = catIds.join(',');
  }
  return apiClient.get<PageResponse<Recipe>>('/recipes', query);
}

export async function fetchRecipeDetail(id: number): Promise<Recipe> {
  return apiClient.get<Recipe>(`/recipes/${id}`);
}

/**
 * 分类表近乎静态，但首页、分类页、分类详情页都会各要一次。
 * 缓存同一个 Promise 而不是结果：并发调用只发一次请求，失败时清掉缓存留给下次重试。
 */
let categoriesPromise: Promise<RecipeCategory[]> | null = null;

export function fetchRecipeCategories(force = false): Promise<RecipeCategory[]> {
  if (categoriesPromise && !force) {
    return categoriesPromise;
  }
  const pending = apiClient
    .get<RecipeCategory[]>('/recipe-categories')
    .catch((error: unknown) => {
      // 失败不留在缓存里，否则一次网络抖动会让分类页永远空白
      if (categoriesPromise === pending) {
        categoriesPromise = null;
      }
      throw error;
    });
  categoriesPromise = pending;
  return pending;
}

export async function fetchFavorites(page = 0, size = 20): Promise<PageResponse<Recipe>> {
  return apiClient.get<PageResponse<Recipe>>('/recipes/favorites', { page, size });
}

export async function fetchHistory(page = 0, size = 20): Promise<PageResponse<Recipe>> {
  return apiClient.get<PageResponse<Recipe>>('/recipes/history', { page, size });
}

export async function favoriteRecipe(id: number): Promise<void> {
  await apiClient.post(`/recipes/${id}/favorite`);
}

export async function unfavoriteRecipe(id: number): Promise<void> {
  await apiClient.delete(`/recipes/${id}/favorite`);
}

export async function likeRecipe(id: number): Promise<RecipeLikeResult> {
  return apiClient.post<RecipeLikeResult>(`/recipes/${id}/like`);
}

export async function fetchMyRecipes(page = 0, size = 20): Promise<PageResponse<Recipe>> {
  return apiClient.get<PageResponse<Recipe>>('/recipes/mine', { page, size });
}

/** 上传菜谱封面图到 COS（files/dishes 目录），返回公网图片 URL */
export async function uploadRecipeCover(filePath: string): Promise<string> {
  return uploadFile<string>('/files/upload', filePath, { dir: 'dishes' });
}

/** 创建菜谱（App 用户提交后进入待审核） */
export async function createRecipe(payload: RecipeRequest): Promise<Recipe> {
  return apiClient.post<Recipe>('/recipes', payload as unknown as Record<string, unknown>);
}

/** 更新菜谱（作者本人，修改后重新进入待审核） */
export async function updateRecipe(id: number, payload: RecipeRequest): Promise<Recipe> {
  return apiClient.put<Recipe>(`/recipes/${id}`, payload as unknown as Record<string, unknown>);
}

export async function deleteRecipe(id: number): Promise<void> {
  await apiClient.delete(`/recipes/${id}`);
}
