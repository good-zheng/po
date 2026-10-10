"""生成言外（apps/echo-talk）小程序底部 tab 图标。

尺寸与叮叮厨一致：81x81 RGBA PNG，4x 超采样后 LANCZOS 缩回，边缘才不带锯齿。
形状只画一次（画在 alpha 蒙版上），换色就是换前景色，所以 normal / active 一定是同一个形状。

    py -3 tools/tab-icons.py
"""

import os

from PIL import Image, ImageDraw

SS = 4  # 超采样倍数
SIZE = 81
OUT_DIR = os.path.join("apps", "echo-talk", "src", "assets", "icons")

# 与 src/app.config.ts 的 tabBar.color / selectedColor 保持一致
NORMAL = (154, 154, 162)  # 9a9aa2
ACTIVE = (59, 91, 219)  # 3b5bdb
STROKE = 6 * SS


def canvas():
    mask = Image.new("L", (SIZE * SS, SIZE * SS), 0)
    return mask, ImageDraw.Draw(mask)


def bubble():
    """会话：气泡轮廓 + 一句实线（说出口的话）和一句虚线（没说出口的那句）"""
    mask, d = canvas()
    d.rounded_rectangle([8 * SS, 8 * SS, 73 * SS, 56 * SS], radius=14 * SS, outline=255, width=STROKE)
    # 尾巴：贴着气泡左下、指向左下的实心三角
    d.polygon(
        [(22 * SS, 50 * SS), (22 * SS, 74 * SS), (44 * SS, 56 * SS)],
        fill=255,
    )
    # 气泡内两条文案线
    d.rounded_rectangle([24 * SS, 24 * SS, 57 * SS, 30 * SS], radius=3 * SS, fill=255)
    d.rounded_rectangle([24 * SS, 37 * SS, 37 * SS, 43 * SS], radius=3 * SS, fill=255)
    d.rounded_rectangle([44 * SS, 37 * SS, 57 * SS, 43 * SS], radius=3 * SS, fill=255)
    return mask


def person():
    """我的：头环 + 肩线（描边风格，和气泡同粗细）"""
    mask, d = canvas()
    d.ellipse([28 * SS, 8 * SS, 53 * SS, 33 * SS], outline=255, width=STROKE)
    # 肩线取圆的上半弧：bbox 超出画布，落进画布的正是肩宽那段
    d.arc([9 * SS, 41 * SS, 72 * SS, 104 * SS], start=180, end=360, fill=255, width=STROKE)
    return mask


def render(mask, color):
    icon = Image.new("RGBA", mask.size, color + (0,))
    icon.putalpha(mask)
    return icon.resize((SIZE, SIZE), Image.LANCZOS)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shapes = {"tab-session": bubble(), "tab-mine": person()}
    for name, mask in shapes.items():
        for suffix, color in (("", NORMAL), ("-active", ACTIVE)):
            path = os.path.join(OUT_DIR, f"{name}{suffix}.png")
            render(mask, color).save(path)
            print("wrote", path, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
