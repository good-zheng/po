import Taro from '@tarojs/taro';

export type AuthUser = {
  id: number;
  username: string;
  nickname?: string | null;
  role: string;
  avatar?: string | null;
  email?: string | null;
  phoneNumber?: string | null;
};

export type AuthSession = {
  token: string;
  user: AuthUser;
};

const SESSION_KEY = 'po.session';
let currentToken: string | null = null;

function parseSession(raw: string | null): AuthSession | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<AuthSession>;
    if (typeof parsed.token !== 'string' || !parsed.token) return null;
    const user = parsed.user as Partial<AuthUser> | undefined;
    if (!user || typeof user.id !== 'number' || typeof user.username !== 'string' || typeof user.role !== 'string') {
      return null;
    }
    return { token: parsed.token, user: user as AuthUser };
  } catch {
    return null;
  }
}

export function restorePersistedSession(): AuthSession | null {
  const raw = Taro.getStorageSync(SESSION_KEY);
  const session = parseSession(raw || null);
  currentToken = session?.token ?? null;
  return session;
}

export function persistSession(session: AuthSession): void {
  currentToken = session.token;
  Taro.setStorageSync(SESSION_KEY, JSON.stringify(session));
}

export function clearPersistedSession(): void {
  currentToken = null;
  Taro.removeStorageSync(SESSION_KEY);
}

export function getSessionToken(): string | null {
  return currentToken;
}
