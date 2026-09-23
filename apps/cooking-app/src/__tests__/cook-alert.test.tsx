import { act, renderHook } from '@testing-library/react-native';
import { Vibration } from 'react-native';

import { useCookAlert } from '@/lib/cooking/use-cook-alert';

const mockPlay = jest.fn();
const mockPause = jest.fn();
const mockSeekTo = jest.fn(async () => {});
const mockSetAudioModeAsync = jest.fn(async (_mode: unknown) => {});
const mockPlayer = {
  loop: false,
  pause: mockPause,
  play: mockPlay,
  seekTo: mockSeekTo,
};

jest.mock('expo-audio', () => ({
  setAudioModeAsync: (mode: unknown) => mockSetAudioModeAsync(mode),
  useAudioPlayer: () => mockPlayer,
}));

describe('useCookAlert', () => {
  beforeEach(() => {
    jest.useFakeTimers();
    mockPlayer.loop = false;
    mockPlay.mockClear();
    mockPause.mockClear();
    mockSeekTo.mockClear();
    mockSetAudioModeAsync.mockClear();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('replays the alert from the start and buzzes', async () => {
    const vibrate = jest
      .spyOn(Vibration, 'vibrate')
      .mockImplementation(() => {});

    const { result } = await renderHook(() => useCookAlert());
    await act(async () => result.current.play());

    expect(mockSeekTo).toHaveBeenCalledWith(0);
    expect(mockPlay).toHaveBeenCalledTimes(1);
    expect(vibrate).toHaveBeenCalledWith(400);

    vibrate.mockRestore();
  });

  it('plays even when the phone is on silent', async () => {
    await renderHook(() => useCookAlert());

    expect(mockSetAudioModeAsync).toHaveBeenCalledWith({
      interruptionMode: 'duckOthers',
      playsInSilentMode: true,
    });
  });

  it('keeps ringing for 30 seconds when nobody reacts', async () => {
    const { result } = await renderHook(() => useCookAlert());
    await act(async () => result.current.play());

    expect(result.current.ringing).toBe(true);
    expect(mockPlayer.loop).toBe(true);

    await act(async () => {
      jest.advanceTimersByTime(29_000);
    });
    expect(mockPause).not.toHaveBeenCalled();

    await act(async () => {
      jest.advanceTimersByTime(1_000);
    });
    expect(result.current.ringing).toBe(false);
    expect(mockPlayer.loop).toBe(false);
    expect(mockPause).toHaveBeenCalledTimes(1);
  });

  it('stops right away when the user acts', async () => {
    const { result } = await renderHook(() => useCookAlert());
    await act(async () => result.current.play());

    await act(async () => result.current.stop());

    expect(result.current.ringing).toBe(false);
    expect(mockPause).toHaveBeenCalledTimes(1);
    expect(mockPlayer.loop).toBe(false);

    // 已经手动停过，30 秒到点不该再补一次
    await act(async () => {
      jest.advanceTimersByTime(30_000);
    });
    expect(mockPause).toHaveBeenCalledTimes(1);
  });

  it('forgets the timer once the screen is gone', async () => {
    const { result, unmount } = await renderHook(() => useCookAlert());
    await act(async () => result.current.play());

    await unmount();
    mockPause.mockClear();

    // 组件卸载后 expo-audio 会释放播放器，定时器不能再去碰它
    await act(async () => {
      jest.advanceTimersByTime(30_000);
    });
    expect(mockPause).not.toHaveBeenCalled();
  });
});
