# Dark Gradient Style — Prompt Templates

## Font Guidance

| Platform | Verb (line 1) | Descriptor (line 2) |
|----------|--------------|---------------------|
| **iOS** | SF Pro Display Black (`SFCompact.ttf`) | SF Pro Text Regular (`SFNS.ttf`) |
| **Android** | Roboto Black (`Roboto-Black.ttf`) | Roboto Regular (`Roboto-Regular.ttf`) |

The scaffold handles typography automatically via `mockup_compose.py`. Nano Banana should NOT redraw or alter the text.

---

## Enhancement Prompt (Two-Stage — Scaffold → edit_image)

Use this when enhancing a compose.py scaffold with Nano Banana `edit_image`. The scaffold already has correct text, device frame, and screenshot. Nano Banana only adds background styling and optional breakout elements.

### Base Prompt (copy and customize per screenshot)

```
This is a SCAFFOLD for an App Store screenshot. Your job is to add background styling and ONE optional breakout element. Do NOT change anything else.

DO NOT TOUCH:
- The headline text — keep all text exactly as it is, same font, same size, same position
- The iPhone device frame — keep exactly as is
- The app screenshot inside the phone — keep exactly as is, do not redraw, alter, or add to the screen content

ADD THESE:
- Dark gradient background: near-black #080808 blending to dark teal #0A1A1D
- Soft radial cyan glow (#10D6E6) behind the phone — subtle, not overpowering
- Black vignette at top and bottom edges
- Soft drop shadow behind the phone

OPTIONAL — ONE BREAKOUT ELEMENT (only if it reinforces the headline):
[BREAKOUT — describe the specific UI card to extract, or write "No breakout needed"]

Style: Clean, minimal, premium dark-mode. Less is more. The phone and text are the heroes.
No sparkles, no floating icons, no particles, no extra decorative elements.
```

### Per-Screenshot Breakout Descriptions

#### 1. FORECAST YOUR WEIGHT LOSS
```
BREAKOUT: The weight trend chart card (showing forecast line, dosage phase colors, target line) — extract from the phone screen and float it in front, extending beyond both left and right edges of the device frame, with subtle drop shadow. Frosted glass border effect.
```

#### 2. MANAGE PEN INVENTORY
```
BREAKOUT: The "Current Progress 15 mg" card with pen inventory (1/4 dose, 5/8 doses, 2 pens) — extract and float in front, extending beyond both edges, drop shadow. Frosted glass border.
```

#### 3. TRACK EVERY INJECTION
```
BREAKOUT: The medication concentration chart (teal waveform showing current level) — extract and float in front, extending beyond both edges, drop shadow.
```

#### 4. REACH YOUR GOALS
```
BREAKOUT: The "Progress Towards Goal" card with 42% progress circle and stats (Lost: 20.1 kg, To Goal: 28.9 kg) — extract and float in front, extending beyond both edges, drop shadow. Frosted glass border.
```

#### 5. LOG SIDE EFFECTS
```
BREAKOUT: The "Most Common Effects" section with colored badges (yellow Food Noise, purple Injection Site Reaction) — extract and float in front, extending beyond both edges, drop shadow.
```

---

## Style Reference Values

- **Background dark**: `#080808`
- **Background teal**: `#0A1A1D`
- **Accent cyan**: `#10D6E6`
- **Accent glow intensity**: Soft, not neon-bright
- **Vignette**: Heavy black at top/bottom 10%
- **Phone shadow**: 50% opacity black, 50px blur
