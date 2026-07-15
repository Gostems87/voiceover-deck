# Voice cloning for deck narration

A condensed comparison of self-serve voice-cloning tools, and the recommended production method for narrating a deck.

## Recommendation: ElevenLabs

Of the self-serve voice-cloning tools compared (ElevenLabs, PlayHT, Descript, Resemble AI, Murf, Cartesia), ElevenLabs is the right default: browser-based, no coding, a genuinely natural clone from about a minute of recording, low entry cost (roughly £4.50–£16.50/month), and the most complete privacy paperwork of the group (SOC 2, a published GDPR Data Processing Agreement, EU-US Data Privacy Framework certification, an optional Zero Retention Mode, and a published deletion right).

## Quickstart

**One-time: clone the voice**
1. Sign up at elevenlabs.io and take the Starter plan (~£4.50/month) — the free tier has no commercial-use rights; Starter unlocks Instant Voice Cloning plus commercial use.
2. Record one to three minutes of clean speech on a phone, in a quiet room, with natural variation in tone. No studio or special microphone needed.
3. Voices → Create Voice → Instant Voice Clone → upload the recording. A usable voice is ready in about a minute.

**One-time: connect the API (unlocks the automatic generator below)**
1. Go to `https://elevenlabs.io/app/settings/api-keys` and click "Create API Key". This needs API access on the plan — check it's enabled if the key doesn't work.
2. Open this project's `.env` (if it doesn't exist yet, copy the `.env.example` file that ships in this skill folder into your project's root folder and rename it `.env`) and paste the key in:
   ```
   ELEVENLABS_API_KEY=your-key-here
   ```
3. Find and confirm the cloned voice's id — no need to open the ElevenLabs website for this:
   ```
   python scripts/generate_voice.py --list-voices
   ```
   (run from wherever this skill folder lives, adjusting the path to `generate_voice.py` and the Python command to match your setup)
   This lists every voice on the account with its id, marking cloned voices `(cloned)`. If there's exactly one cloned voice, the generator will use it automatically and this step is just a sanity check. If there's more than one, copy the right id and add it to `.env`:
   ```
   ELEVENLABS_VOICE_ID=the-id-you-copied
   ```

That's the whole one-time setup. From here on, voicing a deck is one command — see "Automatic (default): the generator script" below.

## Automatic (default): the generator script

`scripts/generate_voice.py` calls the ElevenLabs Text-to-Speech API directly — no pasting scripts into a website, no manual downloads or renaming. It reads `voiceover.json` (written next to `index.html` when the deck is generated — see SKILL.md step 3) and writes `audio/slide-01.mp3` … `slide-NN.mp3` straight into the deck folder, zero-padded and numbered exactly as the deck template expects.

**Voice the whole deck (the single command that does it):**
```
python scripts/generate_voice.py --dir <deck-folder>
```
(run from wherever this skill folder lives, adjusting the path to `generate_voice.py` and the Python command to match your setup — e.g. `python3`, or a virtual environment's `python.exe`)

**Other flags:**
| Flag | What it does |
|---|---|
| `--dir <folder>` | Deck folder containing `index.html` and `voiceover.json`. Defaults to the current folder. |
| `--all` | Generate every slide — this is the default when `--slide` isn't given, listed for clarity. |
| `--slide N` | Regenerate just one slide's MP3 (e.g. after editing its script). No need to redo the whole deck. |
| `--voice <id>` | Use a different voice for this run only, without changing `.env`. |
| `--list-voices` | Print every voice on the account with its id — the way to find/confirm a voice id without visiting the website. |
| `--dry-run` | Show exactly what would be generated and an estimated character/credit cost — makes no API calls, spends nothing. Always safe to run first. |

The script reads `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` from **this project's `.env`** only (never a global config file), and it never guesses which voice to use: if `ELEVENLABS_VOICE_ID` is unset and there's more than one cloned voice on the account, it lists them and asks rather than picking one silently. If the key isn't set at all, it prints the exact steps to create one and where to paste it, then exits cleanly — no error dump.

Because ElevenLabs bills by character, run `--dry-run` first on anything long to see the estimate before spending credits. Update a single line of narration later by editing that slide's entry in `voiceover.json` and re-running with `--slide N`, no need to redo the rest.

## Manual (fallback): the ElevenLabs website

Use this if there's no API key set up yet, or a one-off clip is wanted without touching the terminal.

1. For each slide, paste that slide's spoken narration text (not the on-screen headline — see SKILL.md step 2) into ElevenLabs' Text to Speech screen.
2. Select the cloned voice, click Generate, download the MP3.
3. Rename the file to match the deck's audio manifest: `slide-01.mp3`, `slide-02.mp3`, … `slide-NN.mp3`, zero-padded to two digits, numbered in the same order as `DECK.slides` in the deck file.
4. Drop all the files into an `audio/` folder next to the deck's `index.html`. No code change needed — the deck template already looks for exactly these filenames.

Update a single line of narration later by re-typing that one sentence in ElevenLabs and re-generating just that file — no need to re-record.

**Optional, later:** for the highest fidelity on something like a real client pitch, record a 30+ minute script and switch to Professional Voice Clone (included on the Creator plan, ~£16.50/month) — same workflow, a few hours' training wait, one "voice-captcha" liveness check for consent.

## The phonetic-respelling trick

If a brand or product word comes out wrong when generated (common with unusual names, acronyms, or made-up words — an invented brand name like "Quovyx" is a good example), don't change the deck's on-screen narration. Instead, respell that one word phonetically **only in the text that actually gets sent to the voice tool** — for example "Kwo-viks" instead of "Quovyx".

- **Automatic path:** respell it in that slide's `tts_text` in `voiceover.json`. `DECK.slides[].narration` (what shows in the caption/script overlay) stays correctly spelled; `voiceover.json`'s `tts_text` is what the generator actually sends to ElevenLabs, so it's the one that carries the phonetic version.
- **Manual path:** respell it only in the text box pasted into ElevenLabs' website for that one generation. The saved deck narration stays spelled correctly; the phonetic version is a one-off input, thrown away once the MP3 is generated.

## Privacy note

Every mainstream voice-cloning tool, including ElevenLabs, is a US company processing data in the US by default — EU-only processing exists only as an ElevenLabs Enterprise add-on. That's an acceptable trade-off for a proof-of-concept using your own voice reading public marketing copy. It stops being acceptable the moment the recording captures anyone else's voice, or the narration references anything confidential or not yet public — at that point, get the right sign-off before recording, not just before publishing. Keep whatever's typed into the Text to Speech box to public, approved content only (see SKILL.md's guardrails section).
