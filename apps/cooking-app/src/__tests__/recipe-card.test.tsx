import type { Recipe } from '@po/types';
import { render } from '@testing-library/react-native';

import { RecipeCard } from '@/components/recipe-card';

const recipe: Recipe = {
  authorId: 1,
  category: '湘菜',
  description: '鲜辣开胃的经典下饭菜。',
  difficulty: 2,
  id: 1,
  isPublic: true,
  likesCount: 128,
  servings: 4,
  tags: '下饭,经典,辣',
  title: '剁椒鱼头',
  totalTime: 35,
};

describe('RecipeCard', () => {
  it('renders the recipe summary', async () => {
    const screen = await render(<RecipeCard recipe={recipe} />);

    expect(screen.getByText('剁椒鱼头')).toBeOnTheScreen();
    expect(screen.getByText('35 分钟')).toBeOnTheScreen();
    expect(screen.getByText('湘菜')).toBeOnTheScreen();
  });
});
