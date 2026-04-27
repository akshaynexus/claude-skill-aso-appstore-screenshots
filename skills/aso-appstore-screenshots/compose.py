#!/usr/bin/env python3
"""
App Store / Google Play Screenshot Composer
Composites headline text, device frame template, and app screenshot
into a pixel-perfect store-ready image.

Supports multiple device profiles via --device flag:
  iphone-6.7  (default) — 1290×2796, App Store Connect
  iphone-6.5  — 1242×2688, App Store Connect
  iphone-6.9  — 1320×2868, App Store Connect
  android      — 1080×2400, Google Play Store
"""

import argparse
import os
import platform
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageChops

SKILL_DIR = os.path.dirname(__file__)

# ── Device profiles ─────────────────────────────────────────────────
# All layout values are derived from canvas size so each profile
# produces correctly proportioned output.
DEVICE_PROFILES = {
    "iphone-6.7": {
        "canvas": (1290, 2796),
        "device_w": 1030,
        "bezel": 15,
        "screen_corner_r": 62,
        "device_y": 720,
        "text_top": 200,
        "frame_file": "device_frame.png",
    },
    "iphone-6.5": {
        "canvas": (1242, 2688),
        "device_w": 994,
        "bezel": 15,
        "screen_corner_r": 60,
        "device_y": 692,
        "text_top": 192,
        "frame_file": "device_frame.png",
    },
    "iphone-6.9": {
        "canvas": (1320, 2868),
        "device_w": 1056,
        "bezel": 15,
        "screen_corner_r": 64,
        "device_y": 738,
        "text_top": 205,
        "frame_file": "device_frame.png",
    },
    "android": {
        "canvas": (1080, 2400),
        "device_w": 864,
        "bezel": 8,
        "screen_corner_r": 44,
        "device_y": 625,
        "text_top": 163,
        "frame_file": "device_frame_android.png",
    },
}

# ── Typography (proportional to canvas width) ───────────────────────
TEXT_W_RATIO = 0.92        # max text width as fraction of canvas
VERB_SIZE_MAX_RATIO = 0.198   # ~256/1290
VERB_SIZE_MIN_RATIO = 0.116   # ~150/1290
DESC_SIZE_RATIO = 0.096       # ~124/1290
VERB_DESC_GAP = 20
DESC_LINE_GAP = 24

# ── Cross-platform font resolution ─────────────────────────────────
_SYSTEM = platform.system()

if _SYSTEM == "Darwin":
    _FONT_DIRS = [
        "/System/Library/Fonts",
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ]
    # iOS: SF Pro Display Black → SFCompact → Helvetica Neue → Arial
    _FONT_FALLBACKS_IOS = [
        "SF-Pro-Display-Black.otf", "SFCompact.ttf", "SFNS.ttf",
        "HelveticaNeue.ttc", "Arial Unicode.ttf",
    ]
    # Android: Roboto Black → Noto Sans Black → Arial
    _FONT_FALLBACKS_ANDROID = [
        "Roboto-Black.ttf", "Roboto-VariableFont_wdth,wght.ttf",
        "NotoSans-Black.ttf", "Arial Unicode.ttf",
    ]
elif _SYSTEM == "Linux":
    _FONT_DIRS = [
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts/truetype",
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        os.path.expanduser("~/.local/share/fonts"),
    ]
    _FONT_FALLBACKS_IOS = ["NotoSans-Black.ttf", "NotoSans-Bold.ttf"]
    _FONT_FALLBACKS_ANDROID = ["Roboto-Black.ttf", "NotoSans-Black.ttf"]
else:  # Windows
    _FONT_DIRS = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")]
    _FONT_FALLBACKS_IOS = ["arialbd.ttf", "arial.ttf"]
    _FONT_FALLBACKS_ANDROID = ["arialbd.ttf", "arial.ttf"]

_DEFAULT_FONT_IOS = _FONT_FALLBACKS_IOS[0]
_DEFAULT_FONT_ANDROID = _FONT_FALLBACKS_ANDROID[0]
_DEFAULT_FONT = _DEFAULT_FONT_IOS


def _resolve_font(font_name, fallbacks=None):
    """Find a font file by name, searching platform-appropriate directories.

    Accepts either a bare filename (searched in platform font dirs) or a full
    absolute path. On Linux, falls back to ``fc-match`` if the file isn't
    found in the standard directories.

    If font_name is not found and fallbacks is provided, tries each fallback in order.
    """
    candidates = [font_name] + (fallbacks or [])
    for name in candidates:
        if os.path.isabs(name) and os.path.isfile(name):
            return name
        for d in _FONT_DIRS:
            candidate = os.path.join(d, name)
            if os.path.isfile(candidate):
                return candidate
        # Linux fallback: ask fontconfig
        if _SYSTEM == "Linux":
            try:
                result = subprocess.run(
                    ["fc-match", "-f", "%{file}", name],
                    capture_output=True, text=True,
                )
                if result.returncode == 0 and os.path.isfile(result.stdout.strip()):
                    return result.stdout.strip()
            except FileNotFoundError:
                pass
    raise FileNotFoundError(
        f"No font found. Tried: {', '.join(candidates)}. "
        f"Searched in: {', '.join(_FONT_DIRS)}. "
        f"Pass a full path with --font /path/to/font.ttf"
    )


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def word_wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, max_w, size_max, size_min, font_path):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        f = ImageFont.truetype(font_path, size)
        bbox = dummy.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_w:
            return f
    return ImageFont.truetype(font_path, size_min)


def draw_centered(draw, y, text, font, canvas_w, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((canvas_w // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + DESC_LINE_GAP
    return y


def _detect_screen_area(frame_path):
    """Detect the actual screen area (transparent region) from the frame template.
    
    Finds the bounding box of the transparent/semi-transparent area
    where the app screenshot should be placed.
    """
    frame = Image.open(frame_path).convert("RGBA")
    pixels = frame.load()
    w, h = frame.size
    
    # Find the bounds of the transparent area (alpha < 128)
    min_x, min_y, max_x, max_y = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 128:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    if max_x <= min_x or max_y <= min_y:
        return None
    
    return (min_x, min_y, max_x - min_x, max_y - min_y)


def compose(bg_hex, verb, desc, screenshot_path, output_path, device="iphone-6.7", font=None):
    profile = DEVICE_PROFILES[device]
    canvas_w, canvas_h = profile["canvas"]
    device_w = profile["device_w"]
    bezel = profile["bezel"]
    screen_w = device_w - 2 * bezel
    screen_corner_r = profile["screen_corner_r"]
    device_y = profile["device_y"]
    text_top = profile["text_top"]
    frame_path = os.path.join(SKILL_DIR, "assets", profile["frame_file"])

    # Compute typography sizes from canvas width
    max_text_w = int(canvas_w * TEXT_W_RATIO)
    max_verb_w = int(canvas_w * TEXT_W_RATIO)
    verb_size_max = int(canvas_w * VERB_SIZE_MAX_RATIO)
    verb_size_min = int(canvas_w * VERB_SIZE_MIN_RATIO)
    desc_size = int(canvas_w * DESC_SIZE_RATIO)

    # Pick platform-appropriate default font based on device profile
    if font:
        font_path = _resolve_font(font)
    elif device == "android":
        font_path = _resolve_font(_DEFAULT_FONT_ANDROID, fallbacks=_FONT_FALLBACKS_ANDROID)
    else:
        font_path = _resolve_font(_DEFAULT_FONT_IOS, fallbacks=_FONT_FALLBACKS_IOS)

    bg = hex_to_rgb(bg_hex)

    # ── 1. Canvas ───────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Text ─────────────────────────────────────────────────────
    verb_font = fit_font(verb.upper(), max_verb_w, verb_size_max, verb_size_min, font_path)
    desc_font = ImageFont.truetype(font_path, desc_size)

    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, max_w=max_text_w)

    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    # ── 3. Screenshot into screen area ──────────────────────────────
    # Auto-detect the actual screen area from the frame template
    detected_screen = _detect_screen_area(frame_path)
    if detected_screen:
        # Use detected area offset from frame, accounting for device position
        frame_screen_x, frame_screen_y, frame_screen_w, frame_screen_h = detected_screen
        actual_screen_x = device_x + frame_screen_x
        actual_screen_y = device_y + frame_screen_y
        actual_screen_w = frame_screen_w
        actual_screen_h = frame_screen_h
    else:
        # Fallback to calculated values
        actual_screen_x = screen_x
        actual_screen_y = screen_y
        actual_screen_w = screen_w
        actual_screen_h = canvas_h - screen_y

    shot = Image.open(screenshot_path).convert("RGBA")
    
    # Scale to FILL the screen area (cover mode, like CSS background-size: cover)
    # Use the larger scale factor so no black gaps appear
    scale_w = actual_screen_w / shot.width
    scale_h = actual_screen_h / shot.height
    scale = max(scale_w, scale_h)
    sc_w = int(shot.width * scale)
    sc_h = int(shot.height * scale)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)
    
    # Center the screenshot within the screen area if it overflows
    paste_x = actual_screen_x + (actual_screen_w - sc_w) // 2
    paste_y = actual_screen_y + (actual_screen_h - sc_h) // 2

    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [actual_screen_x, actual_screen_y, actual_screen_x + actual_screen_w, actual_screen_y + actual_screen_h],
        radius=screen_corner_r,
        fill=255,
    )

    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [actual_screen_x, actual_screen_y, actual_screen_x + actual_screen_w, actual_screen_y + actual_screen_h],
        radius=screen_corner_r,
        fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (paste_x, paste_y))
    scr_layer.putalpha(scr_mask)
    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 4. Device frame template ───────────────────────────────────
    frame_template = Image.open(frame_path).convert("RGBA")

    # Scale frame if device_w differs from template width
    if frame_template.width != device_w:
        scale_f = device_w / frame_template.width
        frame_template = frame_template.resize(
            (device_w, int(frame_template.height * scale_f)), Image.LANCZOS
        )

    frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    frame_layer.paste(frame_template, (device_x, device_y))
    canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 5. Save ────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}×{canvas_h}) [{device}]")


def main():
    p = argparse.ArgumentParser(description="Compose store screenshot")
    p.add_argument("--bg", required=True, help="Background hex colour (#E31837)")
    p.add_argument("--verb", required=True, help="Action verb (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (TRADING CARD PRICES)")
    p.add_argument("--screenshot", required=True, help="Simulator/emulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument("--font", default=None,
                   help="Font filename or full path. Auto-detected per platform: "
                        "SF Pro Display Black (macOS), Noto Sans Black (Linux), "
                        "Arial Bold (Windows)")
    p.add_argument(
        "--device",
        choices=list(DEVICE_PROFILES.keys()),
        default="iphone-6.7",
        help="Device profile (default: iphone-6.7)",
    )
    args = p.parse_args()

    compose(args.bg, args.verb, args.desc, args.screenshot, args.output,
            device=args.device, font=args.font)


if __name__ == "__main__":
    main()
