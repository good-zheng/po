export type DiffLine = {
  kind: 'same' | 'add' | 'del';
  /** 同类别内取来源行号：换版本对时整个数组会被替换，键仍不重复，供 React key 用 */
  key: string;
  text: string;
};

/**
 * 行级 diff（LCS 回溯），给中栏的「改了什么」视图用。
 *
 * 一期不引第三方 diff 库：章节正文按段落切，几十行的量级用得上 DP，也读得懂这段代码。
 * 超长（> 800 行任一侧）时退回「整段替换」，避免 O(n·m) 在浏览器里卡住。
 */
export function diffLines(before: string, after: string): DiffLine[] {
  const a = before.split('\n');
  const b = after.split('\n');
  if (a.length > 800 || b.length > 800) {
    return [
      ...a.map((text, i) => ({ kind: 'del' as const, key: `d${i}`, text })),
      ...b.map((text, j) => ({ kind: 'add' as const, key: `a${j}`, text })),
    ];
  }
  const table: number[][] = Array.from({ length: a.length + 1 }, () =>
    new Array(b.length + 1).fill(0),
  );
  for (let i = a.length - 1; i >= 0; i -= 1) {
    for (let j = b.length - 1; j >= 0; j -= 1) {
      table[i][j] =
        a[i] === b[j]
          ? table[i + 1][j + 1] + 1
          : Math.max(table[i + 1][j], table[i][j + 1]);
    }
  }
  const out: DiffLine[] = [];
  let i = 0;
  let j = 0;
  while (i < a.length && j < b.length) {
    if (a[i] === b[j]) {
      out.push({ kind: 'same', key: `s${i}`, text: a[i] });
      i += 1;
      j += 1;
    } else if (table[i + 1][j] >= table[i][j + 1]) {
      out.push({ kind: 'del', key: `d${i}`, text: a[i] });
      i += 1;
    } else {
      out.push({ kind: 'add', key: `a${j}`, text: b[j] });
      j += 1;
    }
  }
  while (i < a.length) {
    out.push({ kind: 'del', key: `d${i}`, text: a[i] });
    i += 1;
  }
  while (j < b.length) {
    out.push({ kind: 'add', key: `a${j}`, text: b[j] });
    j += 1;
  }
  return out;
}
