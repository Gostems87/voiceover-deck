# Deploying a deck, and good practice before you publish

A deck works perfectly well as a local file — open it by double-click, or attach it. This reference is only for when you want a link you can send instead.

## Deploy method (Vercel)

From the deck's folder (containing `index.html` and its `audio/` folder):

```
vercel deploy --prod --yes
```

That's it — no build step, no config needed for a static HTML file. Vercel returns a public URL. (Needs a free Vercel account and the `vercel` CLI installed; any other static host works too — Netlify, GitHub Pages, or your own server.)

## Keep local-only files off the public site

Any file in the deck's folder that isn't `index.html` or `audio/*.mp3` gets published too unless excluded — including README notes, production notes, or anything with a local file path in it. Add a `.vercelignore` file next to `index.html` before deploying:

```
README.md
DEPLOYMENT.md
audio/PUT-YOUR-VOICE-FILES-HERE.txt
*.md
```

Adjust the list to whatever helper files actually exist in that deck's folder — the pattern is: only the deck itself and its audio should ever be public.

## Verify it's genuinely public and nothing leaked

After deploying:
1. Fetch the live URL and confirm a plain `200` with no login wall (some hosting setups can accidentally inherit team-level password protection — check for this explicitly).
2. Confirm the audio files load (`https://<url>/audio/slide-01.mp3` etc. return `200`).
3. Confirm anything excluded via `.vercelignore` genuinely 404s on the live URL — don't just trust the ignore file, request the excluded paths and check.

## Good practice — check before anything is sent or deployed

- **Never put confidential or client data in a deck you publish.** No real client or supplier names, no internal or unpublished figures — headline, support copy, narration script, or captions.
- **Public, approved figures only.** Any stat used (satisfaction scores, response times, years trading, etc.) should be something you'd be comfortable seeing published — re-verify it's still current before a major re-share, since some of these are rolling figures.
- **Board-appropriate tone throughout** — these links get forwarded outside the room they were made for.
- **Get the right sign-off before making anything public.** If you're building this for an organisation, that means checking with whoever owns brand, legal, or client-data approval before the deck goes live — before deploying, before emailing the link, before attaching the HTML file to anything leaving the building. Draft, preview locally, and iterate freely without this — the gate is specifically at the point something becomes reachable by someone outside the immediate build team.
- It's worth keeping a short record alongside the deck of who built it, who reviewed it, and what's still open — a plain `DEPLOYMENT.md` or similar note in the deck's own folder works well, especially if more than one person might pick it up later.

For a personal project or a quick demo, the sign-off step above won't apply — but the no-real-names and public-figures-only discipline is still good practice generally. Don't publish anything that would embarrass someone if forwarded.
