import { fireEvent, render } from '@testing-library/react-native';
import type { ReactNode } from 'react';
import { Text } from 'react-native';

import LoginScreen from '@/app/login';
import { ApiError } from '@/lib/api/client';

const mockSignIn = jest.fn();

const mockLink = ({ children }: { children: ReactNode }) => (
  <Text>{children}</Text>
);

jest.mock('expo-router', () => ({
  Link: (props: { children: ReactNode }) => mockLink(props),
}));

jest.mock('@/lib/auth/auth-context', () => ({
  useAuth: () => ({
    signIn: mockSignIn,
    signOut: jest.fn(),
    signUp: jest.fn(),
    status: 'unauthenticated',
    user: null,
  }),
}));

describe('LoginScreen', () => {
  beforeEach(() => {
    mockSignIn.mockReset();
  });

  it('requires a username and a password', async () => {
    const screen = await render(<LoginScreen />);

    await fireEvent.press(screen.getByText('登录'));

    expect(screen.getByText('请输入用户名和密码')).toBeOnTheScreen();
    expect(mockSignIn).not.toHaveBeenCalled();
  });

  it('signs in with the trimmed username', async () => {
    mockSignIn.mockResolvedValueOnce(undefined);
    const screen = await render(<LoginScreen />);

    await fireEvent.changeText(
      screen.getByPlaceholderText('请输入用户名'),
      ' chef ',
    );
    await fireEvent.changeText(
      screen.getByPlaceholderText('请输入密码'),
      'secret',
    );
    await fireEvent.press(screen.getByText('登录'));

    expect(mockSignIn).toHaveBeenCalledWith('chef', 'secret');
  });

  it('shows the message returned by the backend', async () => {
    mockSignIn.mockRejectedValueOnce(
      new ApiError('用户名或密码错误', 401, 200),
    );
    const screen = await render(<LoginScreen />);

    await fireEvent.changeText(
      screen.getByPlaceholderText('请输入用户名'),
      'chef',
    );
    await fireEvent.changeText(
      screen.getByPlaceholderText('请输入密码'),
      'wrong',
    );
    await fireEvent.press(screen.getByText('登录'));

    expect(await screen.findByText('用户名或密码错误')).toBeOnTheScreen();
    expect(screen.queryByText('请输入用户名和密码')).not.toBeOnTheScreen();
  });
});
