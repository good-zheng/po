import type { RequestOptions } from '@@/plugin-request/request';
import type { RequestConfig } from '@umijs/max';
import { getIntl } from '@umijs/max';
import { message as messageAntd, notification } from 'antd';

import { TOKEN_STORAGE_KEY } from '@/utils/session';

// 错误处理方案： 错误类型
enum ErrorShowType {
  SILENT = 0,
  WARN_MESSAGE = 1,
  ERROR_MESSAGE = 2,
  NOTIFICATION = 3,
  REDIRECT = 9,
}
// 与后端约定的响应数据格式
interface ResponseStructure {
  success: boolean;
  data: unknown;
  code?: number;
  message?: string;
  showType?: ErrorShowType;
}

const LOGIN_PATH = '/user/login';

/** 会话失效：清除本地令牌并回到登录页（带着回跳地址） */
function redirectToLogin() {
  if (typeof window === 'undefined') {
    return;
  }
  localStorage.removeItem(TOKEN_STORAGE_KEY);
  if (window.location.pathname === LOGIN_PATH) {
    return;
  }
  const { pathname, search, hash } = window.location;
  const redirect = encodeURIComponent(pathname + search + hash);
  window.location.href = `${LOGIN_PATH}?redirect=${redirect}`;
}

/**
 * @name 错误处理
 * pro 自带的错误处理， 可以在这里做自己的改动
 * @doc https://umijs.org/docs/max/request#配置
 */
export const errorConfig: RequestConfig = {
  // 错误处理： umi@3 的错误处理方案。
  errorConfig: {
    // 错误抛出
    errorThrower: (res) => {
      const { success, data, code, message, showType } =
        res as unknown as ResponseStructure;
      if (!success) {
        const error: any = new Error(message);
        error.name = 'BizError';
        error.info = { code, message, showType, data };
        throw error; // 抛出自制的错误
      }
    },
    // 错误接收及处理
    errorHandler: (error: any, opts: any) => {
      if (opts?.skipErrorHandler) throw error;
      // 我们的 errorThrower 抛出的错误。
      if (error.name === 'BizError') {
        const errorInfo: ResponseStructure | undefined = error.info;
        if (errorInfo) {
          const { message, code } = errorInfo;
          switch (errorInfo.showType) {
            case ErrorShowType.SILENT:
              // do nothing
              break;
            case ErrorShowType.WARN_MESSAGE:
              messageAntd.warning(message);
              break;
            case ErrorShowType.ERROR_MESSAGE:
              messageAntd.error(message);
              break;
            case ErrorShowType.NOTIFICATION:
              notification.open({
                title: code,
                description: message,
              });
              break;
            case ErrorShowType.REDIRECT:
              window.location.href = '/user/login';
              break;
            default:
              messageAntd.error(message);
          }
        }
      } else if (error.response) {
        // Axios 的错误
        // 请求成功发出且服务器也响应了状态码，但状态代码超出了 2xx 的范围
        const { status, data } = error.response;
        const serverMessage = (data as ResponseStructure | undefined)?.message;
        if (status === 401) {
          messageAntd.error(serverMessage || '登录状态已失效，请重新登录');
          redirectToLogin();
        } else if (status === 403) {
          messageAntd.error(serverMessage || '没有访问权限');
        } else {
          messageAntd.error(serverMessage || `Response status:${status}`);
        }
      } else if (typeof navigator !== 'undefined' && !navigator.onLine) {
        messageAntd.error(
          getIntl().formatMessage({
            id: 'app.request.offline',
            defaultMessage:
              'Network unavailable. Please check your connection and try again.',
          }),
        );
      } else if (error.request) {
        messageAntd.error('None response! Please retry.');
      } else {
        messageAntd.error('Request error, please retry.');
      }
    },
  },

  // 请求拦截器
  requestInterceptors: [
    (config: RequestOptions) => {
      // 拦截请求配置，进行个性化处理。
      // 示例：为请求附加 token（按需启用）
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

  // 响应拦截器
  responseInterceptors: [],
};
