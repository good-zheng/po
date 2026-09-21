import { request } from '@umijs/max';
import type {
  Ingredient,
  PageResponse,
  Recipe,
  RecipeCategory,
  RecipeRequest,
  Result,
  Step,
} from '@po/types';

export type {
  Ingredient,
  Recipe,
  RecipeCategory,
  RecipeListParams,
  RecipeRequest,
  Step,
} from '@po/types';

// ── Categories ───────────────────────────────────────────────────────────────

/** 获取所有菜谱分类 */
export async function getRecipeCategories(options?: Record<string, unknown>) {
  return request<Result<RecipeCategory[]>>('/api/recipe-categories', {
    method: 'GET',
    ...(options || {}),
  });
}

// ── Recipes ──────────────────────────────────────────────────────────────────

/** 分页获取菜谱列表 */
export async function getRecipes(
  params: {
    page?: number;
    size?: number;
    keyword?: string;
    categoryIdStr?: string;
  },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<Recipe>>>('/api/recipes', {
    method: 'GET',
    params,
    ...(options || {}),
  });
}

/** 获取单个菜谱详情 */
export async function getRecipe(id: number, options?: Record<string, unknown>) {
  return request<Result<Recipe>>(`/api/recipes/${id}`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 创建菜谱 */
export async function createRecipe(
  body: RecipeRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<Recipe>>('/api/recipes', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新菜谱 */
export async function updateRecipe(
  id: number,
  body: RecipeRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<Recipe>>(`/api/recipes/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 删除菜谱（软删除） */
export async function deleteRecipe(
  id: number,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>(`/api/recipes/${id}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}
