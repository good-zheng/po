import { useEffect, type ReactNode } from 'react';
import Taro from '@tarojs/taro';
import { useAuth } from '@/lib/auth/auth-context';
import { currentPageUrl, saveReturnTo } from '@/lib/auth/return-path';

export function AuthGuard({ children, returnTo }: { children: ReactNode; returnTo?: string }) {
  const { status } = useAuth();

  useEffect(() => {
    if (status === 'unauthenticated') {
      const url = returnTo || currentPageUrl();
      if (url) saveReturnTo(url);
      Taro.navigateTo({ url: '/pages/login/index' });
    }
  }, [status, returnTo]);

  if (status === 'loading') {
    return null;
  }

  if (status === 'unauthenticated') {
    return null;
  }

  return <>{children}</>;
}
