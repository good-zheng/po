/** 菜谱审核状态：pending=待审核，approved=已通过，rejected=已驳回 */
export type RecipeStatus = 'pending' | 'approved' | 'rejected';

/** 菜谱列表排序：recommend=推荐（默认），likes=点赞数降序，newest=最新发布 */
export type RecipeSort = 'recommend' | 'likes' | 'newest';

export type RecipeCategory = {
  id: number;
  name: string;
  icon: string | null;
  description: string | null;
  sortOrder: number;
  createdAt?: string;
  updatedAt?: string;
};

/** 菜谱分类创建/更新请求（管理端） */
export type RecipeCategoryRequest = {
  name: string;
  icon?: string;
  description?: string;
  sortOrder?: number;
};

export type Ingredient = {
  id?: number;
  name: string;
  amount?: string | null;
  unit?: string | null;
  isEssential?: boolean;
  sortOrder?: number;
  imageUrl?: string | null;
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
  /** 审核状态（管理员/作者可见；公开列表恒为 approved） */
  status?: RecipeStatus;
  /** 驳回原因（status=rejected 时有值） */
  rejectReason?: string | null;
  /** 当前用户是否已收藏（登录用户视角） */
  isFavorited?: boolean;
  /** 当前用户是否已点赞（登录用户视角） */
  isLiked?: boolean;
  /** 收藏时间（收藏列表返回） */
  favoritedAt?: string | null;
  /** 最近浏览时间（历史列表返回） */
  viewedAt?: string | null;
  ingredients?: Ingredient[];
  steps?: Step[];
  createdAt?: string;
  updatedAt?: string;
};

/** 菜谱卡片摘要：聊天工具结果（search_recipes / get_recipe_detail）下发的渲染源 */
export type RecipeBrief = {
  id: number;
  title: string;
  description?: string | null;
  coverImageUrl?: string | null;
  prepTime?: number | null;
  cookTime?: number | null;
  totalTime?: number | null;
  difficulty?: number | null;
  servings?: number | null;
  category?: string | null;
  tags?: string | null;
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
    imageUrl?: string;
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
  /** 难度筛选：1=简单，2=中等，3=困难 */
  difficulty?: number;
  /** 排序，默认 recommend（推荐） */
  sort?: RecipeSort;
};

/** 管理端审核请求：approve=通过，reject=驳回（需填 reason） */
export type RecipeAuditRequest = {
  action: 'approve' | 'reject';
  reason?: string;
};

/** 点赞切换结果 */
export type RecipeLikeResult = {
  liked: boolean;
  likesCount: number;
};
