import { Link, useLocation } from '@umijs/max';
import React from 'react';

import { clearToken, hasToken } from '@/services/auth';

/**
 * 全站页头页脚。阅读页（/read/**）不渲染，保证正文占满视口。
 *
 * 登录态只看「本地有没有令牌」，不读 initialState：rootContainer 比
 * initialState 的 Provider 更外层，在那里 useModel 会直接抛错。
 * 登录与登出都走整页跳转，所以不需要额外的响应式同步。
 */
const Chrome: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { pathname } = useLocation();
  const immersive = pathname.startsWith('/read/');
  const signedIn = hasToken();
  const redirect = encodeURIComponent(pathname);

  return (
    <div className="site-shell">
      {!immersive && (
        <header className="site-head">
          <Link to="/" className="site-brand">
            <span className="site-mark" aria-hidden="true">
              言
            </span>
            言外书斋
          </Link>
          {signedIn ? (
            <button
              type="button"
              className="site-head-link"
              onClick={() => {
                // 后端没有登出接口，清本地令牌即为登出（与管理端一致）
                clearToken();
                window.location.assign('/');
              }}
            >
              退出
            </button>
          ) : (
            <Link
              to={`/user/login?redirect=${redirect}`}
              className="site-head-link"
            >
              登录
            </Link>
          )}
        </header>
      )}

      <main className={immersive ? 'site-main site-main-flush' : 'site-main'}>
        {children}
      </main>

      {!immersive && (
        <footer className="site-foot">
          <div className="site-foot-rule" aria-hidden="true" />
          <span>言外书斋 · 文字作品在线阅读 · 游客可直接浏览</span>
        </footer>
      )}
    </div>
  );
};

export default Chrome;
