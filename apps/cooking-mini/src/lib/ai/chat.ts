import type { Recipe, RecipeCategory } from '@po/types';

import { type AssistantReply, buildReply, parseIntent } from '@/lib/ai/assistant';
import { fetchRecipeCategories, fetchRecipeDetail, fetchRecipes } from '@/lib/api/recipes';

const RECOMMEND_POOL_SIZE = 9;
const RECOMMEND_PICK_SIZE = 3;
const SEARCH_SIZE = 5;

/**
 * 把一句用户提问变成一条助手回复：先识别意图，再按意图取本地菜谱数据。
 * 这条链路只读菜谱库接口，不经过任何模型，也是小程序唯一的应答来源。
 */
export async function askAssistant(
  message: string,
  categories: RecipeCategory[] = [],
): Promise<AssistantReply> {
  try {
    const resolvedCategories =
      categories.length > 0 ? categories : await fetchRecipeCategories();
    const intent = parseIntent(message, resolvedCategories);

    if (intent.kind === 'greeting' || intent.kind === 'help') {
      return buildReply({ categories: resolvedCategories, intent, recipes: [] });
    }

    if (intent.kind === 'recommend') {
      const page = await fetchRecipes({
        ...(intent.category ? { categoryIds: [intent.category.id] } : {}),
        page: 0,
        size: RECOMMEND_POOL_SIZE,
      });

      return buildReply({
        categories: resolvedCategories,
        intent,
        recipes: shuffle(page.content).slice(0, RECOMMEND_PICK_SIZE),
      });
    }

    const page = await fetchRecipes({ keyword: intent.keyword, page: 0, size: SEARCH_SIZE });
    const matched =
      page.content.find((recipe) => recipe.title === intent.keyword) ?? page.content[0];
    const detail = matched ? await loadDetail(matched.id) : undefined;

    return buildReply({
      categories: resolvedCategories,
      detail,
      intent,
      recipes: page.content,
    });
  } catch {
    return {
      text: '网络好像不太顺畅，没查到这个菜。稍后再问我一次吧。',
    };
  }
}

/** 详情只用来补充食材清单，拿不到也不影响回复 */
async function loadDetail(id: number): Promise<Recipe | undefined> {
  try {
    return await fetchRecipeDetail(id);
  } catch {
    return undefined;
  }
}

function shuffle(recipes: Recipe[]): Recipe[] {
  const result = [...recipes];

  for (let index = result.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [result[index], result[swapIndex]] = [result[swapIndex], result[index]];
  }

  return result;
}
