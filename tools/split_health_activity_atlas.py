from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "design" / "v2" / "health-activity-icon-atlas.png"
OUTPUT = ROOT / "src" / "common" / "images" / "metrics"

NAMES = (
    "heart",
    "oxygen",
    "respiration",
    "temperature",
    "hrv",
    "blood-pressure",
    "sleep",
    "stress",
    "steps",
    "distance",
    "calories",
    "active-minutes",
    "stand",
    "elevation",
    "battery",
    "activity-rings",
)


def main() -> None:
    atlas = Image.open(SOURCE).convert("RGB")
    width, height = atlas.size
    OUTPUT.mkdir(parents=True, exist_ok=True)

    for index, name in enumerate(NAMES):
        row, column = divmod(index, 4)
        left = round(column * width / 4)
        top = round(row * height / 4)
        right = round((column + 1) * width / 4)
        bottom = round((row + 1) * height / 4)
        tile = atlas.crop((left, top, right, bottom))

        inset_x = round(tile.width * 0.15)
        inset_y = round(tile.height * 0.15)
        tile = tile.crop((inset_x, inset_y, tile.width - inset_x, tile.height - inset_y))
        tile.thumbnail((256, 256), Image.Resampling.LANCZOS)

        rgba = tile.convert("RGBA")
        pixels = []
        for red, green, blue, _ in rgba.getdata():
            peak = max(red, green, blue)
            alpha = 0 if peak < 18 else min(255, (peak - 18) * 3)
            pixels.append((red, green, blue, alpha))
        rgba.putdata(pixels)

        canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        canvas.alpha_composite(rgba, ((256 - rgba.width) // 2, (256 - rgba.height) // 2))
        canvas.save(OUTPUT / f"{name}.png", optimize=True)


if __name__ == "__main__":
    main()
