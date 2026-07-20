"""Margin-aware Elo (bball-03 §2c-ii) — the robust cross-check + cold-start prior.

A FiveThirtyEight-style Elo that updates on MARGIN OF VICTORY (not just W/L),
with diminishing returns on blowouts and a preseason regression toward the mean.
Its jobs (bball-03 §2c-ii): (a) carry team strength ACROSS seasons through the
info-poor early weeks better than a within-season ridge, so it SEEDS the ridge
prior during burn-in; and (b) stay a permanent ensemble member the core mean
blends with. Pure numpy — streaming, no ORM.

Scale: Elo points convert to an expected point margin via `ELO_PER_POINT`
(~28 Elo == 1 pt, the practitioner NBA figure). Home advantage enters as a fixed
Elo bump so it participates in both the win prob and the expected margin.
"""

import numpy as np

MEAN_ELO = 1500.0
K = 20.0  # update speed
HOME_ADV_ELO = 70.0  # ~2.5 pt home edge at the NBA ELO_PER_POINT
ELO_PER_POINT = 28.0  # Elo points per expected point of margin
PRESEASON_REGRESS = 0.25  # fraction pulled back to the mean between seasons


def expected_win_prob(elo_home: float, elo_away: float, home_adv: float = HOME_ADV_ELO) -> float:
    """Logistic expected home win probability from the Elo gap (+ home bump)."""
    diff = (elo_home + home_adv) - elo_away
    return float(1.0 / (1.0 + 10.0 ** (-diff / 400.0)))


def expected_margin(elo_home: float, elo_away: float, home_adv: float = HOME_ADV_ELO) -> float:
    """Expected home point margin implied by the Elo gap — the core-model
    ensemble input (bball-03 §2c-ii)."""
    return float(((elo_home + home_adv) - elo_away) / ELO_PER_POINT)


def mov_multiplier(margin: float, elo_diff_winner: float) -> float:
    """FiveThirtyEight margin-of-victory multiplier: rewards bigger wins with
    diminishing returns, and autocorrelation-corrects for the favorite (a strong
    favorite winning big should move less)."""
    return float(((abs(margin) + 3.0) ** 0.8) / (7.5 + 0.006 * elo_diff_winner))


def update(
    elo_home: float,
    elo_away: float,
    home_margin: float,
    k: float = K,
    home_adv: float = HOME_ADV_ELO,
) -> tuple[float, float]:
    """Post-game (elo_home, elo_away). `home_margin` = home_score - away_score."""
    exp_home = expected_win_prob(elo_home, elo_away, home_adv)
    home_won = 1.0 if home_margin > 0 else (0.5 if home_margin == 0 else 0.0)
    # elo gap from the WINNER's perspective, home-adv included (538 convention)
    diff = (elo_home + home_adv) - elo_away
    elo_diff_winner = diff if home_margin > 0 else -diff
    mult = mov_multiplier(home_margin, elo_diff_winner)
    shift = k * mult * (home_won - exp_home)
    return float(elo_home + shift), float(elo_away - shift)


def regress_to_mean(elo: float, frac: float = PRESEASON_REGRESS, mean: float = MEAN_ELO) -> float:
    """Between-season carry-over: pull `frac` of the way back to the mean."""
    return float(elo + frac * (mean - elo))


class EloModel:
    """Streaming margin-Elo over a chronological game sequence. `ratings` holds
    the current Elo per team; `predict` prices the NEXT game before `observe`
    updates it (so a walk-forward loop is leakage-free by construction)."""

    def __init__(self, k: float = K, home_adv: float = HOME_ADV_ELO, mean: float = MEAN_ELO):
        self.k = k
        self.home_adv = home_adv
        self.mean = mean
        self.ratings: dict = {}

    def get(self, team) -> float:
        return self.ratings.get(team, self.mean)

    def predict(self, home_team, away_team) -> dict:
        eh, ea = self.get(home_team), self.get(away_team)
        return {
            "p_home": expected_win_prob(eh, ea, self.home_adv),
            "exp_margin": expected_margin(eh, ea, self.home_adv),
            "elo_home": eh,
            "elo_away": ea,
        }

    def observe(self, home_team, away_team, home_margin: float) -> None:
        eh, ea = self.get(home_team), self.get(away_team)
        self.ratings[home_team], self.ratings[away_team] = update(
            eh, ea, home_margin, self.k, self.home_adv
        )

    def new_season(self, frac: float = PRESEASON_REGRESS) -> None:
        for t in list(self.ratings):
            self.ratings[t] = regress_to_mean(self.ratings[t], frac, self.mean)
