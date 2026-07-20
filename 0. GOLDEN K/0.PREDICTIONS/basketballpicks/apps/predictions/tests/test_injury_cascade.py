"""Injury-cascade lineup re-solve (bball-03 §4d). Pure-math — no DB."""

import pytest

from apps.predictions.engines.injury_cascade import (
    LineupPlayer,
    minutes_conserved,
    resolve_lineup,
)


def _lineup():
    return [
        LineupPlayer("star_g", "G", 34, 28),
        LineupPlayer("wing", "G-F", 30, 20),
        LineupPlayer("big", "C", 30, 22),
        LineupPlayer("role_f", "F", 26, 14),
        LineupPlayer("starter5", "G", 26, 16),
        LineupPlayer("bench_g", "G", 16, 12),
        LineupPlayer("bench_f", "F", 12, 10),
        LineupPlayer("deep_c", "C", 6, 8),
    ]


def test_out_star_minutes_flow_to_teammates():
    players = _lineup()
    resolved = resolve_lineup(players, out_ids=["star_g"])
    assert "star_g" not in resolved
    # the same-position backup guard should absorb meaningful minutes
    assert resolved["bench_g"]["minutes_gain"] > 0
    assert resolved["starter5"]["minutes_gain"] > 0
    # total gains equal the freed minutes (unless capped out)
    total_gain = sum(v["minutes_gain"] for v in resolved.values())
    assert total_gain == pytest.approx(34.0, abs=0.5)


def test_usage_bumps_follow_absorbed_minutes():
    players = _lineup()
    resolved = resolve_lineup(players, out_ids=["star_g"])
    # freed usage (28) redistributes; whoever gains the most minutes gains usage
    gainer = max(resolved.values(), key=lambda v: v["minutes_gain"])
    assert gainer["usage_gain"] > 0
    total_usage_gain = sum(v["usage_gain"] for v in resolved.values())
    assert total_usage_gain == pytest.approx(28.0, abs=0.5)


def test_team_minutes_conserved():
    players = _lineup()
    resolved = resolve_lineup(players, out_ids=["star_g", "big"])
    assert minutes_conserved(players, resolved, out_ids=["star_g", "big"])


def test_minute_cap_respected():
    players = _lineup()
    resolved = resolve_lineup(players, out_ids=["star_g", "wing"], minute_cap=40.0)
    assert all(v["minutes"] <= 40.0 + 1e-6 for v in resolved.values())


def test_no_outs_is_identity():
    players = _lineup()
    resolved = resolve_lineup(players, out_ids=[])
    for p in players:
        assert resolved[p.id]["minutes"] == pytest.approx(p.base_minutes)
        assert resolved[p.id]["minutes_gain"] == 0.0
