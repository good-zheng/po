"""合成做菜提示音：厨房上菜铃三连「叮」+ 锅气滋滋底噪。

输出 apps/cooking-app/assets/sounds/step-done.wav（44.1kHz / 16bit / 单声道）。
计时结束进入下一步前播放，改参数重跑即可调音色。
"""
import io
import math
import os
import random
import struct
import sys
import wave

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'apps',
    'cooking-app',
    'assets',
    'sounds',
    'step-done.wav',
)

SR = 44100
DUR = 2.0
# 三次敲击的时刻（秒），间隔 0.26s 读作一声「钉钉钉」
STRIKES = (0.0, 0.26, 0.52)
BELL_F0 = 1046.5  # C6：小喇叭形上菜铃的基音，手机小喇叭也听得清
# 分音：(频率比, 增益, 衰减时间常数秒)；高次分音衰减快，才有金属余音
PARTIALS = (
    (1.00, 1.00, 0.80),
    (2.00, 0.45, 0.58),
    (3.01, 0.22, 0.40),
    (4.16, 0.12, 0.27),
    (5.43, 0.07, 0.19),
    (6.79, 0.04, 0.13),
)
BELL_GAIN = 0.50
# 锅气：连续底噪 + 油爆两层，都先合成成宽带信号再一起过 1.2k-7.5k 带通，
# 音色才统一；具体倍数由 tools 里的响度测量调到「比铃低十几个 dB、听得见不抢戏」
SIZZLE_GAIN = 0.70
SIZZLE_TAU = 0.55  # 底噪衰减，比最后一击略长一点，声音才落回锅里的感觉
POP_RATE_EARLY = 6.0  # 敲铃期间只零星几下，不抢三声「叮」的清晰度
POP_RATE_LATE = 26.0  # 最后一击落下后油爆密起来，读作「叮叮叮 + 滋啦」
POP_RAMP = 0.62  # 油爆密度切换时刻（秒），紧跟在最后一击之后
POP_GAIN = 1.70
POP_WINDOW = 1.30  # 油爆只在前段，之后干净收尾
POP_TAIL = 0.004  # 单次油爆的长度（秒）
POP_DECAY = 0.0009
PEAK_TARGET = 0.85  # 归一化目标，留 ~1.4dB 余量

rng = random.Random(20260923)


def add_strike(buf, t0):
    start = int(t0 * SR)
    length = min(int(1.6 * SR), len(buf) - start)
    for i in range(length):
        t = i / SR
        # 敲击起音 0.4ms，避免爆音
        attack = 1.0 - math.exp(-t / 0.0004)
        s = 0.0
        for ratio, gain, decay in PARTIALS:
            s += gain * math.exp(-t / decay) * math.sin(2 * math.pi * BELL_F0 * ratio * t)
        buf[start + i] += BELL_GAIN * attack * s
    # 槌子敲在金属上的瞬态
    for i in range(int(0.004 * SR)):
        if start + i >= len(buf):
            break
        t = i / SR
        buf[start + i] += 0.05 * math.exp(-t / 0.0012) * rng.uniform(-1, 1)


def add_sizzle(buf):
    """锅气：1.2k-7.5k 带通噪声 + 零星油爆，像热锅里还在煎着东西。

    底噪和油爆先合成一条宽带激励，再一起过带通，两者音色才同源。
    """
    a_hi = 1 - math.exp(-2 * math.pi * 7500 / SR)
    a_lo = 1 - math.exp(-2 * math.pi * 1200 / SR)

    drive = [0.0] * len(buf)
    for i in range(len(buf)):
        t = i / SR
        env = SIZZLE_GAIN * (1 - math.exp(-t / 0.03)) * math.exp(-t / SIZZLE_TAU)
        drive[i] = env * rng.uniform(-1, 1)

    t_pop = 0.05
    while t_pop < POP_WINDOW:
        idx = int(t_pop * SR)
        amp = POP_GAIN * rng.uniform(0.55, 1.0)
        for i in range(int(POP_TAIL * SR)):
            if idx + i >= len(buf):
                break
            drive[idx + i] += amp * math.exp(-i / SR / POP_DECAY) * rng.uniform(-1, 1)
        rate = POP_RATE_EARLY if t_pop < POP_RAMP else POP_RATE_LATE
        t_pop += -math.log(1 - rng.random()) / rate

    lp_hi = 0.0
    lp_lo = 0.0
    for i, x in enumerate(drive):
        lp_hi += a_hi * (x - lp_hi)
        lp_lo += a_lo * (x - lp_lo)
        buf[i] += lp_hi - lp_lo


def write_wav(path, buf):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(
            struct.pack('<h', int(round(max(-1.0, min(1.0, v)) * 32767))) for v in buf
        ))


def goertzel(buf, freq, start, length):
    """单频点能量，用于自检分音是否落在预期频率上。"""
    w = 2 * math.pi * freq / SR
    coeff = 2 * math.cos(w)
    s0 = s1 = s2 = 0.0
    for i in range(start, min(start + length, len(buf))):
        s0 = buf[i] + coeff * s1 - s2
        s2 = s1
        s1 = s0
    return math.sqrt(max(s1 * s1 + s2 * s2 - coeff * s1 * s2, 0.0))


def main():
    n = int(SR * DUR)
    buf = [0.0] * n

    for t0 in STRIKES:
        add_strike(buf, t0)
    add_sizzle(buf)

    # 尾部 0.4s 淡出，避免截断声
    fade = int(0.4 * SR)
    for i in range(fade):
        buf[n - fade + i] *= 0.5 * (1 + math.cos(math.pi * i / fade))

    peak = max(abs(v) for v in buf)
    scale = PEAK_TARGET / peak if peak > 0 else 1.0
    buf = [max(-1.0, min(1.0, v * scale)) for v in buf]

    write_wav(OUT, buf)

    rms = math.sqrt(sum(v * v for v in buf) / len(buf))
    print(f'wrote {OUT}')
    print(f'duration {DUR:.2f}s  peak {20 * math.log10(PEAK_TARGET):.1f} dBFS  '
          f'rms {20 * math.log10(rms):.1f} dBFS')
    win = int(0.25 * SR)
    for ratio, gain, _ in PARTIALS[:3]:
        e = goertzel(buf, BELL_F0 * ratio, 0, win)
        print(f'  partial x{ratio:>4}: energy {e:8.1f}')

    # 包络剖面：三声之间要能回落，才读作「钉钉钉」而不是一声长鸣
    step = int(0.04 * SR)
    env = [max(abs(v) for v in buf[i:i + step]) for i in range(0, int(1.0 * SR), step)]
    print('  envelope(40ms) 0-1.0s: ' + ' '.join(f'{v:.2f}' for v in env))
    tail = [max(abs(v) for v in buf[i:i + step])
            for i in range(int(1.2 * SR), len(buf) - step, step)]
    print(f'  tail(1.2s+) max {max(tail):.3f}')


if __name__ == '__main__':
    main()
