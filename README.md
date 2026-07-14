# Voiceover Deck

A Claude Code skill that builds narrated, self-playing slide decks — a single web page that talks you through a pitch, an explainer, or an update, all by itself.

Think of it as a slide deck that presents itself. You open it (or send someone a link), it plays through the slides one by one with a voice reading each one aloud, and the viewer can pause, skip back and forth, or jump to fullscreen whenever they like. No PowerPoint, no video recording, no faffing about with screen-share.

## What you get

- One HTML file that contains the whole deck — no app to install, no server to run.
- A voice reading each slide aloud automatically. Out of the box it uses your browser's own built-in voice, so it works the moment you open it. Add a free-to-low-cost ElevenLabs account later and you can have it narrated in your own cloned voice instead.
- A proper control bar: play/pause, back/forward, turn the voice on or off, show the script on screen as captions, and go fullscreen.
- A tidy default look (a neutral colour palette and a text logo) that you can restyle with your own colours, fonts and logo in a couple of minutes.
- You can open it locally by double-clicking the file, or put it on a free static host (Vercel, Netlify, GitHub Pages) and send it as a link.

## How to install it

This is a **skill** for Claude Code — a folder of instructions and files that teaches Claude how to build these decks for you. You don't need to know how any of it works; you just need to put the folder in the right place and ask Claude.

**1. Download this repository**

Either clone it with git, or click the green "Code" button on GitHub and choose "Download ZIP", then unzip it wherever's convenient.

**2. Copy the `voiceover-deck` folder into your Claude skills folder**

Inside this repository is a folder called `voiceover-deck`. Copy that whole folder (not the repo's outer folder — the one inside it, the one with `SKILL.md` in it) into your Claude Code skills folder:

- **Windows:** `C:\Users\<your-username>\.claude\skills\`
- **Mac or Linux:** `~/.claude/skills/`

If the `skills` folder doesn't exist yet, create it — that's fine, Claude Code will pick it up.

When you're done, the path should look like `...\.claude\skills\voiceover-deck\SKILL.md` (Windows) or `.../.claude/skills/voiceover-deck/SKILL.md` (Mac/Linux).

**3. Restart Claude Code**

Close and reopen your Claude Code session (or start a new one) so it notices the new skill.

That's it — no extra software, no API keys required to get started.

## How to use it

Just ask, in plain English. For example:

> "Build me a narrated deck about our new product launch, aimed at investors, about seven slides."

> "I need a self-playing deck I can send my team explaining the new process."

Claude will ask you a few quick questions (what the deck's for, who it's for, roughly how many slides), write the on-screen text and the spoken narration for each slide, and produce a working HTML file. Open it in a browser and it plays immediately — read aloud by your browser's own voice, no setup needed.

## Making it sound like you

The deck plays out of the box using your browser's built-in text-to-speech voice, which is perfectly serviceable and costs nothing. If you'd like it narrated in an actual cloned voice — yours, or anyone else's with their consent — you can connect a free ElevenLabs account:

1. Sign up at [elevenlabs.io](https://elevenlabs.io) and take the Starter plan (a few pounds a month — the free tier doesn't allow the cloning or API access this needs).
2. Record a minute or two of yourself talking on your phone, upload it, and ElevenLabs builds a voice clone from it in about a minute.
3. Create an API key on the ElevenLabs site and add it to a `.env` file in whichever project folder you're building the deck in.

Once that's set up, generating the voiceover for a whole deck is a single command that Claude can run for you — full details are in `voiceover-deck/references/voice-cloning.md` inside the skill folder.

## What it costs

- Building the deck itself: free — it's just a skill Claude uses, no charge beyond your normal Claude Code usage.
- Playing it with the browser's built-in voice: free, always.
- Adding your own cloned voice (optional): a few pounds a month for ElevenLabs, plus a small per-character cost for generating the audio — for a typical seven-to-nine-slide deck this comes to pennies, not pounds.

## A note on what's in this repository

`voiceover-deck/` is the skill folder itself — this is the bit you copy into your `.claude/skills/` folder. Everything inside it (`SKILL.md`, `assets/`, `references/`, `scripts/`) is what Claude reads to know how to build a deck.

This version has been stripped of any particular brand — it ships with a neutral default look (slate and indigo colours, a plain text logo) that you're meant to restyle for your own use. Claude will ask what colours, fonts and logo you'd like when you first ask it to build a deck, or you can just go with the tidy defaults for a quick demo.

## Licence

MIT — see `LICENSE`. Use it, change it, share it, no strings attached.
