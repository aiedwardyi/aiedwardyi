# README Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current "shipping board" profile README with an editorial cream design whose hero banner bakes in contributions and current streak, regenerated daily via a GitHub Action.

**Architecture:** Python 3.12 script pulls contribution data from the GitHub GraphQL API, computes totals + streak + weekly series, and renders two SVGs (`hero.svg`, `activity.svg`) using `string.Template` substitution. A GitHub Action runs daily and on push, committing updated SVGs back to `main`. README embeds only the two SVGs.

**Tech Stack:** Python 3.12, `requests`, `pytest`, GitHub GraphQL API, GitHub Actions.

**Reference spec:** `docs/superpowers/specs/2026-04-18-readme-redesign-design.md`

---

## File Structure

New files:

| Path | Responsibility |
|---|---|
| `scripts/profile_data.py` | Fetch GraphQL contributions, compute totals/streak/weekly series. Pure data module — no SVG, no I/O beyond HTTP. |
| `scripts/profile_render.py` | Hero + activity SVG template strings and render functions. No network, no data computation. |
| `scripts/generate_profile.py` | Entry point. CLI with `--dry-run`. Wires data → render → disk. |
| `tests/test_profile_data.py` | Unit tests for streak computation and weekly aggregation using fixture data. |
| `requirements.txt` | Runtime deps (`requests`). |
| `requirements-dev.txt` | Dev deps (`pytest`). |
| `.github/workflows/update-profile.yml` | Daily cron + push trigger. Runs script, commits SVGs if changed. |
| `assets/hero.svg` | Generated. Committed. |
| `assets/activity.svg` | Generated. Committed. |

Modified files:

| Path | Change |
|---|---|
| `README.md` | Replace 3 `<img>` tags with 2 `<img>` tags pointing to new SVGs. |
| `.gitignore` | Append Python artifacts. |

---

## Task 1: Python project setup

**Files:**
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `tests/__init__.py`
- Modify: `.gitignore`

- [ ] **Step 1: Create `requirements.txt`**

```
requests==2.32.3
```

- [ ] **Step 2: Create `requirements-dev.txt`**

```
-r requirements.txt
pytest==8.3.3
```

- [ ] **Step 3: Create empty `tests/__init__.py`**

```python
```

- [ ] **Step 4: Append Python patterns to `.gitignore`**

Existing content of `.gitignore`:
```
.superpowers/
```

Append so final file is:
```
.superpowers/

# Python
__pycache__/
*.py[cod]
*$py.class
.venv/
venv/
.pytest_cache/
```

- [ ] **Step 5: Create and activate local virtualenv, install dev deps**

Run (bash/git-bash on Windows):
```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows git-bash; use .venv/bin/activate on macOS/Linux
pip install -r requirements-dev.txt
```
Expected: `pytest` and `requests` install successfully. No errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt requirements-dev.txt tests/__init__.py .gitignore
git commit -m "Add Python tooling for profile generator"
```

---

## Task 2: Data layer — streak computation (TDD)

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/profile_data.py`
- Create: `tests/test_profile_data.py`

- [ ] **Step 1: Create empty `scripts/__init__.py`**

```python
```

- [ ] **Step 2: Write failing tests for `compute_current_streak`**

Create `tests/test_profile_data.py`:

```python
from scripts.profile_data import compute_current_streak


def _days(*counts):
    """Build a list of {'date': ..., 'count': n} dicts, oldest first.

    Dates are fake - only order matters for streak computation.
    """
    return [{"date": f"2026-01-{i+1:02d}", "count": c} for i, c in enumerate(counts)]


def test_streak_is_zero_when_no_contributions_today():
    # Last day is today and has 0 contributions
    days = _days(1, 1, 1, 0)
    assert compute_current_streak(days) == 0


def test_streak_counts_consecutive_days_ending_today():
    # Last 3 days all have contributions
    days = _days(0, 1, 1, 1)
    assert compute_current_streak(days) == 3


def test_streak_stops_at_first_zero_from_today_backward():
    # Gap breaks streak
    days = _days(1, 1, 0, 1, 1)
    assert compute_current_streak(days) == 2


def test_streak_with_single_day_of_contributions():
    days = _days(1)
    assert compute_current_streak(days) == 1


def test_streak_with_empty_list():
    assert compute_current_streak([]) == 0
```

- [ ] **Step 3: Run tests — verify they fail with import error**

Run: `pytest tests/test_profile_data.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.profile_data'` or `ImportError`

- [ ] **Step 4: Implement `compute_current_streak`**

Create `scripts/profile_data.py`:

```python
"""Data layer for profile generator.

Fetches contribution calendar data from the GitHub GraphQL API and computes
summary metrics. Pure functions where possible - only the fetch layer does I/O.
"""
from __future__ import annotations

from typing import Iterable


def compute_current_streak(days: Iterable[dict]) -> int:
    """Count consecutive days with count >= 1, walking backward from the last day.

    Args:
        days: Sequence of {'date': str, 'count': int} dicts, oldest first.

    Returns:
        Integer streak length. Zero if today (the last day) has no contributions.
    """
    streak = 0
    for day in reversed(list(days)):
        if day["count"] >= 1:
            streak += 1
        else:
            break
    return streak
```

- [ ] **Step 5: Run tests — verify they pass**

Run: `pytest tests/test_profile_data.py -v`
Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add scripts/__init__.py scripts/profile_data.py tests/test_profile_data.py
git commit -m "Add current streak computation with tests"
```

---

## Task 3: Data layer — weekly aggregation (TDD)

**Files:**
- Modify: `scripts/profile_data.py`
- Modify: `tests/test_profile_data.py`

- [ ] **Step 1: Add failing tests for `aggregate_weekly`**

Append to `tests/test_profile_data.py`:

```python
from scripts.profile_data import aggregate_weekly


def test_aggregate_weekly_sums_each_week_of_seven():
    # 14 days, 1 contribution each = two weeks of 7
    days = _days(*([1] * 14))
    weeks = aggregate_weekly(days)
    assert weeks == [7, 7]


def test_aggregate_weekly_handles_partial_trailing_week():
    # 10 days: week of 7 + partial week of 3
    days = _days(*([2] * 10))
    weeks = aggregate_weekly(days)
    assert weeks == [14, 6]


def test_aggregate_weekly_empty():
    assert aggregate_weekly([]) == []


def test_aggregate_weekly_single_day():
    days = _days(5)
    assert aggregate_weekly(days) == [5]
```

- [ ] **Step 2: Run tests — verify they fail**

Run: `pytest tests/test_profile_data.py -v`
Expected: 4 new failures (`ImportError` for `aggregate_weekly`)

- [ ] **Step 3: Implement `aggregate_weekly`**

Append to `scripts/profile_data.py`:

```python
def aggregate_weekly(days: Iterable[dict]) -> list[int]:
    """Sum contributions into weekly buckets of 7, oldest week first.

    Args:
        days: Sequence of {'date': str, 'count': int} dicts, oldest first.

    Returns:
        List of weekly sums. Final bucket may contain fewer than 7 days.
    """
    days = list(days)
    weeks: list[int] = []
    for start in range(0, len(days), 7):
        weeks.append(sum(d["count"] for d in days[start : start + 7]))
    return weeks
```

- [ ] **Step 4: Run tests — verify they pass**

Run: `pytest tests/test_profile_data.py -v`
Expected: 9 passed total

- [ ] **Step 5: Commit**

```bash
git add scripts/profile_data.py tests/test_profile_data.py
git commit -m "Add weekly aggregation with tests"
```

---

## Task 4: Data layer — GitHub API fetch

**Files:**
- Modify: `scripts/profile_data.py`

No unit tests for this layer — it's a thin wrapper over HTTP and GraphQL. Smoke-tested in Task 7 via real API call.

- [ ] **Step 1: Add fetch functions**

Append to `scripts/profile_data.py`:

```python
import os
from datetime import datetime, timezone

import requests

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

_CREATED_AT_QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
  }
}
"""

_CONTRIBUTIONS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def _post(query: str, variables: dict, token: str) -> dict:
    resp = requests.post(
        GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={"Authorization": f"bearer {token}"},
        timeout=30,
    )
    resp.raise_for_status()
    payload = resp.json()
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def fetch_account_created_at(login: str, token: str) -> datetime:
    data = _post(_CREATED_AT_QUERY, {"login": login}, token)
    return datetime.fromisoformat(data["user"]["createdAt"].replace("Z", "+00:00"))


def fetch_year_window(login: str, token: str, from_dt: datetime, to_dt: datetime) -> dict:
    """Fetch one contribution calendar window (max ~1 year per GraphQL spec)."""
    data = _post(
        _CONTRIBUTIONS_QUERY,
        {
            "login": login,
            "from": from_dt.isoformat().replace("+00:00", "Z"),
            "to": to_dt.isoformat().replace("+00:00", "Z"),
        },
        token,
    )
    return data["user"]["contributionsCollection"]["contributionCalendar"]


def _flatten_days(calendar: dict) -> list[dict]:
    out: list[dict] = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            out.append({"date": day["date"], "count": day["contributionCount"]})
    return out


def fetch_full_profile(login: str, token: str) -> dict:
    """Fetch all data needed to render the profile.

    Returns:
        {
          'total_contributions': int,       # full lifetime total
          'days_last_year': list[{date,count}],  # ordered oldest->newest
          'current_streak': int,
          'weekly_last_year': list[int],    # 52/53 weekly totals
        }
    """
    now = datetime.now(timezone.utc)
    created_at = fetch_account_created_at(login, token)

    # Lifetime total: sum contributionCalendar.totalContributions across each year window
    lifetime_total = 0
    start_year = created_at.year
    end_year = now.year
    for year in range(start_year, end_year + 1):
        window_from = datetime(year, 1, 1, tzinfo=timezone.utc)
        window_to = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        if window_from < created_at:
            window_from = created_at
        if window_to > now:
            window_to = now
        cal = fetch_year_window(login, token, window_from, window_to)
        lifetime_total += cal["totalContributions"]

    # Last-year window for streak + weekly graph
    last_year_from = now.replace(year=now.year - 1)
    cal = fetch_year_window(login, token, last_year_from, now)
    days = _flatten_days(cal)

    return {
        "total_contributions": lifetime_total,
        "days_last_year": days,
        "current_streak": compute_current_streak(days),
        "weekly_last_year": aggregate_weekly(days),
    }


def get_token_from_env() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN must be set")
    return token
```

- [ ] **Step 2: Run existing tests — verify nothing broke**

Run: `pytest tests/test_profile_data.py -v`
Expected: 9 passed (no new tests; just make sure imports still work)

- [ ] **Step 3: Commit**

```bash
git add scripts/profile_data.py
git commit -m "Add GitHub GraphQL fetch for profile data"
```

---

## Task 5: Hero SVG renderer

**Files:**
- Create: `scripts/profile_render.py`

No unit tests — SVG output is visual, verified by eye in Task 7.

- [ ] **Step 1: Create `scripts/profile_render.py` with hero template**

```python
"""SVG templates for the editorial cream profile.

Uses string.Template ($var substitution) because SVG/CSS are dense with braces
and f-string escaping gets ugly fast.
"""
from __future__ import annotations

from datetime import datetime
from string import Template

HERO_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-labelledby="hero-title">
  <title id="hero-title">Edward Yi profile hero</title>
  <style>
    .bg { fill: #f4efe6; stroke: #d8d1c2; stroke-width: 1; }
    .ink { fill: #141414; }
    .muted { fill: #555555; }
    .tan { fill: #8a7a5a; }
    .sub-tan { fill: #7a6a4a; }
    .dot { fill: #c94a2a; }
    .serif { font-family: "Charter", "Iowan Old Style", "Times New Roman", Georgia, serif; }
    .mono { font-family: ui-monospace, "SF Mono", Consolas, "Liberation Mono", monospace; }
    .rule { stroke: #141414; stroke-width: 1; }
  </style>

  <rect class="bg" x="0.5" y="0.5" width="1199" height="359" rx="6"/>

  <!-- Top rule -->
  <text class="mono ink" x="48" y="56" font-size="11" letter-spacing="3" text-transform="uppercase">$dateline</text>
  <circle class="dot" cx="968" cy="51.5" r="3.5"/>
  <text class="mono ink" x="980" y="56" font-size="11" letter-spacing="3">SHIPPING DAILY</text>
  <text class="mono ink" x="1140" y="56" font-size="11" letter-spacing="3" text-anchor="end">SEOUL</text>
  <line class="rule" x1="48" y1="70" x2="1152" y2="70"/>

  <!-- Left column: byline, name, abstract -->
  <text class="mono muted" x="48" y="112" font-size="11" letter-spacing="2.5">AI ENGINEER  ·  FOUNDER</text>
  <text class="serif ink" x="48" y="184" font-size="64" font-weight="500" letter-spacing="-0.8">Edward Yi</text>
  <text class="mono tan" x="48" y="224" font-size="11" letter-spacing="2.5">ABSTRACT</text>

  <!-- Abstract body, two lines -->
  <text class="serif ink" x="48" y="254" font-size="16" font-style="italic">
    <tspan x="48" dy="0">Building systems where agents ship real work into production.</tspan>
    <tspan x="48" dy="22">Previously led a 90-dev org shipping 200+ products.</tspan>
  </text>

  <!-- Right column: stats -->
  <line class="rule" x1="780" y1="100" x2="780" y2="300"/>

  <text class="mono ink" x="812" y="128" font-size="11" letter-spacing="2.5" opacity="0.7">CONTRIBUTIONS</text>
  <text class="serif ink" x="812" y="192" font-size="54" font-weight="500" letter-spacing="-1.2">$contributions_total</text>
  <text class="mono sub-tan" x="812" y="214" font-size="11">since $created_year</text>

  <text class="mono ink" x="984" y="128" font-size="11" letter-spacing="2.5" opacity="0.7">DAY STREAK</text>
  <text x="984" y="192">
    <tspan class="serif ink" font-size="54" font-weight="500" letter-spacing="-1.2">$streak</tspan><tspan class="mono muted" font-size="14" dy="-20" dx="4">d</tspan>
  </text>
  <text class="mono sub-tan" x="984" y="214" font-size="11">current</text>
</svg>
""")


def render_hero(
    *,
    contributions_total: int,
    streak: int,
    created_year: int,
    now: datetime | None = None,
) -> str:
    now = now or datetime.utcnow()
    dateline = f"No. {now.month:02d}·{now.day:02d}·{now.year}"
    return HERO_TEMPLATE.substitute(
        dateline=dateline,
        contributions_total=f"{contributions_total:,}",
        streak=str(streak),
        created_year=str(created_year),
    )
```

- [ ] **Step 2: Smoke test the renderer with fake data**

Run (one-liner, paste into terminal):

```bash
python -c "from scripts.profile_render import render_hero; import datetime; open('assets/hero.svg','w').write(render_hero(contributions_total=2611, streak=62, created_year=2018, now=datetime.datetime(2026,4,18)))"
```

Expected: no error, `assets/hero.svg` exists.

- [ ] **Step 3: Visually inspect `assets/hero.svg`**

Open `assets/hero.svg` in a browser or VS Code preview. Confirm:
- Cream paper background, dark serif "Edward Yi"
- `No. 04·18·2026` top-left, red dot + `SHIPPING DAILY` top-middle, `SEOUL` top-right
- Abstract italic text visible and readable
- `2,611` with "since 2018" caption, `62` with "d" unit and "current" caption

If anything looks off (clipped text, misaligned columns), adjust coordinates in the template before moving on.

- [ ] **Step 4: Commit**

```bash
git add scripts/profile_render.py assets/hero.svg
git commit -m "Add editorial cream hero SVG renderer"
```

---

## Task 6: Activity graph SVG renderer

**Files:**
- Modify: `scripts/profile_render.py`

- [ ] **Step 1: Add activity template and renderer**

Append to `scripts/profile_render.py`:

```python
ACTIVITY_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="220" viewBox="0 0 1200 220" role="img" aria-labelledby="activity-title">
  <title id="activity-title">Contribution activity, trailing 12 months</title>
  <style>
    .bg { fill: #f4efe6; stroke: #d8d1c2; stroke-width: 1; }
    .ink { fill: #141414; }
    .muted { fill: #555555; }
    .sub-tan { fill: #7a6a4a; }
    .dot { fill: #c94a2a; }
    .serif { font-family: "Charter", "Iowan Old Style", "Times New Roman", Georgia, serif; }
    .mono { font-family: ui-monospace, "SF Mono", Consolas, "Liberation Mono", monospace; }
    .rule { stroke: #141414; stroke-width: 1; }
    .grid { stroke: #141414; stroke-opacity: 0.06; stroke-dasharray: 2 4; }
    .line { fill: none; stroke: #141414; stroke-width: 1.4; }
  </style>

  <rect class="bg" x="0.5" y="0.5" width="1199" height="219" rx="6"/>

  <!-- Header -->
  <text x="48" y="44" class="serif ink" font-size="18" font-weight="500">Figure I. <tspan font-style="italic">Contribution activity, trailing 12 months.</tspan></text>
  <text x="1152" y="44" class="mono muted" font-size="11" letter-spacing="2" text-anchor="end">WEEKLY TOTALS  ·  N = $n_weeks</text>
  <line class="rule" x1="48" y1="58" x2="1152" y2="58"/>

  <!-- Grid -->
  <line class="grid" x1="48" y1="90" x2="1152" y2="90"/>
  <line class="grid" x1="48" y1="130" x2="1152" y2="130"/>
  <line class="grid" x1="48" y1="170" x2="1152" y2="170"/>

  <!-- Area fill -->
  <defs>
    <linearGradient id="inkFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#141414" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#141414" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <path d="$area_path" fill="url(#inkFill)"/>
  <path class="line" d="$line_path"/>

  $markers

  <!-- X axis -->
  <text x="48" y="200" class="mono sub-tan" font-size="10" letter-spacing="1">$month_1</text>
  <text x="232" y="200" class="mono sub-tan" font-size="10" letter-spacing="1">$month_2</text>
  <text x="416" y="200" class="mono sub-tan" font-size="10" letter-spacing="1">$month_3</text>
  <text x="600" y="200" class="mono sub-tan" font-size="10" letter-spacing="1" text-anchor="middle">$month_4</text>
  <text x="784" y="200" class="mono sub-tan" font-size="10" letter-spacing="1">$month_5</text>
  <text x="968" y="200" class="mono sub-tan" font-size="10" letter-spacing="1">$month_6</text>
  <text x="1152" y="200" class="mono sub-tan" font-size="10" letter-spacing="1" text-anchor="end">TODAY</text>
</svg>
""")


_CHART_LEFT = 48
_CHART_RIGHT = 1152
_CHART_TOP = 70
_CHART_BOTTOM = 180


def _build_chart_paths(weekly: list[int]) -> tuple[str, str, list[tuple[float, float]]]:
    """Return (line_path, area_path, points) given weekly totals."""
    if not weekly:
        return "", "", []
    peak = max(weekly) or 1
    width = _CHART_RIGHT - _CHART_LEFT
    height = _CHART_BOTTOM - _CHART_TOP
    step = width / max(len(weekly) - 1, 1)
    points: list[tuple[float, float]] = []
    for i, v in enumerate(weekly):
        x = _CHART_LEFT + i * step
        y = _CHART_BOTTOM - (v / peak) * height
        points.append((x, y))
    line_segments = [f"M{points[0][0]:.1f},{points[0][1]:.1f}"]
    for x, y in points[1:]:
        line_segments.append(f"L{x:.1f},{y:.1f}")
    line_path = " ".join(line_segments)
    area_path = (
        line_path
        + f" L{points[-1][0]:.1f},{_CHART_BOTTOM} L{points[0][0]:.1f},{_CHART_BOTTOM} Z"
    )
    return line_path, area_path, points


def _build_markers(points: list[tuple[float, float]], weekly: list[int]) -> str:
    """Mark the two highest peaks + today's point."""
    if not points:
        return ""
    # Indices of top 2 peaks (excluding the last point, which is always marked)
    indexed = list(enumerate(weekly[:-1]))
    indexed.sort(key=lambda t: t[1], reverse=True)
    peak_indices = [i for i, _ in indexed[:2]]
    markers = []
    for i in peak_indices:
        x, y = points[i]
        markers.append(f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="2.5"/>')
    # Today (last point) - larger ringed marker
    x, y = points[-1]
    markers.append(
        f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="3.5" stroke="#f4efe6" stroke-width="2"/>'
    )
    return "\n  ".join(markers)


_MONTH_ABBREV = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _axis_months(now: datetime) -> list[str]:
    """Return 6 month labels spaced ~2 months apart ending 2 months before today."""
    # Starting 12 months ago, pick months at offsets [0, 2, 4, 6, 8, 10] from start
    start_month = (now.month - 11) % 12 or 12
    start_year = now.year if now.month - 11 > 0 else now.year - 1
    months: list[str] = []
    for offset in (0, 2, 4, 6, 8, 10):
        m = (start_month - 1 + offset) % 12
        months.append(_MONTH_ABBREV[m])
    return months


def render_activity(weekly: list[int], now: datetime | None = None) -> str:
    now = now or datetime.utcnow()
    line_path, area_path, points = _build_chart_paths(weekly)
    markers = _build_markers(points, weekly)
    months = _axis_months(now)
    return ACTIVITY_TEMPLATE.substitute(
        n_weeks=str(len(weekly)),
        line_path=line_path or "M0,0",
        area_path=area_path or "M0,0",
        markers=markers,
        month_1=months[0],
        month_2=months[1],
        month_3=months[2],
        month_4=months[3],
        month_5=months[4],
        month_6=months[5],
    )
```

- [ ] **Step 2: Smoke test with fake weekly data**

Run:

```bash
python -c "from scripts.profile_render import render_activity; import datetime, random; random.seed(1); weekly = [random.randint(5, 90) for _ in range(52)]; open('assets/activity.svg','w').write(render_activity(weekly, now=datetime.datetime(2026,4,18)))"
```

Expected: no error, `assets/activity.svg` exists.

- [ ] **Step 3: Visually inspect `assets/activity.svg`**

Open in browser/VS Code preview. Confirm:
- Cream background, black 1px border
- Header: `Figure I. Contribution activity, trailing 12 months.` + `WEEKLY TOTALS · N = 52`
- Hairline dashed grid lines
- Ink line chart with soft gray fill below
- 2-3 red dot markers on peaks and today
- Month labels across the bottom in mono

- [ ] **Step 4: Commit**

```bash
git add scripts/profile_render.py assets/activity.svg
git commit -m "Add cream editorial activity graph renderer"
```

---

## Task 7: Entry point + first real run

**Files:**
- Create: `scripts/generate_profile.py`

- [ ] **Step 1: Create entry point script**

```python
"""CLI entry point: fetch data, render SVGs, write to disk."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.profile_data import fetch_full_profile, get_token_from_env, fetch_account_created_at
from scripts.profile_render import render_hero, render_activity


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate profile README SVGs")
    parser.add_argument("--login", default="aiedwardyi", help="GitHub login")
    parser.add_argument(
        "--out-dir", default="assets", help="Directory to write hero.svg and activity.svg"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print SVGs to stdout instead of writing files",
    )
    args = parser.parse_args()

    token = get_token_from_env()
    profile = fetch_full_profile(args.login, token)
    created_at = fetch_account_created_at(args.login, token)

    hero_svg = render_hero(
        contributions_total=profile["total_contributions"],
        streak=profile["current_streak"],
        created_year=created_at.year,
    )
    activity_svg = render_activity(profile["weekly_last_year"])

    if args.dry_run:
        print("=== HERO ===")
        print(hero_svg)
        print("=== ACTIVITY ===")
        print(activity_svg)
        return 0

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "hero.svg").write_text(hero_svg, encoding="utf-8")
    (out / "activity.svg").write_text(activity_svg, encoding="utf-8")
    print(f"Wrote {out / 'hero.svg'} and {out / 'activity.svg'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Get a GitHub personal access token**

Create a PAT at https://github.com/settings/tokens with `read:user` scope. Note: if this is a user running the plan, they'll need to create their own PAT — this step cannot be automated.

Set it in the environment:
```bash
export GH_TOKEN=ghp_your_token_here  # macOS/Linux or git-bash on Windows
```

- [ ] **Step 3: Run the script for real**

```bash
python -m scripts.generate_profile --login aiedwardyi
```

Expected: `Wrote assets/hero.svg and assets/activity.svg`. No exceptions.

- [ ] **Step 4: Visually inspect both SVGs**

Open both files in browser/preview. Confirm the numbers are realistic (contributions > 2,000, streak in the tens) and the chart shape looks like real data, not a random blob.

- [ ] **Step 5: Commit**

```bash
git add scripts/generate_profile.py assets/hero.svg assets/activity.svg
git commit -m "Add profile generator entry point and first real run"
```

---

## Task 8: GitHub Action workflow

**Files:**
- Create: `.github/workflows/update-profile.yml`

- [ ] **Step 1: Create workflow**

```yaml
name: Update profile

on:
  schedule:
    - cron: "0 0 * * *"
  push:
    branches: [main]
    paths:
      - scripts/generate_profile.py
      - scripts/profile_data.py
      - scripts/profile_render.py
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

      - name: Install deps
        run: pip install -r requirements.txt

      - name: Generate SVGs
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: python -m scripts.generate_profile --login aiedwardyi

      - name: Commit if changed
        run: |
          git config user.name "profile-bot"
          git config user.email "profile-bot@users.noreply.github.com"
          git add assets/hero.svg assets/activity.svg
          if git diff --cached --quiet; then
            echo "No changes"
          else
            git commit -m "Update profile SVGs"
            git push
          fi
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/update-profile.yml
git commit -m "Add daily profile update workflow"
```

- [ ] **Step 3: Push and test with workflow_dispatch**

```bash
git push origin main
```

Then on github.com, go to **Actions → Update profile → Run workflow**. Watch the run. Expected: green checkmark. If "No changes" appears, that's also success (assets are already current from Task 7).

- [ ] **Step 4: Verify the next scheduled run**

Nothing to do here actively. Note that the next cron run is tomorrow at 00:00 UTC. Check Actions tab then to confirm the scheduled run fired. If it didn't, troubleshoot cron (common gotchas: workflow file must be on `main`, repo must have had activity in last 60 days).

---

## Task 9: README rewrite

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace README**

Replace the entire contents of `README.md` with:

```markdown
<p align="center">
  <img src="./assets/hero.svg" width="96%" alt="Edward Yi — AI Engineer and Founder, Seoul" />
</p>

<p align="center">
  <img src="./assets/activity.svg" width="96%" alt="Contribution activity, trailing 12 months" />
</p>
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "Rewrite README for editorial cream profile"
```

- [ ] **Step 3: Push**

```bash
git push origin main
```

- [ ] **Step 4: Verify on github.com/aiedwardyi**

Open the profile page in a browser (both dark and light mode via GitHub's theme toggle). Confirm:
- Hero renders cream, Edward Yi serif, contributions + streak visible and large
- Activity graph renders cream with ink line
- No broken images, no alignment surprises
- Both modes look intentional (cream-on-dark magazine clipping, cream-on-white paper-on-paper)

---

## Self-Review

**Spec coverage:**
- Editorial cream hero with dateline, byline, name, abstract, contributions, streak → Task 5 ✓
- Cream activity graph with header, hairline grid, ink line, red markers, month axis → Task 6 ✓
- Python generator fetching GraphQL data → Tasks 2, 3, 4 ✓
- Lifetime contribution sum via per-year loop → Task 4 (`fetch_full_profile`) ✓
- Current streak computation → Task 2 ✓
- Weekly aggregation → Task 3 ✓
- Daily GitHub Action cron + push trigger + workflow_dispatch → Task 8 ✓
- No commit when SVG unchanged → Task 8 ✓
- README with only two SVG embeds → Task 9 ✓
- `.gitignore` with `.superpowers/` → already committed pre-plan; Python patterns added in Task 1 ✓
- Error handling: non-zero exit on GraphQL failure (requests `raise_for_status`, `RuntimeError` on errors key) → Task 4 ✓

**Placeholder scan:** No TBDs, TODOs, or "similar to Task N" references. All code steps include complete code. All commands include expected output. Personal access token creation (Task 7 Step 2) is described explicitly because it cannot be automated.

**Type consistency:** `compute_current_streak`, `aggregate_weekly`, `fetch_full_profile`, `render_hero`, `render_activity` names used consistently across tasks. `days` dicts are always `{"date": str, "count": int}`.

**Out of scope (per spec):** Removing legacy `profile-hero-alt-*.svg` files and pruning `concepts/` — intentionally deferred.
