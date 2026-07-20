"""Pace + opponent-adjusted efficiency ratings (bball-03 §2b/§2c-i) — pure
numpy/sklearn, NO ORM (services own persistence, mirroring safepicks ADR 003).

The identity (bball-03 §2a):  Points = Possessions x Points-Per-Possession.
We estimate the two factors SEPARATELY so pace and efficiency stay cleanly
separable (the KenPom/Oliver decomposition):

  * POSSESSIONS from the box-score identity  Poss = FGA - ORB + TOV + 0.44*FTA
    (bball-03 §2b); a game's pace combines the two teams' tendencies against
    league average — a fast team drags a slow team up.
  * ADJUSTED EFFICIENCY by RIDGE regression (bball-03 §2c-i): each team's
    per-100 offensive output is  y = mu + off[O] + def[D] + hca*is_home + eps,
    solved for every team's off/def simultaneously. The L2 penalty shrinks
    toward the league mean — the prior that keeps early-season and thin-sample
    (WNBA, small-conference) ratings stable instead of wild. Games are
    exponentially time-decay weighted (exp(-xi*days_ago)), safepicks' xi lever.

`off` is offensive quality (higher scores more); `def` is defensive LEAKINESS
(higher allows more — a good defense is negative). Both are re-centered mean-zero
and the means folded into `mu` for interpretability, so an average team is
(off=0, def=0) and `mu` is the league per-100 baseline.
"""

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import Ridge

DEFAULT_XI = 0.03  # per-day decay; roster-churn sport => faster than soccer's .0065
DEFAULT_WINDOW_DAYS = 400
DEFAULT_ALPHA = 50.0  # ridge L2 strength (shrink-to-mean prior); tuned per league
MIN_GAMES = 40  # burn-in before a ridge fit is trusted (lean on Elo prior below this)


def possessions(fga, orb, tov, fta):
    """Box-score possession estimate (basketball-reference identity)."""
    return np.asarray(fga, float) - np.asarray(orb, float) + np.asarray(tov, float) + 0.44 * np.asarray(fta, float)


def game_pace(pace_home: float, pace_away: float, pace_league: float) -> float:
    """Opponent-adjusted game pace (bball-03 §2b): both teams play ~the same
    number of possessions, so the game rate combines the two tendencies against
    league average."""
    if pace_league <= 0:
        return float((pace_home + pace_away) / 2.0)
    return float(pace_home * pace_away / pace_league)


def decay_weights(days_ago, xi: float = DEFAULT_XI) -> np.ndarray:
    return np.exp(-xi * np.asarray(days_ago, dtype=float))


@dataclass
class EfficiencyRatings:
    teams: list  # team ids, fixed order
    off: np.ndarray  # opponent-adjusted offense, pts/100 above league mean
    deff: np.ndarray  # opponent-adjusted defensive leakiness, pts/100 above mean
    mu: float  # league-average points per 100 possessions
    hca: float  # home-court advantage, pts/100

    def index(self) -> dict:
        return {t: i for i, t in enumerate(self.teams)}

    def has(self, team) -> bool:
        return team in self.index()

    def off_rating(self, team) -> float:
        """Absolute adjusted offensive rating (pts scored / 100 vs league-avg D)."""
        return float(self.mu + self.off[self.index()[team]])

    def def_rating(self, team) -> float:
        """Absolute adjusted defensive rating (pts allowed / 100 vs league-avg O)."""
        return float(self.mu + self.deff[self.index()[team]])

    def expected_ppp100(self, off_team, def_team, is_home: bool) -> float:
        """Points per 100 possessions `off_team` scores on `def_team`."""
        idx = self.index()
        return float(
            self.mu
            + self.off[idx[off_team]]
            + self.deff[idx[def_team]]
            + (self.hca if is_home else 0.0)
        )


def fit_efficiency(
    off_team,
    def_team,
    is_home,
    pts_per100,
    weights,
    teams: list,
    alpha: float = DEFAULT_ALPHA,
) -> EfficiencyRatings:
    """Weighted ridge over 2 rows per game (each team's offensive possession
    output vs the opponent's defense).

    Parameters are parallel arrays of length = 2 * n_games:
      off_team[k]  team whose offense produced pts_per100[k]
      def_team[k]  the opponent's defense
      is_home[k]   True if off_team was home for that half of the observation
      pts_per100[k] points per 100 possessions scored
      weights[k]   recency weight (decay_weights)
    """
    n = len(teams)
    idx = {t: i for i, t in enumerate(teams)}
    m = len(pts_per100)
    X = np.zeros((m, 2 * n + 1))
    rows = np.arange(m)
    X[rows, [idx[t] for t in off_team]] = 1.0
    X[rows, [n + idx[t] for t in def_team]] = 1.0
    X[:, 2 * n] = np.asarray(is_home, dtype=float)

    ridge = Ridge(alpha=alpha, fit_intercept=True)
    ridge.fit(X, np.asarray(pts_per100, dtype=float), sample_weight=np.asarray(weights, dtype=float))
    coef = ridge.coef_
    off = coef[:n]
    deff = coef[n : 2 * n]
    hca = float(coef[2 * n])
    # re-center mean-zero, fold the means into mu (identifiability + readability)
    off_mean, def_mean = float(off.mean()), float(deff.mean())
    return EfficiencyRatings(
        teams=list(teams),
        off=off - off_mean,
        deff=deff - def_mean,
        mu=float(ridge.intercept_) + off_mean + def_mean,
        hca=hca,
    )


def build_observations(games: list[dict]) -> dict:
    """Expand game dicts into the parallel offense-observation arrays
    `fit_efficiency` wants. Each game dict needs:
      home_team, away_team, home_pts, away_pts, home_poss, away_poss, days_ago.
    Two observations per game (home offense, away offense). Possessions are
    per-side but nearly equal; per-100 normalizes either way.
    """
    off_team, def_team, is_home, y, days = [], [], [], [], []
    for g in games:
        hp = g["home_poss"] or ((g.get("away_poss") or 0) or 1)
        ap = g["away_poss"] or hp
        # home offense
        off_team.append(g["home_team"]); def_team.append(g["away_team"])
        is_home.append(True); y.append(100.0 * g["home_pts"] / max(hp, 1e-9)); days.append(g["days_ago"])
        # away offense
        off_team.append(g["away_team"]); def_team.append(g["home_team"])
        is_home.append(False); y.append(100.0 * g["away_pts"] / max(ap, 1e-9)); days.append(g["days_ago"])
    return {
        "off_team": off_team,
        "def_team": def_team,
        "is_home": is_home,
        "pts_per100": np.asarray(y, dtype=float),
        "days_ago": np.asarray(days, dtype=float),
    }


def fit_from_games(games: list[dict], xi: float = DEFAULT_XI, alpha: float = DEFAULT_ALPHA) -> EfficiencyRatings:
    """Convenience: observations -> decay weights -> ridge fit."""
    obs = build_observations(games)
    teams = sorted(set(obs["off_team"]) | set(obs["def_team"]))
    weights = decay_weights(obs["days_ago"], xi)
    return fit_efficiency(
        obs["off_team"], obs["def_team"], obs["is_home"], obs["pts_per100"], weights, teams, alpha
    )


def team_pace_tendencies(games: list[dict], xi: float = DEFAULT_XI) -> tuple[dict, float]:
    """Decayed average possessions/game each team imposes, and the league mean —
    the pace channel (bball-03 §2b). Returns ({team: pace}, league_pace)."""
    num: dict = {}
    den: dict = {}
    tot_num = 0.0
    tot_den = 0.0
    for g in games:
        w = float(np.exp(-xi * g["days_ago"]))
        for t, poss in ((g["home_team"], g["home_poss"]), (g["away_team"], g["away_poss"])):
            if poss is None:
                continue
            num[t] = num.get(t, 0.0) + w * poss
            den[t] = den.get(t, 0.0) + w
            tot_num += w * poss
            tot_den += w
    league = tot_num / tot_den if tot_den else 100.0
    pace = {t: (num[t] / den[t] if den.get(t) else league) for t in num}
    return pace, float(league)
