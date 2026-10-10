/**
 * 路由表。游客可读的三页不带 access，未登录也能进。
 *
 * /studio（创作端）在 M3 落地，届时补上这两条路由并挂 access: 'canAdmin'：
 *   { path: '/studio', component: './studio', access: 'canAdmin' }
 *   { path: '/studio/book/:id', component: './studio/book', access: 'canAdmin' }
 * 现在不留占位组件，避免构建指向不存在的文件。
 *
 * @doc https://umijs.org/docs/guides/routes
 */
export default [
  {
    path: '/',
    component: './bookshelf',
  },
  {
    path: '/book/:id',
    component: './book',
  },
  {
    path: '/read/:bookId/:chapterId',
    component: './read',
  },
  {
    path: '/user/login',
    component: './user/login',
  },
  {
    path: '*',
    component: './404',
  },
];
