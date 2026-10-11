/**
 * 从一句话里抠出「写第几章到第几章」。
 *
 * 只做解析，不做决策：真正的起点与章数由服务端按库里的已定稿章数收敛（只追加、
 * 不改写已定稿正文），这里解析出来的数只是给界面一句人话预告，以及帧里的建议值。
 */
export type ChapterRange = {
  from: number | null;
  to: number | null;
  count: number | null;
};

const CN_DIGITS: Record<string, number> = {
  〇: 0,
  零: 0,
  一: 1,
  二: 2,
  两: 2,
  三: 3,
  四: 4,
  五: 5,
  六: 6,
  七: 7,
  八: 8,
  九: 9,
};

const CN_UNITS: Record<string, number> = { 十: 10, 百: 100, 千: 1000 };

/** 一个数：阿拉伯数字或中文数字（十三 / 二十 / 一百零五 / 二〇二六）。 */
export function chineseNumber(raw: string): number | null {
  const token = raw.trim();
  if (!token) return null;
  if (/^\d+$/.test(token)) return Number(token);
  const chars = [...token];
  if (!chars.every((char) => char in CN_DIGITS || char in CN_UNITS))
    return null;
  // 纯数字串按位拼读（「二〇二六」→ 2026）；带进位单位的走位值累加。
  if (chars.every((char) => char in CN_DIGITS)) {
    return Number(chars.map((char) => String(CN_DIGITS[char])).join(''));
  }
  let total = 0;
  let current = 0;
  for (const char of chars) {
    const digit = CN_DIGITS[char];
    if (digit !== undefined) {
      current = digit;
      continue;
    }
    total += (current === 0 ? 1 : current) * CN_UNITS[char];
    current = 0;
  }
  return total + current;
}

// 序数与额度都靠「章/节」这个量词锚定，量词前后允许空格：作者会打「第 3 至 10 章」。
const NUM = '([0-9]+|[〇零一二两三四五六七八九十百千]+)';
const SEP = String.raw`[至到~～\-—–]`;

const RANGE_RE = new RegExp(
  String.raw`(?:第\s*)?${NUM}\s*[章节]?\s*${SEP}\s*(?:第\s*)?${NUM}\s*[章节]`,
);
const ORDINAL_RE = new RegExp(String.raw`第\s*${NUM}\s*[章节]`, 'g');
const COUNT_RE = new RegExp(String.raw`${NUM}\s*[章节]`, 'g');

/** 数词前面是这几个字，说明它是序数（第 3 章 / 到第 3 章），不是「写 3 章」的额度。 */
const NOT_COUNT = new Set(['第', '到', '至']);

function charBefore(text: string, index: number): string {
  let cursor = index - 1;
  while (cursor >= 0 && /\s/.test(text[cursor])) cursor -= 1;
  return cursor >= 0 ? text[cursor] : '';
}

export function parseChapterRange(text: string): ChapterRange {
  const source = text ?? '';

  const range = RANGE_RE.exec(source);
  if (range) {
    const from = chineseNumber(range[1]);
    const to = chineseNumber(range[2]);
    // 倒着要（第 10 至 3 章）不猜意图，当作没写章数。
    if (from == null || to == null || to < from)
      return { from: null, to: null, count: null };
    return { from, to, count: to - from + 1 };
  }

  let from: number | null = null;
  let to: number | null = null;
  for (const match of source.matchAll(ORDINAL_RE)) {
    const value = chineseNumber(match[1]);
    if (value == null) continue;
    const head = charBefore(source, match.index);
    if (head === '到' || head === '至') {
      to = value;
      break;
    }
    if (from == null) from = value;
  }

  if (from == null && to == null) {
    for (const match of source.matchAll(COUNT_RE)) {
      if (NOT_COUNT.has(charBefore(source, match.index))) continue;
      const value = chineseNumber(match[1]);
      if (value != null) return { from: null, to: null, count: value };
    }
  }

  return { from, to, count: null };
}

/**
 * 把「作者的一句话 + 库里已写章数」算成这一轮真正发出去的键，以及同一套算法的人话预告。
 *
 * 收敛规则必须与服务端 `_continue_conceive` 一致（`end = from + count - 1`，只从
 * 「已定稿章数 + 1」往后追加，上限 20 章）：两边各算一遍而结果不同时，界面预告写的章数
 * 就成了作者对不上账的那一句。区间两头都说了时发字面区间，让服务端自己按库里进度收敛。
 */
export type ContinueRun = {
  fromChapter: number | null;
  chapterCount: number | null;
  /** 本轮实际起点（永远是已写章数 + 1） */
  start: number;
  /** 本轮实际章数（已按上限收敛） */
  count: number;
  /** 界面上给作者看的那句预告 */
  preview: string;
};

export function resolveContinueRun(
  text: string,
  written: number,
  options: { defaultCount?: number; maxCount?: number } = {},
): ContinueRun {
  const defaultCount = options.defaultCount ?? 3;
  const maxCount = options.maxCount ?? 20;
  const range = parseChapterRange(text);
  const chapterCount =
    range.from != null && range.to != null
      ? range.count
      : range.to != null
        ? Math.max(1, range.to - written)
        : range.count;
  const end =
    range.from != null && chapterCount != null
      ? range.from + chapterCount - 1
      : written + (chapterCount ?? defaultCount);
  const count = Math.min(Math.max(end - written, 1), maxCount);
  const start = written + 1;
  return {
    fromChapter: range.from,
    chapterCount,
    start,
    count,
    preview: `这本书已写 ${written} 章，本轮往后追加第 ${start} 至 ${
      start + count - 1
    } 章共 ${count} 章，不改写已定稿正文`,
  };
}
