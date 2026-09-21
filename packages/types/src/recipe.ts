export type RecipeCategory = {
  id: number;
  name: string;
  icon: string | null;
  description: string | null;
  sortOrder: number;
  createdAt?: string;
  updatedAt?: string;
};

export type Ingredient = {
  id?: number;
  name: string;
  amount?: string | null;
  unit?: string | null;
  isEssential?: boolean;
  sortOrder?: number;
};

export type Step = {
  id?: number;
  stepNumber: number;
  content: string;
  imageUrl?: string | null;
  videoUrl?: string | null;
  duration?: number | null;
};

export type Recipe = {
  id: number;
  title: string;
  description?: string | null;
  coverImageUrl?: string | null;
  prepTime?: number | null;
  cookTime?: number | null;
  totalTime?: number | null;
  difficulty: number;
  servings?: number | null;
  category?: string | null;
  tags?: string | null;
  authorId: number;
  isPublic: boolean;
  likesCount: number;
  calories?: number | null;
  protein?: number | null;
  fat?: number | null;
  carbs?: number | null;
  tips?: string | null;
  flavorProfile?: string | null;
  ingredients?: Ingredient[];
  steps?: Step[];
  createdAt?: string;
  updatedAt?: string;
};

export type RecipeRequest = {
  title: string;
  description?: string;
  coverImageUrl?: string;
  prepTime?: number;
  cookTime?: number;
  totalTime?: number;
  difficulty: number;
  servings?: number;
  category?: string;
  tags?: string;
  isPublic?: boolean;
  calories?: number;
  protein?: number;
  fat?: number;
  carbs?: number;
  tips?: string;
  flavorProfile?: string;
  ingredients?: Array<{
    name: string;
    amount?: string;
    unit?: string;
    isEssential?: boolean;
    sortOrder?: number;
  }>;
  steps?: Array<{
    stepNumber: number;
    content: string;
    imageUrl?: string;
    videoUrl?: string;
    duration?: number;
  }>;
};

export type RecipeListParams = {
  current?: number;
  pageSize?: number;
  keyword?: string;
  categoryId?: number[];
};
