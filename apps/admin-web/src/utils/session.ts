/** 本地会话令牌在 localStorage 中的键名，请求拦截器与登录页共用 */
export const TOKEN_STORAGE_KEY = 'token';

/** 与后端 ClientConstants 对应：管理后台只接受管理员与超级管理员 */
export const isAdminRole = (role?: string) =>
  role === 'admin' || role === 'superadmin';

/** 角色不符时的提示，带上后端返回的角色，避免只说「没权限」 */
export const noAdminPermissionMessage = (role?: string) =>
  `该账号无管理端权限（当前角色：${role ?? '未知'}）`;
