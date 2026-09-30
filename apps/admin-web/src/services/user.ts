import { request } from '@umijs/max';
import type {
  ChangePasswordRequest,
  PageResponse,
  ProfileRequest,
  Result,
  UserItem,
  UserRequest,
} from '@po/types';

export type { ProfileRequest, UserItem, UserRequest } from '@po/types';

// ── API ──────────────────────────────────────────────────────────────────────

/** 获取当前登录用户信息 */
export async function getCurrentUser(options?: Record<string, unknown>) {
  return request<Result<UserItem>>('/api/users/me', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 更新当前用户个人资料（仅 nickname/email/phoneNumber/avatar） */
export async function updateCurrentUser(
  body: ProfileRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<UserItem>>('/api/users/me', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 上传当前用户头像，成功后后端直接写入 avatar 字段并返回 URL */
export async function uploadAvatar(
  file: File,
  options?: Record<string, unknown>,
) {
  const formData = new FormData();
  formData.append('file', file);
  return request<Result<string>>('/api/users/me/avatar', {
    method: 'POST',
    data: formData,
    ...(options || {}),
  });
}

/** 修改当前用户密码（需验证原密码） */
export async function changePassword(
  body: ChangePasswordRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>('/api/users/me/password', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 分页获取用户列表（需管理员及以上权限） */
export async function getUsers(
  params: { page?: number; size?: number; keyword?: string },
  options?: Record<string, unknown>,
) {
  return request<Result<PageResponse<UserItem>>>('/api/users', {
    method: 'GET',
    params,
    ...(options || {}),
  });
}

/** 获取单个用户详情 */
export async function getUser(
  id: number,
  options?: Record<string, unknown>,
) {
  return request<Result<UserItem>>(`/api/users/${id}`, {
    method: 'GET',
    ...(options || {}),
  });
}

/** 创建用户（角色受操作者权限限制） */
export async function createUser(
  body: UserRequest,
  options?: Record<string, unknown>,
) {
  return request<Result<UserItem>>('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 更新用户（含角色调整，角色变更受权限校验） */
export async function updateUser(
  id: number,
  body: Partial<UserRequest>,
  options?: Record<string, unknown>,
) {
  return request<Result<UserItem>>(`/api/users/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: body,
    ...(options || {}),
  });
}

/** 修改用户角色 */
export async function updateUserRole(
  id: number,
  role: string,
  options?: Record<string, unknown>,
) {
  return request<Result<UserItem>>(`/api/users/${id}/role`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: { role },
    ...(options || {}),
  });
}

/** 删除用户 */
export async function deleteUser(
  id: number,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>(`/api/users/${id}`, {
    method: 'DELETE',
    ...(options || {}),
  });
}

/** 批量更新用户状态 */
export async function batchUpdateUserStatus(
  ids: number[],
  status: string,
  options?: Record<string, unknown>,
) {
  return request<Result<string>>('/api/users/batch/status', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: { ids, status },
    ...(options || {}),
  });
}

/** 获取待审批用户列表 */
export async function getPendingUsers(options?: Record<string, unknown>) {
  return request<Result<UserItem[]>>('/api/users/pending', {
    method: 'GET',
    ...(options || {}),
  });
}

/** 审批用户（approved / rejected） */
export async function approveUser(
  id: number,
  action: 'approved' | 'rejected',
  options?: Record<string, unknown>,
) {
  return request<Result<UserItem>>(`/api/users/${id}/approval`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    data: { action },
    ...(options || {}),
  });
}
