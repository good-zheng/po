import type { Recipe, RecipeCategory } from '@po/types';

import { totalMinutes } from '@/lib/recipe-utils';

export type AssistantIntent =
  | { kind: 'greeting' }
  | { kind: 'help' }
  | { kind: 'recommend'; category?: RecipeCategory }
  | { kind: 'search'; keyword: string };

export type AssistantReply = {
  text: string;
  recipes?: Recipe[];
  suggestions?: string[];
};

export type AssistantContext = {
  intent: AssistantIntent;
  categories: RecipeCategory[];
  recipes: Recipe[];
  detail?: Recipe;
};

const GREETING_PATTERN = /^(你好|您好|哈喽|哈啰|嗨|hi|hello|在吗|在么)/i;
const HELP_PATTERN =
  /(你是谁|你能做什么|能帮我做什么|能做什么|怎么用|使用说明|会做什么|有什么功能|帮助)/;

/** 提问里的填充词，去掉后剩下的才是菜名/关键词 */
const FILLER_WORDS = [
  '的做法',
  '怎么做好吃',
  '怎么做',
  '怎样做',
  '如何做',
  '怎么弄',
  '做法',
  '步骤',
  '教程',
  '需要什么材料',
  '需要什么食材',
  '要什么材料',
  '需要什么',
  '需要哪些',
  '什么材料',
  '什么食材',
  '材料',
  '食材',
  '配料',
  '调料',
  '介绍一下',
  '告诉我',
  '请问',
  '帮我',
  '帮忙',
  '我想',
  '我要',
  '想学',
  '给我',
  '可以吗',
  '好不好',
  '能不能',
  '有没有',
  '怎么',
  '如何',
  '哪些',
  '多少',
  '什么',
  '一下',
  '一点',
  '推荐',
  '菜谱',
  '好吃吗',
  '好吃',
  '简单',
  '吗',
  '呢',
  '吧',
  '的',
  '了',
  '啊',
  '？',
  '?',
  '。',
  '，',
  ',',
  '！',
  '!',
  '、',
  '：',
  ':',
  '「',
  '」',
  '“',
  '”',
];

/** 只剩这些词说明用户没指明具体菜名，走推荐 */
const GENERIC_WORDS = [
  '今晚',
  '中午',
  '晚上',
  '早上',
  '晚饭',
  '午饭',
  '早餐',
  '夜宵',
  '吃的',
  '吃点',
  '菜',
  '好菜',
  '荤菜',
  '素菜',
  '硬菜',
  '快手',
  '家常',
  '下饭',
  '随机',
  '随便',
  '一些',
  '几道',
  '点',
];

const FALLBACK_SUGGESTIONS = ['今晚吃什么', '推荐几道快手菜', '剁椒鱼头怎么做'];

export function parseIntent(
  raw: string,
  categories: RecipeCategory[] = [],
): AssistantIntent {
  const message = raw.trim();
  if (!message) {
    return { kind: 'help' };
  }

  const category = categories.find((item) => message.includes(item.name));
  if (category) {
    return { kind: 'recommend', category };
  }

  if (HELP_PATTERN.test(message)) {
    return { kind: 'help' };
  }

  if (GREETING_PATTERN.test(message) && message.length <= 6) {
    return { kind: 'greeting' };
  }

  const keyword = extractKeyword(message);
  if (keyword && !isGenericKeyword(keyword)) {
    return { kind: 'search', keyword };
  }

  return { kind: 'recommend' };
}

export function buildReply({
  intent,
  categories,
  recipes,
  detail,
}: AssistantContext): AssistantReply {
  const suggestions = suggestionsFor(categories);

  if (intent.kind === 'greeting') {
    return {
      suggestions,
      text: '你好！我是你的做菜助手，想吃点什么？直接报菜名就行，比如「剁椒鱼头怎么做」；也可以让我按分类挑几道。',
    };
  }

  if (intent.kind === 'help') {
    return {
      suggestions,
      text: [
        '我可以帮你：',
        '· 报菜名查做法，讲清食材和步骤',
        '· 按分类挑菜，比如「推荐几道快手菜」',
        '· 点「开始做菜」后一步步带你做，该等的步骤帮你计时',
      ].join('\n'),
    };
  }

  if (intent.kind === 'recommend') {
    const scope = intent.category ? `「${intent.category.name}」` : '';

    if (recipes.length === 0) {
      return {
        suggestions,
        text: `暂时没有找到${scope || '合适的'}菜谱，换个分类或直接报菜名试试？`,
      };
    }

    return {
      recipes: recipes.slice(0, 3),
      suggestions,
      text: `给你挑了几道${scope}的菜，看看有没有想吃的。想动手就点「开始做菜」，我带着你一步步做。`,
    };
  }

  const exact = recipes.filter((recipe) => recipe.title === intent.keyword);
  const matches = exact.length > 0 ? exact : recipes;

  if (matches.length === 0) {
    return {
      suggestions,
      text: `没找到「${intent.keyword}」相关的菜谱。换个说法试试，比如直接报菜名，或者让我按分类推荐。`,
    };
  }

  if (matches.length === 1) {
    return {
      recipes: matches,
      suggestions,
      text: describeRecipe(
        matches[0],
        detail?.id === matches[0].id ? detail : undefined,
      ),
    };
  }

  return {
    recipes: matches.slice(0, 3),
    suggestions,
    text: `找到 ${matches.length} 道相关的菜，看看有没有想吃的。`,
  };
}

function describeRecipe(recipe: Recipe, detail?: Recipe): string {
  const minutes = totalMinutes(recipe);
  const meta = [
    recipe.category ? `属于${recipe.category}` : undefined,
    minutes ? `预计 ${minutes} 分钟` : undefined,
    recipe.servings ? `${recipe.servings} 人份` : undefined,
    difficultySummary(recipe.difficulty),
  ].filter(Boolean);

  const lines = [`「${recipe.title}」${meta.join('，')}。`];
  const ingredients = detail?.ingredients ?? [];
  const steps = detail?.steps ?? [];

  if (ingredients.length > 0) {
    const names = ingredients.slice(0, 6).map((item) => item.name);
    lines.push(
      `需要 ${ingredients.length} 种食材：${names.join('、')}${ingredients.length > names.length ? ' 等' : ''}。`,
    );
  }

  lines.push(
    steps.length > 0
      ? `共 ${steps.length} 个步骤，点「开始做菜」我带你一步步做，该等的步骤帮你计时。`
      : '点「查看详情」可以看到完整食材与步骤。',
  );

  return lines.join('\n');
}

function difficultySummary(difficulty?: number | null): string | undefined {
  if (!difficulty) {
    return undefined;
  }

  return ['难度简单', '难度中等', '难度偏高'][difficulty - 1] ?? undefined;
}

function extractKeyword(message: string): string | undefined {
  let text = message;

  for (const word of FILLER_WORDS) {
    text = text.split(word).join(' ');
  }

  const cleaned = text.replace(/[\s\p{P}]+/gu, ' ').trim();

  return cleaned.length >= 2 ? cleaned : undefined;
}

function isGenericKeyword(keyword: string): boolean {
  return (
    keyword.length > 12 || GENERIC_WORDS.some((word) => keyword.includes(word))
  );
}

function suggestionsFor(categories: RecipeCategory[]): string[] {
  const categoryPicks = categories
    .slice(0, 2)
    .map((category) => `推荐几道${category.name}`);

  return [...categoryPicks, ...FALLBACK_SUGGESTIONS].slice(0, 4);
}
