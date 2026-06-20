from datetime import date
from xml.etree import ElementTree

import scripts.generate_profile as generate_profile


def test_generator_writes_both_hero_themes_and_activity_charts(
    monkeypatch, tmp_path
):
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
        assert ">123</tspan>" in svg
