import { useSearchParams } from '@umijs/max';
import React, { useState } from 'react';
import { clearToken, login, saveToken } from '@/services/auth';

/** 只接受站内绝对路径，'//' 开头会被浏览器当成协议相对 URL 跳到外站 */
const safeRedirect = (value: string | null) => {
  if (!value) return '/';
  try {
    const decoded = decodeURIComponent(value);
    return decoded.startsWith('/') && !decoded.startsWith('//') ? decoded : '/';
  } catch (_error) {
    return '/';
  }
};

/**
 * 管理员登录（创作端 /studio 的入口，M3 接通）。
 * 读者侧不需要它：书架、详情、阅读都是 permitAll。
 */
export default function LoginPage() {
  const [searchParams] = useSearchParams();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string>();

  const redirectTo = safeRedirect(searchParams.get('redirect'));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setError(undefined);
    try {
      const res = await login({ username: username.trim(), password });
      const data = res?.data;
      if (!data?.token) {
        clearToken();
        setError(
          data?.approvalStatus && data.approvalStatus !== 'approved'
            ? '账号尚未通过审核'
            : '该账号没有创作端权限',
        );
        return;
      }
      saveToken(data.token);
      // 整页跳转：让 getInitialState 重新拉一次用户，避免停在游客态
      window.location.assign(redirectTo);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '登录失败，请重试');
      setSubmitting(false);
    }
  };

  return (
    <div className="login-card">
      <div className="login-head">
        <span className="site-mark" aria-hidden="true">
          言
        </span>
        <h1 className="login-title">管理员登录</h1>
      </div>
      <p className="form-note">
        阅读不需要登录，此页仅供创作端（/studio）使用。
      </p>

      <form onSubmit={submit} className="login-form">
        <label className="field">
          <span className="field-label">账号</span>
          <input
            className="field-input"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
          />
        </label>
        <label className="field">
          <span className="field-label">密码</span>
          <input
            className="field-input"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </label>

        {error ? <p className="form-error">{error}</p> : null}

        <button className="btn-primary" type="submit" disabled={submitting}>
          {submitting ? '登录中…' : '登录'}
        </button>
      </form>
    </div>
  );
}
