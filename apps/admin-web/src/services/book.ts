import { request } from '@umijs/max';
import type {
  Book,
  BookChapter,
  BookCharacter,
  BookRequest,
  ChapterRequest,
  CharacterRequest,
  GenreOption,
  PageResponse,
  Result,
} from '@po/types';

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

// ── Genres ───────────────────────────────────────────────────────────────────

/** 获取小说类型字典 */
export async function getBookGenres(options?: Record<string, unknown>) {
  return request<Result<GenreOption[]>>('/api/books/genres', {
    method: 'GET',
    ...(options || {}),
  });
}

// ── Books ────────────────────────────────────────────────────────────────────

/** 分页获取书籍列表 */
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

/** 获取单个书籍详情 */
export async function getBook(id: number, options?: Record<string, unknown>) {
  return request<Result<Book>>(`/api/books/${id}`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 创建书籍 */
export async function createBook(body: BookRequest, options?: Record<string, unknown>) {
  return request<Result<Book>>('/api/books', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新书籍 */
export async function updateBook(
  id: number,
  body: BookRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<Book>>(`/api/books/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 删除书籍（软删除，级联删除章节与角色） */
export async function deleteBook(id: number, options?: Record<string, unknown>) {
  return request<Result<string>>(`/api/books/${id}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}

// ── Chapters ─────────────────────────────────────────────────────────────────

/** 获取书籍章节列表 */
export async function getChapters(bookId: number, options?: Record<string, unknown>) {
  return request<Result<BookChapter[]>>(`/api/books/${bookId}/chapters`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 获取单个章节 */
export async function getChapter(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(
    `/api/books/${bookId}/chapters/${chapterId}`,
    { method: 'GET', ...(options || {}) },
  );
}

/** 创建章节 */
export async function createChapter(
  bookId: number,
  body: ChapterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(`/api/books/${bookId}/chapters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新章节 */
export async function updateChapter(
  bookId: number,
  chapterId: number,
  body: ChapterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookChapter>>(
    `/api/books/${bookId}/chapters/${chapterId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 删除章节（软删除） */
export async function deleteChapter(
  bookId: number,
  chapterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>(`/api/books/${bookId}/chapters/${chapterId}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}

// ── Characters ───────────────────────────────────────────────────────────────

/** 获取书籍角色列表 */
export async function getCharacters(bookId: number, options?: Record<string, unknown>) {
  return request<Result<BookCharacter[]>>(`/api/books/${bookId}/characters`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 创建角色 */
export async function createCharacter(
  bookId: number,
  body: CharacterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookCharacter>>(`/api/books/${bookId}/characters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新角色 */
export async function updateCharacter(
  bookId: number,
  characterId: number,
  body: CharacterRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<BookCharacter>>(
    `/api/books/${bookId}/characters/${characterId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      data: body,
      ...(options || {}),
    },
  );
}

/** 删除角色（软删除） */
export async function deleteCharacter(
  bookId: number,
  characterId: number,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>(`/api/books/${bookId}/characters/${characterId}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}
