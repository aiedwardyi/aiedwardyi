"""SVG templates for the editorial profile.

Two themes: cream (light mode) and charcoal (dark mode). Same editorial
skeleton, inverted palette. Uses string.Template ($var substitution)
because SVG/CSS are dense with braces and f-string escaping gets ugly fast.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from string import Template


# Cream: warm paper on light mode.
CREAM = {
    "bg": "#f4efe6",
    "border": "#d8d1c2",
    "ink": "#141414",
    "muted": "#555555",
    "tan": "#8a7a5a",
    "sub_tan": "#7a6a4a",
    "dot": "#c94a2a",
    "grid_opacity": "0.06",
    "area_top_opacity": "0.18",
    "marker_ring": "#f4efe6",
}

# Charcoal: warm deep paper on dark mode. Sits intentionally above
# GitHub dark canvas (#0d1117) as a distinct piece.
CHARCOAL = {
    "bg": "#1a1612",
    "border": "#2c2720",
    "ink": "#ebdfc5",
    "muted": "#a89b81",
    "tan": "#c19a5d",
    "sub_tan": "#9c8456",
    "dot": "#e87252",
    "grid_opacity": "0.12",
    "area_top_opacity": "0.22",
    "marker_ring": "#1a1612",
}


HERO_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-labelledby="hero-title">
  <title id="hero-title">Edward Yi profile hero</title>
  <style>
    .bg { fill: $bg; stroke: $border; stroke-width: 1; }
    .ink { fill: $ink; }
    .muted { fill: $muted; }
    .tan { fill: $tan; }
    .sub-tan { fill: $sub_tan; }
    .dot { fill: $dot; }
    .serif { font-family: "Charter", "Iowan Old Style", "Times New Roman", Georgia, serif; }
    .mono { font-family: ui-monospace, "SF Mono", Consolas, "Liberation Mono", monospace; }
    .rule { stroke: $ink; stroke-width: 1; }
  </style>

  <rect class="bg" x="0.5" y="0.5" width="1199" height="359" rx="6"/>

  <!-- Top rule -->
  <text class="mono ink" x="48" y="56" font-size="11" letter-spacing="3" text-transform="uppercase">$dateline</text>
  <circle class="dot" cx="840" cy="51.5" r="3.5"/>
  <text class="mono ink" x="852" y="56" font-size="11" letter-spacing="3">SHIPPING DAILY</text>
  <text class="mono ink" x="1152" y="56" font-size="11" letter-spacing="3" text-anchor="end">SEOUL</text>
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


ACTIVITY_TEMPLATE = Template("""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="220" viewBox="0 0 1200 220" role="img" aria-labelledby="activity-title">
  <title id="activity-title">Contribution activity since $since_label</title>
  <style>
    .bg { fill: $bg; stroke: $border; stroke-width: 1; }
    .ink { fill: $ink; }
    .muted { fill: $muted; }
    .sub-tan { fill: $sub_tan; }
    .dot { fill: $dot; }
    .serif { font-family: "Charter", "Iowan Old Style", "Times New Roman", Georgia, serif; }
    .mono { font-family: ui-monospace, "SF Mono", Consolas, "Liberation Mono", monospace; }
    .rule { stroke: $ink; stroke-width: 1; }
    .grid { stroke: $ink; stroke-opacity: $grid_opacity; stroke-dasharray: 2 4; }
    .line { fill: none; stroke: $ink; stroke-width: 1.4; }
  </style>

  <rect class="bg" x="0.5" y="0.5" width="1199" height="219" rx="6"/>

  <!-- Header -->
  <text x="48" y="44" class="serif ink" font-size="18" font-weight="500">Figure I. <tspan font-style="italic">Contribution activity, since $since_label.</tspan></text>
  <text x="1152" y="44" class="mono muted" font-size="11" letter-spacing="2" text-anchor="end">WEEKLY TOTALS  ·  N = $n_weeks</text>
  <line class="rule" x1="48" y1="58" x2="1152" y2="58"/>

  <!-- Grid -->
  <line class="grid" x1="48" y1="90" x2="1152" y2="90"/>
  <line class="grid" x1="48" y1="130" x2="1152" y2="130"/>
  <line class="grid" x1="48" y1="170" x2="1152" y2="170"/>

  <!-- Area fill -->
  <defs>
    <linearGradient id="inkFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="$ink" stop-opacity="$area_top_opacity"/>
      <stop offset="100%" stop-color="$ink" stop-opacity="0"/>
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


def _build_markers(
    points: list[tuple[float, float]],
    weekly: list[int],
    marker_ring: str,
) -> str:
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
        f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="3.5" stroke="{marker_ring}" stroke-width="2"/>'
    )
    return "\n  ".join(markers)


_MONTH_ABBREV = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _axis_months_range(start: date, end: date) -> list[str]:
    """Return 6 month abbreviations evenly spaced across [start, end)."""
    total_days = (end - start).days
    if total_days <= 0:
        return [_MONTH_ABBREV[end.month - 1]] * 6
    months: list[str] = []
    for i in range(6):
        offset_days = int(total_days * i / 6)
        d = start + timedelta(days=offset_days)
        months.append(_MONTH_ABBREV[d.month - 1])
    return months


def _since_label(start: date) -> str:
    """Format a human-readable 'since' label like 'Jan 2026'."""
    return f"{_MONTH_ABBREV[start.month - 1].capitalize()} {start.year}"


def render_hero(
    *,
    contributions_total: int,
    streak: int,
    created_year: int,
    theme: dict = CREAM,
    now: datetime | None = None,
) -> str:
    now = now or datetime.now(timezone.utc)
    dateline = f"No. {now.month:02d}·{now.day:02d}·{now.year}"
    return HERO_TEMPLATE.substitute(
        **theme,
        dateline=dateline,
        contributions_total=f"{contributions_total:,}",
        streak=str(streak),
        created_year=str(created_year),
    )


def render_activity(
    weekly: list[int],
    *,
    start_date: date,
    theme: dict = CREAM,
    now: datetime | None = None,
) -> str:
    now = now or datetime.now(timezone.utc)
    line_path, area_path, points = _build_chart_paths(weekly)
    markers = _build_markers(points, weekly, theme["marker_ring"])
    months = _axis_months_range(start_date, now.date())
    return ACTIVITY_TEMPLATE.substitute(
        **theme,
        n_weeks=str(len(weekly)),
        since_label=_since_label(start_date),
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
