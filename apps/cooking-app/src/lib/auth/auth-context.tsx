import { useQueryClient } from '@tanstack/react-query';
import {
  createContext,
  type ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';

import {
  fetchCurrentUser,
  loginRequest,
  registerRequest,
} from '@/lib/api/auth';
import { setUnauthorizedHandler } from '@/lib/api/client';
import {
  type AuthSession,
  type AuthUser,
  clearPersistedSession,
  persistSession,
  restorePersistedSession,
} from '@/lib/auth/session';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

export type RegisterInput = {
  username: string;
  password: string;
  email?: string;
};

type AuthContextValue = {
  status: AuthStatus;
  user: AuthUser | null;
  signIn: (username: string, password: string) => Promise<void>;
  signUp: (input: RegisterInput) => Promise<void>;
  signOut: () => Promise<void>;
  /** 资料变更后重新拉取当前用户并同步会话（保留原 token） */
  refreshUser: () => Promise<void>;
};

/** 与后端 ClientConstants 对应：app 来源只允许普通用户登录 */
const APP_ROLE = 'user';

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [session, setSession] = useState<AuthSession | null>(null);
  const [status, setStatus] = useState<AuthStatus>('loading');

  const signOut = useCallback(async () => {
    await clearPersistedSession();
    queryClient.clear();
    setSession(null);
    setStatus('unauthenticated');
  }, [queryClient]);

  const signIn = useCallback(async (username: string, password: string) => {
    const next = await loginRequest(username, password);
    await persistSession(next);
    setSession(next);
    setStatus('authenticated');
  }, []);

  const signUp = useCallback(async (input: RegisterInput) => {
    await registerRequest(input);
    const next = await loginRequest(input.username, input.password);
    await persistSession(next);
    setSession(next);
    setStatus('authenticated');
  }, []);

  const refreshUser = useCallback(async () => {
    const user = await fetchCurrentUser();
    setSession((prev) => {
      if (!prev) {
        return prev;
      }
      const next = { token: prev.token, user };
      void persistSession(next);
      return next;
    });
  }, []);

  // 启动时恢复会话：本地有 token 先放行，再后台校验并刷新资料
  useEffect(() => {
    let cancelled = false;

    void (async () => {
      const restored = await restorePersistedSession();
      if (cancelled) {
        return;
      }
      // 双向隔离：App 仅允许普通用户，管理员账号不能停留在移动端
      if (!restored || restored.user.role !== APP_ROLE) {
        await clearPersistedSession();
        if (!cancelled) {
          setStatus('unauthenticated');
        }
        return;
      }
      setSession(restored);
      setStatus('authenticated');

      try {
        const user = await fetchCurrentUser();
        if (cancelled) {
          return;
        }
        if (user.role !== APP_ROLE) {
          await signOut();
          return;
        }
        const next = { token: restored.token, user };
        await persistSession(next);
        if (!cancelled) {
          setSession(next);
        }
      } catch {
        // 网络异常时保留本地会话（离线可用）；token 失效由 401 统一处理登出
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [signOut]);

  // 任意请求返回未登录时，清空会话回到登录页
  useEffect(() => {
    setUnauthorizedHandler(() => {
      void signOut();
    });
    return () => setUnauthorizedHandler(undefined);
  }, [signOut]);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user: session?.user ?? null,
      signIn,
      signUp,
      signOut,
      refreshUser,
    }),
    [status, session, signIn, signUp, signOut, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth 必须在 AuthProvider 内使用');
  }
  return context;
}
