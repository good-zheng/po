import type { UserItem } from '@po/types';
import type { RequestConfig } from '@umijs/max';

import { clearToken, getBookMe, hasToken } from '@/services/auth';
import { errorConfig } from './requestErrorConfig';

export interface InitialState {
  currentUser?: UserItem;
  /** 游客态：没有本地令牌，或令牌换不到用户。阅读三页在此态下照常可用 */
  guest: boolean;
  loading?: boolean;
  refreshCurrentUser: () => Promise<UserItem | undefined>;
}

/**
 * 与管理端的关键差别：这里不做「拿不到用户就跳登录」。
 * 书架/详情/阅读是后端 permitAll 的公开内容，游客态是正常状态而非异常。
 * 创作端 /studio（M3）才要求登录，由路由 access 拦，不靠全局重定向。
 */
export async function getInitialState(): Promise<InitialState> {
  const refreshCurrentUser = async () => {
    if (!hasToken()) {
      return undefined;
    }
    try {
      const res = await getBookMe({ skipErrorHandler: true });
      return res?.data;
    } catch (_error) {
      // 令牌失效只降级为游客，不劫持路由
      clearToken();
      return undefined;
    }
  };

  const currentUser = await refreshCurrentUser();

  return {
    currentUser,
    guest: !currentUser,
    loading: false,
    refreshCurrentUser,
  };
}

/**
 * dev 刻意同源（baseURL 空串）：请求打到同域 /api，由 config/proxy.ts 接给本地 Spring，
 * mock 层也才拦得到——写死绝对地址会让本地看到的接口行为失真。
 * 生产烘进 .env.production 的线上 api 域名（与两个小程序同一个服务），此时容器里 nginx 的
 * /api 反代只是「没配变量时」的兜底通道，两条路都指向同一个后端。
 * 后端 CORS 已是 AllowedOriginPatterns("*") + AllowedHeaders("*")，跨域直连不需要改 api。
 */
export const request: RequestConfig = {
  baseURL:
    process.env.NODE_ENV === 'production'
      ? process.env.UMI_APP_API_BASE_URL
      : '',
  ...errorConfig,
};
