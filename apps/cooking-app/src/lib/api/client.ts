import type { Result } from '@po/types';
import axios, { type AxiosResponse } from 'axios';
import { Platform } from 'react-native';

import { getSessionToken } from '@/lib/auth/session';

const defaultApiUrl = 'http://localhost:8080/api';

// Web 版必须与后端同源：开发时由 Metro dev server 代理 /api，生产由网关转发；
// 原生端需要绝对地址，模拟器可用默认值，真机在 .env 里改成局域网地址。
const configuredApiUrl = process.env.EXPO_PUBLIC_API_URL ?? defaultApiUrl;
const isWeb = Platform.OS === 'web';
const apiBaseUrl = isWeb ? '/api' : configuredApiUrl;
const apiRoot = isWeb ? '' : configuredApiUrl.replace(/\/api\/?$/, '');

type UnauthorizedHandler = () => void;

let unauthorizedHandler: UnauthorizedHandler | undefined;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: number,
    public readonly status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  headers: {
    Accept: 'application/json',
  },
  timeout: 15_000,
});

apiClient.interceptors.request.use((config) => {
  const token = getSessionToken();
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`);
  }
  return config;
});

/** 后端统一用 Result.code 表达未登录（HTTP 状态仍为 200） */
export function isUnauthorizedResult(payload: unknown): boolean {
  if (typeof payload !== 'object' || payload === null) {
    return false;
  }
  const result = payload as Partial<Result<unknown>>;
  return result.success === false && result.code === 401;
}

function handleUnauthorized() {
  // 登录接口凭据错误同样返回 401，只有携带本地会话的请求才代表会话失效
  if (getSessionToken()) {
    unauthorizedHandler?.();
  }
}

apiClient.interceptors.response.use(
  (response) => {
    if (isUnauthorizedResult(response.data)) {
      handleUnauthorized();
    }

    return response;
  },
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      handleUnauthorized();
    }

    return Promise.reject(error);
  },
);

export function setUnauthorizedHandler(handler?: UnauthorizedHandler) {
  unauthorizedHandler = handler;
}

/** 把后端返回的相对资源路径（如 /api/avatars/x.jpg）解析为可访问地址，Web 上保持同源相对路径 */
export function resolveAssetUrl(path?: string | null): string | undefined {
  if (!path) {
    return undefined;
  }
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  return `${apiRoot}${path.startsWith('/') ? path : `/${path}`}`;
}

export function unwrap<T>(response: AxiosResponse<Result<T>>): T {
  const result = response.data;

  if (!result.success) {
    throw new ApiError(
      result.message || '请求失败',
      result.code,
      response.status,
    );
  }

  return result.data;
}
