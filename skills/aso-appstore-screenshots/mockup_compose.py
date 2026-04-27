#!/usr/bin/env python3
"""
Mockup-based App Store Screenshot Composer v2.
- Converts orange/copper frame to black
- Fits entire phone in canvas (no bottom crop)
- Proper screen compositing with rounded corners
"""

import argparse
import os
import platform
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SKILL_DIR = os.path.dirname(__file__)
MOCKUP_PATH = os.path.join(SKILL_DIR, "assets", "iPhone_17_Mockup_5.png")

CANVAS_W, CANVAS_H = 1290, 2796

# Exact screen area in the native mockup (1161x2387) — measured by Gemini
SCREEN_X, SCREEN_Y = 44, 44
SCREEN_W, SCREEN_H = 1073, 2299
SCREEN_CORNER_R = 136

# Dynamic Island
ISLAND_X, ISLAND_Y = 428, 75
ISLAND_W, ISLAND_H = 304, 84
ISLAND_R = 42

# Typography
VERB_SIZE_MAX_RATIO = 0.18
VERB_SIZE_MIN_RATIO = 0.116
DESC_SIZE_RATIO = 0.09
TEXT_W_RATIO = 0.88
VERB_DESC_GAP = 16
DESC_LINE_GAP = 20

# Font setup
_SYSTEM = platform.system()
if _SYSTEM == "Darwin":
    _FONT_DIRS = ["/System/Library/Fonts", "/Library/Fonts", os.path.expanduser("~/Library/Fonts")]
    _FONT_FALLBACKS = ["SF-Pro-Display-Black.otf", "SFCompact.ttf", "SFNS.ttf", "HelveticaNeue.ttc"]
elif _SYSTEM == "Linux":
    _FONT_DIRS = ["/usr/share/fonts/truetype/noto", "/usr/share/fonts", os.path.expanduser("~/.local/share/fonts")]
    _FONT_FALLBACKS = ["NotoSans-Black.ttf", "NotoSans-Bold.ttf"]
else:
    _FONT_DIRS = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")]
    _FONT_FALLBACKS = ["arialbd.ttf"]


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
                r = subprocess.run(["fc-match", "-f", "%{file}", name], capture_output=True, text=True)
                if r.returncode == 0 and os.path.isfile(r.stdout.strip()):
                    return r.stdout.strip()
            except FileNotFoundError:
                pass
    raise FileNotFoundError(f"No font found. Tried: {candidates}")


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def word_wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
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


def color_shift_to_black(mockup):
    """Shift the orange/copper frame to pure black/dark gray.
    
    Aggressively darkens frame pixels while preserving screen area.
    """
    mockup = mockup.convert("RGBA")
    pixels = mockup.load()
    w, h = mockup.size

    # Screen area mask
    screen_mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        [SCREEN_X, SCREEN_Y, SCREEN_X + SCREEN_W, SCREEN_Y + SCREEN_H],
        radius=SCREEN_CORNER_R, fill=255
    )
    sm = screen_mask.load()

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 50:
                continue
            if sm[x, y] > 0:
                continue
            # Frame pixel — force to near-black
            brightness = (r + g + b) / 3
            if brightness > 10:
                # Set to very dark gray (12,12,12) to preserve some edge detail
                val = max(8, int(brightness * 0.04))
                pixels[x, y] = (val, val, val, a)

    return mockup


def compose(bg_hex, verb, desc, screenshot_path, output_path, font=None):
    mockup = Image.open(MOCKUP_PATH).convert("RGBA")
    shot = Image.open(screenshot_path).convert("RGBA")

    # ── 1. Color-shift frame from orange to black ────────────────────
    mockup = color_shift_to_black(mockup)

    # ── 2. Scale mockup so phone is 20% smaller ────────────────────────
    # Phone needs ~62% of canvas height (20% smaller than original 78%)
    # Then scaled down an additional 17% for proper sizing: 78% * 0.83 * 1.17 = 75.7% ≈ 76%
    target_h = int(CANVAS_H * 0.76)
    scale = target_h / mockup.size[1]
    new_w = int(mockup.size[0] * scale)
    new_h = int(mockup.size[1] * scale)
    mockup_scaled = mockup.resize((new_w, new_h), Image.LANCZOS)

    # Scaled screen area
    sx = int(SCREEN_X * scale)
    sy = int(SCREEN_Y * scale)
    sw = int(SCREEN_W * scale)
    sh = int(SCREEN_H * scale)
    sr = int(SCREEN_CORNER_R * scale)

    # ── 3. Cut screen area from mockup (make transparent) ────────────
    cut_mask = Image.new("L", (new_w, new_h), 0)
    ImageDraw.Draw(cut_mask).rounded_rectangle(
        [sx, sy, sx + sw, sy + sh], radius=sr, fill=255
    )
    px = mockup_scaled.load()
    cm = cut_mask.load()
    for y in range(new_h):
        for x in range(new_w):
            if cm[x, y] > 0:
                r, g, b, a = px[x, y]
                px[x, y] = (r, g, b, 0)

    # ── 4. Canvas ────────────────────────────────────────────────────
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (*hex_to_rgb(bg_hex), 255))

    # ── 5. Screenshot (cover mode, clipped to screen) ────────────────
    scale_s = max(sw / shot.width, sh / shot.height)
    shot_w = int(shot.width * scale_s)
    shot_h = int(shot.height * scale_s)
    shot_resized = shot.resize((shot_w, shot_h), Image.LANCZOS)

    # Position: center phone horizontally, position lower on canvas
    mockup_x = (CANVAS_W - new_w) // 2
    mockup_y = int(CANVAS_H * 0.22)  # moved up from 0.30, tighter gap to text

    # Screenshot paste position (centered in screen area)
    paste_x = mockup_x + sx + (sw - shot_w) // 2
    paste_y = mockup_y + sy + (sh - shot_h) // 2

    # Clip screenshot to screen area
    scr_mask = Image.new("L", (CANVAS_W, CANVAS_H), 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [mockup_x + sx, mockup_y + sy, mockup_x + sx + sw, mockup_y + sy + sh],
        radius=sr, fill=255
    )
    scr_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    scr_layer.paste(shot_resized, (paste_x, paste_y))
    scr_layer.putalpha(scr_mask)
    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 6. Mockup on top (bezel + Dynamic Island) ────────────────────
    mockup_layer = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    mockup_layer.paste(mockup_scaled, (mockup_x, mockup_y))
    canvas = Image.alpha_composite(canvas, mockup_layer)

    # ── 7. Text — platform-specific font variants for hierarchy ───────
    draw = ImageDraw.Draw(canvas)
    max_text_w = int(CANVAS_W * TEXT_W_RATIO)
    verb_size_max = int(CANVAS_W * VERB_SIZE_MAX_RATIO)
    verb_size_min = int(CANVAS_W * VERB_SIZE_MIN_RATIO)
    desc_size = int(CANVAS_W * DESC_SIZE_RATIO)

    if font:
        font_path = _resolve_font(font, fallbacks=_FONT_FALLBACKS)
        verb_font = fit_font(verb.upper(), max_text_w, verb_size_max, verb_size_min, font_path)
        desc_font = ImageFont.truetype(font_path, desc_size)
    else:
        # iOS font variants: SF Pro Display Black (verb) + SF Pro Regular (descriptor)
        # Android font variants: Roboto Black (verb) + Roboto Regular (descriptor)
        VERB_FONT_CANDIDATES = [
            # iOS: SF Pro Display Black
            ("/System/Library/Fonts/SFCompact.ttf", 0, 0),       # SF Compact Black
            ("/System/Library/Fonts/SFNS.ttf", 0, 0),             # SF NS fallback
            # Android: Roboto Black
            ("Roboto-Black.ttf", 0, 0),
            ("Roboto-VariableFont_wdth,wght.ttf", 0, 0),
        ]
        DESC_FONT_CANDIDATES = [
            # iOS: SF Pro Text Regular (lighter weight)
            ("/System/Library/Fonts/SFNS.ttf", 0, 0),             # SF Pro Regular
            ("/System/Library/Fonts/SFCompactRounded.ttf", 0, 0), # SF Rounded
            # Android: Roboto Regular
            ("Roboto-VariableFont_wdth,wght.ttf", 0, 0),
            ("NotoSans-Black.ttf", 0, 0),
        ]

        def _find_font(candidates):
            for fp, idx, _ in candidates:
                if os.path.isabs(fp) and os.path.isfile(fp):
                    try:
                        return ImageFont.truetype(fp, 72, index=idx), fp, idx
                    except:
                        continue
                else:
                    # Search font dirs
                    for d in _FONT_DIRS:
                        full = os.path.join(d, fp)
                        if os.path.isfile(full):
                            try:
                                return ImageFont.truetype(full, 72, index=idx), full, idx
                            except:
                                continue
            return None, None, None

        _, verb_fp, verb_idx = _find_font(VERB_FONT_CANDIDATES)
        _, desc_fp, desc_idx = _find_font(DESC_FONT_CANDIDATES)

        if not verb_fp:
            verb_fp = _resolve_font(_FONT_FALLBACKS[0], fallbacks=_FONT_FALLBACKS)
            verb_idx = 0
        if not desc_fp:
            desc_fp = verb_fp
            desc_idx = verb_idx

        # Fit verb font to canvas
        verb_font = fit_font(verb.upper(), max_text_w, verb_size_max, verb_size_min, verb_fp)
        # Recreate with index for TTC support
        try:
            verb_font = ImageFont.truetype(verb_fp, verb_font.size, index=verb_idx)
        except:
            pass
        desc_font = ImageFont.truetype(desc_fp, desc_size, index=desc_idx)

    text_top = int(CANVAS_H * 0.080)
    y = text_top
    y = draw_centered(draw, y, verb.upper(), verb_font, CANVAS_W)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, CANVAS_W, max_w=max_text_w)

    # ── 8. Save ──────────────────────────────────────────────────────
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({CANVAS_W}×{CANVAS_H})")


def main():
    p = argparse.ArgumentParser(description="Mockup-based store screenshot composer")
    p.add_argument("--bg", required=True)
    p.add_argument("--verb", required=True)
    p.add_argument("--desc", required=True)
    p.add_argument("--screenshot", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--font", default=None)
    args = p.parse_args()
    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, font=args.font)


if __name__ == "__main__":
    main()
