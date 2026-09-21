export type GenreOption = {
  value: string;
  label: string;
};

export type Book = {
  id: number;
  authorId: number;
  title: string;
  description?: string | null;
  coverImage?: string | null;
  genre?: string | null;
  status: string;
  wordCount: number;
  author?: string | null;
  createdAt?: string;
  updatedAt?: string;
};

export type BookRequest = {
  title: string;
  description?: string;
  coverImage?: string;
  genre?: string;
  author?: string;
  status?: string;
};

export type BookChapter = {
  id: number;
  bookId: number;
  chapterIndex: number;
  title: string;
  content?: string | null;
  wordCount: number;
  createdAt?: string;
  updatedAt?: string;
};

export type ChapterRequest = {
  title: string;
  content?: string;
  chapterIndex?: number;
};

export type BookCharacter = {
  id: number;
  bookId: number;
  name: string;
  description?: string | null;
  avatar?: string | null;
  createdAt?: string;
  updatedAt?: string;
};

export type CharacterRequest = {
  name: string;
  description?: string;
  avatar?: string;
};

export type BookListParams = {
  current?: number;
  pageSize?: number;
  keyword?: string;
  genre?: string;
  status?: string;
};
