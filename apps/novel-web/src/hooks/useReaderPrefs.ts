import { useCallback, useEffect, useMemo, useState } from 'react';

export const FONT_SIZES = [15, 17, 19, 21, 23] as const;
export const LINE_HEIGHTS = { snug: 1.6, loose: 1.95 } as const;
export const THEMES = ['light', 'sepia', 'dark'] as const;

export type ReaderTheme = (typeof THEMES)[number];

export type ReaderPrefs = {
  fontIndex: number;
  lineHeight: keyof typeof LINE_HEIGHTS;
  theme: ReaderTheme;
};

const STORAGE_KEY = 'novel.reader.prefs';

const DEFAULTS: ReaderPrefs = {
  fontIndex: 1,
  lineHeight: 'snug',
  theme: 'light',
};

const clampIndex = (value: unknown) => {
  const n = Number(value);
  if (!Number.isFinite(n)) return DEFAULTS.fontIndex;
  return Math.min(FONT_SIZES.length - 1, Math.max(0, Math.round(n)));
};

const read = (): ReaderPrefs => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULTS;
    const parsed = JSON.parse(raw) as Partial<ReaderPrefs>;
    return {
      fontIndex: clampIndex(parsed.fontIndex),
      lineHeight: parsed.lineHeight === 'loose' ? 'loose' : 'snug',
      theme: THEMES.includes(parsed.theme as ReaderTheme)
        ? (parsed.theme as ReaderTheme)
        : 'light',
    };
  } catch (_error) {
    return DEFAULTS;
  }
};

/**
 * 阅读偏好。写入 localStorage，跨书复用；初值跟随系统的深色偏好。
 * 主题类名挂在正文容器上，由 global.less 里的 [data-reader-theme] 消费。
 */
export function useReaderPrefs() {
  const [prefs, setPrefs] = useState<ReaderPrefs>(() => {
    const stored = read();
    if (
      !localStorage.getItem(STORAGE_KEY) &&
      window.matchMedia?.('(prefers-color-scheme: dark)').matches
    ) {
      return { ...stored, theme: 'dark' };
    }
    return stored;
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }, [prefs]);

  const fontSize = FONT_SIZES[prefs.fontIndex];
  const lineHeight = LINE_HEIGHTS[prefs.lineHeight];

  const stepFont = useCallback((delta: number) => {
    setPrefs((prev) => ({
      ...prev,
      fontIndex: clampIndex(prev.fontIndex + delta),
    }));
  }, []);

  const toggleLineHeight = useCallback(() => {
    setPrefs((prev) => ({
      ...prev,
      lineHeight: prev.lineHeight === 'snug' ? 'loose' : 'snug',
    }));
  }, []);

  const cycleTheme = useCallback(() => {
    setPrefs((prev) => ({
      ...prev,
      theme: THEMES[(THEMES.indexOf(prev.theme) + 1) % THEMES.length],
    }));
  }, []);

  const style = useMemo(
    () => ({ fontSize: `${fontSize}px`, lineHeight }) as React.CSSProperties,
    [fontSize, lineHeight],
  );

  return {
    prefs,
    fontSize,
    lineHeight,
    style,
    stepFont,
    toggleLineHeight,
    cycleTheme,
  };
}
