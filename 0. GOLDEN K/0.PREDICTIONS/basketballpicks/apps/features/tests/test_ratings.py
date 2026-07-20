"""Ridge opponent-adjusted efficiency + pace identities (bball-03 §2b/§2c).
Pure-math — no DB."""

import numpy as np
import pytest

from apps.features import ratings


def test_possessions_identity():
    # Poss = FGA - ORB + TOV + 0.44*FTA
    assert ratings.possessions(85, 10, 14, 25) == pytest.approx(85 - 10 + 14 + 0.44 * 25)


def test_game_pace_combines_tendencies():
    # a fast team (105) vs a slow team (95) against league 100 lands between
    p = ratings.game_pace(105, 95, 100)
    assert 95 < p < 105
    assert p == pytest.approx(105 * 95 / 100)


def test_decay_weights_monotone():
    w = ratings.decay_weights([0, 10, 30], xi=0.03)
    assert w[0] == pytest.approx(1.0)
    assert w[0] > w[1] > w[2] > 0


def test_ridge_recovers_known_ratings():
    rng = np.random.default_rng(0)
    n_teams = 8
    true_off = rng.normal(0, 5, n_teams)
    true_off -= true_off.mean()
    true_def = rng.normal(0, 4, n_teams)
    true_def -= true_def.mean()
    mu, hca = 112.0, 3.0

    off_team, def_team, is_home, y = [], [], [], []
    for _ in range(3):  # repeated double round-robin
        for h in range(n_teams):
            for a in range(n_teams):
                if h == a:
                    continue
                # home offense
                off_team.append(h); def_team.append(a); is_home.append(True)
                y.append(mu + true_off[h] + true_def[a] + hca)
                # away offense
                off_team.append(a); def_team.append(h); is_home.append(False)
                y.append(mu + true_off[a] + true_def[h])
    weights = np.ones(len(y))
    teams = list(range(n_teams))
    r = ratings.fit_efficiency(off_team, def_team, is_home, np.array(y), weights, teams, alpha=1.0)

    assert np.corrcoef(r.off, true_off)[0, 1] > 0.95
    assert np.corrcoef(r.deff, true_def)[0, 1] > 0.95
    assert r.hca == pytest.approx(hca, abs=1.0)
    # a clearly better offense scores more against the same defense
    best, worst = int(np.argmax(true_off)), int(np.argmin(true_off))
    assert r.expected_ppp100(best, 0, True) > r.expected_ppp100(worst, 0, True)


def test_fit_from_games_and_pace():
    games = [
        {"home_team": "A", "away_team": "B", "home_pts": 112, "away_pts": 104,
         "home_poss": 100, "away_poss": 100, "days_ago": 5},
        {"home_team": "B", "away_team": "A", "home_pts": 108, "away_pts": 110,
         "home_poss": 98, "away_poss": 98, "days_ago": 2},
    ]
    r = ratings.fit_from_games(games)
    assert r.has("A") and r.has("B")
    pace, league = ratings.team_pace_tendencies(games)
    assert 90 < league < 110
    assert set(pace) == {"A", "B"}
