"""core-v1: the pace x efficiency Gaussian team model (bball-03 §2) — pure, no
ORM. Combines the opponent-adjusted efficiency ratings (features.ratings), the
pace channel, the margin-Elo ensemble member (features.elo) and the fully-known
schedule context (rest / B2B / travel) into a `MarginTotalDistribution`.

Points = Possessions x Points-Per-Possession (bball-03 §2a):
    poss      = game_pace(pace_home, pace_away, pace_league)
    pts_home  = poss/100 * expected_ppp100(home off vs away def, home)
    pts_away  = poss/100 * expected_ppp100(away off vs home def, away)
    mu_margin = pts_home - pts_away + rest/B2B/travel adjustments
    mu_total  = pts_home + pts_away

Context (bball-03 §3, FREE-DERIVABLE — included to MATCH the line, not beat it):
rest-day differential, back-to-back penalty, 3-in-4 fatigue, travel. All small
(1-3 pts) and mostly already in the closing line. The margin is then blended
with the Elo expectation (ensemble member + cold-start prior, §2c-ii), and
sigma_margin WIDENS under lineup uncertainty so "we don't know who's playing"
shows up as honest doubt (bball-03 §3 design consequence, §2d).
"""

from dataclasses import dataclass, field

from apps.features.ratings import game_pace
from apps.predictions.distribution import (
    FAMILY_NORMAL,
    MarginTotalDistribution,
)


@dataclass
class CoreConfig:
    """Per-league config (bball-03 §2d/§3). sigmas are EMPIRICAL, estimated from
    core-v1's own residuals per league; HCA/rest/travel are fit per season, not
    hardcoded — the defaults are sane NBA priors for cold start."""

    league: str = "NBA"
    sigma_margin: float = 12.0  # NBA practitioner consensus ~11-13
    sigma_total: float = 16.0
    elo_weight: float = 0.25  # ensemble share on the Elo margin
    b2b_margin_penalty: float = 1.8  # pts a back-to-back team loses on the spread
    rest_per_day: float = 0.4  # margin pts per day of rest differential (capped)
    rest_cap_days: float = 3.0
    three_in_four_penalty: float = 0.8  # additional fatigue on a 3-in-4 night
    travel_per_1000mi: float = 0.3  # small road-fatigue term
    b2b_total_penalty: float = 1.5  # tired legs slow pace -> totals dip
    lineup_widen: float = 0.6  # sigma_margin *= (1 + lineup_widen * uncertainty)
    margin_family: str = FAMILY_NORMAL
    total_family: str = FAMILY_NORMAL
    dof: float | None = None
    skew: float = 0.0


@dataclass
class GameContext:
    """Everything core-v1 needs to price one game. Ratings/pace come from the
    features layer as of a date STRICTLY before tipoff (leakage guard)."""

    home_team: object
    away_team: object
    ratings: object  # features.ratings.EfficiencyRatings
    pace: dict  # {team: pace tendency}
    pace_league: float
    elo_margin: float = 0.0  # features.elo.EloModel.predict(...)["exp_margin"]
    home_rest_days: float = 2.0
    away_rest_days: float = 2.0
    home_b2b: bool = False
    away_b2b: bool = False
    home_three_in_four: bool = False
    away_three_in_four: bool = False
    travel_miles_home: float = 0.0
    travel_miles_away: float = 0.0
    lineup_uncertainty: float = 0.0  # 0 = confirmed lineups, 1 = a star is GTD
    meta: dict = field(default_factory=dict)


def _pace_for(pace: dict, team, league: float) -> float:
    return float(pace.get(team, league))


class CoreTeamModel:
    """core-v1. `predict(ctx)` -> MarginTotalDistribution; `prob_vector(ctx)` ->
    the stored Prediction JSON (dist block + priced ladder at fair lines)."""

    def __init__(self, config: CoreConfig | None = None):
        self.config = config or CoreConfig()

    # ---- context adjustments ---------------------------------------------
    def _margin_context(self, ctx: GameContext) -> float:
        c = self.config
        adj = 0.0
        rest_diff = max(-c.rest_cap_days, min(c.rest_cap_days, ctx.home_rest_days - ctx.away_rest_days))
        adj += c.rest_per_day * rest_diff
        if ctx.home_b2b:
            adj -= c.b2b_margin_penalty
        if ctx.away_b2b:
            adj += c.b2b_margin_penalty
        if ctx.home_three_in_four:
            adj -= c.three_in_four_penalty
        if ctx.away_three_in_four:
            adj += c.three_in_four_penalty
        adj -= c.travel_per_1000mi * (ctx.travel_miles_home / 1000.0)
        adj += c.travel_per_1000mi * (ctx.travel_miles_away / 1000.0)
        return adj

    def _total_context(self, ctx: GameContext) -> float:
        c = self.config
        adj = 0.0
        if ctx.home_b2b:
            adj -= c.b2b_total_penalty
        if ctx.away_b2b:
            adj -= c.b2b_total_penalty
        return adj

    # ---- the model --------------------------------------------------------
    def predict(self, ctx: GameContext) -> MarginTotalDistribution:
        c = self.config
        r = ctx.ratings
        off_h = r.expected_ppp100(ctx.home_team, ctx.away_team, is_home=True)
        off_a = r.expected_ppp100(ctx.away_team, ctx.home_team, is_home=False)
        poss = game_pace(
            _pace_for(ctx.pace, ctx.home_team, ctx.pace_league),
            _pace_for(ctx.pace, ctx.away_team, ctx.pace_league),
            ctx.pace_league,
        )
        pts_h = poss / 100.0 * off_h
        pts_a = poss / 100.0 * off_a

        mu_margin_struct = (pts_h - pts_a) + self._margin_context(ctx)
        # ensemble with the Elo margin (cold-start prior + permanent member)
        mu_margin = (1.0 - c.elo_weight) * mu_margin_struct + c.elo_weight * ctx.elo_margin
        mu_total = (pts_h + pts_a) + self._total_context(ctx)

        sigma_margin = c.sigma_margin * (1.0 + c.lineup_widen * float(ctx.lineup_uncertainty))
        sigma_total = c.sigma_total

        return MarginTotalDistribution(
            mu_margin=mu_margin,
            sigma_margin=sigma_margin,
            mu_total=mu_total,
            sigma_total=sigma_total,
            margin_family=c.margin_family,
            total_family=c.total_family,
            dof=c.dof,
            skew=c.skew,
            meta={
                "model": "core-v1",
                "league": c.league,
                "poss": round(float(poss), 2),
                "pts_home": round(float(pts_h), 2),
                "pts_away": round(float(pts_a), 2),
                "mu_margin_struct": round(float(mu_margin_struct), 3),
                "elo_margin": round(float(ctx.elo_margin), 3),
                "elo_weight": c.elo_weight,
                "sigma_widened": bool(ctx.lineup_uncertainty > 0),
                "lineup_uncertainty": round(float(ctx.lineup_uncertainty), 3),
            },
        )

    def prob_vector(self, ctx: GameContext) -> dict:
        """The stored Prediction.prob_vector: distribution params (source of
        truth) + the ladder priced at the model's own fair lines. Downstream
        re-prices at the actual book line via MarginTotalDistribution."""
        dist = self.predict(ctx)
        fair_spread = round(-dist.mu_margin * 2) / 2.0  # nearest 0.5, home perspective
        fair_total = round(dist.mu_total * 2) / 2.0
        home_tt_line = round((dist.mu_total + dist.mu_margin) / 2.0 * 2) / 2.0
        away_tt_line = round((dist.mu_total - dist.mu_margin) / 2.0 * 2) / 2.0
        return {
            "dist": dist.dist_block(),
            "ML": dist.moneyline(),
            "SPREAD": dist.spread(fair_spread),
            "TOTAL": dist.total(fair_total),
            "TEAM_TOTAL": {
                "HOME": dist.team_total(home_tt_line, home=True),
                "AWAY": dist.team_total(away_tt_line, home=False),
            },
            "meta": dist.meta,
        }
