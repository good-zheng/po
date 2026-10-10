import { useEffect, type ReactNode } from 'react';
import Taro from '@tarojs/taro';

import { useAuth } from '@/lib/auth/auth-context';
import { currentPageUrl, saveReturnTo } from '@/lib/auth/return-path';

/**
 * 非 tab 页的登录门（如「编辑资料」）：未登录直接去登录页并记住来路。
 * tab 页不要用这个组件，要显示 GuestPlaceholder —— 自动跳转在返回时会白屏。
 */
export function AuthGuard({ children, returnTo }: { children: ReactNode; returnTo?: string }) {
  const { status } = useAuth();

  useEffect(() => {
    if (status === 'unauthenticated') {
      const url = returnTo || currentPageUrl();
      if (url) saveReturnTo(url);
      Taro.navigateTo({ url: '/pages/login/index' });
    }
  }, [status, returnTo]);

  if (status !== 'authenticated') {
    return null;
  }

  return <>{children}</>;
}
