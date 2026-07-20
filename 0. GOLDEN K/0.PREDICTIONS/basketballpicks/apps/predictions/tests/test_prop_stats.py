"""Per-stat prop distributions (bball-03 §4c). Pure-math — no DB."""

import numpy as np
import pytest

from apps.predictions.engines import prop_stats as ps


def test_neg_binom_matches_target_moments():
    d = ps.neg_binom(mean=8.0, vmr=1.5)
    assert d.mean() == pytest.approx(8.0, rel=0.02)
    assert d.var() == pytest.approx(1.5 * 8.0, rel=0.05)  # var = vmr*mean


def test_neg_binom_falls_back_to_poisson_when_not_overdispersed():
    d = ps.neg_binom(mean=5.0, vmr=1.0)
    assert d.family == "poisson"
    assert d.var() == pytest.approx(5.0, rel=0.03)


def test_prob_over_monotone_decreasing():
    d = ps.neg_binom(mean=9.0, vmr=1.4)
    assert d.prob_over(6.5) > d.prob_over(8.5) > d.prob_over(11.5)


def test_over_under_integer_line_pushes():
    d = ps.neg_binom(mean=8.0, vmr=1.3)
    ou = d.over_under(8)  # integer line -> push mass
    assert ou["OVER"] + ou["UNDER"] + ou["PUSH"] == pytest.approx(1.0, abs=1e-9)
    assert ou["PUSH"] > 0
    assert d.over_under(8.5)["PUSH"] == 0.0


def test_points_compound_mean():
    d = ps.points_compound(lam2=6.0, lam3=2.0, lam_ft=4.0)
    assert d.mean() == pytest.approx(2 * 6 + 3 * 2 + 4, rel=0.02)  # = 22
    # 3-point jumps create a right tail: variance exceeds a plain Poisson's
    assert d.var() > d.mean()


def test_threes_made_binomial():
    d = ps.threes_made(attempts_mean=8, three_pct=0.375)
    assert d.mean() == pytest.approx(8 * 0.375, rel=0.02)


def test_copula_correlation_widens_the_sum():
    m1 = ps.neg_binom(12.0, 1.4)  # points-ish
    m2 = ps.neg_binom(7.0, 1.4)  # rebounds-ish
    lo = ps.combine_copula([m1, m2], corr=np.array([[1.0, 0.0], [0.0, 1.0]]), seed=0)
    hi = ps.combine_copula([m1, m2], corr=np.array([[1.0, 0.6], [0.6, 1.0]]), seed=0)
    # positively correlated components -> a wider sum (bball-03 §4c)
    assert hi.var() > lo.var()
    # the sum's mean is preserved regardless of correlation
    assert lo.mean() == pytest.approx(hi.mean(), rel=0.03)
    assert lo.mean() == pytest.approx(19.0, rel=0.05)


def test_materialize_roundtrip_prices_a_line():
    d = ps.neg_binom(9.0, 1.4)
    payload = d.materialize()
    restored = ps.StatDistribution(payload["pmf"], payload["support_start"])
    assert restored.prob_over(8.5) == pytest.approx(d.prob_over(8.5), abs=1e-3)
