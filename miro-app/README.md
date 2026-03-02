# Score — Arc Designer

A design tool for immersive experience makers. Browse a library of 356 plays — atomic experience beats drawn from immersive theater, ARGs, pervasive games, and transformative experience design — arrange them into arcs, check them for structural problems, and score them against participant profiles.

Works as a **standalone web app** (no account needed) and as a **Miro sidebar panel** that reads your board and drops play cards directly onto it.

| Plays library | Engagement planner |
|---|---|
| ![Plays library tab — browse, filter, and expand plays](assets/screenshot-library.png) | ![Analyze tab — Pattern Seeker profile with Big Five sliders and mechanism weights](assets/screenshot-analyze.png) |

---

## Try it now

**[→ Open the standalone app](#)** — no Miro account needed. Browse all 356 plays, build an arc in the text box, run the linter and planner right in your browser.

> Replace `#` above with your GitHub Pages URL once the repo is public: `https://your-username.github.io/score/panel.html`

---

## What's in the library

356 plays across every domain that matters for immersive experience design:

- **Immersive theater** — mask mechanics, one-on-ones, environmental narrative, actor loops (Punchdrunk, Sleep No More)
- **ARGs and pervasive games** — real domains, planted evidence, breadcrumb trails, alternate reality layers (Jejune Institute, Ingress)
- **Transformative experience design** — micro-authorization cascades, counter-identity encounters, reintegration scaffolding (McLain)
- **Group dynamics** — faction formation, allegiance forks, shared crisis beats, group synchronization (Galactic Starcruiser)
- **Con artistry and intelligence tradecraft** — convincer mechanics, cold read, tradecraft patterns (Maurer, Goffman, FBI BCSM)
- **Ritual design** — graduation rituals, liminal transitions, threshold marking (van Gennep)
- **Physical world** — dead drops, spatial messages, location dispatch, certified mail (Jejune, early ARGs)
- **Digital and AI-native** — AI character interfaces, voice clones, synthetic media, LLM contamination

Each play has 27 fields: mechanisms, beat function, arc fit, somatic quality, identity invite, dwell time, detection window, reversibility, required grants, and more.

---

## Getting it into Miro

The app is a folder of static files. You host it somewhere, then register a Miro app pointing at it. Takes about 10 minutes.

### Step 1 — Get a hosted URL

**Easiest: Netlify Drop** (no account required, 2 minutes)

1. Download or clone this repo
2. Open a terminal in the folder and run:
   ```sh
   npm install
   npm run build
   ```
   This creates a `dist/` folder.
3. Go to [app.netlify.com/drop](https://app.netlify.com/drop) and drag the `dist/` folder onto the page
4. Netlify gives you a URL — copy it

**Free forever: GitHub Pages**

If this repo is public on GitHub, enable GitHub Pages under **Settings → Pages → GitHub Actions**, then add this workflow file:

<details>
<summary>.github/workflows/deploy.yml</summary>

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm install && npm run build
      - uses: actions/upload-pages-artifact@v3
        with: { path: dist }
      - uses: actions/deploy-pages@v4
        id: deployment
```
</details>

Your URL will be `https://your-username.github.io/score`.

### Step 2 — Register in Miro

1. Go to [developers.miro.com](https://developers.miro.com/) and sign in
2. Click **Create new app** — name it whatever you like
3. Under **App URL**, paste your URL with `/panel.html` added to the end
   - Example: `https://wonderful-name-123.netlify.app/panel.html`
4. Under **Permissions**, tick **boards:read** and **boards:write**
5. Click **Install app and get OAuth token** → pick your team → **Add**

### Step 3 — Open it

Open any Miro board. The Score icon appears in the left toolbar. Click it.

---

## How to use it

**Browse plays** — search by keyword, filter by phase (build, escalate, threshold, climax) or pacing (ramp, spike, hold). Expand any play to read its full description. Drag the ⠿ handle to drop it as a card on your Miro board.

**Build an arc** — in Miro, arrange play cards left to right in sequence order. In the standalone app, type or paste play IDs into the arc input box one per line.

**Check Arc** — runs the structural linter against your sequence. Flags CONTRAINDICATED pairs, missing permissions, detection accumulation, rhythm problems, and more.

**Analyze for Profile** — load a participant profile (use one of the three templates as a starting point, or build from scratch with the Big Five sliders and mechanism weights), then run the planner to see engagement scores for each beat.

**Guide tab** — drop reference arcs onto your board: Sleep No More, House of the Latitude, The Game, Galactic Starcruiser, and others. See what a real arc sequence looks like as a starting point.

---

## Bringing your own library

The library ships with all 356 plays in `public/`. To use a custom dataset, replace the three files:

- `public/plays_strips.json` — compact notation for the linter and planner
- `public/plays_mechanisms.json` — mechanism index for engagement scoring
- `public/plays_info.json` — display metadata (title, invite text)

Then rebuild and redeploy.

---

## For developers

```sh
npm install
npm run dev        # dev server at http://localhost:5174
npm run build      # TypeScript check + Vite build → dist/
npm run test       # Vitest unit tests
npm run typecheck  # tsc --noEmit
npm run lint       # Biome lint
npm run format     # Biome format (writes)
```

To point the dev server at a custom library directory:
```sh
SCORE_DATA_DIR=/path/to/library npm run dev
```

**Project structure**
```
public/        Library data (plays_strips.json, plays_mechanisms.json, plays_info.json)
assets/        README screenshots
src/
  main.ts      Panel entry: tabs, lint/plan handlers, standalone detection
  library.ts   Plays browser: search, filter, frecency, drag-to-board
  profile.ts   Profile editor: Big Five sliders, mechanism picker, 3 save slots
  linter.ts    loadStrips() + lintArc() — all constraint checks
  planner.ts   engagementProb() + planArc()
  demos.ts     Reference arc data + board/textarea drop
  board.ts     Read Miro board state, parse card descriptions
  render.ts    HTML generation for lint/plan output
  data.ts      Load and cache the three data files
  types.ts     Shared TypeScript types
```

**Strip notation** — plays use a compact 4-line format parsed by the linter and planner:
```
@play_id F·A·0·1
#mechanism_a·mechanism_b [b·e] /
C·n·l·a·e·n·e
prm:S
```
Beat functions: `/` ramp · `^` spike · `-` hold · `_` rest · `>` transition · `~` liminal.

---

## License

MIT
