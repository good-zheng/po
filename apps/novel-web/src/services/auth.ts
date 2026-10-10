import type { LoginRequest, Result, UserItem } from '@po/types';
import { request } from '@umijs/max';

/** 与后端 LoginResponse 对齐；token 只在 approved 时非空 */
export type LoginResponse = {
  id?: number;
  token?: string | null;
  username?: string;
  nickname?: string;
  role?: string;
  phoneNumber?: string;
  approvalStatus?: string;
};

export const TOKEN_STORAGE_KEY = 'token';
export const LOGIN_PATH = '/user/login';

/**
 * 账密登录。client 固定 'admin'：后端 ClientConstants 只认 admin|app，
 * 且 admin 只放行 admin|superadmin 角色——创作端就是管理员在用，
 * 读者侧无需 token（读接口 permitAll），所以这里不新增 client 值。
 */
export async function login(body: { username: string; password: string }) {
  const payload: LoginRequest = { ...body, client: 'admin' };
  return request<Result<LoginResponse>>('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: payload,
  });
}

/** 当前登录用户 */
export async function getBookMe(options?: Record<string, unknown>) {
  return request<Result<UserItem>>('/api/users/me', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 管理端与本站共用同一个 localStorage key，切换站点时会话直接复用 */
export function saveToken(token: string) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function hasToken() {
  return !!localStorage.getItem(TOKEN_STORAGE_KEY);
}
