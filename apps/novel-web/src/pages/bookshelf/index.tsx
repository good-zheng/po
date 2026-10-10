import type { Book, GenreOption } from '@po/types';
import { Link } from '@umijs/max';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import BookCover from '@/components/BookCover';
import StateCard from '@/components/StateCard';
import { readAllProgress } from '@/hooks/useReadingProgress';
import { getBookGenres, getBooks } from '@/services/book';

const PAGE_SIZE = 24;

/** 与后端 status 取值一致（schema.sql 默认 ongoing） */
const statusText: Record<string, string> = {
  ongoing: '连载中',
  completed: '已完结',
  paused: '暂停更新',
};

/** 骨架屏格子内容一致，key 取固定常量而不是下标（biome noArrayIndexKey） */
const SHELF_SKELETON = Array.from({ length: 8 }, (_unused, i) => `slot-${i}`);

export default function BookshelfPage() {
  const [genres, setGenres] = useState<GenreOption[]>([]);
  const [keywordInput, setKeywordInput] = useState('');
  const [query, setQuery] = useState({ keyword: '', genre: '' });
  const [books, setBooks] = useState<Book[]>([]);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const progress = useMemo(() => readAllProgress(), []);

  useEffect(() => {
    getBookGenres({ skipErrorHandler: true })
      .then((res) => setGenres(res.data ?? []))
      .catch(() => setGenres([]));
  }, []);

  const load = useCallback(
    async (nextPage: number, replace: boolean) => {
      setLoading(true);
      setFailed(false);
      try {
        const res = await getBooks({
          page: nextPage,
          size: PAGE_SIZE,
          keyword: query.keyword || undefined,
          genre: query.genre || undefined,
        });
        const result = res.data;
        setBooks((prev) =>
          replace ? result.content : [...prev, ...result.content],
        );
        setPage(nextPage);
        setTotalPages(result.totalPages || 1);
        setTotal(result.totalElements);
      } catch (_error) {
        // 后端未起或网关异常：书架给出重试入口而不是白屏
        setFailed(true);
        if (replace) setBooks([]);
      } finally {
        setLoading(false);
      }
    },
    [query],
  );

  useEffect(() => {
    load(0, true);
  }, [load]);

  const activeGenreLabel = genres.find(
    (item) => item.value === query.genre,
  )?.label;

  return (
    <>
      <div className="page-head">
        <h1 className="page-title">书架</h1>
        {!loading && !failed && books.length > 0 ? (
          <p className="page-sub">
            {total} 部作品
            {activeGenreLabel ? ` · ${activeGenreLabel}` : ''}
            {query.keyword ? ` · 「${query.keyword}」` : ''}
          </p>
        ) : null}
      </div>

      <form
        className="filter-row"
        onSubmit={(event) => {
          event.preventDefault();
          setQuery((prev) => ({ ...prev, keyword: keywordInput.trim() }));
        }}
      >
        <input
          className="filter-input"
          type="search"
          inputMode="search"
          placeholder="按书名或作者搜索"
          value={keywordInput}
          onChange={(event) => setKeywordInput(event.target.value)}
          aria-label="搜索书籍"
        />
        <button className="filter-search" type="submit">
          搜索
        </button>
      </form>

      <div className="filter-chips">
        <button
          type="button"
          className={`filter-chip${query.genre === '' ? ' filter-chip-on' : ''}`}
          onClick={() => setQuery((prev) => ({ ...prev, genre: '' }))}
        >
          全部
        </button>
        {genres.map((item) => (
          <button
            type="button"
            key={item.value}
            className={`filter-chip${query.genre === item.value ? ' filter-chip-on' : ''}`}
            onClick={() => setQuery((prev) => ({ ...prev, genre: item.value }))}
          >
            {item.label}
          </button>
        ))}
      </div>

      {failed ? (
        <StateCard
          kind="error"
          title="暂时读不到书架内容"
          hint="后端服务可能没起来，或网络不通。"
          action={
            <button
              type="button"
              className="btn-ghost"
              onClick={() => load(0, true)}
            >
              重试
            </button>
          }
        />
      ) : !loading && books.length === 0 ? (
        <StateCard
          title={
            query.keyword || query.genre ? '没有匹配的作品' : '书架还是空的'
          }
          hint={
            query.keyword || query.genre
              ? '换个关键词或体裁试试。'
              : '创作端上线后，作品会出现在这里。'
          }
        />
      ) : loading && books.length === 0 ? (
        <div className="shelf-grid" aria-hidden="true">
          {SHELF_SKELETON.map((slot) => (
            <div className="book-card" key={slot}>
              <div className="sk sk-cover" />
              <div className="book-card-body">
                <div className="sk sk-line" />
                <div className="sk sk-line sk-line-sm" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="shelf-grid">
          {books.map((book) => {
            const saved = progress[String(book.id)];
            return (
              <Link className="book-card" key={book.id} to={`/book/${book.id}`}>
                <div className="book-card-cover">
                  <BookCover
                    src={book.coverImage}
                    title={book.title}
                    author={book.author}
                    alt=""
                  />
                  <span
                    className={`book-card-badge${
                      book.status === 'completed' ? ' book-card-badge-done' : ''
                    }`}
                  >
                    {statusText[book.status] ?? book.status}
                  </span>
                </div>
                <div className="book-card-body">
                  <p className="book-card-title">{book.title}</p>
                  <p className="book-card-meta">
                    {book.author || '佚名'}
                    {book.genre ? ` · ${book.genre}` : ''}
                  </p>
                  {saved ? (
                    <>
                      <p className="book-card-meta">
                        读到第 {saved.chapterIndex} 章
                        {typeof saved.percent === 'number'
                          ? ` · ${saved.percent}%`
                          : ''}
                      </p>
                      {typeof saved.percent === 'number' ? (
                        <div className="progress-thin">
                          <span
                            className="progress-thin-fill"
                            style={{ width: `${saved.percent}%` }}
                          />
                        </div>
                      ) : null}
                    </>
                  ) : null}
                </div>
              </Link>
            );
          })}
        </div>
      )}

      {page + 1 < totalPages ? (
        <div className="shelf-more">
          <button
            type="button"
            className="btn-ghost"
            disabled={loading}
            onClick={() => load(page + 1, false)}
          >
            {loading ? '加载中…' : '加载更多'}
          </button>
        </div>
      ) : null}
    </>
  );
}
