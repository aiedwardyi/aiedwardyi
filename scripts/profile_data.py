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
