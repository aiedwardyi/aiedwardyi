# Profile Generator Copy and Stats Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make daily profile generation preserve the corrected abstract, remove the unreliable lifetime contribution counter, and retain the streak and activity chart.

**Architecture:** Simplify the data layer to fetch only the trailing 365-day contribution calendar used by the streak and chart. Simplify the hero renderer API to accept only the streak, remove the lifetime-stat markup, and center the streak in the right panel. Protect the behavior with data-layer and renderer regression tests before regenerating the checked-in SVG assets.

**Tech Stack:** Python 3.12, requests, pytest, GitHub GraphQL API, SVG/XML

---

### Task 1: Lock the hero behavior with renderer tests

**Files:**
- Create: `tests/test_profile_render.py`
- Modify: `scripts/profile_render.py`

- [ ] **Step 1: Write failing hero regression tests**

Create `tests/test_profile_render.py`:

```python
from datetime import datetime, timezone
from xml.etree import ElementTree

import pytest

from scripts.profile_render import CHARCOAL, CREAM, render_hero


@pytest.mark.parametrize("theme", [CREAM, CHARCOAL])
def test_render_hero_uses_current_abstract_and_only_streak_stat(theme):
    svg = render_hero(
        streak=123,
        theme=theme,
        now=datetime(2026, 6, 20, tzinfo=timezone.utc),
    )

    ElementTree.fromstring(svg)
    assert "Building systems where agents ship real work into production." in svg
    assert "9 years leading client delivery and dev teams." in svg
    assert "90-dev" not in svg
    assert "200+ products" not in svg
    assert "CONTRIBUTIONS" not in svg
    assert "since 2018" not in svg
    assert ">DAY STREAK<" in svg
    assert ">123<" in svg
    assert ">current<" in svg
    assert 'x="966"' in svg
    assert 'text-anchor="middle"' in svg
```

- [ ] **Step 2: Run the renderer test to verify RED**

Run:

```powershell
python -m pytest tests/test_profile_render.py -v
```

Expected: FAIL because `render_hero` still requires `contributions_total` and `created_year`, and the template still includes the old copy and contribution counter.

- [ ] **Step 3: Simplify the hero template and renderer interface**

In `scripts/profile_render.py`, replace the second abstract line with:

```xml
<tspan x="48" dy="22">9 years leading client delivery and dev teams.</tspan>
```

Replace the right-panel stats markup with:

```xml
  <text class="mono ink" x="966" y="128" font-size="11" letter-spacing="2.5" opacity="0.7" text-anchor="middle">DAY STREAK</text>
  <text x="966" y="192" text-anchor="middle">
    <tspan class="serif ink" font-size="54" font-weight="500" letter-spacing="-1.2">$streak</tspan><tspan class="mono muted" font-size="14" dy="-20" dx="4">d</tspan>
  </text>
  <text class="mono sub-tan" x="966" y="214" font-size="11" text-anchor="middle">current</text>
```

Change `render_hero` to:

```python
def render_hero(
    *,
    streak: int,
    theme: dict = CREAM,
    now: datetime | None = None,
) -> str:
    now = now or datetime.now(timezone.utc)
    dateline = f"No. {now.month:02d}·{now.day:02d}·{now.year}"
    return HERO_TEMPLATE.substitute(
        **theme,
        dateline=dateline,
        streak=str(streak),
    )
```

- [ ] **Step 4: Run the renderer tests to verify GREEN**

Run:

```powershell
python -m pytest tests/test_profile_render.py -v
```

Expected: 2 tests pass.

### Task 2: Remove lifetime contribution fetching

**Files:**
- Modify: `tests/test_profile_data.py`
- Modify: `scripts/profile_data.py`

- [ ] **Step 1: Write a failing single-window data test**

Append to `tests/test_profile_data.py`:

```python
from datetime import datetime, timezone

import scripts.profile_data as profile_data


def test_fetch_full_profile_uses_only_trailing_year_window(monkeypatch):
    now = datetime(2026, 6, 20, 12, 0, tzinfo=timezone.utc)
    calls = []
    calendar = {
        "totalContributions": 999,
        "weeks": [
            {
                "contributionDays": [
                    {"date": "2026-06-18", "contributionCount": 1},
                    {"date": "2026-06-19", "contributionCount": 2},
                    {"date": "2026-06-20", "contributionCount": 3},
                ]
            }
        ],
    }

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return now

    def fake_fetch_year_window(login, token, from_dt, to_dt):
        calls.append((login, token, from_dt, to_dt))
        return calendar

    monkeypatch.setattr(profile_data, "datetime", FixedDateTime)
    monkeypatch.setattr(profile_data, "fetch_year_window", fake_fetch_year_window)

    result = profile_data.fetch_full_profile("aiedwardyi", "token")

    assert len(calls) == 1
    assert calls[0][2] == now - profile_data.timedelta(days=365)
    assert calls[0][3] == now
    assert "total_contributions" not in result
    assert "created_at" not in result
    assert result["current_streak"] == 3
    assert result["weekly_active"] == []
```

- [ ] **Step 2: Run the data test to verify RED**

Run:

```powershell
python -m pytest tests/test_profile_data.py::test_fetch_full_profile_uses_only_trailing_year_window -v
```

Expected: FAIL because `fetch_full_profile` calls `fetch_account_created_at` and performs annual lifetime queries.

- [ ] **Step 3: Simplify the GraphQL data flow**

In `scripts/profile_data.py`:

- Remove `_CREATED_AT_QUERY`.
- Remove `fetch_account_created_at`.
- Remove the annual `lifetime_total` loop.
- Keep a single call using `now - timedelta(days=365)` through `now`.
- Remove `total_contributions` and `created_at` from the documented and returned profile dictionary.

The start of `fetch_full_profile` becomes:

```python
    now = datetime.now(timezone.utc)
    today_iso = now.date().isoformat()

    last_year_from = now - timedelta(days=365)
    cal = fetch_year_window(login, token, last_year_from, now)
```

The return dictionary becomes:

```python
    return {
        "days_active": days_active,
        "current_streak": compute_current_streak(days_active),
        "weekly_active": weekly_active,
        "activity_start": activity_start,
    }
```

- [ ] **Step 4: Run all data tests to verify GREEN**

Run:

```powershell
python -m pytest tests/test_profile_data.py -v
```

Expected: all data tests pass.

### Task 3: Wire the simplified renderer and regenerate assets

**Files:**
- Create: `tests/test_generate_profile.py`
- Modify: `scripts/generate_profile.py`
- Modify: `assets/hero.svg`
- Modify: `assets/hero-dark.svg`

- [ ] **Step 1: Write a failing generator integration test**

Create `tests/test_generate_profile.py`:

```python
from datetime import date
from xml.etree import ElementTree

import scripts.generate_profile as generate_profile


def test_generator_writes_both_hero_themes_and_activity_charts(monkeypatch, tmp_path):
    profile = {
        "current_streak": 123,
        "weekly_active": [7, 14],
        "activity_start": date(2026, 6, 1),
    }

    monkeypatch.setattr(generate_profile, "get_token_from_env", lambda: "token")
    monkeypatch.setattr(
        generate_profile,
        "fetch_full_profile",
        lambda login, token: profile,
    )
    monkeypatch.setattr(
        generate_profile.sys,
        "argv",
        ["generate_profile", "--out-dir", str(tmp_path)],
    )

    assert generate_profile.main() == 0
    for name in ("hero.svg", "hero-dark.svg", "activity.svg", "activity-dark.svg"):
        ElementTree.parse(tmp_path / name)

    hero = (tmp_path / "hero.svg").read_text(encoding="utf-8")
    dark_hero = (tmp_path / "hero-dark.svg").read_text(encoding="utf-8")
    for svg in (hero, dark_hero):
        assert "9 years leading client delivery and dev teams." in svg
        assert "CONTRIBUTIONS" not in svg
        assert ">123<" in svg
```

- [ ] **Step 2: Run the generator test to verify RED**

Run:

```powershell
python -m pytest tests/test_generate_profile.py -v
```

Expected: FAIL with `KeyError: 'total_contributions'` because the generator still passes removed lifetime fields to `render_hero`.

- [ ] **Step 3: Update generator calls**

Change both hero calls in `scripts/generate_profile.py` to:

```python
        "hero.svg": render_hero(
            streak=profile["current_streak"],
            theme=CREAM,
        ),
        "hero-dark.svg": render_hero(
            streak=profile["current_streak"],
            theme=CHARCOAL,
        ),
```

- [ ] **Step 4: Run the full test suite**

Run:

```powershell
python -m pytest -v
```

Expected: all tests pass.

- [ ] **Step 5: Regenerate the two hero SVG assets from the fixed renderer**

Run:

```powershell
$streak = [regex]::Match((Get-Content -Raw assets/hero.svg), '<tspan class="serif ink"[^>]*>(\d+)</tspan>').Groups[1].Value
@"
from pathlib import Path
from scripts.profile_render import CHARCOAL, CREAM, render_hero
streak = int("$streak")
Path("assets/hero.svg").write_text(render_hero(streak=streak, theme=CREAM), encoding="utf-8")
Path("assets/hero-dark.svg").write_text(render_hero(streak=streak, theme=CHARCOAL), encoding="utf-8")
"@ | python -
```

This uses the most recently generated streak already present in the checked-in asset. The activity assets remain unchanged because their data and renderer are unchanged; the scheduled workflow will refresh all four assets after the fixed generator lands.

- [ ] **Step 6: Verify generated output**

Run:

```powershell
$files = @('assets/hero.svg','assets/hero-dark.svg','assets/activity.svg','assets/activity-dark.svg')
foreach ($file in $files) { [void][xml](Get-Content -Raw $file) }
rg -n "9 years leading client delivery|90-dev|200\+ products|CONTRIBUTIONS|since 2018|DAY STREAK" assets scripts tests
git diff --check
```

Expected:

- both hero assets contain the corrected abstract;
- neither scripts nor generated assets contain the old copy;
- neither hero contains the contribution counter;
- both heroes retain the streak;
- all four SVGs parse as XML;
- `git diff --check` exits successfully.

- [ ] **Step 7: Commit the implementation**

Run:

```powershell
git add scripts/profile_data.py scripts/profile_render.py scripts/generate_profile.py tests/test_profile_data.py tests/test_profile_render.py tests/test_generate_profile.py assets/hero.svg assets/hero-dark.svg docs/superpowers/plans/2026-06-20-profile-generator-copy-and-stats.md
git commit -m "Fix generated profile banner stats"
```

- [ ] **Step 8: Verify commit metadata and push**

Run:

```powershell
git show --quiet --format=fuller HEAD
git show --quiet --format=%B HEAD
git push origin main
git ls-remote origin refs/heads/main
```

Expected: the commit is authored and committed by `aiedwardyi`, contains no attribution trailers, and the remote `main` SHA matches local `HEAD`.
