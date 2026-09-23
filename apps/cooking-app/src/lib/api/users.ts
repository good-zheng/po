import type { ProfileRequest, UserItem } from '@po/types';

import { apiClient, unwrap } from '@/lib/api/client';

/** 当前用户自助更新基本资料（昵称/手机号/邮箱/头像） */
export async function updateProfile(
  payload: ProfileRequest,
): Promise<UserItem> {
  const response = await apiClient.put('/users/me', payload);

  return unwrap<UserItem>(response);
}
