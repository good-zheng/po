import { useCallback, useEffect, useRef } from 'react';

export type ReadingProgress = {
  chapterId: number;
  /** 冗余存章号：书架要显示「读到第 N 章」，不该为此再请求一次目录 */
  chapterIndex: number;
  scrollTop: number;
  /** 章内读位百分比（0-100），书架据此画进度条；改版前的旧数据没有这个字段 */
  percent?: number;
  savedAt: number;
};

const key = (bookId: number) => `novel.progress.${bookId}`;

export function readProgress(bookId: number): ReadingProgress | undefined {
  try {
    const raw = localStorage.getItem(key(bookId));
    if (!raw) return undefined;
    const parsed = JSON.parse(raw) as ReadingProgress;
    return Number.isFinite(parsed.chapterId) ? parsed : undefined;
  } catch (_error) {
    return undefined;
  }
}

/** 书架上显示「读到第 N 章」用；只认数字 chapterId，脏数据直接忽略 */
export function readAllProgress(): Record<string, ReadingProgress> {
  const out: Record<string, ReadingProgress> = {};
  for (let i = 0; i < localStorage.length; i += 1) {
    const storageKey = localStorage.key(i);
    if (!storageKey?.startsWith('novel.progress.')) continue;
    const bookId = Number(storageKey.replace('novel.progress.', ''));
    if (!Number.isFinite(bookId)) continue;
    const progress = readProgress(bookId);
    if (progress) out[String(bookId)] = progress;
  }
  return out;
}

/**
 * 阅读进度：本机记忆，一期不入库（跨设备同步是二期，见 PRD §6）。
 * 滚动只按 500ms 静默窗口落盘一次，并离开页面/卸载时补一次——
 * 不在每个 scroll 事件写 localStorage，也不做逐段状态更新。
 */
export function useReadingProgress(
  bookId: number,
  chapterId: number,
  chapterIndex: number,
) {
  const timer = useRef<number | undefined>(undefined);

  const save = useCallback(() => {
    const scrollable =
      document.documentElement.scrollHeight - window.innerHeight;
    const scrollTop = window.scrollY;
    localStorage.setItem(
      key(bookId),
      JSON.stringify({
        chapterId,
        chapterIndex,
        scrollTop,
        percent:
          scrollable > 0
            ? Math.round(
                Math.min(100, Math.max(0, (scrollTop / scrollable) * 100)),
              )
            : 100,
        savedAt: Date.now(),
      } satisfies ReadingProgress),
    );
  }, [bookId, chapterId, chapterIndex]);

  useEffect(() => {
    const onScroll = () => {
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(save, 500);
    };
    window.addEventListener('scroll', onScroll, { passive: true });

    window.addEventListener('pagehide', save);

    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('pagehide', save);
      window.clearTimeout(timer.current);
      save();
    };
  }, [save]);
}
