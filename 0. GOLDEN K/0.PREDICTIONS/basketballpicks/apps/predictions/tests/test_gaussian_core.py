"""core-v1 end-to-end on synthetic ratings (bball-03 §2). Pure-math — no DB."""

import numpy as np
import pytest

from apps.features.ratings import EfficiencyRatings
from apps.predictions.gaussian_core import CoreTeamModel, GameContext


def _ratings(off_home=6.0, off_away=-2.0):
    # team 0 = home-ish strong offense, team 1 = weaker
    return EfficiencyRatings(
        teams=[0, 1],
        off=np.array([off_home, off_away]),
        deff=np.array([0.0, 0.0]),
        mu=112.0,
        hca=2.5,
    )


def _ctx(**kw):
    base = dict(
        home_team=0,
        away_team=1,
        ratings=_ratings(),
        pace={0: 100.0, 1: 100.0},
        pace_league=100.0,
        elo_margin=6.0,
    )
    base.update(kw)
    return GameContext(**base)


def test_stronger_home_team_is_favored():
    d = CoreTeamModel().predict(_ctx())
    assert d.mu_margin > 0
    assert d.prob_home_ml() > 0.5


def test_back_to_back_penalizes_home_margin():
    model = CoreTeamModel()
    base = model.predict(_ctx()).mu_margin
    b2b = model.predict(_ctx(home_b2b=True)).mu_margin
    assert b2b < base
    # an away B2B helps the home margin
    assert model.predict(_ctx(away_b2b=True)).mu_margin > base


def test_lineup_uncertainty_widens_sigma():
    model = CoreTeamModel()
    tight = model.predict(_ctx(lineup_uncertainty=0.0)).sigma_margin
    wide = model.predict(_ctx(lineup_uncertainty=1.0)).sigma_margin
    assert wide > tight


def test_elo_ensemble_pulls_margin():
    model = CoreTeamModel()
    low_elo = model.predict(_ctx(elo_margin=-10.0)).mu_margin
    high_elo = model.predict(_ctx(elo_margin=20.0)).mu_margin
    assert high_elo > low_elo


def test_prob_vector_shape_and_coherence():
    pv = CoreTeamModel().prob_vector(_ctx())
    assert set(pv) >= {"dist", "ML", "SPREAD", "TOTAL", "TEAM_TOTAL", "meta"}
    assert pv["ML"]["HOME"] + pv["ML"]["AWAY"] == pytest.approx(1.0)
    s = pv["SPREAD"]
    assert s["HOME"] + s["AWAY"] + s["PUSH"] == pytest.approx(1.0, abs=1e-9)
    assert pv["dist"]["margin"]["sigma"] > 0
    # totals should be sane basketball numbers
    assert 150 < pv["dist"]["total"]["mu"] < 300
