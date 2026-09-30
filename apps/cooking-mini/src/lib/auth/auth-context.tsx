import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  fetchCurrentUser,
  openIdLoginRequest,
  passwordLoginRequest,
  appRegisterRequest,
  type LoginResult,
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

type AuthContextValue = {
  status: AuthStatus;
  user: AuthUser | null;
  signInWithOpenId: (loginCode: string) => Promise<LoginResult>;
  signInWithPassword: (username: string, password: string) => Promise<LoginResult>;
  register: (username: string, password: string, nickname?: string) => Promise<LoginResult>;
  signOut: () => void;
  refreshUser: () => Promise<void>;
};

const APP_ROLE = 'user';
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [status, setStatus] = useState<AuthStatus>('loading');

  const signOut = useCallback(() => {
    clearPersistedSession();
    setSession(null);
    setStatus('unauthenticated');
  }, []);

  const applyLoginResult = useCallback((result: LoginResult) => {
    if (result.approved && result.session) {
      persistSession(result.session);
      setSession(result.session);
      setStatus('authenticated');
    }
    return result;
  }, []);

  const signInWithOpenId = useCallback(async (loginCode: string) => {
    const result = await openIdLoginRequest(loginCode);
    return applyLoginResult(result);
  }, [applyLoginResult]);

  const signInWithPassword = useCallback(async (username: string, password: string) => {
    const result = await passwordLoginRequest(username, password);
    return applyLoginResult(result);
  }, [applyLoginResult]);

  const register = useCallback(async (username: string, password: string, nickname?: string) => {
    const result = await appRegisterRequest(username, password, nickname);
    return applyLoginResult(result);
  }, [applyLoginResult]);

  const refreshUser = useCallback(async () => {
    const user = await fetchCurrentUser();
    setSession((prev) => {
      if (!prev) return prev;
      const next = { token: prev.token, user };
      persistSession(next);
      return next;
    });
  }, []);

  useEffect(() => {
    const restored = restorePersistedSession();
    if (!restored || restored.user.role !== APP_ROLE) {
      clearPersistedSession();
      setStatus('unauthenticated');
      return;
    }
    setSession(restored);
    setStatus('authenticated');

    fetchCurrentUser()
      .then((user) => {
        if (user.role !== APP_ROLE) {
          signOut();
          return;
        }
        const next = { token: restored.token, user };
        persistSession(next);
        setSession(next);
      })
      .catch(() => {
        // 网络异常时保留本地会话
      });
  }, [signOut]);

  useEffect(() => {
    setUnauthorizedHandler(() => signOut());
    return () => setUnauthorizedHandler(undefined);
  }, [signOut]);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user: session?.user ?? null,
      signInWithOpenId,
      signInWithPassword,
      register,
      signOut,
      refreshUser,
    }),
    [status, session, signInWithOpenId, signInWithPassword, register, signOut, refreshUser],
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
