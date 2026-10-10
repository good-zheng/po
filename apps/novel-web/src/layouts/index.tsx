import { Outlet } from '@umijs/max';
import React from 'react';

import Chrome from '@/components/Chrome';

/**
 * 全站布局。必须走路由嵌套（config/routes.ts 的第一层），不能放在
 * app.tsx 的 rootContainer 里——rootContainer 在 Router 外层，
 * 在那儿调用 useLocation 会直接抛错。
 */
export default function Layout() {
  return (
    <Chrome>
      <Outlet />
    </Chrome>
  );
}
