# ASO App Store Screenshots

> Forked from [adamlyttleapps/claude-skill-aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots) by Adam Lyttle.

AI-powered skills for generating App Store & Google Play screenshots and icons. Works with Claude Code, Codex, OpenCode, Cursor, and 40+ agents via [npx skills](https://skills.sh).

## Changes from Upstream

| Feature | Description |
|---------|-------------|
| Android (Google Play) | Device profiles (`--device android`) outputs 1080×2400 screenshots with punch-hole frame |
| Codex + OpenCode support | Dual runtime via `agents/openai.yaml` and shared JSON ledger |
| npx skills CLI | Install to 40+ agents with one command |
| Cross-platform fonts | `--font` flag with auto-detection: SF Pro (macOS), Noto Sans (Linux), Arial (Windows) |
| Cross-platform resize | `resize.py` replaces macOS-only `sips` |
| Proportional typography | Font sizes scale with canvas width across all device profiles |

## Skills

| Skill | Description |
|-------|-------------|
| `aso-appstore-screenshots` | Analyzes app → discovers benefits → pairs screenshots → generates App Store/Google Play images via `compose.py` + Gemini MCP |
| `aso-appstore-icon` | Audits icons → drafts directions → generates concepts → normalizes to App Store specs |

## Install

### npx skills CLI (recommended)

Installs to all detected agents in one command:

```bash
# Install both skills to all agents (project scope)
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots

# Specific agent
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a claude-code
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a codex
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -a opencode

# Global (all projects)
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -g

# Non-interactive
npx skills add akshaynexus/claude-skill-aso-appstore-screenshots -y
```

### Manual (alternative)

```bash
# Claude Code
ln -s "$(pwd)/skills/aso-appstore-screenshots" "$HOME/.claude/skills/aso-appstore-screenshots"

# Codex / OpenCode
ln -s "$(pwd)/skills/aso-appstore-screenshots" "$HOME/.agents/skills/aso-appstore-screenshots"

# Icon skill (any agent)
ln -s "$(pwd)/skills/aso-appstore-icon" "$HOME/.agents/skills/aso-appstore-icon"
```

## Configure Gemini MCP

Both skills need the Gemini MCP server. Pick your agent:

**Claude Code** — add to `~/.claude/settings.json`:

```json
{ "mcpServers": { "gemini": { "command": "npx", "args": ["-y", "@houtini/gemini-mcp"], "env": { "GEMINI_API_KEY": "your-key" } } } }
```

**Codex** — CLI:

```bash
codex mcp add gemini --env GEMINI_API_KEY=your-key -- npx -y @houtini/gemini-mcp
```

**OpenCode** — CLI:

```bash
opencode mcp add    # interactive wizard
opencode mcp list   # verify it's added
```

Or add manually to `opencode.json`:

```json
{ "$schema": "https://opencode.ai/config.json", "mcp": { "gemini": { "type": "local", "command": ["npx", "-y", "@houtini/gemini-mcp"], "environment": { "GEMINI_API_KEY": "your-key" }, "enabled": true } } }
```

Other OpenCode MCP commands:

```bash
opencode mcp list          # list all MCP servers
opencode mcp auth <name>   # authenticate OAuth server
opencode mcp logout <name> # remove OAuth credentials
opencode mcp debug <name>  # debug connection issues
```

## Usage

Mention the skill in your prompt:

```
Use aso-appstore-screenshots to generate App Store screenshots for my app
$aso-appstore-icon
```

Claude Code also supports `/aso-appstore-screenshots` slash command.

## Device Profiles

| Profile | Dimensions | Store | Flag |
|---------|-----------|-------|------|
| `iphone-6.7` | 1290×2796 | App Store | `--device iphone-6.7` (default) |
| `iphone-6.5` | 1242×2688 | App Store | `--device iphone-6.5` |
| `iphone-6.9` | 1320×2868 | App Store | `--device iphone-6.9` |
| `android` | 1080×2400 | Google Play | `--device android` |

## Font

Auto-detected per platform. Override with `--font`:

```bash
python3 skills/aso-appstore-screenshots/compose.py --font "Inter-Black.otf" ...
```

| macOS | Linux | Windows |
|-------|-------|---------|
| SF Pro Display Black | Noto Sans Black | Arial Bold |

## Python Deps

Pillow is required. The skill auto-creates a `.venv/` on first use — no manual setup needed.

## Output

```
screenshots/
  01-benefit/          ← scaffold + 3 AI versions
  final/               ← approved, App Store-ready
  showcase.png         ← side-by-side preview
```

State saved to `.agents/aso-appstore-screenshots/state.json`.

## Files

| File | Purpose |
|------|---------|
| `skills/aso-appstore-screenshots/` | Screenshot skill (SKILL.md, compose.py, generate_frame.py, showcase.py, resize.py, assets/) |
| `skills/aso-appstore-icon/` | Icon skill (SKILL.md, prepare_icon.py, preview_icons.py) |
| `CLAUDE.md` | Claude Code guidance |
| `AGENTS.md` | Engineering guidance |

## License

MIT
