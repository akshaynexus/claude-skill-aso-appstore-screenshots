#!/usr/bin/env python3
"""
Mockup-based App Store Screenshot Composer v2.
Supports iPhone and Android mockups using the same screen bounds
and profile system as the scaffold flow.
"""

import argparse
import os
import platform
import subprocess

from PIL import Image, ImageDraw, ImageFont

SKILL_DIR = os.path.dirname(__file__)

MOCKUP_PROFILES = {
    "iphone-6.7": {
        "canvas": (1290, 2796),
        "mockup": os.path.join(SKILL_DIR, "assets", "iPhone_17_Mockup_5.png"),
        "screen": (44, 44, 1073, 2299, 136),
    },
    "iphone-6.5": {
        "canvas": (1242, 2688),
        "mockup": os.path.join(SKILL_DIR, "assets", "iPhone_17_Mockup_5.png"),
        "screen": (44, 44, 1073, 2299, 136),
    },
    "iphone-6.9": {
        "canvas": (1320, 2868),
        "mockup": os.path.join(SKILL_DIR, "assets", "iPhone_17_Mockup_5.png"),
        "screen": (44, 44, 1073, 2299, 136),
    },
    "android": {
        "canvas": (1080, 2400),
        "mockup": os.path.join(SKILL_DIR, "assets", "fixed-s24ultra-mockup.png"),
        "screen": (49, 43, 938, 2022, 37),
    },
}

# Typography
VERB_SIZE_MAX_RATIO = 0.18
VERB_SIZE_MIN_RATIO = 0.116
DESC_SIZE_RATIO = 0.09
TEXT_W_RATIO = 0.88
VERB_DESC_GAP = 16
DESC_LINE_GAP = 20
TEXT_TOP_RATIO = 0.08

# Font setup
_SYSTEM = platform.system()
if _SYSTEM == "Darwin":
    _FONT_DIRS = [
        "/System/Library/Fonts",
        "/Library/Fonts",
        os.path.expanduser("~/Library/Fonts"),
    ]
    _FONT_FALLBACKS_IOS = [
        "SF-Pro-Display-Black.otf",
        "SFCompact.ttf",
        "SFNS.ttf",
        "HelveticaNeue.ttc",
    ]
    _FONT_FALLBACKS_ANDROID = [
        "Roboto-Black.ttf",
        "Roboto-VariableFont_wdth,wght.ttf",
        "NotoSans-Black.ttf",
    ]
elif _SYSTEM == "Linux":
    _FONT_DIRS = [
        "/usr/share/fonts/truetype/noto",
        "/usr/share/fonts",
        os.path.expanduser("~/.local/share/fonts"),
    ]
    _FONT_FALLBACKS_IOS = ["NotoSans-Black.ttf", "NotoSans-Bold.ttf"]
    _FONT_FALLBACKS_ANDROID = ["Roboto-Black.ttf", "NotoSans-Black.ttf"]
else:
    _FONT_DIRS = [os.path.join(os.environ.get("WINDIR", r"C:\\Windows"), "Fonts")]
    _FONT_FALLBACKS_IOS = ["arialbd.ttf"]
    _FONT_FALLBACKS_ANDROID = ["arialbd.ttf"]


def _resolve_font(font_name, fallbacks=None):
    candidates = [font_name] + (fallbacks or [])
    for name in candidates:
        if os.path.isabs(name) and os.path.isfile(name):
            return name
        for d in _FONT_DIRS:
            c = os.path.join(d, name)
            if os.path.isfile(c):
                return c
        if _SYSTEM == "Linux":
            try:
                r = subprocess.run(
                    ["fc-match", "-f", "%{file}", name],
                    capture_output=True,
                    text=True,
                )
                if r.returncode == 0 and os.path.isfile(r.stdout.strip()):
                    return r.stdout.strip()
            except FileNotFoundError:
                pass
    raise FileNotFoundError(f"No font found. Tried: {candidates}")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def word_wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
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


def parse_hex_color(value):
    """Parse #RRGGBB-like colors, with '#' optional."""
    if not value:
        return None
    h = value.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError("Frame color must be #RRGGBB")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def color_shift_to_black(
    mockup, screen_x, screen_y, screen_w, screen_h, screen_r, frame_color_hex=None
):
    """Shift the frame color to a tinted target while preserving screen transparency."""
    mockup = mockup.convert("RGBA")
    pixels = mockup.load()
    w, h = mockup.size
    frame_rgb = parse_hex_color(frame_color_hex)
    screen_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_r,
        fill=255,
    )
    sm = screen_mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 50 or sm[x, y] > 0:
                continue
            brightness = (r + g + b) / 3
            if brightness > 10:
                if frame_rgb is None:
                    # Keep old deterministic behavior.
                    val = max(8, int(brightness * 0.04))
                    pixels[x, y] = (val, val, val, a)
                    continue
                # Keep the frame dark, but tint it toward the target frame color.
                intensity = 0.15 + min(0.85, brightness / 255.0 * 1.6)
                fr, fg, fb = frame_rgb
                pixels[x, y] = (
                    max(4, int(fr * intensity)),
                    max(4, int(fg * intensity)),
                    max(4, int(fb * intensity)),
                    a,
                )
    return mockup


def compose(
    bg_hex,
    verb,
    desc,
    screenshot_path,
    output_path,
    font=None,
    device="iphone-6.7",
    frame_color=None,
):
    profile = MOCKUP_PROFILES[device]
    canvas_w, canvas_h = profile["canvas"]
    mockup_path = profile["mockup"]
    screen_x, screen_y, screen_w, screen_h, screen_r = profile["screen"]

    mockup = Image.open(mockup_path).convert("RGBA")
    shot = Image.open(screenshot_path).convert("RGBA")

    # Make frame darker (or tinted) and keep screen area transparent.
    mockup = color_shift_to_black(
        mockup,
        screen_x,
        screen_y,
        screen_w,
        screen_h,
        screen_r,
        frame_color_hex=frame_color,
    )

    # Keep phone fill around 76% of canvas height and center on the canvas.
    target_h = int(canvas_h * 0.76)
    scale = target_h / mockup.size[1]
    new_w = int(mockup.size[0] * scale)
    new_h = int(mockup.size[1] * scale)
    mockup_scaled = mockup.resize((new_w, new_h), Image.LANCZOS)

    # Scaled screen region inside mockup.
    sx = int(screen_x * scale)
    sy = int(screen_y * scale)
    sw = int(screen_w * scale)
    sh = int(screen_h * scale)
    sr = int(screen_r * scale)

    cut_mask = Image.new("L", (new_w, new_h), 0)
    ImageDraw.Draw(cut_mask).rounded_rectangle(
        [sx, sy, sx + sw, sy + sh],
        radius=sr,
        fill=255,
    )
    mp = mockup_scaled.load()
    cm = cut_mask.load()
    for y in range(new_h):
        for x in range(new_w):
            if cm[x, y] > 0:
                r, g, b, a = mp[x, y]
                mp[x, y] = (r, g, b, 0)

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*hex_to_rgb(bg_hex), 255))

    # Screenshot placement with cover scale and cropped area exactly matching the screen.
    scale_s = max(sw / shot.width, sh / shot.height)
    shot_w = int(shot.width * scale_s)
    shot_h = int(shot.height * scale_s)
    shot_resized = shot.resize((shot_w, shot_h), Image.LANCZOS)
    crop_left = (shot_w - sw) // 2
    crop_top = (shot_h - sh) // 2
    shot_cropped = shot_resized.crop((crop_left, crop_top, crop_left + sw, crop_top + sh))

    mockup_x = (canvas_w - new_w) // 2
    mockup_y = int(canvas_h * 0.22)
    paste_x = mockup_x + sx
    paste_y = mockup_y + sy

    screen_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    screen_layer.paste(shot_cropped, (paste_x, paste_y))
    screen_mask = Image.new("L", (canvas_w, canvas_h), 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        [paste_x, paste_y, paste_x + sw, paste_y + sh],
        radius=sr,
        fill=255,
    )
    screen_layer.putalpha(screen_mask)
    canvas = Image.alpha_composite(canvas, screen_layer)

    # Place the bezel/mockup frame above the screenshot.
    mockup_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    mockup_layer.paste(mockup_scaled, (mockup_x, mockup_y))
    canvas = Image.alpha_composite(canvas, mockup_layer)

    # Text
    draw = ImageDraw.Draw(canvas)
    max_text_w = int(canvas_w * TEXT_W_RATIO)
    verb_size_max = int(canvas_w * VERB_SIZE_MAX_RATIO)
    verb_size_min = int(canvas_w * VERB_SIZE_MIN_RATIO)
    desc_size = int(canvas_w * DESC_SIZE_RATIO)

    if font:
        font_path = _resolve_font(font)
    elif device == "android":
        font_path = _resolve_font(_FONT_FALLBACKS_ANDROID[0], fallbacks=_FONT_FALLBACKS_ANDROID)
    else:
        font_path = _resolve_font(_FONT_FALLBACKS_IOS[0], fallbacks=_FONT_FALLBACKS_IOS)

    verb_font = fit_font(verb.upper(), max_text_w, verb_size_max, verb_size_min, font_path)
    desc_font = ImageFont.truetype(font_path, desc_size)

    text_top = int(canvas_h * TEXT_TOP_RATIO)
    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w, max_w=max_text_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, max_w=max_text_w)

    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}×{canvas_h}) [{device}]")


def main():
    p = argparse.ArgumentParser(description="Mockup-based store screenshot composer")
    p.add_argument("--bg", required=True)
    p.add_argument("--verb", required=True)
    p.add_argument("--desc", required=True)
    p.add_argument("--screenshot", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--font", default=None)
    p.add_argument(
        "--frame-color",
        default=None,
        help="Optional frame color in hex (e.g. #2f2f2f). Omit for default dark frame.",
    )
    p.add_argument(
        "--device",
        choices=list(MOCKUP_PROFILES.keys()),
        default="iphone-6.7",
        help="Device profile (iphone-6.7, iphone-6.5, iphone-6.9, android)",
    )
    args = p.parse_args()
    compose(
        args.bg,
        args.verb,
        args.desc,
        args.screenshot,
        args.output,
        font=args.font,
        device=args.device,
        frame_color=args.frame_color,
    )


if __name__ == "__main__":
    main()
