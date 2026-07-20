"""The margin+total predictive distribution & the derived market ladder
(bball-03 §2d/§2e). Pure-math — no DB."""

import numpy as np
import pytest
from scipy.stats import norm

from apps.predictions.distribution import (
    FAMILY_T,
    MarginTotalDistribution,
    estimate_sigma,
    _frozen,
)


def _d(mu_m=5.0, sig_m=12.0, mu_t=224.0, sig_t=16.0, **kw):
    return MarginTotalDistribution(mu_m, sig_m, mu_t, sig_t, **kw)


def test_moneyline_matches_normal_survival():
    d = _d()
    assert d.prob_home_ml() == pytest.approx(norm.sf(0, 5, 12), abs=1e-6)
    ml = d.moneyline()
    assert ml["HOME"] + ml["AWAY"] == pytest.approx(1.0)


def test_spread_win_push_lose_sums_to_one():
    d = _d()
    s = d.spread(-5)  # integer line -> push band
    assert s["HOME"] + s["AWAY"] + s["PUSH"] == pytest.approx(1.0, abs=1e-9)
    assert s["PUSH"] > 0
    # at the fair-ish line the home cover prob is near 0.5
    assert 0.4 < s["HOME"] < 0.6


def test_spread_monotone_in_line():
    d = _d()
    # a smaller favorite line is easier to cover than a larger one
    assert d.spread(-3)["HOME"] > d.spread(-7)["HOME"]


def test_total_monotone_and_pushes():
    d = _d()
    assert d.total(214)["OVER"] > d.total(234)["OVER"]
    t = d.total(224)
    assert t["OVER"] + t["UNDER"] + t["PUSH"] == pytest.approx(1.0, abs=1e-9)
    assert t["PUSH"] > 0
    # half-line never pushes
    assert d.total(224.5)["PUSH"] == 0.0


def test_team_totals_consistent_with_game():
    d = _d(mu_m=6, mu_t=220)
    home = d.team_total(113, home=True)
    away = d.team_total(107, home=False)
    for blk in (home, away):
        assert 0.0 <= blk["OVER"] <= 1.0
        assert blk["OVER"] + blk["UNDER"] + blk["PUSH"] == pytest.approx(1.0, abs=1e-9)


def test_crps_matches_metric():
    from apps.predictions.metrics import crps_gaussian

    d = _d()
    assert d.crps_margin(3.0) == pytest.approx(float(crps_gaussian(5, 12, 3)), abs=1e-9)


def test_pit_uniform_under_correct_model():
    from apps.predictions.metrics import pit_calibration_error, pit_values

    rng = np.random.default_rng(1)
    mu, sig = 4.0, 12.0
    actuals = rng.normal(mu, sig, 20000)
    d = _d(mu_m=mu, sig_m=sig)
    pits = pit_values([d.pit_margin(a) for a in actuals])
    assert pits.mean() == pytest.approx(0.5, abs=0.02)
    assert pit_calibration_error(pits) < 0.05


def test_student_t_preserves_sd():
    dist = _frozen(0.0, 12.0, FAMILY_T, dof=8, skew=0.0)
    samples = dist.rvs(size=200000, random_state=0)
    assert np.std(samples) == pytest.approx(12.0, rel=0.03)


def test_estimate_sigma_clamped():
    assert estimate_sigma(np.random.default_rng(0).normal(0, 12, 500)) == pytest.approx(12, abs=1.5)
    assert estimate_sigma([1.0]) >= 8.0  # degenerate sample clamped to floor
    assert estimate_sigma(np.zeros(50)) == 8.0  # zero-variance clamps to floor
