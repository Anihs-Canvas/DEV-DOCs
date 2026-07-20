"""Minutes distribution + usage->stat projection (bball-03 §4a/§4b).
Pure-math — no DB."""

import numpy as np
import pytest

from apps.predictions.distribution import MarginTotalDistribution
from apps.predictions.engines.minutes import (
    MinutesDistribution,
    UsageProjection,
    blowout_prob_from_core,
)


def test_effective_moments_baseline():
    m = MinutesDistribution(mean=32.0, sd=5.0, p_active=1.0, blowout_prob=0.0)
    mean, var = m.effective_moments()
    assert mean == pytest.approx(32.0)
    assert var == pytest.approx(25.0, rel=1e-6)


def test_dnp_gate_scales_mean_and_adds_variance():
    m = MinutesDistribution(mean=30.0, sd=5.0, p_active=0.5)
    mean, var = m.effective_moments()
    assert mean == pytest.approx(15.0)
    # DNP risk adds a big between-state variance term
    assert var > 25.0


def test_blowout_haircut_lowers_conditional_mean():
    base = MinutesDistribution(mean=34.0, sd=5.0, blowout_prob=0.0).conditional_moments()[0]
    blown = MinutesDistribution(mean=34.0, sd=5.0, blowout_prob=0.5, blowout_haircut=8.0)
    assert blown.conditional_moments()[0] < base


def test_blowout_prob_from_core_rises_with_margin():
    lopsided = MarginTotalDistribution(mu_margin=15, sigma_margin=12, mu_total=224, sigma_total=16)
    even = MarginTotalDistribution(mu_margin=0, sigma_margin=12, mu_total=224, sigma_total=16)
    assert blowout_prob_from_core(lopsided) > blowout_prob_from_core(even)


def test_usage_projection_feeds_stats_with_minutes_driven_overdispersion():
    m = MinutesDistribution(mean=32.0, sd=6.0, p_active=0.95)
    up = UsageProjection(m, reb_per_min=0.25, ast_per_min=0.18, base_overdisp=1.15)
    reb = up.rebounds()
    em, _ = m.effective_moments()
    assert reb.mean() == pytest.approx(0.25 * em, rel=0.05)
    # minutes uncertainty pushes the counting stat into overdispersion (NB, vmr>1)
    assert reb.var() > reb.mean()


def test_usage_points_and_combo():
    m = MinutesDistribution(mean=34.0, sd=5.0)
    up = UsageProjection(
        m, reb_per_min=0.2, ast_per_min=0.15,
        fg2_makes_per_min=0.18, tpm_per_min=0.08, ft_makes_per_min=0.12,
    )
    pts = up.points()
    em, _ = m.effective_moments()
    assert pts.mean() == pytest.approx((2 * 0.18 + 3 * 0.08 + 0.12) * em, rel=0.05)
    pra = up.combo(["points", "rebounds", "assists"])
    # PRA mean ~ sum of component means
    assert pra.mean() == pytest.approx(pts.mean() + up.rebounds().mean() + up.assists().mean(), rel=0.05)
