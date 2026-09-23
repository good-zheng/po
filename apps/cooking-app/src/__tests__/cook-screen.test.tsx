import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { act, fireEvent, render } from '@testing-library/react-native';
import type { ReactNode } from 'react';

import CookModeScreen from '@/app/cook/[id]';
import { CookingProvider } from '@/lib/cooking/cooking-context';

const STEP_CONTENT = '热锅下油，把鱼头煎到两面微黄';
const mockAlert = {
  play: jest.fn(),
  ringing: false,
  stop: jest.fn(),
};

jest.mock('expo-keep-awake', () => ({ useKeepAwake: () => {} }));

jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaInsets: () => ({ bottom: 0, left: 0, right: 0, top: 0 }),
}));

jest.mock('expo-router', () => ({
  useLocalSearchParams: () => ({ id: '7' }),
  useRouter: () => ({
    back: jest.fn(),
    canGoBack: () => false,
    replace: jest.fn(),
  }),
}));

jest.mock('@/lib/cooking/use-cook-alert', () => ({
  useCookAlert: () => mockAlert,
}));

jest.mock('@/lib/api/recipes', () => ({
  fetchRecipeDetail: jest.fn(async () => ({
    authorId: 1,
    difficulty: 2,
    id: 7,
    isPublic: true,
    likesCount: 0,
    steps: [
      {
        content: '热锅下油，把鱼头煎到两面微黄',
        duration: 1,
        id: 1,
        stepNumber: 1,
      },
      { content: '铺上剁椒上锅蒸八分钟', id: 2, stepNumber: 2 },
    ],
    title: '剁椒鱼头',
  })),
}));

function renderCook() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={client}>
        <CookingProvider>{children}</CookingProvider>
      </QueryClientProvider>
    );
  }

  return render(<CookModeScreen />, { wrapper: Wrapper });
}

describe('CookModeScreen', () => {
  beforeEach(() => {
    mockAlert.ringing = false;
    mockAlert.play.mockClear();
    mockAlert.stop.mockClear();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('plays the alert as soon as the countdown is skipped', async () => {
    const screen = await renderCook();

    expect(await screen.findByText(STEP_CONTENT)).toBeOnTheScreen();
    expect(screen.getByText('01:00')).toBeOnTheScreen();
    expect(mockAlert.play).not.toHaveBeenCalled();

    await fireEvent.press(screen.getByText('跳过等待'));

    expect(mockAlert.play).toHaveBeenCalledTimes(1);
    expect(screen.getByText('时间到，可以进行下一步了')).toBeOnTheScreen();
    expect(screen.getByText('下一步：铺上剁椒上锅蒸八分钟')).toBeOnTheScreen();
  });

  it('plays the alert when the countdown reaches zero', async () => {
    jest.useFakeTimers();
    const screen = await renderCook();

    expect(await screen.findByText(STEP_CONTENT)).toBeOnTheScreen();
    expect(mockAlert.play).not.toHaveBeenCalled();

    await act(async () => {
      await jest.advanceTimersByTimeAsync(60_000);
    });

    expect(screen.getByText('00:00')).toBeOnTheScreen();
    expect(mockAlert.play).toHaveBeenCalledTimes(1);
  });

  it('lets the user cut the ringing short', async () => {
    mockAlert.ringing = true;
    const screen = await renderCook();

    await fireEvent.press(await screen.findByText('跳过等待'));

    await fireEvent.press(screen.getByText('停止响铃'));

    expect(mockAlert.stop).toHaveBeenCalledTimes(1);
  });

  it('stops the alert once the user moves on', async () => {
    mockAlert.ringing = true;
    const screen = await renderCook();

    await fireEvent.press(await screen.findByText('跳过等待'));
    await fireEvent.press(screen.getByText('进入下一步'));

    expect(mockAlert.stop).toHaveBeenCalled();
  });
});
