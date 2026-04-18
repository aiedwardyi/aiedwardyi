"""CLI entry point: fetch data, render SVGs, write to disk."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.profile_data import fetch_full_profile, get_token_from_env
from scripts.profile_render import CHARCOAL, CREAM, render_activity, render_hero


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate profile README SVGs")
    parser.add_argument("--login", default="aiedwardyi", help="GitHub login")
    parser.add_argument(
        "--out-dir", default="assets", help="Directory to write SVGs"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print SVGs to stdout instead of writing files",
    )
    args = parser.parse_args()

    token = get_token_from_env()
    profile = fetch_full_profile(args.login, token)

    variants = {
        "hero.svg": render_hero(
            contributions_total=profile["total_contributions"],
            streak=profile["current_streak"],
            created_year=profile["created_at"].year,
            theme=CREAM,
        ),
        "hero-dark.svg": render_hero(
            contributions_total=profile["total_contributions"],
            streak=profile["current_streak"],
            created_year=profile["created_at"].year,
            theme=CHARCOAL,
        ),
        "activity.svg": render_activity(
            profile["weekly_active"],
            start_date=profile["activity_start"],
            theme=CREAM,
        ),
        "activity-dark.svg": render_activity(
            profile["weekly_active"],
            start_date=profile["activity_start"],
            theme=CHARCOAL,
        ),
    }

    if args.dry_run:
        for name, svg in variants.items():
            print(f"=== {name} ===")
            print(svg)
        return 0

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, svg in variants.items():
        (out / name).write_text(svg, encoding="utf-8")
    print(f"Wrote {len(variants)} SVGs to {out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
