import type { ProfileRequest, UserItem } from '@po/types';
import { Platform } from 'react-native';

import { apiClient, unwrap } from '@/lib/api/client';

/** 当前用户自助更新基本资料（昵称/手机号/邮箱/头像） */
export async function updateProfile(
  payload: ProfileRequest,
): Promise<UserItem> {
  const response = await apiClient.put('/users/me', payload);

  return unwrap<UserItem>(response);
}

/**
 * 上传头像：后端直接写回用户 avatar 字段并返回资源路径。
 * 原生端把本地文件 uri 交给 RN 的 FormData，Web 端先取 Blob。
 */
export async function uploadAvatar(uri: string): Promise<string> {
  const formData = new FormData();
  const filename = `avatar-${Date.now()}.jpg`;

  if (Platform.OS === 'web') {
    const blob = await (await fetch(uri)).blob();
    formData.append('file', blob, filename);
  } else {
    formData.append('file', {
      name: filename,
      type: 'image/jpeg',
      uri,
    } as unknown as Blob);
  }

  const response = await apiClient.post('/users/me/avatar', formData);

  return unwrap<string>(response);
}
