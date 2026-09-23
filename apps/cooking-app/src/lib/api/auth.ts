import type { LoginRequest, UserItem } from '@po/types';

import { apiClient, unwrap } from '@/lib/api/client';
import type { AuthSession, AuthUser } from '@/lib/auth/session';

type LoginPayload = {
  id: number;
  token: string;
  username: string;
  nickname?: string | null;
  role: string;
  phoneNumber?: string | null;
};

export type RegisterParams = {
  username: string;
  password: string;
  email?: string;
};

export async function loginRequest(
  username: string,
  password: string,
): Promise<AuthSession> {
  const body: LoginRequest = { username, password, client: 'app' };
  const response = await apiClient.post('/auth/login', body);
  const payload = unwrap<LoginPayload>(response);

  return {
    token: payload.token,
    user: {
      id: payload.id,
      username: payload.username,
      nickname: payload.nickname,
      role: payload.role,
      phoneNumber: payload.phoneNumber,
    },
  };
}

export async function registerRequest({
  username,
  password,
  email,
}: RegisterParams): Promise<void> {
  // 后端注册接口通过查询参数接收表单
  const response = await apiClient.post('/auth/register', null, {
    params: { username, password, email },
  });
  unwrap<string>(response);
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const response = await apiClient.get('/users/me');
  const user = unwrap<UserItem>(response);

  return {
    id: user.id,
    username: user.username,
    nickname: user.nickname,
    role: user.role,
    avatar: user.avatar,
    email: user.email,
    phoneNumber: user.phoneNumber,
  };
}
