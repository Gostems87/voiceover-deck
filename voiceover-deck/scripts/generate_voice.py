#!/usr/bin/env python3
"""generate_voice.py - turn a deck's narration into real MP3s via ElevenLabs.

Replaces the manual "paste each script into the ElevenLabs website and
download the file" step. Reads a per-deck narration manifest
(`voiceover.json`, sitting next to the deck's `index.html`) and calls the
ElevenLabs Text-to-Speech API once per slide, writing `audio/slide-01.mp3`,
`slide-02.mp3`, ... - the exact filenames the deck template's AUDIO
manifest already expects (see assets/deck-template.html), so nothing else
about the deck needs to change.

Pure REST over `requests`, no elevenlabs SDK required.

Pointing this at your own deck: pass --dir followed by the folder that
contains your deck's index.html and voiceover.json (the folder you copied
assets/deck-template.html into and built your deck in). Everything else
about this script works the same regardless of where that folder lives.

voiceover.json shape (an ordered array, one entry per slide):
    [
      { "slide": 1, "tts_text": "Spoken sentence for slide one..." },
      { "slide": 2, "tts_text": "Spoken sentence for slide two..." }
    ]
`tts_text` is the SPOKEN string, already phonetically respelled where a
brand word needs it (see references/voice-cloning.md). This keeps the
on-screen `DECK.slides[].narration` spelled correctly while the audio still
sounds right; the two are allowed to differ for exactly that reason.

Config (read from THIS PROJECT'S .env, the one in the current working
directory, never a global ~/.claude/.env):
    ELEVENLABS_API_KEY   required. Create one at
                         https://elevenlabs.io/app/settings/api-keys
    ELEVENLABS_VOICE_ID  optional. The cloned voice to narrate with. If
                         unset, the script asks ElevenLabs for the
                         account's voices; if there's exactly one cloned
                         voice it uses that (and says so), otherwise it
                         prints every voice and its id and stops. It
                         never guesses which voice to use.

Usage (replace "python" with whatever runs Python on your machine, e.g.
python3 or a virtual environment's python.exe):
    Generate every slide for a deck:
        python generate_voice.py --dir <deck-folder>

    See what would be generated and the approximate cost, no API calls:
        python generate_voice.py --dir <deck-folder> --dry-run

    Regenerate just one slide (e.g. after editing its script):
        python generate_voice.py --dir <deck-folder> --slide 3

    Find your voice id (no need to visit the ElevenLabs website):
        python generate_voice.py --list-voices

    Use a different voice for one run, without changing .env:
        python generate_voice.py --dir <deck-folder> --voice <voice_id>
"""

import argparse
import json
import os
import sys
import warnings
from pathlib import Path

# Quiet the LibreSSL/urllib3 NotOpenSSLWarning some system Pythons emit, so
# it doesn't pollute the output a non-technical user is reading.
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")

try:
    import requests
except ImportError:
    sys.exit(
        "The 'requests' package isn't installed in this Python environment.\n"
        "Run: .venv/Scripts/python.exe -m pip install requests"
    )

API_BASE = "https://api.elevenlabs.io"

# eleven_multilingual_v2 is ElevenLabs' most natural, emotionally-aware
# model. Narration MP3s are generated ahead of time, not read out live, so
# quality matters more than the ultra-low latency the Flash/Turbo models are
# built for. multilingual_v2 is the right default for a deck voiceover.
TTS_MODEL = "eleven_multilingual_v2"

# ElevenLabs' own default MP3 quality (44.1kHz / 128kbps), plenty for
# narration played through a laptop or a shared link.
OUTPUT_FORMAT = "mp3_44100_128"

# ElevenLabs voice "category" values that mean a real cloned voice (an
# Instant or Professional Voice Clone) rather than one of the built-in
# library voices. Used to auto-detect the user's cloned voice when only one
# exists on the account.
CLONED_CATEGORIES = {"cloned", "professional"}

# eleven_multilingual_v2 bills at 1 credit per character, roughly $0.10 per
# 1,000 characters on the standard API rate (July 2026 pricing). Used only
# for the rough cost estimate this script prints; ElevenLabs' own account
# page is the source of truth for the exact rate on your plan.
USD_PER_1000_CHARS = 0.10


def load_project_env():
    """Read config from THIS PROJECT'S .env only (cwd), never a global one.

    Doesn't override real environment variables that are already set."""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env_path


def no_key_message(env_path):
    return (
        "No ElevenLabs API key found yet, so no voiceover can be generated.\n\n"
        "One-time setup:\n"
        "  1. Go to https://elevenlabs.io/app/settings/api-keys and click\n"
        "     \"Create API Key\" (needs a paid ElevenLabs plan; the free\n"
        "     tier doesn't allow API access).\n"
        "  2. Copy the key it gives you.\n"
        f"  3. Open {env_path}\n"
        "     (if it doesn't exist yet, copy the .env.example file that ships\n"
        "     in this skill folder into your project's root folder and\n"
        "     rename it .env) and add this line:\n\n"
        "         ELEVENLABS_API_KEY=your-key-here\n\n"
        "  4. Save the file and run this command again.\n\n"
        "Full walkthrough, including how to find your voice id, is in\n"
        "references/voice-cloning.md."
    )


def pad2(n):
    return f"{n:02d}"


def list_voices(api_key):
    """GET /v2/voices - every voice on the account, cloned or library."""
    url = f"{API_BASE}/v2/voices"
    try:
        r = requests.get(url, headers={"xi-api-key": api_key}, params={"page_size": 100}, timeout=30)
    except requests.exceptions.RequestException as e:
        sys.exit(f"Could not reach ElevenLabs to list voices: {e}")
    if r.status_code == 401:
        sys.exit(
            "ElevenLabs rejected the API key (401 Unauthorized).\n"
            "Double-check the value pasted into .env at ELEVENLABS_API_KEY."
        )
    if r.status_code >= 400:
        sys.exit(f"ElevenLabs returned an error listing voices (HTTP {r.status_code}): {r.text[:300]}")
    try:
        data = r.json()
    except ValueError:
        sys.exit("ElevenLabs sent back something that wasn't valid JSON while listing voices.")
    return data.get("voices", [])


def print_voices(voices):
    if not voices:
        print("No voices found on this ElevenLabs account.")
        return
    print(f"{len(voices)} voice(s) on this ElevenLabs account:\n")
    for v in voices:
        tag = " (cloned)" if v.get("category") in CLONED_CATEGORIES else ""
        print(f"  {v.get('voice_id')}   {v.get('name')}{tag}")


def resolve_voice_id(api_key, override):
    """Work out which voice to narrate with. Never guesses silently."""
    if override:
        return override, "the --voice option"

    env_voice = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
    if env_voice:
        return env_voice, "ELEVENLABS_VOICE_ID in .env"

    voices = list_voices(api_key)
    cloned = [v for v in voices if v.get("category") in CLONED_CATEGORIES]
    if len(cloned) == 1:
        v = cloned[0]
        print(
            f"ELEVENLABS_VOICE_ID isn't set. Found exactly one cloned voice "
            f"on the account ('{v.get('name')}'), using it."
        )
        return v.get("voice_id"), "auto-detected (only cloned voice on the account)"

    print(
        "Couldn't work out which voice to use. Set ELEVENLABS_VOICE_ID in "
        ".env, or pass --voice <id> for this run.\n"
    )
    print_voices(voices)
    sys.exit(1)


def load_manifest(deck_dir, only_slide=None):
    manifest_path = deck_dir / "voiceover.json"
    if not manifest_path.exists():
        sys.exit(
            f"No voiceover.json found in {deck_dir}.\n\n"
            "This is the narration manifest. It's written alongside "
            "index.html when the deck is generated (see SKILL.md, "
            "'Generate the deck'). If you need to write one by hand, it "
            "should look like:\n\n"
            '  [\n'
            '    { "slide": 1, "tts_text": "Spoken line for slide one." },\n'
            '    { "slide": 2, "tts_text": "Spoken line for slide two." }\n'
            '  ]'
        )
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.exit(f"{manifest_path} isn't valid JSON: {e}")
    if not isinstance(data, list) or not data:
        sys.exit(f"{manifest_path} should be a non-empty JSON array of {{slide, tts_text}} entries.")
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "slide" not in entry or "tts_text" not in entry:
            sys.exit(f"Entry {i} in {manifest_path} is missing 'slide' or 'tts_text'.")
    data = sorted(data, key=lambda e: e["slide"])

    if only_slide is not None:
        data = [e for e in data if e["slide"] == only_slide]
        if not data:
            sys.exit(f"No entry for slide {only_slide} in {manifest_path}.")
    return data


def generate_slide_audio(api_key, voice_id, text, out_path):
    """POST /v1/text-to-speech/{voice_id} and write the MP3 bytes to disk."""
    url = f"{API_BASE}/v1/text-to-speech/{voice_id}"
    body = {
        "text": text,
        "model_id": TTS_MODEL,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    try:
        r = requests.post(
            url,
            headers={"xi-api-key": api_key},
            params={"output_format": OUTPUT_FORMAT},
            json=body,
            timeout=120,
        )
    except requests.exceptions.RequestException as e:
        sys.exit(f"Could not reach ElevenLabs to generate {out_path.name}: {e}")
    if r.status_code == 401:
        sys.exit(
            "ElevenLabs rejected the API key (401 Unauthorized).\n"
            "Double-check the value pasted into .env at ELEVENLABS_API_KEY."
        )
    if r.status_code == 404:
        sys.exit(
            f"ElevenLabs couldn't find voice id '{voice_id}' (404 Not Found).\n"
            "Run --list-voices to see the valid ids on this account."
        )
    if r.status_code >= 400:
        sys.exit(f"ElevenLabs returned an error generating {out_path.name} (HTTP {r.status_code}): {r.text[:300]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(r.content)


def cost_estimate(total_chars):
    usd = total_chars / 1000 * USD_PER_1000_CHARS
    return (
        f"{total_chars} characters, roughly {total_chars} ElevenLabs credits "
        f"(about ${usd:.2f} at the standard multilingual API rate; check "
        "your ElevenLabs plan for the exact rate)."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate a deck's narration MP3s via the ElevenLabs API (no website visits)."
    )
    parser.add_argument("--dir", default=".", help="Deck folder containing index.html and voiceover.json (default: current folder)")
    parser.add_argument("--all", action="store_true", help="Generate every slide (this is the default when --slide is not given)")
    parser.add_argument("--slide", type=int, help="Regenerate just this one slide number")
    parser.add_argument("--voice", help="ElevenLabs voice id to use for this run, overriding ELEVENLABS_VOICE_ID")
    parser.add_argument("--list-voices", action="store_true", help="Print every voice on the account with its id, then exit")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated and an approximate cost, no API calls")
    args = parser.parse_args()

    env_path = load_project_env()
    api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()

    if args.list_voices:
        if not api_key:
            sys.exit(no_key_message(env_path))
        print_voices(list_voices(api_key))
        return

    deck_dir = Path(args.dir).resolve()
    manifest = load_manifest(deck_dir, only_slide=args.slide)

    if args.dry_run:
        total_chars = sum(len(e["tts_text"]) for e in manifest)
        print(f"Dry run. Would write {len(manifest)} file(s) to {deck_dir / 'audio'}:\n")
        for e in manifest:
            fname = f"slide-{pad2(e['slide'])}.mp3"
            preview = e["tts_text"][:60] + ("..." if len(e["tts_text"]) > 60 else "")
            print(f"  {fname}  ({len(e['tts_text'])} chars)  \"{preview}\"")
        print(f"\nTotal: {cost_estimate(total_chars)}")
        if not api_key:
            print(
                "\nNote: ELEVENLABS_API_KEY isn't set yet, so this was a dry "
                "run only. No audio can be produced until it's added. See "
                "references/voice-cloning.md for the one-time setup."
            )
        return

    if not api_key:
        sys.exit(no_key_message(env_path))

    voice_id, voice_source = resolve_voice_id(api_key, args.voice)

    audio_dir = deck_dir / "audio"
    generated = []
    total_chars = 0
    for e in manifest:
        fname = f"slide-{pad2(e['slide'])}.mp3"
        out_path = audio_dir / fname
        generate_slide_audio(api_key, voice_id, e["tts_text"], out_path)
        total_chars += len(e["tts_text"])
        generated.append(fname)
        print(f"Generated {fname} ({len(e['tts_text'])} chars)")

    print(f"\nDone. {len(generated)} file(s) written to {audio_dir}")
    print(f"Voice used: {voice_id} ({voice_source})")
    print(f"Total: {cost_estimate(total_chars)}")


if __name__ == "__main__":
    main()
