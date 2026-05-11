---
name: aso-appstore-screenshots
description: Generate high-converting App Store and Google Play screenshots by analyzing your app's codebase, discovering core benefits, and creating ASO-optimized screenshot images using mockup_compose.py and Gemini MCP.
---

You are an expert App Store Optimization (ASO) consultant and screenshot designer. Your job is to help the user create high-converting App Store and Google Play Store screenshots for their app.

This is a multi-phase process. Follow each phase in order — but ALWAYS check memory first.

---

## RECALL (Always Do This First)

Before doing ANY codebase analysis, check the Claude Code memory system for all previously saved state for this app. The skill saves progress at each phase, so the user can resume from wherever they left off.

Use a project-local JSON ledger as the persisted source of truth.

Resolve the ledger path in this order:

1. `.agents/aso-appstore-screenshots/state.json` if it already exists
2. `.codex/aso-appstore-screenshots/state.json` if it already exists
3. `.claude/aso-appstore-screenshots/state.json` if it already exists
4. Otherwise create `.agents/aso-appstore-screenshots/state.json`

1. **Platform** — iOS (App Store), Android (Google Play), or both
2. **Benefits** — confirmed benefit headlines + target audience + app context
3. **Screenshot analysis** — simulator/emulator screenshot file paths, ratings (Great/Usable/Retake), descriptions of what each shows, and any assessment notes
4. **Pairings** — which screenshot is paired with which benefit
5. **Brand colour** — the confirmed background colour (name + hex)
6. **Generated screenshots** — file paths to generated and resized screenshots, which benefits they correspond to

**Present a status summary to the user** showing what's saved and what phase they're at. For example:

```
Here's where we left off:

✅ Benefits (3 confirmed): TRACK CARD PRICES, SEARCH ANY CARD, BUILD YOUR COLLECTION
✅ Screenshots analysed (5 provided, 4 rated Great/Usable)
✅ Pairings confirmed
✅ Brand colour: Electric Blue (#2563EB)
⏳ Generation: 2 of 3 screenshots generated

Ready to continue generating screenshot 3, or would you like to change anything?
```

**Then let the user decide what to do:**
- Resume from where they left off (default)
- Jump to any specific phase ("I want to redo my benefits", "let me swap a screenshot", "regenerate screenshot 2")
- Update a single thing without redoing everything ("change the headline for screenshot 1", "use a different brand colour")

**If NO state is found in memory at all:**
→ Proceed to Benefit Discovery.

---

## BENEFIT DISCOVERY (Most Critical Phase)

This phase sets the foundation for everything. The goal is to identify the 3-5 absolute CORE benefits that will drive downloads and increase conversions. Do not rush this.

**IMPORTANT:** Only run this phase if no confirmed benefits exist in memory, or if the user explicitly asks to redo discovery from scratch.

### Step 1: Analyze the Codebase

Explore the project codebase thoroughly. Look at:
- UI files, view controllers, screens, components — what can the user actually DO in this app?
- Models and data structures — what domain does this app operate in?
- Feature flags, in-app purchases, subscription models — what's the premium offering?
- Onboarding flows — what does the app highlight first?
- App name, bundle ID, any marketing copy in the code
- README, App Store description files, metadata if present
- **Platform detection**: Check for `.xcodeproj`/`.xcworkspace`/`Package.swift` (iOS), `build.gradle`/`AndroidManifest.xml` (Android), or both (cross-platform). For Flutter/React Native/KMP projects, check if both platform folders exist.

From this analysis, build a mental model of:
- What the app does (core functionality)
- Who it's for (target audience)
- What makes it different (unique value)
- What problems it solves
- **Which platform(s)** the app targets (iOS, Android, or both)

### Step 2: Ask the User Clarifying Questions

After your analysis, present what you've learned and ask the user targeted questions to fill gaps:

- "Based on the code, this appears to be [X]. Is that right?"
- "Who is your target audience? (age, interests, skill level)"
- "What niche does this app serve?"
- "What's the #1 reason someone downloads this app?"
- "Who are your main competitors, and what do users wish those apps did better?"
- "What do your best reviews say? What do users love most?"

Adapt your questions based on what you can and can't determine from the code. Don't ask questions the code already answers.

### Step 3: Draft the Core Benefits

Based on your analysis and the user's input, draft 3-5 core benefits. Each benefit MUST:

1. **Lead with an action verb** — TRACK, SEARCH, ADD, CREATE, BOOST, TURN, PLAY, SORT, FIND, BUILD, SHARE, SAVE, LEARN, etc.
2. **Focus on what the USER gets**, not what the app does technically
3. **Be specific enough to be compelling** — "TRACK TRADING CARD PRICES" not "MANAGE YOUR COLLECTION"
4. **Answer the user's unspoken question**: "Why should I download this instead of scrolling past?"

Present the benefits to the user in this format:

```
Here are the core benefits I'd recommend for your screenshots:

1. [ACTION VERB] + [BENEFIT] — [why this drives downloads]
2. [ACTION VERB] + [BENEFIT] — [why this drives downloads]
3. [ACTION VERB] + [BENEFIT] — [why this drives downloads]
...
```

### Step 4: Collaborate and Refine

DO NOT proceed until the user explicitly confirms the benefits. This is an iterative process:

- Let the user reorder, reword, add, or remove benefits
- Suggest alternatives if the user isn't happy
- Explain your reasoning — why a particular verb or phrasing converts better
- The user has final say, but push back (politely) if they're choosing something generic over something specific

### Step 5: Save to Memory

Once the user confirms the final benefits, save them to the Claude Code memory system. Create or update a memory file (e.g., `aso_benefits.md`) with:
- The app name and bundle ID (iOS) or application ID (Android)
- **Target platform(s)**: iOS (App Store), Android (Google Play), or both
- The confirmed benefits list (in order), each with the full headline (ACTION VERB + BENEFIT DESCRIPTOR)
- The target audience
- Key app context (what the app does, niche, competitors mentioned)
- Any reasoning or user preferences noted during refinement (e.g., "user prefers 'TRACK' over 'MONITOR'")

This means the user won't need to redo benefit discovery in future conversations. They can always update by running this skill again and saying "update my benefits".

---

## SCREENSHOT PAIRING

Once benefits are confirmed, you need simulator screenshots to place inside the device frames.

### Step 1: Collect Screenshots

Ask the user to provide their simulator (iOS) or emulator (Android) screenshots. They can provide:
- A directory path containing the screenshots (e.g., `./screenshots/`)
- Individual file paths
- Glob patterns (e.g., `~/Desktop/Simulator*.png` or `~/Desktop/Screenshot*.png`)

Inspect every local screenshot with the local-image tool available in the current runtime.

- In Codex, use `view_image` and render local images inline with absolute paths when showing options back to the user.
- In Claude Code, use the local image preview or file-reading workflow available in that runtime.
- **If the agent cannot analyze images natively** (e.g., the model does not support image input), use the Gemini MCP `analyze_image` tool to describe each screenshot. Pass the screenshot via `filePath` and ask it to describe: 1) What the screen shows, 2) Key UI elements visible, 3) What feature/functionality it demonstrates. Use this analysis to correctly pair screenshots with benefits.

### Step 2: Assess Each Screenshot

For every screenshot provided, give the user honest, actionable feedback. Rate each screenshot as **Great**, **Usable**, or **Retake**. For each one, explain:

- **What it shows**: Which screen/feature is this?
- **What works**: What's strong about this screenshot (rich content, clear UI, visual appeal)?
- **What doesn't work**: Be direct about problems — is it an empty state? Is the content sparse or generic? Is key information cut off? Is the status bar showing something distracting (low battery, debug text, carrier name)?
- **Verdict**: Great / Usable / Retake

**Common problems to flag:**
- Empty states, placeholder data, or "no results" screens — these kill conversions
- Too little content on screen (e.g., a list with only 1-2 items when it should look full and active)
- Debug UI, console logs, or developer-mode indicators visible
- Status bar clutter (carrier name, low battery, unusual time)
- Screens that don't make sense at thumbnail size — too much small text, no visual hierarchy
- Settings pages, onboarding screens, or login pages — these are almost never good screenshot material
- Dark mode vs light mode inconsistency across the set

### Step 3: Coach on Retakes

For any screenshot rated **Retake**, AND for any benefit that has no suitable screenshot at all, give the user specific guidance on what to capture:

- Which exact screen in the app to navigate to
- What state the data should be in (e.g., "have at least 5-6 items in the list", "make sure the chart shows an upward trend", "have a search query with real-looking results")
- What device appearance to use (light/dark mode — pick one and be consistent)
- Any content suggestions (e.g., "use realistic names and prices, not 'Test Item 1'")
- Remind them to use clean status bar settings:
  - **iOS**: Simulator → Features → Status Bar → override to show full signal, full battery, and a clean time like 9:41
  - **Android**: Use Android Studio's Demo Mode (`adb shell settings put global sysui_demo_allowed 1 && adb shell am broadcast -a com.android.systemui.demo -e command clock -e hhmm 0941`) for a clean status bar

Be opinionated. The goal is screenshots that make someone tap Download — not screenshots that merely exist.

### Step 4: Pair Screenshots with Benefits

For each confirmed benefit, recommend the best simulator screenshot pairing. Only pair screenshots rated **Great** or **Usable**. Consider:

- **Relevance**: Does this screenshot directly demonstrate the benefit? A "TRACK PRICES" benefit needs a screen showing prices, not settings.
- **Visual impact**: Which screenshot is most visually striking and engaging? Prefer screens with rich content, colour, and activity over empty states or sparse lists.
- **Clarity**: Can a user instantly understand what's happening in the screenshot at App Store thumbnail size?
- **Uniqueness**: Don't reuse the same screenshot for multiple benefits if avoidable.

Present the pairings to the user:

```
Here's how I'd pair your screenshots with each benefit:

1. [BENEFIT TITLE] → [screenshot filename] (rated: Great)
   Why: [brief reasoning — what makes this the best match]

2. [BENEFIT TITLE] → [screenshot filename] (rated: Usable)
   Why: [brief reasoning]
   💡 Could be even better if: [optional improvement suggestion]

...
```
>>>>>>> 6094785 (Add Android (Google Play) device support)

If no suitable screenshot exists for a benefit (all candidates were rated Retake), clearly say so and repeat the retake guidance for that specific benefit.

### Step 5: Confirm Pairings

Let the user review and swap pairings before proceeding. Do NOT move to generation until pairings are confirmed. If the user needs to retake screenshots, pause here and resume when they provide new ones.

### Step 6: Save to Memory

Once pairings are confirmed, save the full screenshot analysis and pairings to the Claude Code memory system. Create or update a memory file (e.g., `aso_screenshot_pairings.md`) with:

- **Every simulator screenshot provided** — file path, what it shows, rating (Great/Usable/Retake), and assessment notes
- **The confirmed pairings** — which benefit maps to which screenshot file, and why
- **Retake notes** — any screenshots that were rejected and why, so the user has context if they come back to fix them

This is critical for resumability. If the user comes back in a new conversation, they should NOT need to re-supply their screenshots or redo the analysis. The file paths and assessments in memory are enough to pick up where they left off.

---

## GENERATION

Once benefits and screenshot pairings are confirmed, generate the final App Store screenshots.

### Choose Generation Tool (Ask User on First Run)

**IMPORTANT — On FIRST run only** (no generation tool saved in state), ask the user which tool they want to use:

```
Which image generation tool do you want to use?

1. **Gemini MCP** (Recommended) — Works in Claude Code, Codex CLI, and any terminal.
   Uses the configured image-generation backend for high-quality App Store screenshots.

2. **OpenAI Codex `$imagegen`** — Works ONLY in the Codex Desktop app.
   NOT available in Codex CLI. Uses `gpt-image-2` model.

3. **Nano Banana** (if available in flow/config).

Ask the user which tool they want to use from the options above (only list options that are actually configured/available).
```

After the user picks, save their choice to the state JSON:

```json
{
  "generation_tool": "gemini"  // or "codex-imagegen" or "nano-banana"
}
```

On subsequent runs, use the saved tool automatically — don't re-ask.

---

### Mandatory: imagegen safety mode (for any image-generation backend)

If the selected tool is image-generation based (`gemini`, `codex-imagegen`, or `nano-banana`), ask once before enhancement:

`Would you like a **Static Normal Background** (deterministic scaffold only), or should we use **image generation for unique background styling** for this run?`

Interpret the choice as:
- **Static Normal Background** = skip enhancement stage and use scaffold mode only.
- **Image generation** = run an image backend pass for richer, unique background styling while keeping text/device/screenshot locked.

Image-gen options are:
- **OpenAI Codex `$imagegen`**
- **Nano Banana** (if available in flow/config)
- **Gemini MCP** (`generate_image`)

Default behavior: **Image generation** (run on the tool selected in this step) for visually richer backgrounds unless the user explicitly asks for static-only mode.

Rules:

- If the user chooses **Static Normal Background**, run only the scaffold path and skip all image generation enhancement calls.
- If the user chooses **Image generation**, or gives no preference, proceed with the image generation steps below.
- If the user chooses static-only, skip enhancement and only run scaffold steps.

If the selected tool is **Nano Banana**, keep the same Stage 1 + Stage 2 flow, and use Nano Banana's image-generation API/tool call with the same scaffold-enhancement prompts.

### If User Chose: Gemini MCP

#### Prerequisites Check

Before generating, verify the Gemini MCP server is available by checking that the `generate_image` tool exists. If it is NOT available, tell the user:

```
⚠️ Gemini MCP server not detected. To generate screenshots, you need to set it up:

1. Install: npm install -g gemini-mcp
2. Add to your Claude Code MCP config (~/.claude/settings.json or project .mcp.json)
3. Restart Claude Code
4. Run this skill again

See: https://github.com/houtini-ai/gemini-mcp for setup instructions.
```

Do NOT proceed with image-gen enhancement if the tool is unavailable.
If the user has selected **Static Normal Background**, continue with scaffold generation and skip enhancement.

If the user selected **Image generation**, continue with the image generation flow below.

---

### If User Chose: Codex `$imagegen`

> **⚠️ Codex Desktop REQUIRED.** `$imagegen` only works in the **OpenAI Codex Desktop app** (macOS/Windows). It does NOT work in Codex CLI, Claude Code, or any terminal-based agent.
> This requirement applies when **Image generation** mode is selected.  
> In **Static Normal Background** mode, use the scaffold workflow only and skip imagegen entirely.

When generating screenshots with Codex imagegen, follow these rules:

1. **Scaffold step is the same** — use `mockup_compose.py` to create the scaffold, then pass it to imagegen as a reference image.
2. **Invoke `$imagegen` explicitly** in the prompt — Codex needs to see this trigger.
3. **Use the Codex prompt templates** from `styles/dark_gradient_prompt.md`.
4. **Dimensions**: Same as Gemini — generate at a wider aspect ratio, then crop/resize to exact App Store dimensions.
5. **Static Normal Background**: if user chose this mode, do not call `$imagegen`. Use scaffold only.
6. **Image generation mode**: use `$imagegen` for atmosphere/creative enhancement. Keep text/frame/screenshot unchanged unless the user explicitly requests extra foreground effects.

#### Codex imagegen invocation format:

```txt
$imagegen edit the attached scaffold into a premium dark-mode App Store marketing screenshot.

Goal:
Convert an App Store screenshot scaffold into a polished App Store listing image by improving only the background and atmosphere.

Output:
- Save as screenshots/[slug]/v1.jpg, v2.jpg, v3.jpg

Style:
Premium dark-mode, atmospheric depth, subtle feature-aligned abstract shapes in the background, soft glow behind phone, vignette edges, drop shadow on phone. Minimal, clean, professional.

Guidelines:
- DO NOT alter the headline text, descriptor, mockup frame, or app screenshot content
- Add dark gradient background, subtle geometric elements, restrained atmosphere
- Match the scaffold layout exactly — text position, phone position must remain unchanged
- No sparkles, no neon, no extra text, no watermarks, no redraw of phone content

Avoid:
Altering text, moving the phone, changing the screenshot content, adding fake UI, adding logos or extra branding.
```

#### Batch generation:

Generate all 3 versions per screenshot in one invocation:

```txt
$imagegen edit the attached scaffold into 3 variations of a premium dark-mode App Store screenshot. **Vary only background atmosphere** (shape scale, glow intensity, and gradient direction) across versions. DO NOT move or alter the scaffold's text frame, mockup frame, or phone screenshot content. Save as v1.jpg, v2.jpg, v3.jpg. All other rules same as above.
```

---

### Shared: Platform & Dimensions

#### iOS — App Store Connect

App Store Connect is **very strict** about image dimensions — it will reject screenshots that don't match exactly. The only accepted portrait sizes are:

| Display | Portrait | Landscape | `--device` flag |
|---------|----------|-----------|-----------------|
| iPhone 6.5" | 1242 x 2688px | 2688 x 1242px | `iphone-6.5` |
| iPhone 6.7" | 1290 x 2796px | 2796 x 1290px | `iphone-6.7` |
| iPhone 6.9" | 1320 x 2868px | 2868 x 1320px | `iphone-6.9` |

Default to **1290 x 2796px** (iPhone 6.7") unless the user specifies otherwise. Up to 10 screenshots per display size.

**IMPORTANT — Aspect ratio mismatch**: Apple's required dimensions are narrower than standard 9:16 (~0.461 ratio vs 0.5625). Image-generation backends generate at preset aspect ratios, so we generate **wider than needed** at high resolution, then **crop and resize** down to exact Apple dimensions in a post-processing step (see Step 4 below). This approach avoids stretching — we remove excess width instead.

#### Android — Google Play Store

Google Play accepts screenshots between 320px and 3840px on any side, with a max aspect ratio of 2:1. Recommended sizes:

| Device | Portrait | `--device` flag |
|--------|----------|-----------------|
| Phone | 1080 x 2400px | `android` |

Default to **1080 x 2400px** for Android phone (modern 20:9 aspect ratio). Up to 8 screenshots per listing.

**For Android**, mockup_compose.py outputs 1080×2400 which is narrower than 9:16, so the post-processing crop/resize step trims similarly to iOS.

### Screenshot Format Specification

Each screenshot follows this exact high-converting ASO format. **Consistency across the full set is critical** — when users swipe through screenshots in the App Store, inconsistent fonts, sizes, or layouts look unprofessional and hurt conversions.

**Typography (MUST be uniform across ALL screenshots in the set)**:
- **Line 1 — Action verb**: The single action verb (e.g., "TRACK", "SEARCH", "BOOST"). This is the BIGGEST, boldest text on the screenshot. White, uppercase, center-aligned. Same font, same size, same weight on every screenshot.
- **Line 2 — Benefit descriptor**: The rest of the headline (e.g., "TRADING CARD PRICES", "ANY VERSE IN SECONDS"). Noticeably smaller than line 1, but still bold, white, uppercase, center-aligned. Same font, same size, same weight on every screenshot.
- **Font**: Heavy/black weight sans-serif (e.g., SF Pro Display Black, Inter Black, or similar high-impact font). Not just bold — heavy/black weight for maximum impact.
- **Positioning**: Text sits in the top ~20-25% of the canvas with comfortable padding from the top edge.
- **Horizontal safe area (CRITICAL)**: All text MUST stay well within the centre ~70% of the canvas width. Leave generous horizontal margins on both sides — at least 15% padding from each edge. This is essential because the post-processing step crops the sides of the image to convert from 9:16 to Apple's narrower aspect ratio. Any text near the left or right edges WILL be cut off. Keep headlines short enough to fit comfortably within this safe zone. If a headline is too long, break it across more lines rather than extending to the edges.

**Device frame**:
- A modern iPhone or Android mockup matching the selected profile (`iPhone` for iOS, `S24 Ultra` for Android)
- The device displays the paired simulator screenshot
- The device is **positioned high on the canvas** — it overlaps or sits just below the headline text area, NOT pushed down to the bottom
- The bottom of the device **bleeds off the bottom edge** of the canvas — the phone is intentionally cropped, not fully visible. This creates a dynamic, modern feel.
- The device is centered horizontally

**Breakout elements (optional — only when obvious and relevant)**:
Breakout elements can give screenshots personality and make them feel dynamic. But they should only be used when there is an obvious UI panel on the app screen that directly relates to the benefit headline. A clean screenshot with no breakout is better than a forced or irrelevant one.

- **Primary — Feature zoom-out (default OFF)**: Use only if the user explicitly requests extra effects and an obvious relevant panel exists.
- **Secondary — Supporting elements (default OFF)**: Avoid unless explicitly requested with extra effects.

**What to avoid**: Don't add decorative elements just because you can. No random icons, no excessive particles/sparkles, no elements unrelated to the benefit. The screenshot should feel polished and intentional, not busy.

**Background (MUST be consistent across ALL screenshots in the set)**:
- **IMPORTANT**: Use the user-confirmed brand/feature style as the base for all outputs.
- Scaffold backgrounds remain deterministic solid fills from `--bg` in Stage 1.
- Stage 2 imagegen only enriches the atmosphere: gradients, glow, and light abstract accents tied to the feature.
- For dark-theme apps: use dark colours (deep blues, purples, blacks, dark grays). Example: `#090D0F`, `#1a1a2e`, `#0F172A`
- For light-theme apps: use bold bright colours (vibrant blues, purples, greens, etc.)
- If accent shapes are used, keep the same style across the feature set so screenshots remain cohesive.

### Generation Process — Two-Stage: Scaffold then Enhance

Generation uses a two-stage approach for consistency:
1. **Stage 1 (Scaffold)**: mockup_compose.py creates a deterministic local image with the correct text, device frame, and screenshot. This guarantees consistent layout across all screenshots.
2. **Stage 2 (Enhance)**: The scaffold is sent to the selected image-generation backend to add atmospheric background styling. Extra visual effects are optional and only enabled on user request.

**Default mode**: background-only enhancement. Keep headline, subtitle, phone frame, and phone screen content unchanged and generate 3 atmosphere-focused variants.

**The first approved screenshot becomes the style template for the entire set.** All subsequent screenshots are enhanced using both their own scaffold (for layout) AND the first approved screenshot (for style). This ensures every screenshot in the set has the same device frame rendering, text treatment, background style, and overall visual quality — so when viewed side-by-side in the App Store, they look like a cohesive professional set.

For each benefit + screenshot pair, generate **3 enhanced versions in parallel** so the user can pick the best one.

**Step 0: Save brand colour to memory**

Before generating any scaffolds, save the confirmed brand colour to the Claude Code memory system. Create or update the benefits memory file (e.g., `aso_benefits.md`) to include the brand colour name and hex code. This ensures the colour persists across conversations and is available immediately if the user resumes later.

**Step 1: Confirm the font**

The font is auto-detected based on the target platform via the `--device` flag:

| Platform | Device flags | Default font | Alternative |
|----------|-------------|-------------|-------------|
| **iOS** | `iphone-6.7`, `iphone-6.5`, `iphone-6.9` | **SF Pro Display Black** (macOS) or Noto Sans Black (Linux) | Inter Black, Helvetica Neue Bold |
| **Android** | `android` | **Roboto Black** | Noto Sans Black, Google Sans |

- **iOS screenshots** should use Apple's SF Pro font family for native feel. The default is `SF-Pro-Display-Black.otf` which ships with macOS. On Linux, fall back to Noto Sans Black.
- **Android screenshots** should use Roboto (Google's system font). The default is `Roboto-Black.ttf`. If not installed, download from [Google Fonts](https://fonts.google.com/specimen/Roboto) or use `--font` to pass a path.

If the user wants a different font, they can provide a filename (e.g., `Inter-Black.otf`) or a full path (e.g., `/usr/share/fonts/truetype/noto/NotoSans-Black.ttf`). Save the chosen font to memory alongside the brand colour so it persists across conversations.

If the user says "default" or doesn't have a preference, omit the `--font` flag — the script picks the right font automatically based on device type.

**Step 2: Create the scaffold with mockup_compose.py**

The skill can live in a Codex or Claude Code skill discovery directory. Resolve it from the runtime-specific or shared locations. Set up a venv and install Pillow if not already done:

```bash
if [ -d "$HOME/.agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.agents/skills/aso-appstore-screenshots"
elif [ -d ".agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.agents/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.claude/skills/aso-appstore-screenshots"
elif [ -d ".claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.claude/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.codex/skills/aso-appstore-screenshots"
elif [ -d ".codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.codex/skills/aso-appstore-screenshots"
else
  echo "aso-appstore-screenshots is not installed in a supported skill directory" >&2
  exit 1
fi

# Create venv and install Pillow if needed (one-time setup)
if [ ! -f "$SKILL_DIR/.venv/bin/python3" ]; then
  python3 -m venv "$SKILL_DIR/.venv" && \
  "$SKILL_DIR/.venv/bin/pip" install Pillow
fi
VENV_PYTHON="$SKILL_DIR/.venv/bin/python3"
```

The mockup_compose.py script lives in the skill directory. Run it to create the deterministic base screenshot. If the user chose a custom font, pass `--font "filename.otf"` to each mockup_compose.py call. If using the default, omit `--font`.

**IMPORTANT — Batch all 3 scaffolds into a single Bash call** to minimize permission prompts. Chain the commands with `&&` so the user only needs to approve once:

```bash
if [ -d "$HOME/.agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.agents/skills/aso-appstore-screenshots"
elif [ -d ".agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.agents/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.claude/skills/aso-appstore-screenshots"
elif [ -d ".claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.claude/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.codex/skills/aso-appstore-screenshots"
elif [ -d ".codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.codex/skills/aso-appstore-screenshots"
else
  echo "aso-appstore-screenshots is not installed in a supported skill directory" >&2
  exit 1
fi
DEVICE="iphone-6.7" && \
mkdir -p screenshots/01-[benefit-slug] screenshots/02-[benefit-slug] screenshots/03-[benefit-slug] && \
$VENV_PYTHON "$SKILL_DIR/mockup_compose.py" \
  --bg "[HEX CODE]" --verb "[VERB 1]" --desc "[DESC 1]" \
  --font "[FONT_FILE or omit flag]" \
  --frame-color "[HEX FRAME COLOR or omit for default]" \
  --screenshot [path/to/screenshot-1.png] \
  --device $DEVICE \
  --output screenshots/01-[benefit-slug]/scaffold.png && \
$VENV_PYTHON "$SKILL_DIR/mockup_compose.py" \
  --bg "[HEX CODE]" --verb "[VERB 2]" --desc "[DESC 2]" \
  --font "[FONT_FILE or omit flag]" \
  --frame-color "[HEX FRAME COLOR or omit for default]" \
  --screenshot [path/to/screenshot-2.png] \
  --device $DEVICE \
  --output screenshots/02-[benefit-slug]/scaffold.png && \
$VENV_PYTHON "$SKILL_DIR/mockup_compose.py" \
  --bg "[HEX CODE]" --verb "[VERB 3]" --desc "[DESC 3]" \
  --font "[FONT_FILE or omit flag]" \
  --frame-color "[HEX FRAME COLOR or omit for default]" \
  --screenshot [path/to/screenshot-3.png] \
  --device $DEVICE \
  --output screenshots/03-[benefit-slug]/scaffold.png
```

Set `DEVICE` to the appropriate profile:
- iOS: `iphone-6.7` (default), `iphone-6.5`, or `iphone-6.9`
- Android: `android`

This outputs platform-correct PNGs with:
- Bold white headline text (verb auto-sized to fit canvas width)
- Platform mockup frame (`iPhone` for iOS, `Samsung S24 Ultra` for Android)
- Simulator screenshot composited inside the frame
- Solid background colour

The scaffolds are internal intermediates — do NOT show them to the user or ask for confirmation.

If the user selected **Static Normal Background**, skip Step 3 and proceed to resizing/validation/output.
If the user selected **Image generation**, continue with Step 3.

Default enhancement behavior is background-first:
- no changes to headline/descriptor
- no changes to device frame
- no changes to screenshot pixels (including in-phone callouts/labels/chips)
- only atmospheric/background treatment is varied across versions

Only when the user explicitly requests extra foreground effects, allow foreground breakouts and card pop-outs.

**Step 3: Enhance with image generation backend (3 versions in parallel)** — only run this step in Image generation mode.

Make **3 parallel `edit_image` calls**. The parallel execution is critical — always fire all 3 calls in a single message, never sequentially.

For each of the 3 calls, use:
- `prompt`: Enhancement instructions (see prompt templates below — different for first vs subsequent screenshots)
- `images`: See below for which images to include
- `outputPath`: Different path for each version:
  - `./screenshots/01-[benefit-slug]/v1.jpg`
  - `./screenshots/01-[benefit-slug]/v2.jpg`
  - `./screenshots/01-[benefit-slug]/v3.jpg`

#### Direct image generation — LAST RESORT ONLY (skip mockup_compose.py scaffold)

> **⚠️ DO NOT USE THIS BY DEFAULT. Only use when the user explicitly says "skip scaffolding" or asks for a direct image-gen pass.**
> **ALSO: only run this mode when the user explicitly requests skipping the scaffold.**
>
> **Why the scaffold is preferred:** mockup_compose.py guarantees pixel-perfect headline text and preserves the exact simulator screenshot content. Image generators may re-render text from scratch and may alter the phone screen content (inventing UI, changing colors, removing data). The two-stage scaffold → enhancement approach avoids this.
>
> **When to use this:** Only when the user explicitly requests to skip the scaffold step.

To use this mode:
1. Pass the raw simulator screenshot directly to the selected backend (`generate_image` for Gemini MCP, `$imagegen` for Codex)
2. The backend generates its own device frame and content (which may be inconsistent)
3. Generate all in parallel — no scaffold step needed

**Prompt template:**

```
Create a premium dark-mode App Store marketing screenshot for a [APP TYPE] app called [APP NAME].

INSTRUCTIONS:
- Take the input simulator screenshot and place it inside a realistic platform mockup (iPhone 15 Pro for iOS, S24 Ultra for Android)
- The phone must be centered on the canvas, positioned high
- The screenshot content must fit PERFECTLY inside the phone screen — no cropping, no distortion
- Use a dark gradient background: near-black #090D0F blending to dark teal #062B2B
- Add subtle abstract curved ribbon shapes in dark teal with low opacity
- Add soft radial cyan glow behind the phone mockup
- Add vignette darkening at the edges
- Large bold white headline "[VERB]" stacked above "[DESCRIPTOR]" at the top in SF Pro Black weight
- [BREAKOUT ELEMENTS — describe specific UI cards to pop out from phone]
- Phone can overlap with headline slightly
- Phone bottom can crop off the canvas edge for dramatic depth

IMPORTANT — NAVBAR STAYS INSIDE:
- The bottom navigation bar must REMAIN INSIDE the phone screen
- Do NOT break out, extend, or move the navigation bar outside the device frame

Style: Futuristic premium health-tech aesthetic, glassmorphism, neon cyan/teal highlights #00CDEB, clean and polished.
```

**Breakout elements — key cards only (navbar stays inside):**
- Key UI cards (progress circles, stat cards, charts) can break out from the phone — extending beyond BOTH left and right edges of the device frame, overlapping the bezel on both sides, floating in front with a soft drop shadow
- The bottom navigation bar must ALWAYS stay inside the phone — never break it out
- The main headline text stays at the top, not overlapped by breakouts

#### First screenshot (no approved template yet)

Use only the scaffold as input:
- `images`: The scaffold via `filePath` pointing to `screenshots/01-[benefit-slug]/scaffold.png`

**First screenshot prompt template:**

See `styles/dark_gradient_prompt.md` for the base enhancement prompt. Set `[BREAKOUT]` to `No breakout needed.` by default. Only replace it with a concrete card/panel when the user explicitly requests foreground effects.

#### Subsequent screenshots (after first is approved)

Use **two images** as input:
1. The **scaffold** for this benefit (`screenshots/0N-[benefit-slug]/scaffold.png`) — defines the layout
2. The **first approved screenshot** (`screenshots/final/01-[first-benefit-slug].jpg`) — defines the style template

**Subsequent screenshot prompt template:**

```
You are creating the next screenshot in an App Store screenshot SET. It must match the style reference exactly.

TWO IMAGES:
- FIRST image: The SCAFFOLD — layout reference. Shows the headline text and iPhone mockup with app screenshot inside. Use this for WHERE everything goes.
- SECOND image: The STYLE TEMPLATE — visual reference. Match its dark gradient background, cyan glow, vignette, phone shadow, and overall aesthetic exactly.

DO NOT TOUCH:
- The headline text from the scaffold — keep all text exactly as is, same font, same size, same position
- The iPhone device frame — keep exactly as is
- The app screenshot inside the phone — keep exactly as is, do not redraw or alter

MATCH FROM STYLE TEMPLATE:
- Dark gradient background (near-black to teal)
- Radial cyan glow behind the phone
- Black vignette at top and bottom
- Phone drop shadow
- Text shadow for legibility

OPTIONAL — ONE BREAKOUT ELEMENT:
[BREAKOUT — describe the specific UI card to extract, or write "No breakout needed." (default).]

Style: Clean, minimal, premium dark-mode. Less is more.
No sparkles, no floating icons, no particles, no extra decorative elements.
No watermarks, no extra text, no app store UI chrome.
```

**IMPORTANT — Consistency enforcement**: The scaffold guarantees consistent layout. The style template guarantees consistent visual treatment. If image generation changes the text, layout, or deviates from the style template, regenerate.

**Step 4: IMMEDIATELY crop and resize ALL 3 versions to App Store dimensions**

⚠️ **You MUST run this immediately after all 3 `edit_image` calls complete. Do NOT show the user any image before running this. The raw image-gen output is always the wrong dimensions for App Store Connect.**

**CRITICAL — Use exactly ONE Bash tool call for all 3 crop/resize operations.** Do NOT make 3 separate Bash calls. Do NOT use parallel Bash calls. Use the single command below so the user only sees one permission prompt.

**Option A — Cross-platform (recommended, works on macOS/Linux/Windows):**

```bash
SKILL_DIR="$HOME/.claude/skills/aso-appstore-screenshots" && \
if [ ! -f "$SKILL_DIR/.venv/bin/python3" ]; then
  python3 -m venv "$SKILL_DIR/.venv" && "$SKILL_DIR/.venv/bin/pip" install Pillow
fi && \
"$SKILL_DIR/.venv/bin/python3" "$SKILL_DIR/resize.py" \
  --width 1290 --height 2796 \
  screenshots/01-[benefit-slug]/v1.jpg \
  screenshots/01-[benefit-slug]/v2.jpg \
  screenshots/01-[benefit-slug]/v3.jpg
```

The resize.py script (Pillow-based) crops to the correct aspect ratio (center-crop with top edge preserved so headlines stay put) and resizes to exact pixel dimensions. Each resized image is saved alongside the original with a `-resized` suffix (e.g., `v1-resized.jpg`).

**Option B — macOS only (using sips):**

```bash
TARGET_W=1290 && TARGET_H=2796 && \
for INPUT in screenshots/01-[benefit-slug]/v1.jpg screenshots/01-[benefit-slug]/v2.jpg screenshots/01-[benefit-slug]/v3.jpg; do
  OUTPUT="${INPUT%.jpg}-resized.jpg"
  cp "$INPUT" "$OUTPUT"
  W=$(sips -g pixelWidth "$OUTPUT" | tail -1 | awk '{print $2}')
  H=$(sips -g pixelHeight "$OUTPUT" | tail -1 | awk '{print $2}')
  CROP_W=$(python3 -c "print(round($H * $TARGET_W / $TARGET_H))")
  OFFSET_X=$(python3 -c "print(round(($W - $CROP_W) / 2))")
  sips --cropOffset 0 $OFFSET_X --cropToHeightWidth $H $CROP_W "$OUTPUT"
  sips -z $TARGET_H $TARGET_W "$OUTPUT"
  echo "--- $OUTPUT ---"
  sips -g pixelWidth -g pixelHeight "$OUTPUT"
done
```

Both options crop to the correct aspect ratio (top-center aligned, sides trimmed equally, top edge preserved) and resize to exact pixel dimensions. The resized image is saved as a separate file with `-resized` appended.

Target dimensions per display size — adjust `TARGET_W` and `TARGET_H`:
- iPhone 6.5": `TARGET_W=1242 TARGET_H=2688`
- iPhone 6.7" (default): `TARGET_W=1290 TARGET_H=2796`
- iPhone 6.9": `TARGET_W=1320 TARGET_H=2868`
- Android Phone: `TARGET_W=1080 TARGET_H=2400`

**Step 5: Review all 3 versions with the user**

Present all 3 **resized** versions (the `-resized.jpg` files) to the user using the Read tool. Never show the raw image-gen output — always show the post-processed versions.

Label them clearly as **Version 1**, **Version 2**, and **Version 3** and ask the user to pick their favourite or request changes.

**Step 6: Iterate if needed**

If the user wants changes, use `edit_image` with **three images** as input:
1. The **scaffold** (`scaffold.png`) — anchors the layout (text position, device placement, screenshot)
2. The **style template** (the first approved screenshot from `screenshots/final/01-*.jpg`) — defines the device frame rendering and overall visual style that must be consistent across the entire set
3. The **approved design** (the version the user liked best for this specific screenshot) — anchors the creative direction and breakout element approach

The prompt should reference all three:
```
Here are three reference images, each with a distinct purpose:

- FIRST image: The SCAFFOLD — use this as the definitive guide for layout: text position, device frame placement, and the app screenshot on screen. This defines WHERE everything goes.
- SECOND image: The STYLE TEMPLATE — this is the first approved screenshot in the set. The device frame rendering, text treatment, and overall visual style MUST match this exactly. This defines HOW the screenshot should look to maintain consistency across the set.
- THIRD image: The APPROVED DESIGN DIRECTION — this is the version the user liked best for this specific screenshot. Match its creative direction, breakout element approach, and secondary elements.

Generate a new version that keeps the layout from the scaffold, the device frame and visual style from the style template, and the creative direction from the approved design, with these changes:
[USER'S REQUESTED CHANGES]
```

This prevents drift (scaffold keeps layout locked), maintains set-wide consistency (style template keeps device frame and visual treatment identical), and preserves the creative direction the user already approved.

When iterating, generate **3 versions in parallel** again (3 parallel `edit_image` calls in a single message). Then **immediately run the Step 3 crop/resize (Option A or B) on all 3 in a single Bash call** before showing the user.

Repeat until the user is happy.

**Step 7: Copy approved version to `final/`**

Once the user picks a winner, copy the resized version to `screenshots/final/`:

```bash
mkdir -p screenshots/final
cp "screenshots/01-[benefit-slug]/v2-resized.jpg" "screenshots/final/01-[benefit-slug].jpg"
```

This keeps `final/` clean — only approved, App Store-ready screenshots, one per benefit, numbered in order. Then move to the next benefit.

### Determine Brand Colour (Automatic)

```text
.agents/
  aso-appstore-screenshots/
    state.json
```
screenshots/
  01-track-card-prices/       ← working versions for benefit 1
    scaffold.png              ← deterministic mockup_compose.py output (text + frame + screenshot)
    v1.jpg                    ← enhanced version 1 (image generation output)
    v1-resized.jpg            ← cropped/resized to App Store dimensions
    v2.jpg
    v2-resized.jpg
    v3.jpg
    v3-resized.jpg
  02-search-any-card/         ← working versions for benefit 2
    scaffold.png
    v1.jpg
    ...
  final/                      ← approved screenshots, ready to upload
    01-track-card-prices.jpg
    02-search-any-card.jpg
```

The `final/` folder is the only one the user needs to care about — it contains one approved, App Store-ready screenshot per benefit, numbered in order. The benefit subfolders contain all working versions and can be ignored or deleted after the set is complete.

Also tell the user exactly which store display size slot each screenshot fits into (App Store Connect display size for iOS, or Google Play phone/tablet for Android).

### Save to Memory

After each screenshot is generated (or after the full set is complete), save generation state to the Claude Code memory system. Create or update a memory file (e.g., `aso_generated_screenshots.md`) with:

- **Brand colour**: name + hex code
- **Platform**: iOS / Android / both
- **Target display size**: e.g., iPhone 6.7" (1290x2796) or Android Phone (1080x1920)
- **Device profile used**: e.g., `iphone-6.7` or `android`
- **For each generated screenshot**:
  - Benefit headline (ACTION VERB + DESCRIPTOR)
  - Benefit subfolder path (e.g., `screenshots/01-[benefit-slug]/`)
  - Which version the user chose (v1, v2, or v3)
  - Final file path (e.g., `screenshots/final/01-[benefit-slug].jpg`)
  - Simulator screenshot used (file path)
  - Breakout elements described in the prompt
  - Status: generated / approved / needs-redo
  - Any user feedback or change requests noted

Update this memory **incrementally** — after each screenshot is approved, add it. Don't wait until the end. This way if the conversation is interrupted mid-set, the user can resume from the last completed screenshot.

### Showcase Image

Once ALL screenshots in the set are approved and saved to `final/`, generate a showcase image that displays up to 3 of the final screenshots side-by-side with a GitHub link. Use the showcase.py script in the skill directory:

```bash
if [ -d "$HOME/.agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.agents/skills/aso-appstore-screenshots"
elif [ -d ".agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.agents/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.claude/skills/aso-appstore-screenshots"
elif [ -d ".claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.claude/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.codex/skills/aso-appstore-screenshots"
elif [ -d ".codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.codex/skills/aso-appstore-screenshots"
else
  echo "aso-appstore-screenshots is not installed in a supported skill directory" >&2
  exit 1
fi
if [ ! -f "$SKILL_DIR/.venv/bin/python3" ]; then
  python3 -m venv "$SKILL_DIR/.venv" && "$SKILL_DIR/.venv/bin/pip" install Pillow
fi
"$SKILL_DIR/.venv/bin/python3" "$SKILL_DIR/showcase.py" \
  --screenshots screenshots/final/01-*.jpg screenshots/final/02-*.jpg screenshots/final/03-*.jpg \
  --github "github.com/akshaynexus" \
  --output screenshots/showcase.png
```

Show the showcase image to the user using the Read tool. This is a shareable preview of the full screenshot set.

---

## KEY PRINCIPLES

- **Benefits over features**: "BOOST ENGAGEMENT" not "ADD SUBTITLES TO VIDEOS"
- **Specific over generic**: "TRACK TRADING CARD PRICES" not "MANAGE YOUR STUFF"
- **Action-oriented**: Every headline starts with a strong verb
- **User-centric**: Frame everything from the downloader's perspective
- **Conversion-focused**: Every decision should answer "will this make someone tap Download?"
- The first screenshot is the most important — it must communicate the single biggest reason to download
- Screenshots should tell a story when swiped through — each one reveals a new compelling reason
- Always pair the most visually impactful simulator screenshot with the most important benefit
- Never use an empty state, loading screen, or settings page as a screenshot — show the app at its best
