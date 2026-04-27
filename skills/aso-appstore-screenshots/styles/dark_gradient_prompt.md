# Dark Gradient Style — Prompt Templates

## Font Guidance

| Platform | Verb (line 1) | Descriptor (line 2) |
|----------|--------------|---------------------|
| **iOS** | SF Pro Display Black (`SFCompact.ttf`) | SF Pro Text Regular (`SFNS.ttf`) |
| **Android** | Roboto Black (`Roboto-Black.ttf`) | Roboto Regular (`Roboto-Regular.ttf`) |

The scaffold handles typography automatically via `mockup_compose.py`. Nano Banana should NOT redraw or alter the text.

---

## Enhancement Prompt (Two-Stage — Scaffold → edit_image)

Use this when enhancing a mockup_compose.py scaffold with Nano Banana `edit_image`. The scaffold already has correct text, device frame, and screenshot. Nano Banana only adds background styling and optional breakout elements.

### Base Prompt

```
This is a SCAFFOLD for an App Store screenshot. Your job is to add background styling, abstract design elements, and ONE optional breakout element. Do NOT change anything else.

DO NOT TOUCH:
- The headline text — keep all text exactly as is, same font, same size, same position
- The iPhone device frame — keep exactly as is
- The app screenshot inside the phone — keep exactly as is, do not redraw, alter, or add to the screen content

ADD THESE - Background Layer:
- Deep dark gradient: near-black #080808 at top to rich dark blue #0A1428 at bottom
- Abstract geometric shapes floating in background: soft blurred circles, subtle curved lines, diagonal streaks — use muted teal/cyan tones (#0D3B4A, #145B6D) at very low opacity (5-15%)
- Particle effects: small subtle dots scattered across the background, barely visible
- Soft radial glow behind the phone in accent color

ADD THESE - Foreground Layer (subtle):
- Very subtle light rays or beam emanating from behind the phone area
- Minimal floating UI elements or floating shapes near the phone edges (low opacity, 10-20%)
- Soft vignette darkening at the very top and bottom edges

OPTIONAL — ONE BREAKOUT ELEMENT (only if it strongly reinforces the headline):
- A key UI card from the app screen that extends beyond both left and right edges of the phone with a soft drop shadow
- Or write "No breakout needed."

Style: Premium dark-mode with depth and dimension. Use layers effectively — background elements should feel atmospheric, foreground elements should be minimal.
- DO add: abstract shapes, particles, subtle gradients, depth
- DO NOT add: sparkles, neon elements, excessive decoration, watermarks, extra text
```

---

## Style Reference Values

- **Background dark**: `#080808`
- **Background blue**: `#0A1428`
- **Accent teal muted**: `#0D3B4A`
- **Accent teal light**: `#145B6D`
- **Accent glow**: soft cyan `#10D6E6` at low intensity
- **Particle opacity**: 5-15%
- **Vignette**: Heavy black at top/bottom 10%
- **Phone shadow**: 50% opacity black, 50px blur
