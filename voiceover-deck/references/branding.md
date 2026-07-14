# Branding the deck

## The default palette

The template's `:root { ... }` block (top of the `<style>` section, marked "BRAND CONFIG") ships with a neutral slate/indigo placeholder palette, and `DECK.logo` renders a plain text wordmark by default. It's a tasteful, professional-looking starting point — nobody's real brand, just something that looks tidy out of the box.

**Tokens:**
| Token | Default value | Used for |
|---|---|---|
| `--navy` | `#1E293B` | ink, dark-slide background |
| `--navy-deep` | `#0F172A` | page background, deepest dark |
| `--turquoise` | `#6366F1` | primary accent, CTA button, progress bar |
| `--blue` | `#0EA5E9` | secondary accent (used via `data-accent="blue"` on alternating slides) |
| Headings | DM Serif Display | via `--font-serif` |
| Body | Inter | via `--font-sans` |

The token names (`--navy`, `--turquoise`, `--blue`) are just labels left over from the original build — they're really "dark ink", "primary accent" and "secondary accent". You can rename them if you like, or just change their values; either way, nothing else in the stylesheet needs to change.

## Setting your own brand

Two edits, no CSS restructuring needed:

1. **Colours and type** — in the `:root` block, change `--navy`, `--navy-deep`, `--turquoise`, `--turquoise-hover`, `--blue`, `--font-serif`, `--font-sans` (and add the new Google Fonts `<link>` in `<head>` if the fonts differ from DM Serif Display/Inter). Everything else in the stylesheet references these variables, so the whole deck reskins from this one block. Note that a handful of glow/shadow effects elsewhere in the stylesheet use the accent colours as literal `rgba(...)` values rather than `var(--turquoise)` — if you want those touches to match a new accent colour exactly, search the stylesheet for `rgba(99,102,241` (the default indigo accent) and `rgba(14,165,233` (the default sky-blue secondary accent) and update them to match your new colour. This is a nice-to-have, not required — the deck works fine either way.

2. **Logo** — in the `DECK.logo` object:
   - To use an image: base64-encode your logo (PNG or SVG) and paste it into `logoDataUri` as `data:image/png;base64,...`. It renders through a `brightness(0) invert(1)` CSS filter, so use a logo with enough contrast that a pure-white silhouette still reads correctly — a wordmark or icon with clean, connected shapes works better than a logo with fine internal detail. Check your source image isn't a version that gets clipped or cropped oddly when scaled down small — test it at the actual title-slide size before locking it in.
   - To skip an image entirely: leave `logoDataUri` empty and set `logoText` — the template automatically renders a serif text wordmark instead using `--font-serif`. This is the default and needs no image at all.

Nothing else — slide layout, the player engine, keyboard shortcuts, responsive behaviour — needs to change for a rebrand.
