import { describe, expect, it } from 'vitest';
import { diffLines } from './lineDiff';

const kinds = (before: string, after: string) =>
  diffLines(before, after).map((l) => l.kind);
const texts = (before: string, after: string) =>
  diffLines(before, after).map((l) => l.text);

describe('diffLines', () => {
  it('两版相同：全是 same，不产生增删', () => {
    expect(kinds('一\n二', '一\n二')).toEqual(['same', 'same']);
  });

  it('插入一行：只有 add，原有行保持 same', () => {
    expect(diffLines('一\n三', '一\n二\n三')).toEqual([
      { kind: 'same', key: 's0', text: '一' },
      { kind: 'add', key: 'a1', text: '二' },
      { kind: 'same', key: 's1', text: '三' },
    ]);
  });

  it('删掉一行：只有 del', () => {
    expect(texts('一\n二\n三', '一\n三')).toEqual(['一', '二', '三']);
    expect(kinds('一\n二\n三', '一\n三')).toEqual(['same', 'del', 'same']);
  });

  it('改一行：先 del 后 add（同位置整行替换）', () => {
    expect(kinds('一\n二', '一\n貳')).toEqual(['same', 'del', 'add']);
  });

  it('兜底路径也走同一套键：任一侧超 800 行时退回整段替换', () => {
    const long = Array.from({ length: 801 }, (_, i) => `第${i}行`).join('\n');
    const out = diffLines(long, '新开头\n新结尾');
    expect(out.filter((l) => l.kind === 'del')).toHaveLength(801);
    expect(out.filter((l) => l.kind === 'add')).toHaveLength(2);
    expect(out.some((l) => l.kind === 'same')).toBe(false);
  });

  // React key 的依据：once 换版本对时整个数组被替换，键不能靠下标
  it('键在同一次结果内唯一', () => {
    const before = Array.from({ length: 40 }, (_, i) => `段落 ${i}`).join('\n');
    const after = Array.from({ length: 40 }, (_, i) =>
      i % 3 === 0 ? `改后 ${i}` : `段落 ${i}`,
    ).join('\n');
    const keys = diffLines(before, after).map((l) => l.key);
    expect(new Set(keys).size).toBe(keys.length);
  });
});
