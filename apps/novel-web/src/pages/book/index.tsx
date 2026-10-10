import type { Book, BookCharacter } from '@po/types';
import { Link, useParams } from '@umijs/max';
import React, { useCallback, useEffect, useState } from 'react';
import BookCover from '@/components/BookCover';
import StateCard from '@/components/StateCard';
import { readProgress } from '@/hooks/useReadingProgress';
import {
  type ChapterBrief,
  getBook,
  getChapters,
  getCharacters,
  toChapterBriefs,
} from '@/services/book';

const statusText: Record<string, string> = {
  ongoing: '连载中',
  completed: '已完结',
  paused: '暂停更新',
};

const wordCountText = (value: number) =>
  value >= 10000 ? `${(value / 10000).toFixed(1)} 万字` : `${value} 字`;

export default function BookPage() {
  const params = useParams<{ id: string }>();
  const bookId = Number(params.id);
  const [book, setBook] = useState<Book>();
  const [chapters, setChapters] = useState<ChapterBrief[]>([]);
  const [characters, setCharacters] = useState<BookCharacter[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const [resume] = useState(() =>
    Number.isFinite(bookId) ? readProgress(bookId) : undefined,
  );

  const load = useCallback(async () => {
    setLoading(true);
    setFailed(false);
    try {
      const [bookRes, chapterRes] = await Promise.all([
        getBook(bookId),
        getChapters(bookId),
      ]);
      setBook(bookRes.data);
      // 目录只要标题与章号：正文由后端在列表接口里一并返回，这里前端裁掉（PRD §7-①）
      setChapters(
        toChapterBriefs(chapterRes.data).sort(
          (a, b) => a.chapterIndex - b.chapterIndex,
        ),
      );
      getCharacters(bookId)
        .then((res) => setCharacters(res.data ?? []))
        .catch(() => setCharacters([]));
    } catch (_error) {
      setFailed(true);
    } finally {
      setLoading(false);
    }
  }, [bookId]);

  useEffect(() => {
    if (!Number.isFinite(bookId)) {
      setFailed(true);
      setLoading(false);
      return;
    }
    load();
  }, [bookId, load]);

  if (failed) {
    return (
      <StateCard
        kind="error"
        title="这本书打不开"
        hint="可能已被删除，或后端服务还没就绪。"
        action={
          <Link to="/" className="btn-ghost">
            返回书架
          </Link>
        }
      />
    );
  }

  if (loading || !book) {
    return (
      <>
        <div className="book-hero" aria-hidden="true">
          <div className="sk sk-cover" />
          <div className="book-hero-info">
            <div className="sk sk-line" style={{ width: '60%', height: 20 }} />
            <div className="sk sk-line" style={{ width: '40%' }} />
            <div className="sk sk-line sk-line-sm" />
          </div>
        </div>
        <div className="sk sk-line" style={{ height: 140 }} />
      </>
    );
  }

  const firstChapter = chapters[0];
  const resumeChapter = resume
    ? (chapters.find((item) => item.id === resume.chapterId) ?? firstChapter)
    : firstChapter;
  const hasProgress = Boolean(resume && resumeChapter);

  return (
    <>
      <div className="book-hero">
        <div className="book-hero-cover">
          <BookCover
            src={book.coverImage}
            title={book.title}
            author={book.author}
            alt={book.title}
          />
        </div>
        <div className="book-hero-info">
          <h1 className="book-hero-title">{book.title}</h1>
          <div className="chip-row">
            <span className="chip">{book.author || '佚名'}</span>
            <span className="chip-sep" aria-hidden="true">
              /
            </span>
            <span
              className={`chip${book.status === 'completed' ? ' chip-accent' : ''}`}
            >
              {statusText[book.status] ?? book.status}
            </span>
            <span className="chip-sep" aria-hidden="true">
              /
            </span>
            <span className="chip">{wordCountText(book.wordCount)}</span>
            {book.genre ? (
              <>
                <span className="chip-sep" aria-hidden="true">
                  /
                </span>
                <span className="chip">{book.genre}</span>
              </>
            ) : null}
          </div>

          <div className="book-cta">
            {resumeChapter ? (
              <Link
                className="btn-primary"
                to={`/read/${book.id}/${resumeChapter.id}?index=${resumeChapter.chapterIndex}`}
              >
                {hasProgress ? '继续阅读' : '开始阅读'}
              </Link>
            ) : null}
            {hasProgress &&
            firstChapter &&
            firstChapter.id !== resumeChapter?.id ? (
              <Link
                className="btn-ghost"
                to={`/read/${book.id}/${firstChapter.id}?index=${firstChapter.chapterIndex}`}
              >
                从第一章开始
              </Link>
            ) : null}
            {!resumeChapter ? <span className="chip">还没有章节</span> : null}
          </div>

          {resume ? (
            <p className="book-resume-note">
              上次读到 第 {resume.chapterIndex} 章
              {typeof resume.percent === 'number'
                ? ` · ${resume.percent}%`
                : ''}
            </p>
          ) : null}
        </div>
      </div>

      {book.description ? (
        <>
          <h2 className="section-title">
            内容简介
            <span className="section-title-note">{chapters.length} 章</span>
          </h2>
          <p className="book-desc">{book.description}</p>
        </>
      ) : null}

      <h2 className="section-title">
        目录
        <span className="section-title-note">
          共 {chapters.length} 章 · {wordCountText(book.wordCount)}
        </span>
      </h2>
      {chapters.length === 0 ? (
        <StateCard title="还没有章节" hint="作者还没更新，过些日子再来。" />
      ) : (
        <div className="toc-card">
          <ul className="toc-list">
            {chapters.map((chapter) => (
              <li className="toc-item" key={chapter.id}>
                <Link
                  className={`toc-link${
                    resume?.chapterId === chapter.id ? ' toc-link-on' : ''
                  }`}
                  to={`/read/${book.id}/${chapter.id}?index=${chapter.chapterIndex}`}
                >
                  <span className="toc-index">{chapter.chapterIndex}</span>
                  <span className="toc-name">{chapter.title}</span>
                  <span className="toc-words">
                    {wordCountText(chapter.wordCount)}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}

      {characters.length > 0 ? (
        <>
          <h2 className="section-title">
            人物
            <span className="section-title-note">{characters.length} 位</span>
          </h2>
          <ul className="char-grid">
            {characters.map((character) => (
              <li className="char-card" key={character.id}>
                <span className="char-mono" aria-hidden="true">
                  {character.name.slice(0, 1)}
                </span>
                <div className="char-meta">
                  <span className="char-name">{character.name}</span>
                  {character.description ? (
                    <span className="char-desc">{character.description}</span>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </>
  );
}
