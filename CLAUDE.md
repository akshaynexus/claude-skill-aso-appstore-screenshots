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

Five files + one asset make up the skill:

- **SKILL.md** — The shared skill prompt. Defines the multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation → Showcase.
- **compose.py** — A Pillow-based compositor that renders deterministic 1290×2796 screenshot scaffolds with the headline text, device frame template, and simulator screenshot.
- **generate_frame.py** — Regenerates `assets/device_frame.png`.
- **showcase.py** — Generates the final side-by-side preview of approved screenshots.
- **resize.py** — Cross-platform screenshot crop/resize (replaces macOS-only `sips`).
- **assets/device_frame.png** — Pre-rendered iPhone frame template used by `compose.py`.

- **SKILL.md** — The skill prompt. Defines a multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation. Uses Claude Code's memory system to persist state across conversations so users can resume mid-workflow. Generation first creates a deterministic scaffold via compose.py, then sends it to Nano Banana Pro for AI enhancement.
- **compose.py** — A standalone Python compositing script (Pillow-based) that deterministically renders App Store screenshots. Takes a background hex colour, action verb, benefit descriptor, and simulator screenshot path, then produces a pixel-perfect 1290×2796 PNG with headline text, device frame template, and the screenshot composited inside. The verb text auto-sizes to fit the canvas width.
- **resize.py** — Cross-platform crop and resize script (Pillow-based). Takes one or more images and crops them to the target aspect ratio (center-crop, top edge preserved) then resizes to exact pixel dimensions. Provides a cross-platform alternative to the macOS-only `sips` commands. Works on macOS, Linux, and Windows.
- **generate_frame.py** — Generates the device frame template PNG (`assets/device_frame.png`). Run once to create or update the template. The template is a 1290×2796 RGBA PNG with a black iPhone body, transparent screen cutout, Dynamic Island, and side buttons.
- **showcase.py** — Generates a showcase image showing up to 3 final screenshots side-by-side with an optional GitHub link at the bottom. Used as the final step after all screenshots are approved.
- **assets/device_frame.png** — Pre-rendered iPhone device frame template used by compose.py. Using a template instead of drawing the frame at compose time ensures pixel-perfect consistency across all generated screenshots.
>>>>>>> ff8f773 (Add cross-platform resize.py, keep sips as macOS fallback)

## Working Conventions

- Keep Claude Code and Codex support aligned instead of treating one as legacy.
- When editing runtime instructions, document Claude-specific and Codex-specific behavior separately if they differ.
- Prefer shared project-local state and shared helper scripts over runtime-specific logic in Python code.
- Do not reintroduce the old Claude memory-file workflow unless explicitly requested. The shared JSON ledger replaced it.

## Verification

Run these checks after changing the screenshot skill packaging or prompt:

```bash
python3 -m py_compile compose.py generate_frame.py showcase.py
git diff --check
```

## Running resize.py

```bash
# Requires: pip install Pillow

# Default: iPhone 6.7" (1290×2796)
python3 resize.py screenshots/01-benefit/v1.jpg screenshots/01-benefit/v2.jpg screenshots/01-benefit/v3.jpg

# Custom dimensions
python3 resize.py --width 1242 --height 2688 screenshots/*.jpg
```

Also confirm:

# Custom dimensions (e.g. iPhone 6.5")
python3 resize.py --width 1242 --height 2688 screenshots/01-benefit/v*.jpg
```

Each input file gets a `-resized` sibling (e.g. `v1.jpg` → `v1-resized.jpg`). Crops to the target aspect ratio (center-crop, top edge preserved) then resizes to exact dimensions.

## Key Design Decisions
>>>>>>> ff8f773 (Add cross-platform resize.py, keep sips as macOS fallback)

- `README.md`, `SKILL.md`, `AGENTS.md`, and `CLAUDE.md` agree on dual-runtime support
- the screenshot skill still resolves from `.agents/skills` and `.claude/skills`
- legacy `.codex` and `.claude` state ledgers remain accepted if they already exist in a consuming app
