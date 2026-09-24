import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

const SESSION_STORAGE_KEY = 'cooking-session-v1';

export type CookingSession = {
  recipeId: number;
  title: string;
  stepCount: number;
  stepIndex: number;
  startedAt: number;
};

/** 一次做完的菜，等聊天页取走并变成一条消息 */
export type CookingNote = {
  key: number;
  recipeId: number;
  title: string;
  stepCount: number;
  startedAt: number;
};

type BeginOptions = {
  /** 从头开始做，忽略已有进度 */
  restart?: boolean;
};

type CookingContextValue = {
  session: CookingSession | null;
  note: CookingNote | null;
  beginCooking: (
    recipe: { id: number; title: string },
    stepCount: number,
    options?: BeginOptions,
  ) => void;
  goToStep: (index: number) => void;
  finishCooking: () => void;
  cancelCooking: () => void;
  clearNote: () => void;
};

const CookingContext = createContext<CookingContextValue | null>(null);

let noteSeq = 0;

export function CookingProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<CookingSession | null>(null);
  const [note, setNote] = useState<CookingNote | null>(null);
  const [hydrated, setHydrated] = useState(false);

  // 启动时恢复上次未做完的菜；读到损坏数据就丢弃，不影响正常使用
  useEffect(() => {
    AsyncStorage.getItem(SESSION_STORAGE_KEY)
      .then((raw) => {
        if (!raw) {
          return;
        }

        const parsed = JSON.parse(raw) as Partial<CookingSession>;
        if (
          typeof parsed.recipeId === 'number' &&
          typeof parsed.stepCount === 'number' &&
          typeof parsed.stepIndex === 'number' &&
          typeof parsed.title === 'string'
        ) {
          setSession({
            recipeId: parsed.recipeId,
            startedAt:
              typeof parsed.startedAt === 'number'
                ? parsed.startedAt
                : Date.now(),
            stepCount: parsed.stepCount,
            stepIndex: parsed.stepIndex,
            title: parsed.title,
          });
        }
      })
      .catch(() => {})
      .finally(() => setHydrated(true));
  }, []);

  // 进度变化即落盘；完成/取消后清掉，避免下次打开又弹回旧进度
  useEffect(() => {
    if (!hydrated) {
      return;
    }

    if (session) {
      AsyncStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(session)).catch(
        () => {},
      );
    } else {
      AsyncStorage.removeItem(SESSION_STORAGE_KEY).catch(() => {});
    }
  }, [hydrated, session]);

  const beginCooking = useCallback<CookingContextValue['beginCooking']>(
    (recipe, stepCount, options) => {
      setSession((prev) => {
        const resumable =
          !options?.restart &&
          prev?.recipeId === recipe.id &&
          prev.stepCount === stepCount &&
          prev.stepIndex < stepCount;

        if (resumable) {
          return prev;
        }

        return {
          recipeId: recipe.id,
          startedAt: Date.now(),
          stepCount,
          stepIndex: 0,
          title: recipe.title,
        };
      });
    },
    [],
  );

  const goToStep = useCallback((index: number) => {
    setSession((prev) => {
      if (!prev) {
        return prev;
      }

      const stepIndex = Math.min(
        Math.max(index, 0),
        Math.max(prev.stepCount - 1, 0),
      );

      return stepIndex === prev.stepIndex ? prev : { ...prev, stepIndex };
    });
  }, []);

  const finishCooking = useCallback(() => {
    if (!session) {
      return;
    }

    noteSeq += 1;
    setNote({
      key: noteSeq,
      recipeId: session.recipeId,
      startedAt: session.startedAt,
      stepCount: session.stepCount,
      title: session.title,
    });
    setSession(null);
  }, [session]);

  const cancelCooking = useCallback(() => {
    setSession(null);
  }, []);

  const clearNote = useCallback(() => {
    setNote(null);
  }, []);

  const value = useMemo<CookingContextValue>(
    () => ({
      beginCooking,
      cancelCooking,
      clearNote,
      finishCooking,
      goToStep,
      note,
      session,
    }),
    [
      beginCooking,
      cancelCooking,
      clearNote,
      finishCooking,
      goToStep,
      note,
      session,
    ],
  );

  return (
    <CookingContext.Provider value={value}>{children}</CookingContext.Provider>
  );
}

export function useCooking(): CookingContextValue {
  const value = useContext(CookingContext);

  if (!value) {
    throw new Error('useCooking 必须在 CookingProvider 内使用');
  }

  return value;
}
