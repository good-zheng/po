import type { Recipe, RecipeCategory } from '@po/types';

import { buildReply, parseIntent } from '@/lib/ai/assistant';

const categories: RecipeCategory[] = [
  { description: null, icon: '⚡', id: 2, name: '快手菜', sortOrder: 2 },
  { description: null, icon: '🌶️', id: 12, name: '湘菜', sortOrder: 100 },
];

const recipe: Recipe = {
  authorId: 1,
  category: '湘菜',
  difficulty: 2,
  id: 1,
  isPublic: true,
  likesCount: 12,
  servings: 4,
  title: '剁椒鱼头',
  totalTime: 35,
};

describe('parseIntent', () => {
  it('detects greetings', () => {
    expect(parseIntent('你好', categories).kind).toBe('greeting');
  });

  it('detects help questions', () => {
    expect(parseIntent('你能做什么', categories).kind).toBe('help');
  });

  it('prefers a category over the keyword', () => {
    const intent = parseIntent('推荐几道快手菜', categories);

    expect(intent).toEqual({ category: categories[0], kind: 'recommend' });
  });

  it('extracts a dish name from a question', () => {
    expect(parseIntent('剁椒鱼头怎么做', categories)).toEqual({
      kind: 'search',
      keyword: '剁椒鱼头',
    });
  });

  it('usually falls back to recommend for vague questions', () => {
    expect(parseIntent('今晚吃什么', categories).kind).toBe('recommend');
  });

  it('treats an empty message as help', () => {
    expect(parseIntent('   ', categories).kind).toBe('help');
  });
});

describe('buildReply', () => {
  it('carries category suggestions', () => {
    const reply = buildReply({
      categories,
      intent: { kind: 'help' },
      recipes: [],
    });

    expect(reply.text).toContain('我可以帮你');
    expect(reply.suggestions).toEqual(
      expect.arrayContaining(['推荐几道快手菜', '今晚吃什么']),
    );
  });

  it('returns at most three recipes for a recommendation', () => {
    const recipes = [1, 2, 3, 4].map((id) => ({ ...recipe, id }));

    const reply = buildReply({
      categories,
      intent: { kind: 'recommend', category: categories[0] },
      recipes,
    });

    expect(reply.recipes).toHaveLength(3);
    expect(reply.text).toContain('快手菜');
  });

  it('explains an empty recommendation', () => {
    const reply = buildReply({
      categories,
      intent: { kind: 'recommend' },
      recipes: [],
    });

    expect(reply.recipes).toBeUndefined();
    expect(reply.text).toContain('换个分类');
  });

  it('describes a matched dish with its detail', () => {
    const reply = buildReply({
      categories,
      detail: {
        ...recipe,
        ingredients: [{ amount: '1.0', name: '鱼头', unit: '个' }],
        steps: [
          { content: '腌制', duration: 15, stepNumber: 1 },
          { content: '上锅蒸', duration: 10, stepNumber: 2 },
        ],
      },
      intent: { kind: 'search', keyword: '剁椒鱼头' },
      recipes: [recipe],
    });

    expect(reply.recipes).toHaveLength(1);
    expect(reply.text).toContain('「剁椒鱼头」');
    expect(reply.text).toContain('鱼头');
    expect(reply.text).toContain('共 2 个步骤');
    expect(reply.text).toContain('开始做菜');
  });

  it('admits when nothing matched', () => {
    const reply = buildReply({
      categories,
      intent: { kind: 'search', keyword: '佛跳墙' },
      recipes: [],
    });

    expect(reply.text).toContain('没找到');
  });
});
