import type { UserItem } from '@po/types';
import { apiClient } from '@/lib/api/client';
import type { AuthSession, AuthUser } from '@/lib/auth/session';

type LoginPayload = {
  id: number;
  token: string | null;
  username: string;
  nickname?: string | null;
  role: string;
  phoneNumber?: string | null;
  approvalStatus: string;
};

export type LoginResult = {
  approved: boolean;
  approvalStatus: string;
  session: AuthSession | null;
};

function toLoginResult(payload: LoginPayload): LoginResult {
  const status = payload.approvalStatus || 'approved';
  if (status !== 'approved' || !payload.token) {
    return { approved: false, approvalStatus: status, session: null };
  }
  return {
    approved: true,
    approvalStatus: status,
    session: {
      token: payload.token,
      user: {
        id: payload.id,
        username: payload.username,
        nickname: payload.nickname,
        role: payload.role,
        phoneNumber: payload.phoneNumber,
      },
    },
  };
}

export async function openIdLoginRequest(loginCode: string): Promise<LoginResult> {
  const payload = await apiClient.post<LoginPayload>('/auth/openid-login', { loginCode });
  return toLoginResult(payload);
}

export async function passwordLoginRequest(username: string, password: string): Promise<LoginResult> {
  const payload = await apiClient.post<LoginPayload>('/auth/login', {
    username,
    password,
    client: 'app',
  });
  return toLoginResult(payload);
}

export async function appRegisterRequest(
  username: string,
  password: string,
  nickname?: string,
): Promise<LoginResult> {
  const payload = await apiClient.post<LoginPayload>('/auth/app-register', {
    username,
    password,
    nickname,
  });
  return toLoginResult(payload);
}

export async function fetchCurrentUser(): Promise<AuthUser> {
  const user = await apiClient.get<UserItem>('/users/me');
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
