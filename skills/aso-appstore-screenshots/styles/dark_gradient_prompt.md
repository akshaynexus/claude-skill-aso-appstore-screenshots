# Dark Gradient Style — Prompt Templates

## Font Guidance

| Platform | Verb (line 1) | Descriptor (line 2) |
|----------|--------------|---------------------|
| **iOS** | SF Pro Display Black (`SFCompact.ttf`) | SF Pro Text Regular (`SFNS.ttf`) |
| **Android** | Roboto Black (`Roboto-Black.ttf`) | Roboto Regular (`Roboto-Regular.ttf`) |

The scaffold handles typography automatically via `mockup_compose.py`; image generators should NOT redraw or alter the text.

---

## Enhancement Prompt (Two-Stage — Scaffold → edit_image)

Use this when enhancing a compose.py scaffold with an image-generation backend `edit_image` in **Image generation** mode. The scaffold already has correct text, device frame, screenshot, and in-device callouts/labels. Default mode is background-only styling; optional breakout elements are only used when explicitly requested.

### Base Prompt

```
This is a SCAFFOLD for an App Store screenshot. Your job is to add background styling and improve atmosphere. Do NOT change anything else.

DO NOT TOUCH:
- The headline text — keep all text exactly as is, same font, same size, same position
- The iPhone device frame — keep exactly as is
- The app screenshot inside the phone — keep exactly as is, do not redraw, alter, or add to the screen content
- Keep in-phone callouts, chips, labels, and UI text exactly as captured from the screenshot
- Do not add text, phone content, frame, or layout changes.

ADD THESE:
- Dark gradient background: near-black #080808 blending to dark teal #0A1A1D
- Soft radial cyan glow (#10D6E6) behind the phone — subtle, not overpowering
- Black vignette at top and bottom edges
- Soft drop shadow behind the phone

OPTIONAL — ONE BREAKOUT ELEMENT (only for explicit "extra effects" requests):
[BREAKOUT — describe the specific UI card/panel from the app screen to extract and float in front of the phone, extending beyond both left and right edges with a drop shadow. Or write "No breakout needed."]

Style: Clean, minimal, premium dark-mode. Less is more. The phone and text are the heroes.
No sparkles, no floating icons, no particles, no extra decorative elements.
```

---

## Style Reference Values

- **Background dark**: `#080808`
- **Background teal**: `#0A1A1D`
- **Accent cyan**: `#10D6E6`
- **Accent glow intensity**: Soft, not neon-bright
- **Vignette**: Heavy black at top/bottom 10%
- **Phone shadow**: 50% opacity black, 50px blur
