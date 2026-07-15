"""SVG templates for the editorial profile.

Two themes: cream (light mode) and charcoal (dark mode). Same editorial
skeleton, inverted palette. Uses string.Template ($var substitution)
because SVG/CSS are dense with braces and f-string escaping gets ugly fast.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from string import Template


# Cream: soft off-white with a whisper of warmth. Tuned to sit naturally
# against GitHub's near-white canvas without reading as yellowed paper.
CREAM = {
    "bg": "#fcfaf5",
    "border": "#eae6da",
    "ink": "#141414",
    "muted": "#555555",
    "tan": "#94876a",
    "sub_tan": "#80735a",
    "dot": "#c94a2a",
    # Seal colors mirror edwardyi.dev (--seal / --seal-negative).
    "seal": "#c03a2b",
    "seal_negative": "#f6efe0",
    "grid_opacity": "0.06",
    "area_top_opacity": "0.18",
    "marker_ring": "#fcfaf5",
}

# Charcoal: cool deep graphite for dark mode. Sits deeper than GitHub's
# canvas (#0d1117) so the card reads as a distinct slab. Cool neutral
# palette; warm red - the dot and the seal - is the only intentional heat.
CHARCOAL = {
    "bg": "#0a0d13",
    "border": "#1d2129",
    "ink": "#dfe4eb",
    "muted": "#8b9099",
    "tan": "#9aa1ac",
    "sub_tan": "#6d7480",
    "dot": "#e87252",
    "seal": "#c8473a",
    "seal_negative": "#14110e",
    "grid_opacity": "0.12",
    "area_top_opacity": "0.20",
    "marker_ring": "#0a0d13",
}


# 674E (Yi) from Shippori Mincho 600, vendored as an outline: GitHub renders
# README SVGs in <img> context where webfonts can't load, and a raw <text>
# glyph would vary by OS or show tofu. Drawn at font-size 44 in the seal's
# 100x100 box, bbox-centered at (50, 53).
_SEAL_GLYPH = (
    "M63.4 37.7Q63.6 37.4 63.9 37.1Q64.2 36.7 64.4 36.4Q64.7 36.1 64.9 36.1"
    "Q65.1 36.1 66.2 36.9Q67.2 37.7 68.2 38.7Q69.1 39.6 69.1 39.9Q69 40.6 68 40.6"
    "H53.6Q56.2 43.5 60.8 45.7Q65.3 48 70 49.3L69.9 49.7Q67.6 50.2 66.7 53.4"
    "Q62.2 51.2 58.4 47.9Q54.6 44.6 52.4 40.6H51.9V43.8Q52 47.8 52.2 50"
    "Q51.9 50.5 50.8 50.9Q49.7 51.4 48.6 51.4Q48.1 51.4 47.9 51.1Q47.6 50.8 47.6 50.5"
    "Q47.8 48.7 47.9 45.9V43.1Q44.7 46.5 40.2 49.3Q35.7 52 30.4 53.9L30 53.3"
    "Q34.4 51 38.3 47.6Q42.2 44.2 44.9 40.6H38.4Q35.3 40.6 31.8 41.2L30.6 39"
    "Q33.1 39.2 36.5 39.3H47.9Q47.9 35.1 47.4 32.5Q50.6 33.2 51.8 33.7Q53 34.1 53 34.4"
    "Q53 34.7 52.6 34.9L51.9 35.4V39.3H62.3ZM57.9 51.8Q58.1 51.6 58.5 51.1"
    "Q59 50.7 59.2 50.7Q59.5 50.7 60.4 51.4Q61.3 52.2 62 53.1Q62.8 54 62.8 54.3"
    "Q62.5 54.5 62.1 54.6Q61.8 54.7 61.1 54.7Q59.7 55.5 57.6 56.4Q55.5 57.2 53.3 57.9"
    "Q53.2 58.2 52.9 58.4Q52.6 58.6 51.9 58.8V61H63L64 59.5Q64.2 59.2 64.5 58.8"
    "Q64.8 58.3 65 58.1Q65.3 57.9 65.4 57.9Q65.7 57.9 66.8 58.7Q67.8 59.5 68.7 60.4"
    "Q69.7 61.3 69.7 61.6Q69.5 62.3 68.5 62.3H51.9V68.4Q51.9 70.1 51.5 71.1"
    "Q51.1 72.1 49.9 72.7Q48.7 73.3 46.3 73.5Q46.2 71.6 45.3 70.7Q44.8 70.2 44 69.9"
    "Q43.1 69.5 41.6 69.3V68.7Q46.3 69 47.1 69Q47.5 69 47.7 68.8Q47.9 68.7 47.9 68.2"
    "V62.3H37.8Q34.7 62.3 31.2 62.9L30.1 60.7Q32.5 60.9 36 61H47.9Q47.9 58.4 47.7 56.9"
    "L52 57.5Q54.3 56 56.2 54.1H45.2Q42.1 54.1 38.6 54.7L37.5 52.5Q39.9 52.7 43.4 52.8H57Z"
)


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

  <!-- Name seal, stamped after the signature. x=352 hugs the rendered width
       of "Edward Yi" at 64px serif; reposition if the name text changes. -->
  <g transform="translate(352,138.5) scale(0.5) rotate(-3 50 50)">
    <rect x="9" y="9" width="82" height="82" rx="7" fill="$seal"/>
    <rect x="17" y="17" width="66" height="66" rx="3" fill="none" stroke="$seal_negative" stroke-opacity="0.5" stroke-width="2.5"/>
    <path d="$seal_glyph" fill="$seal_negative"/>
  </g>

  <text class="mono tan" x="48" y="224" font-size="11" letter-spacing="2.5">ABSTRACT</text>

  <!-- Abstract body, two lines -->
  <text class="serif ink" x="48" y="254" font-size="16" font-style="italic">
    <tspan x="48" dy="0">Building systems where agents ship real work into production.</tspan>
    <tspan x="48" dy="22">9 years leading client delivery and dev teams.</tspan>
  </text>

  <!-- Right column: stats -->
  <line class="rule" x1="780" y1="100" x2="780" y2="300"/>

  <text class="mono ink" x="966" y="128" font-size="11" letter-spacing="2.5" opacity="0.7" text-anchor="middle">DAY STREAK</text>
  <text x="966" y="192" text-anchor="middle">
    <tspan class="serif ink" font-size="54" font-weight="500" letter-spacing="-1.2">$streak</tspan><tspan class="mono muted" font-size="14" dy="-20" dx="4">d</tspan>
  </text>
  <text class="mono sub-tan" x="966" y="214" font-size="11" text-anchor="middle">current</text>
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
        seal_glyph=_SEAL_GLYPH,
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
