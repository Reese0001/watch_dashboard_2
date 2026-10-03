from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "src" / "common" / "images" / "compass" / "dial-scale.png"


def main() -> None:
    size = 720
    center = size / 2
    outer = 336
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    for index in range(120):
        angle = (index * 3 - 90) * pi / 180
        major = index % 10 == 0
        cardinal = index % 30 == 0
        length = 34 if cardinal else 24 if major else 14
        width = 7 if cardinal else 4 if major else 2
        color = (245, 247, 250, 255) if major else (170, 176, 185, 220)
        x1 = center + cos(angle) * outer
        y1 = center + sin(angle) * outer
        x2 = center + cos(angle) * (outer - length)
        y2 = center + sin(angle) * (outer - length)
        draw.line((x1, y1, x2, y2), fill=color, width=width)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.resize((360, 360), Image.Resampling.LANCZOS).save(OUTPUT, optimize=True)


if __name__ == "__main__":
    main()
