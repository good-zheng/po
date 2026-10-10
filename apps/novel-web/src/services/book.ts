import type {
  Book,
  BookChapter,
  BookCharacter,
  GenreOption,
  PageResponse,
  Result,
} from '@po/types';
import { request } from '@umijs/max';

export type {
  Book,
  BookChapter,
  BookCharacter,
  BookListParams,
  BookRequest,
  ChapterRequest,
  CharacterRequest,
  GenreOption,
} from '@po/types';

/**
 * 阅读侧只暴露读接口。写接口（建书、录章节、维护人物）属于 M3 的创作端，
 * 届时从 git 历史捞回：`git show b23a633^:apps/admin-web/src/services/book.ts`。
 */

/** 目录条目：后端尚未提供瘦版投影，这里先把正文从类型与渲染路径上剥掉 */
export type ChapterBrief = Pick<
  BookChapter,
  'id' | 'bookId' | 'chapterIndex' | 'title' | 'wordCount'
>;

export const toChapterBriefs = (chapters: BookChapter[] = []): ChapterBrief[] =>
  chapters.map(({ id, bookId, chapterIndex, title, wordCount }) => ({
    id,
    bookId,
    chapterIndex,
    title,
    wordCount,
  }));

/** 小说类型字典 */
export async function getBookGenres(options?: Record<string, unknown>) {
  return request<Result<GenreOption[]>>('/api/books/genres', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 分页获取书架。后端页码从 0 起 */
export async function getBooks(
  params: {
    page?: number;
    size?: number;
    keyword?: string;
    genre?: string;
    status?: string;
  },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<Book>>>('/api/books', {
    method: 'GET',
    params,
    ...(options || {}),
  });
}

/** 单本书详情 */
export async function getBook(id: number, options?: Record<string, unknown>) {
  return request<Result<Book>>(`/api/books/${id}`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 章节列表（注意：当前后端返回含正文，见 NOVEL_WEB_PRD.md §7-①） */
export async function getChapters(
  bookId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter[]>>(`/api/books/${bookId}/chapters`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 单个章节，正文只在阅读页取 */
export async function getChapter(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(
    `/api/books/${bookId}/chapters/${chapterId}`,
    {
      method: 'GET',
      ...(options || {}),
    },
  );
}

/** 人物列表 */
export async function getCharacters(
  bookId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<BookCharacter[]>>(`/api/books/${bookId}/characters`, {
    method: 'GET',
    ...(options || {}),
  });
}
