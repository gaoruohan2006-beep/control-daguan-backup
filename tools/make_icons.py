#!/usr/bin/env python3
"""从品牌标识（蓝底圆角方块 + 白字「控」）生成 PWA PNG 图标。"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
BLUE = (0, 107, 234, 255)
WHITE = (255, 255, 255, 255)
ROOT = Path(__file__).resolve().parents[1] / "public" / "icons"

def font_for(px):
    return ImageFont.truetype(FONT_PATH, px, index=2)  # Noto Sans CJK SC Bold

def draw_char(draw, cx, cy, font, fill=WHITE, char="控"):
    draw.text((cx, cy), char, font=font, fill=fill, anchor="mm")

def icon_any(size, path):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r = max(1, round(size * 7 / 32))
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=r, fill=BLUE)
    draw_char(draw, size / 2, size / 2, font_for(max(1, round(size * 17 / 32))))
    img.save(path, "PNG", optimize=True)

def icon_fullbleed(size, path, font_ratio=17 / 32):
    img = Image.new("RGBA", (size, size), BLUE)
    draw = ImageDraw.Draw(img)
    draw_char(draw, size / 2, size / 2, font_for(max(1, round(size * font_ratio))))
    img.save(path, "PNG", optimize=True)

def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    icon_any(192, ROOT / "icon-192.png")
    icon_any(512, ROOT / "icon-512.png")
    icon_any(32, ROOT / "favicon-32.png")
    # 安全区为直径 80% 的圆；字形放在约 60% 的中心区域内
    icon_fullbleed(512, ROOT / "icon-512-maskable.png", font_ratio=0.42)
    icon_fullbleed(180, ROOT / "apple-touch-icon.png", font_ratio=17 / 32)
    print("wrote", ROOT)

if __name__ == "__main__":
    main()
