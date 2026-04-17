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
