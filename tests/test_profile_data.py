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
