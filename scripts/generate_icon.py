"""Dev-only helper: (re)generates the placeholder Iqama tray/app icon.

Not part of the packaged app or its runtime dependencies -- run this
manually with Pillow installed whenever the placeholder needs
regenerating:

    python scripts/generate_icon.py

To swap in a real icon later, just replace resources/icon.ico (and
resources/icon.png, used by the tray icon at runtime) with your own
artwork at the same sizes -- nothing else in the app needs to change.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"
BACKGROUND = (18, 58, 82, 255)  # deep navy/teal
FOREGROUND = (245, 245, 240, 255)  # warm off-white


def draw_icon(size: int) -> Image.Image:
    scale = 4  # supersample then downscale for smoother edges at small sizes
    canvas_size = size * scale
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    padding = canvas_size * 0.06
    draw.ellipse(
        [padding, padding, canvas_size - padding, canvas_size - padding],
        fill=BACKGROUND,
    )

    # Crescent: a foreground circle with a background circle cut out of it.
    moon_radius = canvas_size * 0.32
    moon_cx, moon_cy = canvas_size * 0.46, canvas_size * 0.50
    draw.ellipse(
        [moon_cx - moon_radius, moon_cy - moon_radius,
         moon_cx + moon_radius, moon_cy + moon_radius],
        fill=FOREGROUND,
    )
    cut_radius = moon_radius * 0.82
    cut_cx = moon_cx + moon_radius * 0.55
    cut_cy = moon_cy - moon_radius * 0.12
    draw.ellipse(
        [cut_cx - cut_radius, cut_cy - cut_radius,
         cut_cx + cut_radius, cut_cy + cut_radius],
        fill=BACKGROUND,
    )

    # A small 5-point star near the crescent's upper tip.
    star_cx, star_cy = canvas_size * 0.70, canvas_size * 0.32
    star_r = canvas_size * 0.075
    draw.polygon(_star_points(star_cx, star_cy, star_r), fill=FOREGROUND)

    return img.resize((size, size), Image.LANCZOS)


def _star_points(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    import math

    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        radius = r if i % 2 == 0 else r * 0.42
        points.append((cx + radius * math.cos(angle), cy - radius * math.sin(angle)))
    return points


def main() -> None:
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

    png_image = draw_icon(256)
    png_path = RESOURCES_DIR / "icon.png"
    png_image.save(png_path)

    ico_path = RESOURCES_DIR / "icon.ico"
    png_image.save(
        ico_path,
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )

    print(f"Wrote {png_path}")
    print(f"Wrote {ico_path}")


if __name__ == "__main__":
    main()
