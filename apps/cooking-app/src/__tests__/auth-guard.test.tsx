import { renderRouter } from 'expo-router/testing-library';
import { type AuthSession, persistSession } from '@/lib/auth/session';

jest.mock('@/lib/api/recipes', () => ({
  fetchRecipes: jest.fn(async () => ({
    content: [],
    number: 0,
    size: 20,
    totalElements: 0,
    totalPages: 0,
  })),
}));

jest.mock('@/lib/api/auth', () => ({
  loginRequest: jest.fn(),
  registerRequest: jest.fn(),
  fetchCurrentUser: jest.fn(async () => ({
    id: 7,
    role: 'user',
    username: 'chef',
  })),
}));

const session: AuthSession = {
  token: 'token-1',
  user: { id: 7, role: 'user', username: 'chef' },
};

describe('forced login route guard', () => {
  // 首个用例要付出整棵路由树的编译与渲染成本，冷启动时超过 jest 默认 5s
  jest.setTimeout(30000);

  it('sends visitors without a session to the login screen', async () => {
    // renderRouter 的返回值既是渲染结果（异步）又挂了路由断言辅助方法；
    // RNTL v14 起 render 为异步，需先 await 拿到查询 API，路径辅助方法留在原对象上。
    const router = renderRouter('./src/app', { initialUrl: '/' });
    const view = await router;

    expect(await view.findByText('PO 做菜')).toBeOnTheScreen();
    expect(router.getPathname()).toBe('/login');
    expect(view.queryByText('今天吃什么')).not.toBeOnTheScreen();
  });

  it('lets a restored session reach the home tab', async () => {
    await persistSession(session);

    const router = renderRouter('./src/app', { initialUrl: '/' });
    const view = await router;

    expect(await view.findByText('今天吃什么')).toBeOnTheScreen();
    expect(router.getPathname()).toBe('/');
    expect(view.queryByText('PO 做菜')).not.toBeOnTheScreen();
  });
});
