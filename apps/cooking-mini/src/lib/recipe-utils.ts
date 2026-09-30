import type { Ingredient, Recipe, Step } from '@po/types';

const difficultyLabels: Record<number, string> = {
  1: '简单',
  2: '中等',
  3: '困难',
};

export function difficultyLabel(difficulty?: number | null): string {
  if (!difficulty) {
    return '未知';
  }
  return difficultyLabels[difficulty] ?? `难度 ${difficulty}`;
}

export function splitTags(tags?: string | null): string[] {
  return (
    tags
      ?.split(',')
      .map((tag) => tag.trim())
      .filter(Boolean) ?? []
  );
}

/** 部分菜谱没填总时长，用准备 + 烹饪时间兜底 */
export function totalMinutes(
  recipe: Pick<Recipe, 'totalTime' | 'prepTime' | 'cookTime'>,
): number | undefined {
  if (recipe.totalTime) {
    return recipe.totalTime;
  }
  const minutes = (recipe.prepTime ?? 0) + (recipe.cookTime ?? 0);
  return minutes > 0 ? minutes : undefined;
}

export function formatIngredientAmount(ingredient: Ingredient, scale = 1): string {
  const parts = [normalizeAmount(ingredient.amount, scale), ingredient.unit?.trim()].filter(Boolean);
  return parts.join(' ') || '适量';
}

/** 用量在库里是字符串，1.0 / 150.00 这类写法要去掉多余的零；scale 为人份换算系数 */
function normalizeAmount(amount?: string | null, scale = 1): string | undefined {
  const text = amount?.trim();
  if (!text) {
    return undefined;
  }
  const numeric = Number(text);
  if (!Number.isFinite(numeric)) {
    return text;
  }
  return String(Math.round(numeric * scale * 100) / 100);
}

export function sortSteps(steps?: Step[] | null): Step[] {
  return [...(steps ?? [])].sort((a, b) => a.stepNumber - b.stepNumber);
}

/** 步骤时长以分钟存储，做菜模式按秒计时 */
export function stepDurationSeconds(step?: Step | null): number {
  const minutes = step?.duration ?? 0;
  return minutes > 0 ? Math.round(minutes * 60) : 0;
}

export function formatClock(totalSeconds: number): string {
  const seconds = Math.max(0, Math.round(totalSeconds));
  const minutes = Math.floor(seconds / 60);
  const rest = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(rest).padStart(2, '0')}`;
}
