import AsyncStorage from '@react-native-async-storage/async-storage';
import { useCallback, useEffect, useState } from 'react';

const HISTORY_STORAGE_KEY = 'recipe-search-history-v1';
const MAX_ENTRIES = 10;

/** 首页搜索历史：本地持久化，最新在前，去重，最多保留 10 条 */
export function useSearchHistory() {
  const [history, setHistory] = useState<string[]>([]);

  useEffect(() => {
    AsyncStorage.getItem(HISTORY_STORAGE_KEY)
      .then((raw) => {
        if (raw) {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) {
            setHistory(parsed.filter((item) => typeof item === 'string'));
          }
        }
      })
      .catch(() => {});
  }, []);

  const persist = useCallback((next: string[]) => {
    setHistory(next);
    AsyncStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(next)).catch(
      () => {},
    );
  }, []);

  const add = useCallback(
    (term: string) => {
      const trimmed = term.trim();
      if (!trimmed) {
        return;
      }

      persist(
        [trimmed, ...history.filter((item) => item !== trimmed)].slice(
          0,
          MAX_ENTRIES,
        ),
      );
    },
    [history, persist],
  );

  const clear = useCallback(() => {
    persist([]);
  }, [persist]);

  return { add, clear, history };
}
