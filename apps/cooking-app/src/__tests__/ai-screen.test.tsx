import type { Recipe } from '@po/types';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render } from '@testing-library/react-native';
import type { ReactNode } from 'react';

import AiGuideScreen from '@/app/(tabs)/ai';
import { streamAgentReply } from '@/lib/ai/agent-chat';
import { askAssistant } from '@/lib/ai/chat';

const RECIPE: Recipe = {
  authorId: 1,
  difficulty: 2,
  id: 7,
  isPublic: true,
  likesCount: 3,
  servings: 2,
  title: '剁椒鱼头',
  totalTime: 40,
};

jest.mock('@/lib/ai/agent-chat', () => ({
  resetAgentConversation: jest.fn(),
  streamAgentReply: jest.fn(),
}));

jest.mock('@/lib/ai/chat', () => ({ askAssistant: jest.fn() }));

jest.mock('@/lib/api/recipes', () => ({
  fetchRecipeCategories: jest.fn(async () => [
    { id: 1, name: '川菜', sortOrder: 1 },
  ]),
}));

jest.mock('@/lib/cooking/cooking-context', () => ({
  useCooking: () => ({
    cancelCooking: jest.fn(),
    clearNote: jest.fn(),
    note: undefined,
    session: undefined,
  }),
}));

jest.mock('expo-router', () => ({
  Link: ({ children }: { children: ReactNode }) => children,
}));

jest.mock('react-native-safe-area-context', () => ({
  useSafeAreaInsets: () => ({ bottom: 0, left: 0, right: 0, top: 0 }),
}));

const mockStream = streamAgentReply as jest.MockedFunction<
  typeof streamAgentReply
>;
const mockAsk = askAssistant as jest.MockedFunction<typeof askAssistant>;

function renderAi() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(<AiGuideScreen />, {
    wrapper: ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    ),
  });
}

type Screen = Awaited<ReturnType<typeof render>>;

async function ask(screen: Screen, text: string) {
  await fireEvent.changeText(
    screen.getByPlaceholderText('问问今天做什么菜'),
    text,
  );
  await fireEvent.press(screen.getByLabelText('发送'));
}

describe('AiGuideScreen', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the agent stream along with its recipe cards', async () => {
    mockStream.mockImplementation(async (_message, options) => {
      options?.onText?.('剁椒鱼头要蒸 40 分钟。');
      options?.onRecipes?.([RECIPE]);

      return { answered: true };
    });
    const screen = await renderAi();

    await ask(screen, '剁椒鱼头怎么做');

    expect(await screen.findByText('剁椒鱼头要蒸 40 分钟。')).toBeOnTheScreen();
    expect(screen.getByText('剁椒鱼头')).toBeOnTheScreen();
    expect(mockStream).toHaveBeenCalledWith(
      '剁椒鱼头怎么做',
      expect.objectContaining({ signal: expect.anything() }),
    );
    expect(mockAsk).not.toHaveBeenCalled();
  });

  it('falls back to the local recipe rules when the agent stays silent', async () => {
    mockStream.mockResolvedValue({ answered: false, error: '连不上聊天服务' });
    mockAsk.mockResolvedValue({
      recipes: [RECIPE],
      suggestions: ['今晚吃什么'],
      text: '给你挑了几道菜，看看有没有想吃的。',
    });
    const screen = await renderAi();

    await ask(screen, '随便来点');

    expect(
      await screen.findByText('给你挑了几道菜，看看有没有想吃的。'),
    ).toBeOnTheScreen();
    expect(mockAsk).toHaveBeenCalledWith('随便来点', expect.any(Array));
  });

  it('keeps the streamed reply but notes the interruption', async () => {
    mockStream.mockImplementation(async (_message, options) => {
      options?.onText?.('先说到这');

      return { answered: true, error: '聊天服务意外断开。' };
    });
    const screen = await renderAi();

    await ask(screen, '你好');

    expect(
      await screen.findByText('先说到这\n\n（聊天服务意外断开。）'),
    ).toBeOnTheScreen();
    expect(mockAsk).not.toHaveBeenCalled();
  });
});
