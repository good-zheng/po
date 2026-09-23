import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useMemo,
  useState,
} from 'react';

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
