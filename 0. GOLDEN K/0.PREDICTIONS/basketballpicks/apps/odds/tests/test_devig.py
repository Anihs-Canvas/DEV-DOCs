"""Parity tests for the verbatim-copied Shin de-vig (apps.odds.devig). No Django."""

import numpy as np
import pytest

from apps.odds import devig


def test_shin_probabilities_sum_to_one():
    p, z = devig.shin([1.90, 1.95])
    assert p.sum() == pytest.approx(1.0)
    assert 0.0 <= z < 0.5


def test_fair_book_returns_normalized_implied():
    # a book with no overround: shin removes nothing.
    p, z = devig.shin([2.0, 2.0])
    assert p == pytest.approx([0.5, 0.5])
    assert z == 0.0


def test_multiplicative_matches_normalized_implied():
    p = devig.multiplicative([1.5, 3.0])
    imp = np.array([1 / 1.5, 1 / 3.0])
    assert p == pytest.approx(imp / imp.sum())


def test_shin_removes_more_at_odds_on():
    # Shin corrects favourite-longshot bias: longshots are over-bet, so the
    # favourite's FAIR prob is LIFTED above naive multiplicative normalization.
    p, _ = devig.shin([1.20, 4.50])
    raw_fav = (1 / 1.20) / (1 / 1.20 + 1 / 4.50)  # multiplicative fav
    assert p[0] > raw_fav


def test_bad_odds_raise():
    with pytest.raises(ValueError):
        devig.implied([1.0, 2.0])
