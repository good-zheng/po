import { fireEvent, render } from '@testing-library/react-native';
import { Alert } from 'react-native';

import ProfileScreen from '@/app/(tabs)/profile';

const mockSignOut = jest.fn();

jest.mock('@/lib/auth/auth-context', () => ({
  useAuth: () => ({
    signIn: jest.fn(),
    signOut: mockSignOut,
    signUp: jest.fn(),
    status: 'authenticated',
    user: {
      email: 'chef@po.dev',
      id: 7,
      nickname: '大厨',
      role: 'admin',
      username: 'chef',
    },
  }),
}));

describe('ProfileScreen', () => {
  it('shows the signed-in user profile', async () => {
    const screen = await render(<ProfileScreen />);

    expect(screen.getByText('大厨')).toBeOnTheScreen();
    expect(screen.getByText('@chef')).toBeOnTheScreen();
    expect(screen.getByText('管理员')).toBeOnTheScreen();
    expect(screen.getByText('chef@po.dev')).toBeOnTheScreen();
  });

  it('asks for confirmation before signing out', async () => {
    const alert = jest.spyOn(Alert, 'alert').mockImplementation(() => {});
    const screen = await render(<ProfileScreen />);

    fireEvent.press(screen.getByText('退出登录'));

    expect(alert).toHaveBeenCalledTimes(1);
    const buttons = alert.mock.calls[0]?.[2] ?? [];
    expect(buttons.map((button) => button.text)).toEqual(['取消', '退出登录']);

    const confirm = buttons.find((button) => button.style === 'destructive');
    confirm?.onPress?.();

    expect(mockSignOut).toHaveBeenCalledTimes(1);
    alert.mockRestore();
  });
});
