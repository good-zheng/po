import type { Request, Response } from 'express';

/**
 * 仅本地开发用，且**默认不加载**：`pnpm novel:dev` 已是 `MOCK=none`（读真后端），
 * 只有 `pnpm novel:mock` 这一档才会用它顶掉 `/api/books*`。
 *
 * 这里的 4 本书是写死的假数据，与库里 `book` 表那几本不是同一批：
 * 排版、滚动、首屏可以在这儿验，数据对不对必须在 `novel:dev` 上验，
 * 否则读者端和管理端看到的「同一本书」其实来自两个来源。
 *
 * 用途是在 Java novel 模块恢复（M1）之前把阅读三页跑通；数据结构对齐
 * services/api 的 Result 信封与 Spring 的 Page 序列化字段。
 */

type Row = {
  id: number;
  bookId: number;
  chapterIndex: number;
  title: string;
  content: string;
  wordCount: number;
};

/** 真实章节动辄数千字，mock 也按这个量级给，否则测不出滚动位置与首屏表现 */
const paragraphs = (label: string) =>
  Array.from({ length: 26 }, (_unused, i) =>
    i === 0
      ? `${label}。窗外的雨从傍晚下到现在，檐上的水声把屋子衬得更静，他握着笔，迟迟没有落下第一个字。`
      : [
          `“别急，”她把茶盏推过来一点，“想清楚了再写，写出来的东西才站得住。”`,
          `他点点头，目光却落在窗外那条被雨淋亮的石板上。这条路他走过千百回，可今天要写在纸上的那一步，他还没有想好该怎么起头。`,
          `屋里安静了很久。久到茶都凉了一层，他才终于把笔尖按下去，在纸上落下短短的一行。`,
          `雨声填满了剩下的空白。他没有抬头，只是把那一行又看了一遍，然后继续往下写。`,
        ][i % 4],
  ).join('\n');

const chapters: Row[] = Array.from({ length: 12 }, (_unused, i) => ({
  id: 100 + i,
  bookId: 1,
  chapterIndex: i + 1,
  title: `第${['一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二'][i]}章 · 起风`,
  content: paragraphs(`楔子 ${i + 1}`),
  wordCount: 320 + i * 12,
}));

const books = [
  {
    id: 1,
    authorId: 1,
    title: '檐下三年',
    description:
      '一个教书匠在老宅檐下写地方志的三年。故事从一场迟迟不落的笔开始，写缓慢、写耐心，写一个人如何把一件小事做完。',
    coverImage: null as string | null,
    genre: 'other',
    status: 'ongoing',
    wordCount: 128_400,
    author: '示例作者',
    createdAt: '2026-08-01T09:00:00.000Z',
    updatedAt: '2026-09-20T09:00:00.000Z',
  },
  {
    id: 2,
    authorId: 1,
    title: '云海驿',
    description: '边地驿站里往来的旅客，各带着一件不肯说的事。',
    coverImage: null,
    genre: 'wuxia',
    status: 'completed',
    wordCount: 64_200,
    author: '佚名',
    createdAt: '2026-07-11T09:00:00.000Z',
    updatedAt: '2026-08-30T09:00:00.000Z',
  },
];

const wrap = <T>(data: T) => ({
  code: 200,
  success: true,
  data,
  message: 'ok',
});

export default {
  'GET /api/books/genres': (_req: Request, res: Response) => {
    res.send(
      wrap([
        { value: 'fantasy', label: '玄幻' },
        { value: 'wuxia', label: '武侠' },
        { value: 'scifi', label: '科幻' },
        { value: 'romance', label: '言情' },
        { value: 'mystery', label: '悬疑' },
        { value: 'other', label: '其他' },
      ]),
    );
  },

  'GET /api/books': (req: Request, res: Response) => {
    const page = Number(req.query.page ?? 0);
    const size = Number(req.query.size ?? 20);
    const keyword = String(req.query.keyword ?? '').trim();
    const genre = String(req.query.genre ?? '');
    const filtered = books.filter(
      (b) =>
        (!genre || b.genre === genre) &&
        (!keyword ||
          b.title.includes(keyword) ||
          (b.author ?? '').includes(keyword)),
    );
    res.send(
      wrap({
        content: filtered.slice(page * size, page * size + size),
        totalElements: filtered.length,
        totalPages: Math.ceil(filtered.length / size) || 1,
        number: page,
        size,
      }),
    );
  },

  'GET /api/books/:id/characters': (req: Request, res: Response) => {
    res.send(
      wrap([
        {
          id: 1,
          bookId: Number(req.params.id),
          name: '沈砚',
          description: '教书匠，负责修镇上的地方志。',
          avatar: null,
        },
        {
          id: 2,
          bookId: Number(req.params.id),
          name: '阿梨',
          description: '檐下常客，话不多，看得准。',
          avatar: null,
        },
      ]),
    );
  },

  'GET /api/books/:id/chapters/:chapterId': (req: Request, res: Response) => {
    const chapter = chapters.find((c) => c.id === Number(req.params.chapterId));
    if (!chapter) {
      res.send({
        code: 404,
        success: false,
        data: null,
        message: '章节不存在',
      });
      return;
    }
    res.send(wrap(chapter));
  },

  'GET /api/books/:id/chapters': (req: Request, res: Response) => {
    const bookId = Number(req.params.id);
    res.send(wrap(bookId === 1 ? chapters : []));
  },

  'GET /api/books/:id': (req: Request, res: Response) => {
    const book = books.find((b) => b.id === Number(req.params.id));
    if (!book) {
      res.send({
        code: 404,
        success: false,
        data: null,
        message: '书籍不存在',
      });
      return;
    }
    res.send(wrap(book));
  },
};
