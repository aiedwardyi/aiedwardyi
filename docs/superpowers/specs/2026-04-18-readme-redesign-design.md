# README redesign — editorial cream profile

**Date:** 2026-04-18
**Owner:** @aiedwardyi
**Scope:** GitHub profile README (`aiedwardyi/aiedwardyi`)

## Summary

Replace the current "shipping board" profile hero with an editorial cream design. The hero bakes contributions and current streak directly into the banner (no external widgets). A matching cream activity graph sits below it. Both SVGs regenerate daily via a GitHub Action pulling fresh data from the GitHub GraphQL API.

## Why

Current design reads as a 2024 SaaS landing page: dark gradient, glowy rings, buzzword pill tags, animated dash lines. Goal is "professional but cool" — respected, considered, current to 2026. Editorial cream (serif display, paper tone, hairline rules) delivers that register; it also matches an existing cream editorial project in the owner's personal brand.

## Locked decisions

- **Aesthetic:** editorial cream paper, serif display, mono captions
- **Theme:** single cream variant for both GitHub dark and light mode (no paired dark variant — the cream-on-dark "magazine clipping" read is the distinctive move)
- **Data baked in:** total contributions and current day streak live inside the hero, not in a sidecar widget
- **Freshness:** daily GitHub Action regenerates SVGs so numbers are never stale
- **Below the hero:** one activity graph (line + fill, editorial cream), nothing else

## Composition

Two pieces, stacked, full GitHub README width (~1200px):

### 1. Hero banner (`assets/hero.svg`)

- **Background:** `#f4efe6` cream, `#d8d1c2` 1px border, 4px radius
- **Font stack:** serif display (`Times New Roman`/`Charter` family), mono accent (`ui-monospace`/`SF Mono`/`Consolas`)
- **Top rule:** dateline left (`No. MM·DD·YYYY`), status right (red dot `#c94a2a` + "Shipping Daily" + "Seoul"). Hairline bottom border.
- **Left column (≈1.35fr):**
  - Byline: `AI Engineer · Founder` — mono, 10px, 0.22em tracking, uppercase
  - Name: `Edward Yi` — serif, 64px, weight 500, -0.012em tracking
  - Abstract label: `Abstract` — mono, 10.5px, warm tan `#8a7a5a`
  - Abstract body: *"Building systems where agents ship real work into production. Previously led a 90-dev org shipping 200+ products."* — serif italic, 15.5px, max 44ch
- **Right column (≈1fr):** bordered stats (1px left border `#141414`, 28px padding)
  - `Contributions` / `2,611` / `since 2018`
  - `Day Streak` / `62d` / `current`
  - Numbers in serif 54px with tabular numerics; "d" unit in mono

### 2. Activity graph (`assets/activity.svg`)

- **Background:** same cream as hero, same border
- **Header:** `Figure I. *Contribution activity, trailing 12 months.*` left; `Weekly totals · n = 52` caption right (mono, 0.2em tracking)
- **Chart:** 52 weekly points, line (1.4px ink `#141414`) + soft fill gradient (`#141414` at 0.18 → 0 opacity), hairline dashed grid
- **Markers:** red dots (`#c94a2a`) on the two highest peaks + a larger ringed marker on the most recent week
- **X axis:** mono 9px, 0.08em tracking, uppercase months (`MAY`, `JUL`, `SEP`, `NOV`, `JAN`, `MAR`, `TODAY`)

## Architecture

```
scripts/
  generate_profile.py       # fetches GitHub data, renders both SVGs
.github/workflows/
  update-profile.yml        # cron + push trigger
assets/
  hero.svg                  # generated, committed
  activity.svg              # generated, committed
README.md                   # embeds two SVGs, nothing else
```

### Data flow

1. GitHub Action runs at `00:00 UTC` daily (+ on push to `main`, + `workflow_dispatch`)
2. `generate_profile.py` queries GitHub GraphQL API for `user.contributionsCollection.contributionCalendar`, returning `totalContributions` and daily `contributionDays` over the last year
3. Script computes:
   - `contributions_total` — sum from GraphQL (aggregate across contribution years for the full count, not just last year — see "Open questions")
   - `streak_current` — consecutive days with count ≥ 1, walking backward from today
   - `weekly_series` — 52 weekly sums for the activity graph
4. Script renders two SVG strings via string templates (no heavy SVG library — these are hand-authored templates with interpolation slots)
5. Action commits changes back to `main` if the SVG files differ

### GitHub Action

Modeled on the existing `snake.yml` (same repo). Key steps:

```yaml
name: Update profile

on:
  schedule:
    - cron: "0 0 * * *"
  push:
    branches: [main]
    paths:
      - scripts/generate_profile.py
      - .github/workflows/update-profile.yml
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python scripts/generate_profile.py
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Commit if changed
        run: |
          git config user.name "profile-bot"
          git config user.email "profile-bot@users.noreply.github.com"
          git add assets/hero.svg assets/activity.svg
          git diff --cached --quiet || git commit -m "Update profile SVGs"
          git push
```

### Language choice

Python 3.12. No third-party deps except `requests` (installable via pip in the action). SVG rendering is string-template interpolation — no `cairo`/`svgwrite` needed because the design is a fixed layout with only data-driven slots.

## Error handling

- If the GraphQL call fails (network, rate limit, auth), the script exits non-zero and no SVGs are regenerated. The action run fails visibly; existing SVGs stay in place. **Do not commit broken or empty SVGs.**
- If the streak computation returns 0 (rare: no contributions today or yesterday), render "0d" rather than hiding the stat.
- The abstract and byline are hard-coded in the template, not from the API, so they never fail.

## Testing

- **Local dry-run:** `python scripts/generate_profile.py --dry-run` prints SVGs to `stdout` without writing files. Author opens the rendered SVG locally to verify.
- **CI dry-run:** first run via `workflow_dispatch` on a feature branch before merging.
- **Visual regression:** eyeball after first real run — render is deterministic given the same data, so any unexpected diff is a real bug.

## File changes

| Path | Change |
|---|---|
| `README.md` | Rewrite to embed only `./assets/hero.svg` and `./assets/activity.svg` |
| `assets/hero.svg` | New file, generated |
| `assets/activity.svg` | New file, generated |
| `scripts/generate_profile.py` | New file |
| `.github/workflows/update-profile.yml` | New file |
| `.gitignore` | Create with `.superpowers/` entry |
| `assets/profile-hero-*` (old variants) | Leave in place — not deleted as part of this work. Dead code cleanup is its own task. |
| `concepts/` | Leave in place |

## Out of scope

- Pruning the dozen legacy `profile-hero-alt-*.svg` variants and old README concepts in `concepts/`
- A dark-native paired variant (explicitly rejected — cream-only is the decision)
- Project cards, "currently shipping" sections, contact links below the activity graph
- Achievements or language-breakdown widgets

## Open questions (non-blocking)

- **Full contribution count:** the GraphQL `contributionCalendar` returns only the last year. To get the full "since 2018" total, the script must loop over each year from account creation to present and sum. Acceptable cost (≈8 queries, one per year). Confirm before implementation.
- **Abstract wrap width:** 44ch at 15.5px may wrap differently across renderers. If wrapping looks off in real GitHub render, we tune `max-width` during the first live review.
