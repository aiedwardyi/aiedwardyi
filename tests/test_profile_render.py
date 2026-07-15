from datetime import datetime, timezone
from xml.etree import ElementTree

import pytest

from scripts.profile_render import CHARCOAL, CREAM, _SEAL_GLYPH, render_hero


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
    assert "90" + "-dev" not in svg
    assert "200" + "+ products" not in svg
    assert "CONTRIBUTIONS" not in svg
    assert "since " + "2018" not in svg
    assert ">DAY STREAK<" in svg
    assert ">123</tspan>" in svg
    assert ">current</text>" in svg
    assert 'x="966"' in svg
    assert 'text-anchor="middle"' in svg


@pytest.mark.parametrize("theme", [CREAM, CHARCOAL])
def test_render_hero_stamps_name_seal(theme):
    svg = render_hero(
        streak=123,
        theme=theme,
        now=datetime(2026, 6, 20, tzinfo=timezone.utc),
    )

    ElementTree.fromstring(svg)
    assert _SEAL_GLYPH in svg
    assert "rotate(-3 50 50)" in svg
    assert f'fill="{theme["seal"]}"' in svg
    assert f'fill="{theme["seal_negative"]}"' in svg
