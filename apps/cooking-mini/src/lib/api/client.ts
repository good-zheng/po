import Taro from '@tarojs/taro';
import type { Result } from '@po/types';
import { getSessionToken } from '@/lib/auth/session';
import { API_BASE_URL } from '@/config/env';

export class ApiError extends Error {
  code: number;
  status?: number;

  constructor(message: string, code: number, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
  }
}

type UnauthorizedHandler = () => void;
let unauthorizedHandler: UnauthorizedHandler | undefined;

export function setUnauthorizedHandler(handler?: UnauthorizedHandler) {
  unauthorizedHandler = handler;
}

function handleUnauthorized() {
  if (getSessionToken()) {
    unauthorizedHandler?.();
  }
}

function unwrap<T>(result: Result<T>): T {
  if (!result.success) {
    if (result.code === 401) {
      handleUnauthorized();
    }
    throw new ApiError(result.message || '请求失败', result.code);
  }
  return result.data;
}

type RequestOptions = {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  data?: Record<string, unknown> | unknown[];
  params?: Record<string, string | number | boolean | undefined>;
};

async function request<T>(options: RequestOptions): Promise<T> {
  const { url, method = 'GET', data, params } = options;
  const token = getSessionToken();

  let fullUrl = `${API_BASE_URL}${url}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.append(key, String(value));
      }
    });
    const qs = searchParams.toString();
    if (qs) {
      fullUrl += `?${qs}`;
    }
  }

  const response = await Taro.request({
    url: fullUrl,
    method,
    data,
    header: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    timeout: 15000,
  });

  if (response.statusCode === 401) {
    handleUnauthorized();
    throw new ApiError('未登录或登录已过期', 401, 401);
  }

  const result = response.data as Result<T>;
  return unwrap(result);
}

export const apiClient = {
  get<T>(url: string, params?: Record<string, string | number | boolean | undefined>) {
    return request<T>({ url, method: 'GET', params });
  },
  post<T>(url: string, data?: Record<string, unknown> | unknown[]) {
    return request<T>({ url, method: 'POST', data });
  },
  put<T>(url: string, data?: Record<string, unknown> | unknown[]) {
    return request<T>({ url, method: 'PUT', data });
  },
  delete<T>(url: string) {
    return request<T>({ url, method: 'DELETE' });
  },
};

export function resolveAssetUrl(path?: string | null): string | undefined {
  if (!path) return undefined;
  if (/^https?:\/\//i.test(path)) return path;
  const root = API_BASE_URL.replace(/\/api\/?$/, '');
  return `${root}${path.startsWith('/') ? path : `/${path}`}`;
}

/** 上传本地文件（multipart，字段名 file），返回 Result.data；formData 传额外字段（如 dir） */
export function uploadFile<T>(
  url: string,
  filePath: string,
  formData?: Record<string, string>,
): Promise<T> {
  const token = getSessionToken();
  return Taro.uploadFile({
    url: `${API_BASE_URL}${url}`,
    filePath,
    name: 'file',
    formData,
    header: token ? { Authorization: `Bearer ${token}` } : {},
  }).then((response) => {
    if (response.statusCode === 401) {
      handleUnauthorized();
      throw new ApiError('未登录或登录已过期', 401, 401);
    }
    const result = JSON.parse(response.data) as Result<T>;
    return unwrap(result);
  });
}
