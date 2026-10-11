import { describe, expect, it } from 'vitest';

import {
  chineseNumber,
  parseChapterRange,
  resolveContinueRun,
} from './chapterRange';

describe('chineseNumber', () => {
  it.each([
    ['三', 3],
    ['两', 2],
    ['十', 10],
    ['十三', 13],
    ['二十', 20],
    ['二十五', 25],
    ['一百零五', 105],
    ['二千零五十', 2050],
    ['二〇二六', 2026],
    ['12', 12],
  ])('%s → %i', (input, expected) => {
    expect(chineseNumber(input)).toBe(expected);
  });

  it.each(['', '  ', 'abc', '第', '十一章'])('「%s」不是数 → null', (input) => {
    expect(chineseNumber(input)).toBeNull();
  });
});

describe('parseChapterRange', () => {
  it('作者的原话：第三至第十章', () => {
    expect(parseChapterRange('开始创作第三至第十章的内容')).toEqual({
      from: 3,
      to: 10,
      count: 8,
    });
  });

  it('阿拉伯数字与各种分隔符都要认', () => {
    expect(parseChapterRange('写第3-10章')).toEqual({
      from: 3,
      to: 10,
      count: 8,
    });
    expect(parseChapterRange('第二章到第五章')).toEqual({
      from: 2,
      to: 5,
      count: 4,
    });
    expect(parseChapterRange('10～13章')).toEqual({
      from: 10,
      to: 13,
      count: 4,
    });
    expect(parseChapterRange('第 3 至 第 10 章')).toEqual({
      from: 3,
      to: 10,
      count: 8,
    });
  });

  it('只给起点：从第 8 章起往后写', () => {
    expect(parseChapterRange('从第8章起往后写')).toEqual({
      from: 8,
      to: null,
      count: null,
    });
    expect(parseChapterRange('写第三章').from).toBe(3);
  });

  it('只给额度：写五章', () => {
    expect(parseChapterRange('接着写五章')).toEqual({
      from: null,
      to: null,
      count: 5,
    });
    expect(parseChapterRange('再加 2 章').count).toBe(2);
  });

  it('只给终点：接着写到第十章（到/至 前缀算终点，不算起点）', () => {
    expect(parseChapterRange('接着写到第十章')).toEqual({
      from: null,
      to: 10,
      count: null,
    });
    expect(parseChapterRange('更新至第十二章').to).toBe(12);
  });

  it('没写章数就什么都不要猜', () => {
    expect(parseChapterRange('一个程序员能改写物理法则')).toEqual({
      from: null,
      to: null,
      count: null,
    });
    // 倒着要的区间不猜意图
    expect(parseChapterRange('第10至第3章')).toEqual({
      from: null,
      to: null,
      count: null,
    });
  });

  it('序数优先于额度：第三至第十章不会被读成「写 10 章」', () => {
    expect(parseChapterRange('开始创作第三至第十章的内容').count).toBe(8);
  });
});

describe('resolveContinueRun（界面预告必须与服务端收敛一致）', () => {
  it('区间还没写：从第 3 章起补齐到第 10 章', () => {
    expect(resolveContinueRun('开始创作第三至第十章的内容', 2)).toMatchObject({
      fromChapter: 3,
      chapterCount: 8,
      start: 3,
      count: 8,
    });
  });

  it('区间写了一半：已写 5 章时仍只补第 6 至 10 章，不回退去改第 3 章', () => {
    const run = resolveContinueRun('开始创作第三至第十章的内容', 5);
    expect(run).toMatchObject({ start: 6, count: 5 });
    expect(run.preview).toContain('第 6 至 10 章共 5 章');
  });

  it('只要终点：已写 10 章时「写到第十三章」= 追加 3 章', () => {
    expect(resolveContinueRun('写到第十三章', 10)).toMatchObject({
      fromChapter: null,
      chapterCount: 3,
      start: 11,
      count: 3,
    });
  });

  it('没写章数：走服务端默认额度 3 章', () => {
    expect(resolveContinueRun('接着往下写，节奏快一点', 7)).toMatchObject({
      fromChapter: null,
      chapterCount: null,
      start: 8,
      count: 3,
    });
  });

  it('要得比上限多：按 20 章收敛而不是把大纲撑爆', () => {
    expect(resolveContinueRun('第三至第五十章', 2).count).toBe(20);
  });

  it('要的区间早写完了：至少往后追加 1 章而不是原地不动', () => {
    expect(resolveContinueRun('写第一至第三章', 10).count).toBe(1);
  });
});
