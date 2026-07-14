---
name: voiceover-deck
description: Build a narrated, self-playing web slide deck — a single HTML file that advances itself with voiceover, on-screen captions and a control bar (play/pause, prev/next, voiceover toggle, script toggle, fullscreen), openable by double-click or deployable as one shareable link. Dual voiceover mode (cloned-voice MP3s per slide, falling back automatically to the browser's built-in speechSynthesis so it always plays), reveal animations, keyboard shortcuts, a progress bar, and responsive/accessible layout. Use whenever the user asks for a narrated deck, a voiceover presentation, a self-playing slide deck, "a deck I can send as a link", a talking slide deck, voice-over slides, an auto-playing pitch/explainer deck, or wants to reverse-engineer or recreate a tiiny.site-style narrated web deck. Ships with a neutral placeholder brand, swappable via one config block for any project.
---

# Voiceover Deck

## What this builds

A single self-contained `index.html` file: a slide deck that plays itself. Each slide reveals with an animation while a voiceover narrates it (a cloned-voice MP3 if one exists, otherwise the browser reads it aloud automatically), then advances to the next slide. The viewer can also pause, step back and forth, toggle the voiceover, show an on-screen script/caption, and go fullscreen. No build step, no server required — it opens by double-click, or can be dropped onto a static host as one shareable link.

`assets/deck-template.html` is the engine and content template, ready to use as-is. Never edit that file in place — copy it to your destination and build from the copy.

## Workflow

### 1. Gather the brief

Ask (briefly, not all at once) for: the deck's topic/purpose, who it's for, and a rough slide list (title, a handful of key points, a proof/stats slide if there are numbers worth showing, a close/CTA). Five to nine slides is the sweet spot — long enough to say something, short enough that nobody drops off.

**Set the brand before building.** The template ships with a neutral placeholder palette and a plain text wordmark, so it always looks tidy out of the box — but it isn't anyone's real brand yet. Ask what colours, fonts and logo the deck should use (or confirm the defaults are fine for a quick demo), then set them in the BRAND CONFIG block described below. See the Brand section for the full swap procedure.

### 2. Write the narration scripts

For every slide, write two things that can differ:
- **On-screen text** — the headline/support copy the viewer reads.
- **Spoken narration** — the sentences a voice will actually say aloud.

Rules for the spoken narration:
- Write it in full sentences, spoken-aloud style — not a copy of the headline.
- **Spell out numbers and symbols**: "thirty-six" not "36", "plus eighty-six" not "+86", "four-point-four seconds" not "4.4s". TTS and voice-clone tools mispronounce digits and symbols far more often than words.
- If a brand or product word gets mispronounced by the voice tool, **respell it phonetically only in the text that's actually sent to the voice tool** (the `tts_text` field in `voiceover.json`, or the text pasted into ElevenLabs' website if using the manual method) — the on-screen text and `DECK.slides[].narration` stay correctly spelled everywhere else. See `references/voice-cloning.md` for the technique.

### 3. Generate the deck

Copy the template, don't edit it in place:

```
cp assets/deck-template.html <destination>/index.html
```

Open the copy and edit the `DECK` object near the top of the `<script>` block. It is one JavaScript object with:
- `logo` — wordmark (a neutral text placeholder by default; see `references/branding.md` to set your own).
- `slides[]` — an ordered array. Each slide has a `type` (`title`, `content`, `stats`, `convergence`, or `close`) and the fields that type needs (headline, support line, proof chip, tags, stats numbers, convergence chips, narration, etc). Every field is commented in the template. Copy an existing slide of the right type and edit its text — don't hand-write `<section>` markup, the player engine depends on the DOM shape the renderer produces.

The brand's colours, fonts and spacing live in one `:root { ... }` block at the top of the `<style>` section, clearly marked "BRAND CONFIG". Change the hex values and the two `--font-serif`/`--font-sans` lines to reskin the whole deck — nothing else in the CSS needs to change.

The audio manifest (`audio/slide-01.mp3`, `slide-02.mp3`, ...) is generated automatically from however many slides are in `DECK.slides` — adding or removing a slide re-numbers it without any manual editing.

**Also write `voiceover.json` next to the copy's `index.html`** — the narration manifest the voice generator reads (see step 5). It's an ordered array, one entry per slide, built straight from each slide's `narration` field:

```json
[
  { "slide": 1, "tts_text": "Placeholder narration for the title slide..." },
  { "slide": 2, "tts_text": "Placeholder narration for the intro slide..." }
]
```

`slide` numbers match the deck's audio manifest numbering (1-indexed, same order as `DECK.slides`). `tts_text` is the spoken string — normally identical to that slide's `narration` field, except where a brand or product word needs the phonetic-respelling trick (see `references/voice-cloning.md`): the on-screen caption stays correctly spelled in `DECK.slides[].narration`, and only `voiceover.json`'s `tts_text` carries the respelled version fed to the voice generator.

### 4. It plays immediately, with no voice recording

Open the file in a browser and it already works: every slide is narrated by the browser's own built-in voice (`speechSynthesis`). This is the fallback that's always on — there is nothing to configure to get a working, narrated deck on the first try.

### 5. Generate the voiceover automatically (default)

With `ELEVENLABS_API_KEY` set once in this project's `.env` (see `references/voice-cloning.md` for the one-time setup), voicing the whole deck is a single command, no website visits:

```
python scripts/generate_voice.py --dir <destination>
```

(run that from wherever this skill folder lives — adjust the path to `generate_voice.py` to match, and use whichever Python command your setup expects, e.g. `python3` or a virtual environment's `python.exe`)

It reads `voiceover.json`, calls the ElevenLabs API once per slide, and writes `audio/slide-01.mp3` … `slide-NN.mp3` straight into the deck folder — matching filenames the deck template already looks for, so there's no code change. Regenerate a single slide after editing its script with `--slide N`; find or confirm a voice id with `--list-voices`; preview cost with `--dry-run` before spending credits. Full flag reference and the one-time key setup are in `references/voice-cloning.md`.

If there's no API key yet (or the user prefers it), the original manual method — paste each script into the ElevenLabs website and download the MP3 by hand — still works exactly as before and is documented as the fallback in the same reference file. Either way, the deck plays the MP3 for any slide that has one and silently falls back to the browser voice for any slide that doesn't, so it's safe to add voice clips a few at a time.

### 6. Optional: deploy to a shareable link

If the user wants a link they can send rather than a file to open locally, see `references/deploy-and-iso.md` for the Vercel deploy method, how to keep local-only helper files (README, path-bearing notes) off the public site, and how to verify the live URL is genuinely public with no stray files exposed.

## Brand

**Set your brand in the BRAND CONFIG block.** The template ships with a neutral slate/indigo placeholder palette (DM Serif Display headings, Inter body) and a plain text wordmark, so it always looks tidy even before you touch it. To make it yours, change the hex values and font names in the `:root` block marked "BRAND CONFIG", and either point `DECK.logo.logoDataUri` at your own embedded image or leave it empty and set `DECK.logo.logoText` (a serif text wordmark renders automatically). `references/branding.md` covers this swap in full.

## Guardrails (baked in, always check before content is finalised)

- **No real client or supplier names.** Use only generic or fictional examples in any deck content.
- **Public, approved figures only** for any stat or claim (satisfaction scores, response times, years trading, etc.) — nothing internal, unpublished, or confidential.
- **Board-appropriate tone.** These decks are the kind of thing that gets forwarded; write and design accordingly.
- **Get the right sign-off before anything goes public** — a Vercel link, an email attachment, anything leaving your own machine. Draft and preview freely; just don't publish or send something that would embarrass someone if forwarded. See `references/deploy-and-iso.md` for the full checklist.

## Resources

- `assets/deck-template.html` — the deck engine and content template. Copy this, don't edit the original.
- `scripts/generate_voice.py` — calls the ElevenLabs API directly to generate a deck's narration MP3s from `voiceover.json`. Run with your own Python: `python scripts/generate_voice.py --dir <deck-folder>`. `--list-voices` to find a voice id, `--dry-run` to preview cost, `--slide N` to redo one slide.
- `references/voice-cloning.md` — the ElevenLabs one-time setup (API key, voice id), the automatic generator's usage/flags (default path), the manual website method (fallback), the phonetic-respelling trick, and privacy notes.
- `references/branding.md` — the brand tokens and logo, and how to set the template to your own brand.
- `references/deploy-and-iso.md` — Vercel deploy steps, keeping local-only files off the public site, verification steps, and the good-practice checklist before publishing anything.
