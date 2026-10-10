import type { BookChapter } from '@po/types';
import { Link, useParams, useSearchParams } from '@umijs/max';
import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import StateCard from '@/components/StateCard';
import { useReaderPrefs } from '@/hooks/useReaderPrefs';
import { readProgress, useReadingProgress } from '@/hooks/useReadingProgress';
import {
  type ChapterBrief,
  getChapter,
  getChapters,
  toChapterBriefs,
} from '@/services/book';

/**
 * 正文按行切段；只在数据到达时算一次，不随滚动重渲染。
 * key 取段落文本（重复段落加计数后缀），避免用数组下标——换章时整段列表是整体替换的。
 */
type Paragraph = { key: string; text: string };

const toParagraphs = (content: string | null | undefined): Paragraph[] => {
  const seen = new Map<string, number>();
  return (content ?? '')
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((text) => {
      const count = (seen.get(text) ?? 0) + 1;
      seen.set(text, count);
      return { key: count === 1 ? text : `${text}#${count}`, text };
    });
};

/** 骨架行的 key 与宽度都来自常量表，避免用下标做 key */
const READER_SKELETON = [
  { key: 'r1', width: '78%' },
  { key: 'r2', width: '96%' },
  { key: 'r3', width: '92%' },
  { key: 'r4', width: '99%' },
  { key: 'r5', width: '88%' },
  { key: 'r6', width: '46%' },
];

export default function ReadPage() {
  const params = useParams<{ bookId: string; chapterId: string }>();
  const [searchParams] = useSearchParams();
  const bookId = Number(params.bookId);
  const chapterId = Number(params.chapterId);
  const chapterIndex = Number(searchParams.get('index')) || 0;

  const [chapter, setChapter] = useState<BookChapter>();
  const [siblings, setSiblings] = useState<ChapterBrief[]>([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);
  const toplineRef = useRef<HTMLSpanElement>(null);
  const { prefs, style, stepFont, toggleLineHeight, cycleTheme } =
    useReaderPrefs();

  const valid = Number.isFinite(bookId) && Number.isFinite(chapterId);
  useReadingProgress(bookId, chapterId, chapterIndex);

  const load = useCallback(async () => {
    setLoading(true);
    setFailed(false);
    try {
      const [chapterRes, chaptersRes] = await Promise.all([
        getChapter(bookId, chapterId),
        getChapters(bookId),
      ]);
      setChapter(chapterRes.data);
      setSiblings(
        toChapterBriefs(chaptersRes.data).sort(
          (a, b) => a.chapterIndex - b.chapterIndex,
        ),
      );
    } catch (_error) {
      setFailed(true);
    } finally {
      setLoading(false);
    }
  }, [bookId, chapterId]);

  useEffect(() => {
    if (!valid) {
      setFailed(true);
      setLoading(false);
      return;
    }
    load();
  }, [valid, load]);

  // 同一章节回到上次的阅读位置；换章节则从头开始
  useEffect(() => {
    if (loading || failed) return;
    const saved = readProgress(bookId);
    const target = saved && saved.chapterId === chapterId ? saved.scrollTop : 0;
    window.scrollTo(0, target);
  }, [loading, failed, bookId, chapterId]);

  // 顶部读位线直接改 DOM 宽度：滚动不进取省状态，避免每帧重渲染整篇正文
  useEffect(() => {
    if (loading || failed) return;
    const paint = () => {
      const el = toplineRef.current;
      if (!el) return;
      const scrollable =
        document.documentElement.scrollHeight - window.innerHeight;
      const percent =
        scrollable > 0
          ? Math.min(100, Math.max(0, (window.scrollY / scrollable) * 100))
          : 0;
      el.style.width = `${percent}%`;
    };
    paint();
    window.addEventListener('scroll', paint, { passive: true });
    window.addEventListener('resize', paint);
    return () => {
      window.removeEventListener('scroll', paint);
      window.removeEventListener('resize', paint);
    };
  }, [loading, failed]);

  const paragraphs = useMemo(() => toParagraphs(chapter?.content), [chapter]);
  const position = siblings.findIndex((item) => item.id === chapterId);
  const prev = position > 0 ? siblings[position - 1] : undefined;
  const next = position >= 0 ? siblings[position + 1] : undefined;

  if (!valid || failed) {
    return (
      <div className="reader" data-reader-theme={prefs.theme}>
        <div className="reader-inner">
          <StateCard
            kind="error"
            title="这一章打不开"
            hint="章节可能已被删除，或后端服务还没就绪。"
            action={
              <Link
                to={Number.isFinite(bookId) ? `/book/${bookId}` : '/'}
                className="btn-ghost"
              >
                返回目录
              </Link>
            }
          />
        </div>
      </div>
    );
  }

  return (
    <div className="reader" data-reader-theme={prefs.theme}>
      <div className="reader-topline">
        <span className="reader-topline-fill" ref={toplineRef} />
      </div>

      <div className="reader-inner" style={style}>
        {loading ? (
          <>
            <div className="sk sk-line" style={{ width: '40%', height: 22 }} />
            {READER_SKELETON.map((line) => (
              <div
                className="sk sk-line"
                key={line.key}
                style={{ width: line.width, height: 15 }}
              />
            ))}
          </>
        ) : (
          <>
            {chapterIndex > 0 ? (
              <p className="reader-kicker">第 {chapterIndex} 章</p>
            ) : null}
            <h1 className="reader-title">{chapter?.title ?? '未命名章节'}</h1>
            <div className="reader-rule" aria-hidden="true" />

            {paragraphs.length === 0 ? (
              <StateCard title="本章还没有正文" hint="作者还在写。" />
            ) : (
              <div className="reader-body">
                {paragraphs.map((para) => (
                  <p key={para.key}>{para.text}</p>
                ))}
              </div>
            )}

            {paragraphs.length > 0 ? (
              <>
                <p className="reader-end">本章完</p>
                <div className="reader-next">
                  {prev ? (
                    <Link
                      className="btn-ghost"
                      to={`/read/${bookId}/${prev.id}?index=${prev.chapterIndex}`}
                    >
                      上一章
                    </Link>
                  ) : null}
                  {next ? (
                    <Link
                      className="btn-primary"
                      to={`/read/${bookId}/${next.id}?index=${next.chapterIndex}`}
                    >
                      下一章
                    </Link>
                  ) : (
                    <Link className="btn-ghost" to={`/book/${bookId}`}>
                      返回目录
                    </Link>
                  )}
                </div>
              </>
            ) : null}
          </>
        )}
      </div>

      <nav className="reader-bar" aria-label="阅读工具栏">
        <div className="reader-group">
          <Link className="reader-btn" to={`/book/${bookId}`}>
            目录
          </Link>
          {prev ? (
            <Link
              className="reader-btn"
              to={`/read/${bookId}/${prev.id}?index=${prev.chapterIndex}`}
            >
              上一章
            </Link>
          ) : (
            <button className="reader-btn" type="button" disabled>
              上一章
            </button>
          )}
          {next ? (
            <Link
              className="reader-btn"
              to={`/read/${bookId}/${next.id}?index=${next.chapterIndex}`}
            >
              下一章
            </Link>
          ) : (
            <button className="reader-btn" type="button" disabled>
              下一章
            </button>
          )}
        </div>
        <div className="reader-group">
          <button
            className="reader-btn"
            type="button"
            onClick={() => stepFont(-1)}
            aria-label="减小字号"
          >
            A−
          </button>
          <button
            className="reader-btn"
            type="button"
            onClick={() => stepFont(1)}
            aria-label="增大字号"
          >
            A+
          </button>
          <button
            className={`reader-btn${prefs.lineHeight === 'loose' ? ' reader-btn-on' : ''}`}
            type="button"
            onClick={toggleLineHeight}
            aria-label="切换行距"
          >
            行距
          </button>
          <button
            className={`reader-btn${prefs.theme !== 'light' ? ' reader-btn-on' : ''}`}
            type="button"
            onClick={cycleTheme}
            aria-label="切换主题"
          >
            {prefs.theme === 'light'
              ? '浅色'
              : prefs.theme === 'sepia'
                ? '护眼'
                : '夜间'}
          </button>
        </div>
      </nav>
    </div>
  );
}
