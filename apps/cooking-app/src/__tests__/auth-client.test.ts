import type { Result } from '@po/types';
import {
  AxiosError,
  AxiosHeaders,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios';

import { apiClient, setUnauthorizedHandler } from '@/lib/api/client';
import {
  type AuthSession,
  clearPersistedSession,
  persistSession,
} from '@/lib/auth/session';

const session: AuthSession = {
  token: 'token-1',
  user: { id: 7, role: 'user', username: 'chef' },
};

type Adapter = (
  config: InternalAxiosRequestConfig,
) => Promise<AxiosResponse<Result<unknown>>>;

const originalAdapter = apiClient.defaults.adapter;

function respondWith(body: Result<unknown>): Adapter {
  return async (config) => ({
    config,
    data: body,
    headers: {},
    status: 200,
    statusText: 'OK',
  });
}

function captureRequest(): {
  adapter: Adapter;
  requests: InternalAxiosRequestConfig[];
} {
  const requests: InternalAxiosRequestConfig[] = [];

  return {
    adapter: async (config) => {
      requests.push(config);
      return {
        config,
        data: { code: 1, data: null, message: '成功', success: true },
        headers: {},
        status: 200,
        statusText: 'OK',
      };
    },
    requests,
  };
}

afterEach(async () => {
  apiClient.defaults.adapter = originalAdapter;
  setUnauthorizedHandler(undefined);
  await clearPersistedSession();
});

describe('api client authentication', () => {
  it('attaches the bearer token when a session exists', async () => {
    const { adapter, requests } = captureRequest();
    apiClient.defaults.adapter = adapter;
    await persistSession(session);

    await apiClient.get('/recipes');

    const headers = AxiosHeaders.from(requests[0]?.headers);
    expect(headers.get('Authorization')).toBe('Bearer token-1');
  });

  it('sends no authorization header without a session', async () => {
    const { adapter, requests } = captureRequest();
    apiClient.defaults.adapter = adapter;

    await apiClient.get('/recipes');

    const headers = AxiosHeaders.from(requests[0]?.headers);
    expect(headers.has('Authorization')).toBe(false);
  });

  it('handles an expired session reported through the result envelope', async () => {
    const handler = jest.fn();
    setUnauthorizedHandler(handler);
    await persistSession(session);
    apiClient.defaults.adapter = respondWith({
      code: 401,
      data: null,
      message: '未登录',
      success: false,
    });

    await apiClient.get('/users/me');

    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('handles an expired session reported through the http status', async () => {
    const handler = jest.fn();
    setUnauthorizedHandler(handler);
    await persistSession(session);
    apiClient.defaults.adapter = async (config) => {
      throw new AxiosError('Unauthorized', 'ERR_BAD_REQUEST', config, null, {
        config,
        data: null,
        headers: {},
        status: 401,
        statusText: 'Unauthorized',
      });
    };

    await expect(apiClient.get('/users/me')).rejects.toThrow(AxiosError);

    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('ignores credential errors from the login request', async () => {
    const handler = jest.fn();
    setUnauthorizedHandler(handler);
    apiClient.defaults.adapter = respondWith({
      code: 401,
      data: null,
      message: '用户名或密码错误',
      success: false,
    });

    await expect(
      apiClient.post('/auth/login', { password: 'bad', username: 'chef' }),
    ).resolves.toBeDefined();

    expect(handler).not.toHaveBeenCalled();
  });
});
