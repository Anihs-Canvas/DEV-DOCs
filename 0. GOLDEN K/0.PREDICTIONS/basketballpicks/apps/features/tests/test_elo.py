"""Margin-aware Elo (bball-03 §2c-ii). Pure-math — no DB."""

import pytest

from apps.features import elo


def test_home_win_raises_home_elo():
    eh, ea = elo.update(1500, 1500, home_margin=12)
    assert eh > 1500 > ea


def test_bigger_win_moves_more():
    small = elo.update(1500, 1500, home_margin=2)[0] - 1500
    big = elo.update(1500, 1500, home_margin=25)[0] - 1500
    assert big > small > 0


def test_expected_margin_monotone_in_gap():
    assert elo.expected_margin(1600, 1500) > elo.expected_margin(1500, 1500) > elo.expected_margin(1400, 1500)


def test_win_prob_bounds_and_home_edge():
    p = elo.expected_win_prob(1500, 1500)
    assert 0.5 < p < 0.65  # equal teams, home edge tilts above .5


def test_regress_to_mean_pulls_in():
    assert elo.regress_to_mean(1700) < 1700
    assert elo.regress_to_mean(1300) > 1300


def test_streaming_model_predict_then_observe():
    m = elo.EloModel()
    pred = m.predict("A", "B")
    assert pred["elo_home"] == pytest.approx(1500)
    m.observe("A", "B", home_margin=15)
    assert m.get("A") > m.get("B")
    a_before = m.get("A")
    m.new_season()
    assert m.get("A") < a_before  # A was above mean -> regressed downward
