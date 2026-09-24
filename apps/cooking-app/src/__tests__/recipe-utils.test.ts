import type { Step } from '@po/types';

import {
  difficultyLabel,
  formatClock,
  formatIngredientAmount,
  sortSteps,
  splitTags,
  stepDurationSeconds,
  totalMinutes,
} from '@/lib/recipe-utils';

describe('difficultyLabel', () => {
  it('maps known difficulties', () => {
    expect(difficultyLabel(1)).toBe('简单');
    expect(difficultyLabel(3)).toBe('困难');
  });

  it('falls back for missing values', () => {
    expect(difficultyLabel(null)).toBe('未知');
    expect(difficultyLabel(9)).toBe('难度 9');
  });
});

describe('splitTags', () => {
  it('trims and drops empty tags', () => {
    expect(splitTags('下饭, 经典 ,, 辣')).toEqual(['下饭', '经典', '辣']);
  });

  it('returns an empty list without tags', () => {
    expect(splitTags(null)).toEqual([]);
  });
});

describe('formatIngredientAmount', () => {
  it('drops trailing zeros from stored amounts', () => {
    expect(
      formatIngredientAmount({ amount: '1.0', name: '鱼头', unit: '个' }),
    ).toBe('1 个');
    expect(
      formatIngredientAmount({ amount: '150.00', name: '剁椒', unit: 'g' }),
    ).toBe('150 g');
  });

  it('keeps non numeric amounts as-is', () => {
    expect(
      formatIngredientAmount({ amount: '半', name: '蒜', unit: '头' }),
    ).toBe('半 头');
  });

  it('falls back to 适量 without amount or unit', () => {
    expect(formatIngredientAmount({ name: '盐' })).toBe('适量');
    expect(
      formatIngredientAmount({ amount: '  ', name: '盐', unit: ' ' }),
    ).toBe('适量');
  });

  it('scales numeric amounts by the serving factor', () => {
    expect(
      formatIngredientAmount({ amount: '150.00', name: '剁椒', unit: 'g' }, 2),
    ).toBe('300 g');
    expect(
      formatIngredientAmount({ amount: '1.0', name: '鱼头', unit: '个' }, 0.5),
    ).toBe('0.5 个');
  });

  it('keeps non numeric amounts when scaling', () => {
    expect(
      formatIngredientAmount({ amount: '半', name: '蒜', unit: '头' }, 2),
    ).toBe('半 头');
  });
});

describe('totalMinutes', () => {
  it('prefers the stored total time', () => {
    expect(totalMinutes({ cookTime: 10, prepTime: 5, totalTime: 20 })).toBe(20);
  });

  it('falls back to prep plus cook time', () => {
    expect(totalMinutes({ cookTime: 15, prepTime: 20, totalTime: null })).toBe(
      35,
    );
  });

  it('returns nothing without any timing', () => {
    expect(totalMinutes({ cookTime: null, prepTime: null })).toBeUndefined();
  });
});

describe('sortSteps', () => {
  it('orders steps by stepNumber', () => {
    const steps: Step[] = [
      { content: '第三', stepNumber: 3 },
      { content: '第一', stepNumber: 1 },
    ];

    expect(sortSteps(steps).map((step) => step.stepNumber)).toEqual([1, 3]);
  });

  it('handles missing steps', () => {
    expect(sortSteps(null)).toEqual([]);
  });
});

describe('stepDurationSeconds', () => {
  it('converts minutes to seconds', () => {
    expect(
      stepDurationSeconds({ content: '腌', duration: 15, stepNumber: 1 }),
    ).toBe(900);
  });

  it('treats empty durations as no timer', () => {
    expect(stepDurationSeconds({ content: '切', stepNumber: 1 })).toBe(0);
  });
});

describe('formatClock', () => {
  it('formats seconds as MM:SS', () => {
    expect(formatClock(0)).toBe('00:00');
    expect(formatClock(65)).toBe('01:05');
    expect(formatClock(600)).toBe('10:00');
  });

  it('clamps negative values', () => {
    expect(formatClock(-3)).toBe('00:00');
  });
});
