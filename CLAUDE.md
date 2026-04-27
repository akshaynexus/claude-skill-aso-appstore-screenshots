# CLAUDE.md

This file provides guidance to Claude Code when working with the root `aso-appstore-screenshots` skill in this repository.

## What This Is

The repository root is the `aso-appstore-screenshots` skill. It supports both Claude Code and Codex, but this file is the Claude Code-facing guidance.

## Runtime Assumptions

- Claude Code discovers the skill from `.claude/skills/aso-appstore-screenshots` in a project or `$HOME/.claude/skills/aso-appstore-screenshots` for a user install.
- The skill uses a project-local JSON ledger for resumability. Prefer `.agents/aso-appstore-screenshots/state.json`, but keep using `.codex/aso-appstore-screenshots/state.json` or `.claude/aso-appstore-screenshots/state.json` if one already exists for the app.
- Gemini MCP remains the image-enhancement backend.
- `user-invocable: true` is intentionally kept in `SKILL.md` for Claude Code compatibility.

## Architecture

Six files + two assets make up the skill (all under `skills/aso-appstore-screenshots/`):

- **SKILL.md** — The shared skill prompt. Defines the multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation → Showcase.
- **compose.py** — A Pillow-based compositor that renders deterministic screenshot scaffolds with headline text, device frame template, and simulator screenshot. Supports multiple device profiles (iPhone 6.7", 6.5", 6.9", Android) via `--device` flag. Cross-platform font resolution (macOS/Linux/Windows).
- **generate_frame.py** — Regenerates `assets/device_frame.png` and `assets/device_frame_android.png`. Supports `--device` flag for all profiles.
- **showcase.py** — Generates the final side-by-side preview of approved screenshots.
- **resize.py** — Cross-platform screenshot crop/resize (replaces macOS-only `sips`).
- **assets/device_frame.png** — Pre-rendered iPhone frame template used by `compose.py`.
- **assets/device_frame_android.png** — Pre-rendered Android frame template with punch-hole camera.

## Device Profiles

| Profile | Dimensions | Store | Frame |
|---------|-----------|-------|-------|
| `iphone-6.7` | 1290×2796 | App Store | device_frame.png |
| `iphone-6.5` | 1242×2688 | App Store | device_frame.png |
| `iphone-6.9` | 1320×2868 | App Store | device_frame.png |
| `android` | 1080×2400 | Google Play | device_frame_android.png |

## Running compose.py

```bash
# Requires: pip install Pillow

# iPhone 6.7" (default)
python3 skills/aso-appstore-screenshots/compose.py \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "TRADING CARD PRICES" \
  --screenshot path/to/simulator.png \
  --output output.png

# Android (Google Play)
python3 skills/aso-appstore-screenshots/compose.py \
  --bg "#4CAF50" \
  --verb "TRACK" \
  --desc "YOUR EXPENSES" \
  --screenshot path/to/emulator.png \
  --output output.png \
  --device android

# Custom font (cross-platform)
python3 skills/aso-appstore-screenshots/compose.py \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "CARD PRICES" \
  --screenshot path/to/simulator.png \
  --output output.png \
  --font "Inter-Black.otf"
```

## Running resize.py

```bash
# Requires: pip install Pillow

# Default: iPhone 6.7" (1290×2796)
python3 skills/aso-appstore-screenshots/resize.py screenshots/01-benefit/v1.jpg screenshots/01-benefit/v2.jpg screenshots/01-benefit/v3.jpg

# Custom dimensions (e.g. iPhone 6.5")
python3 skills/aso-appstore-screenshots/resize.py --width 1242 --height 2688 screenshots/01-benefit/v*.jpg
```

Each input file gets a `-resized` sibling (e.g. `v1.jpg` → `v1-resized.jpg`). Crops to the target aspect ratio (center-crop, top edge preserved) then resizes to exact dimensions.

## Key Design Decisions

- **Device profiles system**: All layout values are derived from canvas size so each profile produces correctly proportioned output.
- **Proportional typography**: Font sizes scale proportionally to canvas width instead of fixed pixels, ensuring consistent appearance across device profiles.
- **Cross-platform font resolution**: `--font` accepts either a filename (searched in platform font dirs) or a full path. Falls back to platform defaults (SF Pro Display Black on macOS, Noto Sans Black on Linux, Arial Bold on Windows).
- **Two-stage generation**: compose.py creates a deterministic scaffold first (text + frame + screenshot), then Nano Banana Pro enhances it.
- **Shared JSON ledger**: Project-local state at `.agents/aso-appstore-screenshots/state.json` for resumability across Codex and Claude Code.

## Verification

Run these checks after changing the screenshot skill packaging or prompt:

```bash
python3 -m py_compile skills/aso-appstore-screenshots/compose.py skills/aso-appstore-screenshots/generate_frame.py skills/aso-appstore-screenshots/showcase.py skills/aso-appstore-screenshots/resize.py
git diff --check
```

Also confirm:

- `README.md`, `SKILL.md`, `AGENTS.md`, and `CLAUDE.md` agree on dual-runtime support
- the screenshot skill still resolves from `.agents/skills` and `.claude/skills`
- legacy `.codex` and `.claude` state ledgers remain accepted if they already exist in a consuming app
