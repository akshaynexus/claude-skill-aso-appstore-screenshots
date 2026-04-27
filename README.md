# ASO App Store Screenshots

> **Forked from [adamlyttleapps/claude-skill-aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots)** by Adam Lyttle. This fork adds Android/Google Play support, Codex integration, npx skills CLI compatibility, cross-platform font support, and cross-platform resize tooling.

This repository contains two App Store creative skills:

## Changes from Upstream

| Feature | Description |
|---------|-------------|
| **Android (Google Play) support** | Device profiles system with `--device` flag (`iphone-6.7`, `iphone-6.5`, `iphone-6.9`, `android`). Android outputs 1080×2400 Google Play screenshots with punch-hole camera frame. |
| **Codex support** | Dual runtime — works with both Claude Code and Codex via `agents/openai.yaml` metadata and shared JSON ledger at `.agents/aso-appstore-screenshots/state.json`. |
| **npx skills CLI** | Fully compatible with `npx skills add` for installation across 40+ agents (Claude Code, Codex, OpenCode, Cursor, etc.). Skills live in root + `skills/` directory. |
| **Cross-platform font support** | `--font` flag in `compose.py` with auto-detection per platform: SF Pro Display Black (macOS), Noto Sans Black (Linux), Arial Bold (Windows). |
| **Cross-platform resize** | `resize.py` replaces macOS-only `sips` commands with Pillow-based crop/resize that works on macOS, Linux, and Windows. |
| **Proportional typography** | Font sizes scale proportionally to canvas width instead of fixed pixels, ensuring consistent appearance across all device profiles. |

## What It Does

The screenshot skill supports both Codex and Claude Code. The app-icon skill is currently documented for Codex packaging.

## Included Skills

### `aso-appstore-screenshots`

The screenshot skill:

1. Analyzes the app to identify the strongest user benefits
2. Reviews simulator screenshots and pairs each one to the right benefit
3. Builds deterministic screenshot scaffolds with `compose.py`
4. Enhances those scaffolds into App Store-ready creatives with Gemini MCP
5. Generates a final side-by-side showcase image

### `aso-appstore-icon`

The app-icon skill:

1. Analyzes the app, existing icon assets, and brand cues
2. Audits the current icon and competitor or inspiration references
3. Drafts 3 distinct icon directions
4. Generates icon concepts with Gemini MCP
5. Normalizes raw outputs to exact App Store requirements with `prepare_icon.py`
6. Builds review boards with `preview_icons.py` for fast comparison and iteration

## Installation

Both skills live under the [`skills/`](skills/) directory following the [npx skills](https://skills.sh) convention.

### Option 1: Install with npx skills CLI (recommended)

[![npx skills](https://img.shields.io/badge/npm-skills_cli-blue)](https://skills.sh)

The `npx skills` CLI handles installation to **all detected agents** in one command. It auto-detects which coding agents you have installed (Claude Code, Codex, OpenCode, Cursor, Cline, and 40+ more) and installs skills to the correct paths.

```bash
# Install all skills to all detected agents (project scope — committed to repo)
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots

# Install to a specific agent only
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a claude-code
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a codex
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a opencode

# Install globally (available across all your projects)
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -g

# Non-interactive (skip all prompts)
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -y

# List available skills before installing
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots --list
```

**Scope**: Project (default) installs to `./.agents/skills/`, `./.claude/skills/`, etc. in your repo. Global (`-g`) installs to `~/`.

**Installation method**: By default, `npx skills` creates symlinks from each agent directory to a canonical copy — single source of truth, easy to update. Use `--copy` for independent copies if symlinks aren't supported.

**What gets installed**: Both `aso-appstore-screenshots` and `aso-appstore-icon` are detected and installed automatically.

#### Quick start for a specific agent

```bash
# Claude Code — project scope
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a claude-code

# Codex — global
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a codex -g

# OpenCode — project scope
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a opencode
```

After installation, restart your agent to pick up the new skills.

---

### Option 2: Manual install (alternative)

If you prefer not to use `npx skills`, you can symlink the skill directories directly.

#### Screenshot skill — Claude Code

```bash
mkdir -p "$HOME/.claude/skills"
rm -f "$HOME/.claude/skills/aso-appstore-screenshots"
ln -s "$(pwd)/skills/aso-appstore-screenshots" "$HOME/.claude/skills/aso-appstore-screenshots"
```

#### Screenshot skill — Codex / OpenCode

```bash
mkdir -p "$HOME/.agents/skills"
rm -f "$HOME/.agents/skills/aso-appstore-screenshots"
ln -s "$(pwd)/skills/aso-appstore-screenshots" "$HOME/.agents/skills/aso-appstore-screenshots"
```

#### Icon skill — any agent

```bash
mkdir -p "$HOME/.agents/skills"
rm -f "$HOME/.agents/skills/aso-appstore-icon"
ln -s "$(pwd)/skills/aso-appstore-icon" "$HOME/.agents/skills/aso-appstore-icon"
```

#### Project-local install (inside a consuming app repo)

Copy or symlink into your app's skill directories:

- `.agents/skills/aso-appstore-screenshots` — Codex / OpenCode
- `.claude/skills/aso-appstore-screenshots` — Claude Code
- `.agents/skills/aso-appstore-icon` — Icon skill (any agent)

Restart your agent after installing.

---

### 3. Install Python dependencies

Both skills use Pillow-based local helpers. The skill auto-creates a `.venv/` inside its directory on first use — no manual setup needed. To pre-install:

```bash
python3 -m venv skills/aso-appstore-screenshots/.venv
skills/aso-appstore-screenshots/.venv/bin/pip install Pillow
```

### 4. Install the screenshot font dependency

The screenshot scaffold renderer auto-detects a suitable headline font per platform:

| Platform | Default font | Install |
|----------|-------------|---------|
| **macOS** | SF Pro Display Black | [Apple Developer Fonts](https://developer.apple.com/fonts/) → `/Library/Fonts/SF-Pro-Display-Black.otf` |
| **Linux** | Noto Sans Black | `sudo apt install fonts-noto-core` (usually pre-installed) |
| **Windows** | Arial Bold | Pre-installed |

To use a custom font, pass `--font` to `compose.py` with either a filename (searched in platform font dirs) or a full path:

```bash
# By filename (searched in platform font directories)
python3 skills/aso-appstore-screenshots/compose.py --font "Inter-Black.otf" ...

# By full path
python3 skills/aso-appstore-screenshots/compose.py --font "/path/to/CustomFont.otf" ...
```

### 5. Configure Gemini MCP

Both skills use Gemini as the generation and editing backend. Pick the command for your agent:

**Claude Code** — add to `~/.claude/settings.json` (user-level) or `.mcp.json` (project-level):

```json
{
  "mcpServers": {
    "gemini": {
      "command": "npx",
      "args": ["-y", "@houtini/gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here",
        "VERBOSE": "true"
      }
    }
  }
}
```

**Codex** — register via CLI:

```bash
codex mcp add gemini --env GEMINI_API_KEY=your-api-key-here -- npx -y @houtini/gemini-mcp
codex mcp get gemini
```

Codex stores MCP server registrations in `~/.codex/config.toml`.

**OpenCode** — add to `opencode.json` in your project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "gemini": {
      "type": "local",
      "command": ["npx", "-y", "@houtini/gemini-mcp"],
      "environment": {
        "GEMINI_API_KEY": "your-api-key-here",
        "VERBOSE": "true"
      },
      "enabled": true
    }
  }
}
```

If Gemini image generation or editing returns `429 RESOURCE_EXHAUSTED` with zero image quota, generation cannot continue. Enable billing or image-model quota for the Gemini project backing `GEMINI_API_KEY`, then resume later.

## Usage

### Screenshot skill in Claude Code

Claude Code can discover the screenshot skill automatically from `.claude/skills/` or `~/.claude/skills/` when the request matches the skill description.

For explicit use, ask Claude Code to use `aso-appstore-screenshots` for the current app-store creative task. If your Claude Code build exposes user-invocable skills as slash commands, `/aso-appstore-screenshots` also works.

### Screenshot skill in Codex

From inside an app project, invoke the screenshot skill explicitly in your prompt:

```text
Use aso-appstore-screenshots to generate App Store screenshots for my app
```

You can also use the Codex skills picker or slash-command list once the skill is installed.

### Screenshot skill in OpenCode

OpenCode discovers skills from `.opencode/skills/`, `.claude/skills/`, or `.agents/skills/` in your project, plus `~/.config/opencode/skills/`, `~/.claude/skills/`, and `~/.agents/skills/` globally.

The skill loads on-demand via the native `skill` tool. Just mention it in your prompt:

```text
Use aso-appstore-screenshots to generate App Store screenshots for my app
```

### App-icon skill

```text
$aso-appstore-icon
```

You can also use the Codex skills picker or slash-command list once the icon skill is installed.

## State And Output

### Screenshot skill

Resume state is stored at:

```text
.agents/aso-appstore-screenshots/state.json
```

Legacy state at `.codex/aso-appstore-screenshots/state.json` or `.claude/aso-appstore-screenshots/state.json` is still recognized and reused.

Generated assets are stored under:

```text
screenshots/
  01-benefit-slug/          ← working versions
    scaffold.png            ← deterministic compose.py output
    v1.png, v2.png, v3.png  ← AI-enhanced versions
    v1-resized.png, ...     ← cropped to App Store dimensions
  final/                    ← approved screenshots, ready to upload
    01-benefit-slug.png
    02-benefit-slug.png
  showcase.png              ← preview image with all screenshots
```

The `final/` folder contains App Store-ready screenshots at exact Apple dimensions (default: 1290×2796px for iPhone 6.7").

## Files

| File | Purpose |
|------|---------|
| `skills/aso-appstore-screenshots/SKILL.md` | Screenshot skill prompt and workflow |
| `skills/aso-appstore-screenshots/agents/openai.yaml` | Screenshot skill UI metadata |
| `skills/aso-appstore-screenshots/compose.py` | Deterministic screenshot scaffold generator |
| `skills/aso-appstore-screenshots/generate_frame.py` | Regenerates the screenshot device frame template |
| `skills/aso-appstore-screenshots/showcase.py` | Builds the final screenshot showcase image |
| `skills/aso-appstore-screenshots/resize.py` | Cross-platform screenshot crop/resize (replaces macOS-only sips) |
| `skills/aso-appstore-screenshots/assets/device_frame.png` | Pre-rendered iPhone frame template |
| `skills/aso-appstore-screenshots/assets/device_frame_android.png` | Pre-rendered Android frame template |
| `skills/aso-appstore-icon/SKILL.md` | App-icon skill prompt and workflow |
| `skills/aso-appstore-icon/agents/openai.yaml` | App-icon skill UI metadata |
| `skills/aso-appstore-icon/prepare_icon.py` | Normalizes generated icons to exact App Store source requirements |
| `skills/aso-appstore-icon/preview_icons.py` | Builds icon comparison and preview boards |
| `CLAUDE.md` | Claude Code guidance for the screenshot skill |
| `AGENTS.md` | Repository-specific engineering guidance |

## Verification

Run these checks after updating the skill prompts or helper scripts:

```bash
python3 -m py_compile skills/aso-appstore-screenshots/compose.py skills/aso-appstore-screenshots/generate_frame.py skills/aso-appstore-screenshots/showcase.py skills/aso-appstore-screenshots/resize.py
python3 -m py_compile skills/aso-appstore-icon/prepare_icon.py skills/aso-appstore-icon/preview_icons.py
python3 -m unittest discover -s tests
git diff --check
```

## License

MIT
