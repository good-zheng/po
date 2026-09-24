/**
 * @name umi 的路由配置
 * @description 只支持 path,component,routes,redirect,wrappers,name,icon 的配置
 * @param path  path 只支持两种占位符配置，第一种是动态参数 :id 的形式，第二种是 * 通配符，通配符只能出现路由字符串的最后。
 * @param component 配置 location 和 path 匹配后用于渲染的 React 组件路径。可以是绝对路径，也可以是相对路径，如果是相对路径，会从 src/pages 开始找起。
 * @param routes 配置子路由，通常在需要为多个路径增加 layout 组件时使用。
 * @param redirect 配置路由跳转
 * @param wrappers 配置路由组件的包装组件，通过包装组件可以为当前的路由组件组合进更多的功能。 比如，可以用于路由级别的权限校验
 * @param name 配置路由的标题，默认读取国际化文件 menu.ts 中 menu.xxxx 的值，如配置 name 为 login，则读取 menu.ts 中 menu.login 的取值作为标题
 * @param icon 配置路由的图标，取值参考 https://ant.design/components/icon-cn， 注意去除风格后缀和大小写，如想要配置图标为 <StepBackwardOutlined /> 则取值应为 stepBackward 或 StepBackward，如想要配置图标为 <UserOutlined /> 则取值应为 user 或者 User
 * @doc https://umijs.org/docs/guides/routes
 */
export default [
  {
    path: '/user',
    layout: false,
    routes: [
      {
        path: '/user/login',
        name: 'login',
        component: './user/login',
      },
      {
        path: '/user',
        redirect: '/user/login',
      },
      {
        name: 'register-result',
        icon: 'checkCircle',
        path: '/user/register-result',
        component: './user/register-result',
      },
      {
        name: 'register',
        icon: 'userAdd',
        path: '/user/register',
        component: './user/register',
      },
      {
        name: '404',
        component: './exception/404',
        path: '/user/*',
      },
    ],
  },
  // {
  //   path: '/welcome',
  //   name: 'welcome',
  //   icon: 'home',
  //   access: 'canAdmin',
  //   component: './Welcome',
  // },
  {
    path: '/recipes',
    name: 'recipes',
    icon: 'crown',
    access: 'canAdmin',
    routes: [
      {
        path: '/recipes',
        redirect: '/recipes/list',
      },
      {
        path: '/recipes/list',
        name: 'list',
        component: './recipes/list',
      },
      {
        path: '/recipes/review',
        name: 'review',
        component: './recipes/review',
      },
      {
        path: '/recipes/categories',
        name: 'categories',
        component: './recipes/categories',
      },
      {
        path: '/recipes/create',
        name: 'create',
        component: './recipes/create',
      },
      {
        path: '/recipes/edit/:id',
        name: 'edit',
        hideInMenu: true,
        component: './recipes/edit',
      },
      {
        path: '/recipes/detail/:id',
        name: 'detail',
        hideInMenu: true,
        component: './recipes/detail',
      },
    ],
  },
  // {
  //   name: "account",
  //   icon: "user",
  //   path: "/account",
  //   routes: [
  //     {
  //       path: "/account",
  //       redirect: "/account/settings",
  //     },
  //     {
  //       name: "settings",
  //       icon: "setting",
  //       path: "/account/settings",
  //       component: "./account/settings",
  //     },
  //     {
  //       name: 'center',
  //       icon: 'user',
  //       path: '/account/center',
  //       component: './account/center',
  //     },
  //   ],
  // },
  {
    path: '/chatbot',
    name: 'chatbot',
    icon: 'robot',
    access: 'canAdmin',
    component: './chatbot',
  },
  {
    path: '/users',
    name: 'users',
    icon: 'team',
    access: 'canAdmin',
    component: './system/users',
  },
  {
    name: 'settings',
    icon: 'setting',
    path: '/account/settings',
    access: 'canAdmin',
    component: './account/settings',
  },
  // {
  //   name: 'exception',
  //   icon: 'warning',
  //   path: '/exception',
  //   routes: [
  //     {
  //       path: '/exception',
  //       redirect: '/exception/403',
  //     },
  //     {
  //       name: '403',
  //       icon: 'stop',
  //       path: '/exception/403',
  //       component: './exception/403',
  //     },
  //     {
  //       name: '404',
  //       icon: 'warning',
  //       path: '/exception/404',
  //       component: './exception/404',
  //     },
  //     {
  //       name: '500',
  //       icon: 'bug',
  //       path: '/exception/500',
  //       component: './exception/500',
  //     },
  //   ],
  // },
  {
    path: '/',
    redirect: '/recipes/list',
  },
  {
    component: './exception/404',
    path: '/*',
  },
];
