import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

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

const sessionKey = 'po.session';

// axios 拦截器需要同步读取 token，这里与持久化存储保持同步
let currentToken: string | null = null;

function isAuthUser(value: unknown): value is AuthUser {
  if (typeof value !== 'object' || value === null) {
    return false;
  }
  const user = value as Partial<AuthUser>;
  return (
    typeof user.id === 'number' &&
    typeof user.username === 'string' &&
    typeof user.role === 'string'
  );
}

function parseSession(raw: string | null): AuthSession | null {
  if (!raw) {
    return null;
  }
  try {
    const parsed = JSON.parse(raw) as Partial<AuthSession>;
    if (typeof parsed.token !== 'string' || !parsed.token) {
      return null;
    }
    if (!isAuthUser(parsed.user)) {
      return null;
    }
    return { token: parsed.token, user: parsed.user };
  } catch {
    return null;
  }
}

async function readRaw(): Promise<string | null> {
  if (Platform.OS === 'web') {
    return typeof localStorage === 'undefined'
      ? null
      : localStorage.getItem(sessionKey);
  }
  return SecureStore.getItemAsync(sessionKey);
}

async function writeRaw(value: string | null): Promise<void> {
  if (Platform.OS === 'web') {
    if (typeof localStorage !== 'undefined') {
      if (value === null) {
        localStorage.removeItem(sessionKey);
      } else {
        localStorage.setItem(sessionKey, value);
      }
    }
    return;
  }
  if (value === null) {
    await SecureStore.deleteItemAsync(sessionKey);
  } else {
    await SecureStore.setItemAsync(sessionKey, value);
  }
}

export async function restorePersistedSession(): Promise<AuthSession | null> {
  const session = parseSession(await readRaw());
  currentToken = session?.token ?? null;
  return session;
}

export async function persistSession(session: AuthSession): Promise<void> {
  currentToken = session.token;
  await writeRaw(JSON.stringify(session));
}

export async function clearPersistedSession(): Promise<void> {
  currentToken = null;
  await writeRaw(null);
}

export function getSessionToken(): string | null {
  return currentToken;
}
