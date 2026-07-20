"""The props signal engine: de-vig WITH a line shift (bball-04 §2 — the props-only
wrinkle 1X2 never had). PURE module (numpy/scipy only, no ORM, no network) so the
whole edge math is unit-tested without a database.

Two jobs:
  (2a) fair_two_way(): Shin-de-vig a native two-way over/under prop into a fair
       {p_over, p_under} at the SHARP/consensus line — reuses odds.devig.shin so
       props and 1X2 share one audited de-vig. Also reports the multiplicative
       result so the caller can screen method-sensitivity (an edge that survives
       only ONE method is not real — bball-04 §2a).
  (2b) reprice(): the NEW part with no 1X2 analog. DFS says 18.5, the sharp market
       says 21.5 — you cannot compare 18.5-over to 21.5-over. Reconstruct the
       player's stat distribution implied by the sharp market (fit a parametric
       CDF to its de-vigged line ladder incl. alternates) and evaluate it at the
       target line. This means EVEN the "pure arbitrage" path carries a light
       distributional MODEL — the edge is only as clean as that CDF assumption, so
       we HARD-CAP repricing to <= MAX_REPRICE_UNITS from the nearest anchor
       (extrapolation risk explodes past that).

Also prob_over_from_dist(): the MODEL path — evaluate a fitted PropPrediction
distribution (dist + dist_params from apps.predictions, bball-03) at any line,
for the thin/neglected cohort where the sharp market prices nothing to de-vig.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats

from apps.odds import devig

EPS = 1e-9
# bball-04 §2b: sanity-cap repricing to ~2 units from the nearest sharp anchor.
MAX_REPRICE_UNITS = 2.0
_PCLIP = 1e-4  # clip fair probs off {0,1} before inverse-Normal

# Default dispersion per market family, used ONLY when a single anchor point pins
# the mean but not the spread (bball-04 §2b: "one or two anchor points pin
# mean+dispersion; alts refine"). Rough NBA per-game SDs; refined by alts when >1
# point exists. Half-point buffers matter far MORE on low-count stats, so their
# defaults are small and the caller should prefer >=2 points for them.
DEFAULT_SIGMA = {  # keys = props.PropMarket.key (lowercase words)
    "points": 8.5, "pra": 11.0, "pr": 9.0, "pa": 9.5, "ra": 5.0,
    "rebounds": 3.4, "assists": 2.8, "threes": 1.6, "blocks": 1.0, "steals": 1.0,
    "turnovers": 1.5, "fgm": 3.2, "ftm": 2.4, "blocks_steals": 1.5,
}
_FALLBACK_SIGMA = 6.0


# ---------------------------------------------------------------------------
# (2a) native two-way de-vig
# ---------------------------------------------------------------------------


def fair_two_way(over_price: float, under_price: float, method: str = "shin") -> dict:
    """De-vig one book's two-way prop → fair {p_over, p_under}. Returns the Shin
    AND multiplicative results plus their spread for the method-sensitivity gate."""
    if over_price is None or under_price is None:
        return {}
    if over_price <= 1.0 or under_price <= 1.0:
        return {}
    shin_p, z = devig.shin([over_price, under_price])
    mult_p = devig.multiplicative([over_price, under_price])
    p_over = float(shin_p[0] if method == "shin" else mult_p[0])
    return {
        "p_over": p_over,
        "p_under": 1.0 - p_over,
        "p_over_shin": float(shin_p[0]),
        "p_over_mult": float(mult_p[0]),
        "method_spread": abs(float(shin_p[0]) - float(mult_p[0])),
        "z": float(z),
        "booksum": 1.0 / over_price + 1.0 / under_price,
        "method": method,
    }


# ---------------------------------------------------------------------------
# (2b) line-shift repricing — fit a CDF to the anchor ladder, evaluate anywhere
# ---------------------------------------------------------------------------


def continuity_threshold(line: float) -> float:
    """The half-point just above the largest integer that LOSES an over. For a
    .5 line (24.5) this is the line itself; for an integer line (24) it is 24.5.
    Over wins iff stat >= floor(line)+1, so P(over) = P(X > floor(line)+0.5)."""
    return math.floor(line + EPS) + 0.5


@dataclass(frozen=True, slots=True)
class AnchorPoint:
    line: float
    p_over: float  # de-vigged sharp/consensus P(over) at this line


@dataclass(frozen=True, slots=True)
class StatCDF:
    """A fitted implied stat distribution (Normal approximation). `sigma` from the
    anchor ladder when >=2 points exist, else a market default. `anchor_lines` is
    the set the fit was pinned on — repricing distance is measured to the nearest
    of these and CAPPED at MAX_REPRICE_UNITS."""

    mu: float
    sigma: float
    anchor_lines: tuple[float, ...]
    n_points: int
    from_default_sigma: bool

    def p_over(self, line: float) -> float:
        t = continuity_threshold(line)
        return float(1.0 - stats.norm.cdf((t - self.mu) / self.sigma))

    def nearest_anchor_distance(self, line: float) -> float:
        return min(abs(line - a) for a in self.anchor_lines)


def fit_cdf(points: list[AnchorPoint], market: str) -> StatCDF | None:
    """Fit a Normal implied-distribution to the anchor's de-vigged line ladder.

    Each point gives threshold_k = mu + sigma * z_k with z_k = Φ⁻¹(1 − p_over_k).
    With >=2 points we least-squares-solve mu (intercept) and sigma (slope>0);
    with 1 point we pin mu from a market-default sigma. Count stats reuse this
    Normal-in-z approximation for repricing — honest and CLT-reasonable across the
    small half-point shifts we allow, and explicitly bounded by MAX_REPRICE_UNITS.
    """
    pts = [p for p in points if 0.0 < p.p_over < 1.0]
    if not pts:
        return None
    thresholds = np.array([continuity_threshold(p.line) for p in pts], dtype=float)
    z = stats.norm.ppf(np.clip([p.p_over for p in pts], _PCLIP, 1 - _PCLIP))
    z = -z  # z_k = Φ⁻¹(1 − p_over) = −Φ⁻¹(p_over)
    lines = tuple(sorted({p.line for p in pts}))

    if len(pts) >= 2 and np.ptp(z) > EPS:
        # slope = sigma, intercept = mu via ordinary least squares
        A = np.vstack([np.ones_like(z), z]).T
        mu, sigma = np.linalg.lstsq(A, thresholds, rcond=None)[0]
        if sigma > EPS:
            return StatCDF(float(mu), float(sigma), lines, len(pts), from_default_sigma=False)

    # single point (or degenerate z): pin mu from a default sigma
    sigma = DEFAULT_SIGMA.get(market, _FALLBACK_SIGMA)
    mu = float(thresholds[0] - sigma * z[0])
    return StatCDF(mu, float(sigma), lines, len(pts), from_default_sigma=True)


@dataclass(frozen=True, slots=True)
class Repriced:
    p_over: float
    p_under: float
    reprice_units: float  # distance from the nearest anchor line
    within_cap: bool  # False => extrapolation past MAX_REPRICE_UNITS, unreliable
    from_default_sigma: bool


def reprice(cdf: StatCDF, target_line: float) -> Repriced:
    """Evaluate the fitted CDF at a venue's line. `within_cap=False` flags an
    extrapolation the edge engine must route to the model or drop (bball-04 §2b)."""
    p_over = cdf.p_over(target_line)
    dist = cdf.nearest_anchor_distance(target_line)
    return Repriced(
        p_over=p_over,
        p_under=1.0 - p_over,
        reprice_units=dist,
        within_cap=dist <= MAX_REPRICE_UNITS + EPS,
        from_default_sigma=cdf.from_default_sigma,
    )


def anchor_points_from_quotes(quotes, method: str = "shin") -> list[AnchorPoint]:
    """De-vig a set of two-sided anchor quotes (main line + alternates for ONE
    player+market) into AnchorPoints for fit_cdf. `quotes` = iterable of objects
    with .line, .over_price, .under_price (e.g. ParsedPropQuote)."""
    pts: list[AnchorPoint] = []
    for q in quotes:
        fair = fair_two_way(q.over_price, q.under_price, method=method)
        if fair:
            pts.append(AnchorPoint(line=float(q.line), p_over=fair["p_over"]))
    return pts


# ---------------------------------------------------------------------------
# the MODEL path — evaluate a PropPrediction distribution at any line
# ---------------------------------------------------------------------------


def prob_over_from_pmf(pmf, support_start: int, line: float) -> float:
    """P(stat > line) from a PropPrediction's MATERIALIZED ladder (bball-03: the
    predictions app pre-computes pmf + support_start precisely so consumers price
    any line WITHOUT re-instantiating the model). P(X = support_start+i) = pmf[i];
    over wins iff X > line. This is the PREFERRED consumer — it works for every
    family including compound (points) and copula (PRA) that have no closed form."""
    arr = np.asarray(pmf, dtype=float)
    if arr.size == 0:
        raise ValueError("empty pmf")
    total = arr.sum()
    if total <= 0:
        raise ValueError("degenerate pmf")
    idx = np.arange(arr.size) + int(support_start)
    return float(arr[idx > line].sum() / total)


def prob_over_from_dist(dist: str, params: dict, line: float) -> float:
    """P(stat > line) from a fitted PropPrediction distribution when no pmf is
    materialized (bball-03 schema: dist ∈ {poisson, neg_binom, normal}; compound/
    copula MUST use prob_over_from_pmf). Discrete families: over wins iff
    X >= floor(line)+1, so P = 1 − cdf(floor). Normal: continuity-corrected.

    Used ONLY on thin/neglected lines the sharp market does not price (bball-04
    §4) — held to a higher edge threshold + half stake, NEVER trusted vs a well-
    quoted sharp line (the soccer information ceiling holds)."""
    if dist == "poisson":
        lam = params.get("lam", params.get("mu", params.get("lambda")))
        return float(1.0 - stats.poisson.cdf(math.floor(line + EPS), lam))
    if dist == "neg_binom":
        r = params.get("r", params.get("n"))
        p = params.get("p")
        return float(1.0 - stats.nbinom.cdf(math.floor(line + EPS), r, p))
    if dist == "normal":
        mu, sigma = params["mu"], params["sigma"]
        t = continuity_threshold(line)
        return float(1.0 - stats.norm.cdf((t - mu) / sigma))
    raise ValueError(f"unknown/closed-form-less dist {dist!r} — use prob_over_from_pmf")
