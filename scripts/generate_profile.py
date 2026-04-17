"""CLI entry point: fetch data, render SVGs, write to disk."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.profile_data import fetch_full_profile, get_token_from_env
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

    hero_svg = render_hero(
        contributions_total=profile["total_contributions"],
        streak=profile["current_streak"],
        created_year=profile["created_at"].year,
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
