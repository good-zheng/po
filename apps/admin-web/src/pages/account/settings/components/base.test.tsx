import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as service from '@/services/user';
import BaseView from './base';

const DEFAULT_AVATAR =
  'https://gw.alipayobjects.com/zos/rmsportal/BiazfanxmamNRoxxVxka.png';

const mocks = vi.hoisted(() => ({
  setInitialState: vi.fn(),
  messageApi: {
    success: vi.fn(),
    error: vi.fn(),
  },
  form: {
    initialValues: undefined as Record<string, any> | undefined,
    onFinish: undefined as
      | ((values: Record<string, any>) => Promise<any>)
      | undefined,
  },
  upload: {
    beforeUpload: undefined as ((file: File) => boolean) | undefined,
  },
}));

vi.mock('@umijs/max', () => ({
  useModel: () => ({ setInitialState: mocks.setInitialState }),
}));

vi.mock('@/services/user', () => ({
  getCurrentUser: vi.fn(),
  updateCurrentUser: vi.fn(),
  uploadAvatar: vi.fn(),
}));

vi.mock('@ant-design/pro-components', () => ({
  ProForm: ({ children, formRef, initialValues, onFinish }: any) => {
    mocks.form.initialValues = initialValues;
    mocks.form.onFinish = onFinish;
    if (formRef) {
      formRef.current = {};
    }
    return <form onSubmit={(e) => e.preventDefault()}>{children}</form>;
  },
  ProFormText: () => <div />,
}));

vi.mock('antd', () => ({
  Button: ({ children }: any) => <button type="button">{children}</button>,
  Upload: ({ children, beforeUpload }: any) => {
    mocks.upload.beforeUpload = beforeUpload;
    return <div>{children}</div>;
  },
  message: {
    useMessage: () => [mocks.messageApi, null],
  },
}));

vi.mock('@ant-design/icons', () => ({
  UploadOutlined: () => <span />,
}));

vi.mock('./index.style', () => ({
  default: () => ({
    styles: {
      avatar: 'avatar',
      avatar_title: 'avatar-title',
      baseView: 'base-view',
      button_view: 'button-view',
      left: 'left',
      right: 'right',
    },
  }),
}));

describe('BaseView profile form', () => {
  let queryClient: QueryClient;

  const mockUser = {
    id: 1,
    username: 'admin',
    nickname: '管理员',
    email: 'admin@example.com',
    phoneNumber: '13800000000',
    avatar: 'http://cdn.example.com/avatar.png',
    role: 'admin',
    status: 'ACTIVE',
  };

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    mocks.form.initialValues = undefined;
    mocks.form.onFinish = undefined;
    mocks.upload.beforeUpload = undefined;
    vi.clearAllMocks();
    vi.mocked(service.getCurrentUser).mockResolvedValue({
      data: mockUser,
    } as any);
  });

  const renderBaseView = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BaseView />
      </QueryClientProvider>,
    );

  it('initializes the form from the current user profile', async () => {
    renderBaseView();

    await waitFor(() => {
      expect(mocks.form.initialValues).toEqual({
        nickname: '管理员',
        email: 'admin@example.com',
        phoneNumber: '13800000000',
      });
    });
  });

  it('renders the user avatar when available', async () => {
    renderBaseView();

    expect((await screen.findByAltText('avatar')).getAttribute('src')).toBe(
      mockUser.avatar,
    );
  });

  it('falls back to the default avatar when none is set', async () => {
    vi.mocked(service.getCurrentUser).mockResolvedValue({
      data: { ...mockUser, avatar: '' },
    } as any);

    renderBaseView();

    expect((await screen.findByAltText('avatar')).getAttribute('src')).toBe(
      DEFAULT_AVATAR,
    );
  });

  it('fills clearable fields with empty strings on submit', async () => {
    vi.mocked(service.updateCurrentUser).mockResolvedValue({
      data: mockUser,
    } as any);

    renderBaseView();
    await waitFor(() => {
      expect(mocks.form.onFinish).toBeTypeOf('function');
    });

    const result = await mocks.form.onFinish?.({ nickname: '新昵称' });

    expect(result).toBe(true);
    expect(service.updateCurrentUser).toHaveBeenCalledWith(
      { nickname: '新昵称', email: '', phoneNumber: '' },
      { skipErrorHandler: true },
    );
  });

  it('keeps provided optional field values on submit', async () => {
    vi.mocked(service.updateCurrentUser).mockResolvedValue({
      data: mockUser,
    } as any);

    renderBaseView();
    await waitFor(() => {
      expect(mocks.form.onFinish).toBeTypeOf('function');
    });

    await mocks.form.onFinish?.({
      nickname: '昵称',
      email: 'new@example.com',
      phoneNumber: '13900000000',
    });

    expect(service.updateCurrentUser).toHaveBeenCalledWith(
      {
        nickname: '昵称',
        email: 'new@example.com',
        phoneNumber: '13900000000',
      },
      { skipErrorHandler: true },
    );
  });

  it('shows a success message and syncs global state after update', async () => {
    vi.mocked(service.updateCurrentUser).mockResolvedValue({
      data: { ...mockUser, nickname: '新昵称' },
    } as any);

    renderBaseView();
    await waitFor(() => {
      expect(mocks.form.onFinish).toBeTypeOf('function');
    });

    await mocks.form.onFinish?.({ nickname: '新昵称' });

    await waitFor(() => {
      expect(mocks.messageApi.success).toHaveBeenCalledWith('更新基本信息成功');
      expect(mocks.setInitialState).toHaveBeenCalled();
    });

    const updater = mocks.setInitialState.mock.calls[0][0] as (s: any) => any;
    expect(updater({ currentUser: { nickname: '旧昵称' } })).toMatchObject({
      currentUser: { nickname: '新昵称' },
    });
  });

  it('shows the backend error message when update fails', async () => {
    vi.mocked(service.updateCurrentUser).mockRejectedValue(
      new Error('昵称已被占用'),
    );

    renderBaseView();
    await waitFor(() => {
      expect(mocks.form.onFinish).toBeTypeOf('function');
    });

    await expect(mocks.form.onFinish?.({ nickname: 'x' })).rejects.toThrow();

    await waitFor(() => {
      expect(mocks.messageApi.error).toHaveBeenCalledWith('昵称已被占用');
    });
  });

  it('rejects avatars larger than 2MB', async () => {
    renderBaseView();
    await waitFor(() => {
      expect(mocks.upload.beforeUpload).toBeTypeOf('function');
    });

    const oversizedFile = new File(['x'], 'big.png', { type: 'image/png' });
    Object.defineProperty(oversizedFile, 'size', {
      value: 2 * 1024 * 1024 + 1,
    });

    mocks.upload.beforeUpload?.(oversizedFile);

    expect(mocks.messageApi.error).toHaveBeenCalledWith('头像图片不能超过 2MB');
    expect(service.uploadAvatar).not.toHaveBeenCalled();
  });

  it('uploads valid avatars and syncs the returned URL', async () => {
    vi.mocked(service.uploadAvatar).mockResolvedValue({
      data: 'http://cdn.example.com/new-avatar.png',
    } as any);

    renderBaseView();
    await waitFor(() => {
      expect(mocks.upload.beforeUpload).toBeTypeOf('function');
    });

    const file = new File(['x'], 'small.png', { type: 'image/png' });
    mocks.upload.beforeUpload?.(file);

    await waitFor(() => {
      expect(service.uploadAvatar).toHaveBeenCalledWith(file, {
        skipErrorHandler: true,
      });
    });

    await waitFor(() => {
      expect(mocks.messageApi.success).toHaveBeenCalledWith('头像上传成功');
      expect(mocks.setInitialState).toHaveBeenCalled();
    });

    const updater = mocks.setInitialState.mock.calls[0][0] as (s: any) => any;
    expect(updater({ currentUser: { avatar: 'old.png' } })).toMatchObject({
      currentUser: { avatar: 'http://cdn.example.com/new-avatar.png' },
    });
  });
});
