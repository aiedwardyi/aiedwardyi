"""Data layer for profile generator.

Fetches contribution calendar data from the GitHub GraphQL API and computes
summary metrics. Pure functions where possible - only the fetch layer does I/O.
"""
from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

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


def compute_current_streak(days: Iterable[dict]) -> int:
    """Count consecutive days with count >= 1, walking backward from the last day.

    Caller must pre-filter out future-dated days. GitHub's contribution calendar
    returns whole Sun-Sat weeks, padding future days with count=0 - those would
    otherwise break the streak immediately on any non-Saturday.

    Args:
        days: Sequence of {'date': str, 'count': int} dicts, oldest first,
            containing only dates up to and including today.

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

    The weekly series is trimmed to start at the first non-zero week so
    long empty prefixes (e.g., account idle for months then ramped up)
    don't dominate the graph.

    Returns:
        {
          'total_contributions': int,       # full lifetime total
          'created_at': datetime,           # account creation (UTC)
          'days_active': list[{date,count}], # trimmed, ordered oldest->newest, <= today
          'current_streak': int,
          'weekly_active': list[int],       # weekly totals from first active week
          'activity_start': date,           # first day of the first active week
        }
    """
    now = datetime.now(timezone.utc)
    today_iso = now.date().isoformat()
    created_at = fetch_account_created_at(login, token)

    # Lifetime total: sum contributionCalendar.totalContributions across each year window
    lifetime_total = 0
    for year in range(created_at.year, now.year + 1):
        window_from = datetime(year, 1, 1, tzinfo=timezone.utc)
        window_to = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        if window_from < created_at:
            window_from = created_at
        if window_to > now:
            window_to = now
        cal = fetch_year_window(login, token, window_from, window_to)
        lifetime_total += cal["totalContributions"]

    # Trailing 12 months for streak + weekly graph. timedelta (not replace(year=...))
    # so Feb 29 doesn't crash.
    last_year_from = now - timedelta(days=365)
    cal = fetch_year_window(login, token, last_year_from, now)
    days = _flatten_days(cal)
    # Drop future-dated days that GitHub pads into the final Sun-Sat week.
    days = [d for d in days if d["date"] <= today_iso]

    # Trim to first non-zero week so the graph doesn't open on a flat run of zeros.
    weekly_full = aggregate_weekly(days)
    first_active_week = next((i for i, w in enumerate(weekly_full) if w > 0), 0)
    first_day_idx = first_active_week * 7
    days_active = days[first_day_idx:] if days else []
    weekly_active = weekly_full[first_active_week:] if weekly_full else []
    if days_active:
        activity_start = date.fromisoformat(days_active[0]["date"])
    else:
        activity_start = now.date()

    return {
        "total_contributions": lifetime_total,
        "created_at": created_at,
        "days_active": days_active,
        "current_streak": compute_current_streak(days_active),
        "weekly_active": weekly_active,
        "activity_start": activity_start,
    }


def get_token_from_env() -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN must be set")
    return token
