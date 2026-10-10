import { PropsWithChildren } from 'react';

import { AuthProvider } from '@/lib/auth/auth-context';
import '@/styles/app.scss';

function App({ children }: PropsWithChildren) {
  // 登录态由 AuthProvider 统一持有：冷启动回填本地会话、拉一次 /users/me、
  // 并把 401 收敛成「清会话 + 页面转游客态」，不做任何自动跳转（tab 页跳登录再返回会白屏）
  return <AuthProvider>{children}</AuthProvider>;
}

export default App;
