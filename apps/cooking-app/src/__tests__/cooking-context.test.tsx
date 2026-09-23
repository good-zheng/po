import { act, renderHook } from '@testing-library/react-native';
import type { ReactNode } from 'react';

import { CookingProvider, useCooking } from '@/lib/cooking/cooking-context';

function wrapper({ children }: { children: ReactNode }) {
  return <CookingProvider>{children}</CookingProvider>;
}

const dish = { id: 7, title: '剁椒鱼头' };

// RNTL v14 起 renderHook 与 act 都是异步的，必须先 await 再断言
async function setup() {
  return renderHook(() => useCooking(), { wrapper });
}

describe('useCooking', () => {
  it('starts a session at the first step', async () => {
    const { result } = await setup();

    await act(async () => result.current.beginCooking(dish, 3));

    expect(result.current.session).toMatchObject({
      recipeId: 7,
      stepCount: 3,
      stepIndex: 0,
      title: '剁椒鱼头',
    });
  });

  it('resumes the same dish but restarts a different one', async () => {
    const { result } = await setup();

    await act(async () => result.current.beginCooking(dish, 3));
    await act(async () => result.current.goToStep(1));
    await act(async () => result.current.beginCooking(dish, 3));

    expect(result.current.session?.stepIndex).toBe(1);

    await act(async () =>
      result.current.beginCooking({ id: 8, title: '辣椒炒肉' }, 3),
    );

    expect(result.current.session).toMatchObject({ recipeId: 8, stepIndex: 0 });
  });

  it('restarts on demand', async () => {
    const { result } = await setup();

    await act(async () => result.current.beginCooking(dish, 3));
    await act(async () => result.current.goToStep(2));
    await act(async () =>
      result.current.beginCooking(dish, 3, { restart: true }),
    );

    expect(result.current.session?.stepIndex).toBe(0);
  });

  it('clamps step navigation', async () => {
    const { result } = await setup();

    await act(async () => result.current.beginCooking(dish, 3));

    await act(async () => result.current.goToStep(9));
    expect(result.current.session?.stepIndex).toBe(2);

    await act(async () => result.current.goToStep(-4));
    expect(result.current.session?.stepIndex).toBe(0);
  });

  it('moves a finished session into a note', async () => {
    const { result } = await setup();

    await act(async () => result.current.beginCooking(dish, 4));
    await act(async () => result.current.goToStep(3));
    await act(async () => result.current.finishCooking());

    expect(result.current.session).toBeNull();
    expect(result.current.note).toMatchObject({
      recipeId: 7,
      stepCount: 4,
      title: '剁椒鱼头',
    });

    await act(async () => result.current.clearNote());
    expect(result.current.note).toBeNull();
  });

  it('drops a cancelled session without a note', async () => {
    const { result } = await setup();

    await act(async () => result.current.beginCooking(dish, 3));
    await act(async () => result.current.cancelCooking());

    expect(result.current.session).toBeNull();
    expect(result.current.note).toBeNull();
  });
});
