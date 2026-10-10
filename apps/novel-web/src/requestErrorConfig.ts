import type { RequestConfig } from '@umijs/max';
import { message } from 'antd';

import { LOGIN_PATH, TOKEN_STORAGE_KEY } from '@/services/auth';

// 与后端 Result<T> 信封对应（packages/types/src/api.ts）
interface ResponseStructure {
  success: boolean;
  data?: unknown;
  code?: number;
  message?: string;
  showType?: 0 | 1 | 2 | 3 | 9;
}

/** 只有这些前缀下的请求失败才把用户赶去登录页；游客可读页面永不触发 */
const PROTECTED_PREFIXES = ['/studio'];

function isProtectedArea(): boolean {
  if (typeof window === 'undefined') {
    return false;
  }
  const { pathname } = window.location;
  return PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

/** 会话失效：清令牌；仅受保护区回跳登录，阅读区就地保留 */
function handleExpiredSession(serverMessage?: string) {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  message.error(serverMessage || '登录状态已失效，请重新登录');
  if (!isProtectedArea()) {
    return;
  }
  const { pathname, search, hash } = window.location;
  const redirect = encodeURIComponent(pathname + search + hash);
  window.location.href = `${LOGIN_PATH}?redirect=${redirect}`;
}

/**
 * 错误处理沿用管理端方案（apps/admin-web/src/requestErrorConfig.ts），
 * 差异只有 401 的落点：本站默认游客可读，不能一律跳登录。
 */
export const errorConfig: RequestConfig = {
  errorConfig: {
    errorThrower: (res) => {
      const {
        success,
        data,
        code,
        message: msg,
        showType,
      } = res as unknown as ResponseStructure;
      if (!success) {
        const error: any = new Error(msg);
        error.name = 'BizError';
        error.info = { code, message: msg, showType, data };
        throw error;
      }
    },
    errorHandler: (error: any, opts: any) => {
      if (opts?.skipErrorHandler) {
        throw error;
      }
      if (error.name === 'BizError') {
        const info: ResponseStructure | undefined = error.info;
        if (info?.code === 401) {
          handleExpiredSession(info.message);
          return;
        }
        if (info?.code === 403) {
          message.error(info.message || '没有访问权限');
          return;
        }
        message.error(info?.message || '请求失败，请稍后重试');
        return;
      }
      if (error.response) {
        const { status, data } = error.response;
        const serverMessage = (data as ResponseStructure | undefined)?.message;
        if (status === 401) {
          handleExpiredSession(serverMessage);
        } else if (status === 403) {
          message.error(serverMessage || '没有访问权限');
        } else if (status >= 500) {
          message.error(serverMessage || '服务暂时不可用，请稍后重试');
        } else {
          message.error(serverMessage || `Response status:${status}`);
        }
        return;
      }
      if (typeof navigator !== 'undefined' && !navigator.onLine) {
        message.error('当前网络不可用，请检查网络后重试');
        return;
      }
      message.error('请求发送失败，请稍后重试');
    },
  },

  requestInterceptors: [
    (config: any) => {
      const token = localStorage.getItem(TOKEN_STORAGE_KEY);
      if (token) {
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        };
      }
      return config;
    },
  ],

  responseInterceptors: [],
};
