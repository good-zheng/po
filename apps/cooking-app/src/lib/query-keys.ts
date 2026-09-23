import type { RecipeSort } from '@po/types';

export type RecipeListFilter = {
  categoryIds?: number[];
  keyword?: string;
  difficulty?: number;
  sort?: RecipeSort;
};

export const recipeKeys = {
  all: ['recipes'] as const,
  list: (filter: RecipeListFilter = {}) =>
    [
      ...recipeKeys.all,
      'list',
      filter.keyword ?? '',
      (filter.categoryIds ?? []).join(','),
      filter.difficulty ?? '',
      filter.sort ?? 'recommend',
    ] as const,
  detail: (id: number) => [...recipeKeys.all, 'detail', id] as const,
  mine: () => [...recipeKeys.all, 'mine'] as const,
  favorites: () => [...recipeKeys.all, 'favorites'] as const,
  history: () => [...recipeKeys.all, 'history'] as const,
};

export const categoryKeys = {
  all: ['recipe-categories'] as const,
  list: () => [...categoryKeys.all, 'list'] as const,
};

export const userKeys = {
  me: () => ['users', 'me'] as const,
};
