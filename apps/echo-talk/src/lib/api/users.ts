import type { ProfileRequest, UserItem } from '@po/types';

import { apiClient, uploadFile } from '@/lib/api/client';
import { fetchCurrentUser } from '@/lib/api/auth';
import type { AuthUser } from '@/lib/auth/session';

/** 自助更新基本资料（昵称/手机号/邮箱） */
export async function updateProfile(payload: ProfileRequest): Promise<AuthUser> {
  await apiClient.put<UserItem>('/users/me', payload as unknown as Record<string, unknown>);
  // 后端返回完整 User 实体，这里统一重新拉取以复用现有 AuthUser 映射
  return fetchCurrentUser();
}

/** 上传头像：后端直接写回 avatar 字段并返回资源路径，无需二次 PUT */
export async function uploadAvatar(filePath: string): Promise<string> {
  return uploadFile<string>('/users/me/avatar', filePath);
}
