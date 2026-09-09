import functools
import platform
from PIL import Image, ImageDraw, ImageFont

import config

@functools.lru_cache(maxsize=8)
def get_tray_font(size: int) -> ImageFont.ImageFont:
    """Load and cache a bold, high-legibility system font for the tray icon."""
    system = platform.system()
    candidates = []

    if system == "Darwin":
        candidates = [
            "/System/Library/Fonts/SFNS.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf",
        ]
    elif system == "Windows":
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",  # Segoe UI Bold (native Windows UI)
            "C:/Windows/Fonts/arialbd.ttf",   # Arial Bold
            "C:/Windows/Fonts/tahomabd.ttf",  # Tahoma Bold
        ]
    else:  # Linux / BSD
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]

    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue

    # Fallback to default pillow font if none found
    return ImageFont.load_default()

def create_tray_icon(wpm: float) -> Image.Image:
    """
    Generate a clean, high-contrast system tray icon displaying current WPM.
    Renders pure white anti-aliased text centered on a transparent canvas.
    """
    size = config.ICON_SIZE
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    text = str(int(round(wpm)))
    num_digits = len(text)

    # Dynamically select font size to maximize readability without clipping
    if num_digits <= 2:
        font_size = int(size * 0.68)   # ~22px on 32x32
    elif num_digits == 3:
        font_size = int(size * 0.52)   # ~16px on 32x32
    else:
        font_size = int(size * 0.40)   # ~13px for 4+ digits

    font = get_tray_font(font_size)

    # Draw centered text directly (crisp native look, no muddy outlines)
    center = size // 2
    draw.text(
        (center, center),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        anchor="mm"
    )

    return img

