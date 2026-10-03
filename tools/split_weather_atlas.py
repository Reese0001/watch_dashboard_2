from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "design" / "v3" / "forecast-weather-atlas.png"
OUTPUT = ROOT / "src" / "common" / "images" / "weather"

NAMES = (
    "clear-day",
    "clear-night",
    "partly-cloudy-day",
    "partly-cloudy-night",
    "overcast",
    "fog",
    "light-rain",
    "heavy-rain",
    "thunderstorm",
    "hail",
    "light-snow",
    "heavy-snow",
    "sleet",
    "strong-wind",
    "dust-haze",
    "hot-weather",
)


def main() -> None:
    atlas = Image.open(SOURCE).convert("RGBA")
    width, height = atlas.size
    OUTPUT.mkdir(parents=True, exist_ok=True)

    for index, name in enumerate(NAMES):
        row, column = divmod(index, 4)
        left = round(column * width / 4)
        top = round(row * height / 4)
        right = round((column + 1) * width / 4)
        bottom = round((row + 1) * height / 4)
        tile = atlas.crop((left, top, right, bottom))

        alpha_box = tile.getchannel("A").getbbox()
        if alpha_box:
            tile = tile.crop(alpha_box)

        side = max(tile.size) + 24
        icon = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        icon.alpha_composite(tile, ((side - tile.width) // 2, (side - tile.height) // 2))
        icon.thumbnail((256, 256), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
        canvas.alpha_composite(icon, ((256 - icon.width) // 2, (256 - icon.height) // 2))
        canvas.save(OUTPUT / f"{name}.png", optimize=True)


if __name__ == "__main__":
    main()
