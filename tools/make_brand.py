"""Draw the JK BMS Smart icon (original artwork: a prismatic battery pack with a lightning bolt)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "jk_bms_smart"


def draw(size: int) -> Image.Image:
    s = size / 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(56 * s), fill=(20, 24, 30, 255))
    # pack tray
    d.rounded_rectangle([int(28 * s), int(70 * s), int(228 * s), int(214 * s)], radius=int(18 * s), fill=(28, 33, 41, 255),
                        outline=(42, 48, 58, 255), width=max(1, int(3 * s)))
    # 4 prismatic cells with fill levels
    levels = [0.86, 0.9, 0.82, 0.88]
    for i, lv in enumerate(levels):
        x0 = int((44 + i * 44) * s)
        x1 = int((80 + i * 44) * s)
        y0, y1 = int(92 * s), int(198 * s)
        d.rounded_rectangle([x0, y0, x1, y1], radius=int(7 * s), fill=(58, 67, 80, 255))
        top = int(y1 - (y1 - y0 - 10 * s) * lv)
        d.rounded_rectangle([x0 + int(4 * s), top, x1 - int(4 * s), y1 - int(4 * s)], radius=int(5 * s), fill=(69, 214, 154, 255))
        # terminals
        d.rounded_rectangle([x0 + int(4 * s), int(80 * s), x0 + int(14 * s), int(92 * s)], radius=int(2 * s), fill=(201, 162, 74, 255))
        d.rounded_rectangle([x1 - int(14 * s), int(80 * s), x1 - int(4 * s), int(92 * s)], radius=int(2 * s), fill=(154, 163, 175, 255))
    # busbars
    for i in range(3):
        xa = int((76 + i * 44) * s)
        d.rounded_rectangle([xa - int(6 * s), int(80 * s), xa + int(30 * s), int(88 * s)], radius=int(3 * s), fill=(201, 162, 74, 255))
    # bolt
    bolt = [(148, 22), (104, 64), (128, 64), (110, 100), (156, 54), (130, 54), (148, 22)]
    d.polygon([(int(x * s), int(y * s)) for x, y in bolt], fill=(90, 169, 255, 255))
    return img


def main() -> None:
    brand = ROOT / "brand"
    brand.mkdir(exist_ok=True)
    for name, size in (("icon.png", 256), ("icon@2x.png", 512), ("logo.png", 256), ("logo@2x.png", 512),
                       ("dark_icon.png", 256), ("dark_icon@2x.png", 512), ("dark_logo.png", 256), ("dark_logo@2x.png", 512)):
        draw(size).save(brand / name, optimize=True)
    draw(128).save(ROOT / "frontend" / "logo.png", optimize=True)


if __name__ == "__main__":
    main()
