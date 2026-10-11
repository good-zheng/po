import { beforeEach, describe, expect, it, vi } from 'vitest';

// Mock all heavy dependencies before importing app
const mockReplace = vi.fn();
const mockHistory = {
  location: {
    pathname: '/welcome',
    search: '',
    hash: '',
  },
  replace: mockReplace,
};

const mockQueryCurrentUser = vi.fn();
const mockMessageError = vi.fn();

vi.mock('antd', () => ({
  message: { error: mockMessageError },
}));

vi.mock('@umijs/max', () => ({
  history: mockHistory,
  Link: ({ children }: any) => children,
}));

vi.mock('@/services/ant-design-pro/api', () => ({
  currentUser: mockQueryCurrentUser,
}));

vi.mock('@/components', () => ({
  AvatarDropdown: () => null,
  DocLink: () => null,
  ErrorBoundary: ({ children }: any) => children,
  Footer: () => null,
  LangDropdown: () => null,
  OfflineBanner: () => null,
  VersionDropdown: () => null,
}));

vi.mock('@ant-design/pro-components', () => ({
  SettingDrawer: () => null,
}));

vi.mock('@ant-design/icons', () => ({
  LinkOutlined: () => null,
  UserOutlined: () => null,
}));

vi.mock('./requestErrorConfig', () => ({
  errorConfig: {},
}));

vi.mock('../config/defaultSettings', () => ({
  default: { navTheme: 'light' },
}));

describe('app getInitialState', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    mockHistory.location = {
      pathname: '/welcome',
      search: '',
      hash: '',
    };
  });

  it('should fetch currentUser when not on login page', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockResolvedValue({
      data: {
        id: 1,
        username: 'root',
        role: 'admin',
      },
    });

    const state = await getInitialState();

    expect(mockQueryCurrentUser).toHaveBeenCalled();
    expect(state.currentUser).toEqual({
      id: 1,
      username: 'root',
      role: 'admin',
    });
    expect(state.settingDrawerOpen).toBe(false);
    expect(state.fetchUserInfo).toBeDefined();
  });

  it('should redirect to login when currentUser fetch fails (401)', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockRejectedValue(new Error('401 Unauthorized'));

    const state = await getInitialState();

    expect(mockReplace).toHaveBeenCalledWith(
      expect.stringContaining('/user/login?redirect='),
    );
    expect(state.currentUser).toBeUndefined();
    // 访客本地没有令牌，被拒是预期之内，不必弹窗
    expect(mockMessageError).not.toHaveBeenCalled();
  });

  it('should not fetch currentUser on login page', async () => {
    const { getInitialState } = await import('./app');
    mockHistory.location = {
      pathname: '/user/login',
      search: '',
      hash: '',
    };

    const state = await getInitialState();

    expect(mockQueryCurrentUser).not.toHaveBeenCalled();
    expect(state.currentUser).toBeUndefined();
    expect(state.fetchUserInfo).toBeDefined();
  });

  it('should encode redirect path correctly on 401', async () => {
    const { getInitialState } = await import('./app');
    mockHistory.location = {
      pathname: '/admin/users',
      search: '?page=2',
      hash: '#section',
    };
    mockQueryCurrentUser.mockRejectedValue(new Error('401'));

    await getInitialState();

    expect(mockReplace).toHaveBeenCalledWith(
      `/user/login?redirect=${encodeURIComponent('/admin/users?page=2#section')}`,
    );
  });

  it('should include default settings in initial state', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockResolvedValue({
      data: { username: 'root', role: 'admin' },
    });

    const state = await getInitialState();

    expect(state.settings).toEqual({ navTheme: 'light' });
  });

  it('fetchUserInfo should return user data on success', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockResolvedValue({
      data: { id: 2, username: 'operator', role: 'admin' },
    });

    const state = await getInitialState();

    const user = await state.fetchUserInfo?.();
    expect(user).toEqual({ id: 2, username: 'operator', role: 'admin' });
  });

  it('fetchUserInfo should reject a normal user token', async () => {
    const { getInitialState } = await import('./app');
    localStorage.setItem('token', 'user-token');
    mockQueryCurrentUser.mockResolvedValue({
      data: { id: 3, username: 'chef', role: 'user' },
    });

    const state = await getInitialState();

    expect(state.currentUser).toBeUndefined();
    expect(localStorage.getItem('token')).toBeNull();
    expect(mockReplace).toHaveBeenCalledWith(
      expect.stringContaining('/user/login?redirect='),
    );
    expect(mockMessageError).toHaveBeenCalledWith(
      '该账号无管理端权限（当前角色：user）',
    );
  });

  it('fetchUserInfo should tell the caller which role was rejected', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockResolvedValue({
      data: { id: 4, username: 'chef', role: 'user' },
    });

    const state = await getInitialState();

    await expect(state.fetchUserInfo?.()).rejects.toThrow(
      '该账号无管理端权限（当前角色：user）',
    );
  });

  it('fetchUserInfo should report the HTTP status of a failing session call', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockResolvedValue({
      data: { id: 1, username: 'root', role: 'admin' },
    });

    const state = await getInitialState();

    const httpError: any = new Error('Request failed');
    httpError.response = { status: 403 };
    mockQueryCurrentUser.mockRejectedValue(httpError);

    await expect(state.fetchUserInfo?.()).rejects.toThrow(
      '会话接口失败：HTTP 403',
    );
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('fetchUserInfo should prefer the backend business message', async () => {
    const { getInitialState } = await import('./app');
    mockQueryCurrentUser.mockResolvedValue({
      data: { id: 1, username: 'root', role: 'admin' },
    });

    const state = await getInitialState();

    const bizError: any = new Error('未登录或登录状态已失效');
    bizError.name = 'BizError';
    bizError.info = { code: 401, message: '未登录或登录状态已失效' };
    mockQueryCurrentUser.mockRejectedValue(bizError);

    await expect(state.fetchUserInfo?.()).rejects.toThrow(
      '会话接口失败：未登录或登录状态已失效',
    );
  });

  it('should not nest the redirect when already on the login page', async () => {
    const { getInitialState } = await import('./app');
    mockHistory.location = {
      pathname: '/user/login',
      search: '?redirect=%2Fwelcome',
      hash: '',
    };
    localStorage.setItem('token', 'user-token');
    mockQueryCurrentUser.mockResolvedValue({
      data: { id: 3, username: 'chef', role: 'user' },
    });

    const state = await getInitialState();

    // 登录页上会话被拒时只该提示原因，不能再 replace 一次登录页，
    // 否则 redirect 会把自己套进去越滚越长。
    await expect(state.fetchUserInfo?.()).rejects.toThrow(
      '该账号无管理端权限（当前角色：user）',
    );
    expect(mockReplace).not.toHaveBeenCalled();
  });
});

/**
 * 顶栏头像：ProLayout 在 src/icon/children 全空时渲染 null，
 * 所以「账号没上传过头像」曾经表现为右上角整块头像消失而不是空圆圈。
 */
describe('app layout avatarProps', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  /** avatarProps 的类型是「可关掉的插槽」（`… | false`），这里只取回它对象化的一面 */
  type RenderedAvatar = {
    src?: string;
    srcSet?: string;
    icon?: unknown;
    children?: unknown;
    title?: string;
  };

  const render = async (currentUser: any): Promise<RenderedAvatar> => {
    const { layout } = await import('./app');
    return layout({
      initialState: { currentUser },
      setInitialState: vi.fn(),
      loading: false,
    } as any).avatarProps as RenderedAvatar;
  };

  it('gives the header a default avatar when the account has none', async () => {
    const props = await render({ username: 'root', nickname: '管理员' });
    expect(props.src).toBeTruthy();
    // 库里那条判据的原文，avatar 节点只有在至少一项非空时才存在
    expect(
      Boolean(props.src || props.srcSet || props.icon || props.children),
    ).toBe(true);
    expect(props.title).toBe('管理员');
  });

  it('keeps a uploaded avatar as the header image', async () => {
    const props = await render({ avatar: 'https://cdn.example.com/me.png' });
    expect(props.src).toBe('https://cdn.example.com/me.png');
  });

  it('still offers the icon fallback when a stored avatar url dies', async () => {
    const props = await render({ avatar: 'https://cdn.example.com/gone.png' });
    expect(props.icon).toBeTruthy();
  });
});
