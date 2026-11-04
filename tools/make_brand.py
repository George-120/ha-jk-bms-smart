"""Build the JK BMS Smart icon: a photo of the BMS on the Easee Smart dark background.

Usage: python3 tools/make_brand.py path/to/bms-photo.png
The photo's light background is removed by flood-filling from the edges.
"""

from __future__ import annotations

import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "jk_bms_smart"
BG = (20, 24, 30, 255)  # same as Easee Smart Charging (#14181E)


def cut_out(photo: Image.Image, tol: int = 28) -> Image.Image:
    img = photo.convert("RGBA")
    w, h = img.size
    px = img.load()
    seen = bytearray(w * h)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        q.extend([(x, 0), (x, h - 1)])
    for y in range(h):
        q.extend([(0, y), (w - 1, y)])

    def light(p: tuple[int, int, int, int]) -> bool:
        r, g, b, _ = p
        return min(r, g, b) >= 255 - tol and max(r, g, b) - min(r, g, b) < 18

    while q:
        x, y = q.popleft()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        if not light(px[x, y]):
            continue
        px[x, y] = (0, 0, 0, 0)
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny * w + nx]:
                q.append((nx, ny))
    # soften the cut edge a little
    alpha = img.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    img.putalpha(alpha)
    return img.crop(img.getbbox())


def icon(cut: Image.Image, size: int) -> Image.Image:
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=255)
    bg = Image.new("RGBA", (size, size), BG)
    out.paste(bg, (0, 0), mask)
    box = int(size * 0.84)
    scale = min(box / cut.width, box / cut.height)
    part = cut.resize((max(1, int(cut.width * scale)), max(1, int(cut.height * scale))), Image.LANCZOS)
    x = (size - part.width) // 2
    y = (size - part.height) // 2
    shadow = Image.new("RGBA", part.size, (0, 0, 0, 160))
    shadow.putalpha(part.getchannel("A").point(lambda a: int(a * 0.55)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(size / 60))
    out.alpha_composite(shadow, (x, y + max(1, size // 64)))
    out.alpha_composite(part, (x, y))
    return out


def main() -> None:
    cut = cut_out(Image.open(sys.argv[1]))
    brand = ROOT / "brand"
    brand.mkdir(exist_ok=True)
    for name, size in (("icon.png", 256), ("icon@2x.png", 512), ("logo.png", 256), ("logo@2x.png", 512),
                       ("dark_icon.png", 256), ("dark_icon@2x.png", 512), ("dark_logo.png", 256), ("dark_logo@2x.png", 512)):
        icon(cut, size).save(brand / name, optimize=True)
    icon(cut, 128).save(ROOT / "frontend" / "logo.png", optimize=True)


if __name__ == "__main__":
    main()
