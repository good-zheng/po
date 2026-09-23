import * as SecureStore from 'expo-secure-store';

import {
  type AuthSession,
  clearPersistedSession,
  getSessionToken,
  persistSession,
  restorePersistedSession,
} from '@/lib/auth/session';

const session: AuthSession = {
  token: 'token-1',
  user: { id: 7, role: 'user', username: 'chef' },
};

describe('auth session storage', () => {
  it('returns null when nothing is persisted', async () => {
    expect(await restorePersistedSession()).toBeNull();
    expect(getSessionToken()).toBeNull();
  });

  it('persists a session and exposes the token for the api client', async () => {
    await persistSession(session);

    expect(getSessionToken()).toBe('token-1');
    expect(await restorePersistedSession()).toEqual(session);
    expect(getSessionToken()).toBe('token-1');
  });

  it('clears the session from storage and memory', async () => {
    await persistSession(session);
    await clearPersistedSession();

    expect(getSessionToken()).toBeNull();
    expect(await restorePersistedSession()).toBeNull();
  });

  it('ignores corrupted payloads', async () => {
    await SecureStore.setItemAsync('po.session', '{not-json');
    expect(await restorePersistedSession()).toBeNull();

    await SecureStore.setItemAsync('po.session', '{"token":""}');
    expect(await restorePersistedSession()).toBeNull();

    await SecureStore.setItemAsync(
      'po.session',
      JSON.stringify({ token: 'token-1', user: { id: '7' } }),
    );
    expect(await restorePersistedSession()).toBeNull();
    expect(getSessionToken()).toBeNull();
  });
});
