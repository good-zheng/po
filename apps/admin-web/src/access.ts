/**
 * 三级权限体系：
 * - superadmin 超级管理员：全部权限，可管理任何用户及其角色
 * - admin 管理员：可管理普通用户（角色调整 user <-> admin）
 * - user 普通用户：基础权限
 * @see https://umijs.org/docs/max/access#access
 * */
export default function access(
  initialState: { currentUser?: API.CurrentUser } | undefined,
) {
  const { currentUser } = initialState ?? {};
  const role = currentUser?.role;
  return {
    // 超级管理员专属权限（如授予超级管理员角色）
    canSuperAdmin: role === 'superadmin',
    // 管理权限：管理员或超级管理员
    canAdmin: role === 'superadmin' || role === 'admin',
    // 已登录用户
    canUser: !!currentUser,
  };
}
