"""DFS pick'em EV, breakeven, correlation and staking (bball-04 §3). PURE module
(numpy/scipy only) — the whole parlay construct soccer's singles-only ledger never
had, unit-tested against the memo's worked numbers.

The BET is the ENTRY, not the leg. A pick'em is a fixed-multiplier parlay with an
enormous hold (25-61% vs a book's ~4.5-10%), so a leg is +EV ONLY when a stale DFS
line pushes p_true far past the per-leg breakeven b(N)=M^(-1/N). The single biggest
EV lever is CONSERVATIVE POSITIVE CORRELATION on same-game stacks — worth MORE than
the line edge itself (a +0.9% line-only 2-leg becomes +15.5% at rho=0.2) — and also
the noisiest, most self-deceiving input, so credited rho is HARD-CAPPED at 0.15
without a fitted joint model (bball-04 §3c).
"""

from __future__ import annotations

import numpy as np
from scipy import stats

# bball-04 §3c: never credit more than this correlation without a fitted game-level
# joint model — a wrong +0.2 assumption manufactures phantom EV.
RHO_CAP = 0.15
DEFAULT_MARGIN = 0.03  # per-leg edge required OVER breakeven (bball-04 §3b, §6b)


# ---------------------------------------------------------------------------
# breakeven + per-leg qualification
# ---------------------------------------------------------------------------


def breakeven_per_leg(mult: float, n: int) -> float:
    """b(N) = M^(-1/N): the per-leg win prob at which an all-must-hit entry breaks
    even (bball-04 §3a). Odd-leg power plays (3,5) have the LOWEST breakevens."""
    if n <= 0 or mult <= 0:
        raise ValueError("n and mult must be positive")
    return float(mult ** (-1.0 / n))


def leg_qualifies(p_true: float, mult: float, n: int, margin: float = DEFAULT_MARGIN) -> bool:
    return p_true >= breakeven_per_leg(mult, n) + margin


# ---------------------------------------------------------------------------
# joint hit probability (the correlation lever)
# ---------------------------------------------------------------------------


def joint_all_hit_bernoulli(p1: float, p2: float, rho: float) -> float:
    """Two-leg Bernoulli joint with linear correlation rho (bball-04 §3c exact
    form): P(both) = p1·p2 + rho·sqrt(p1(1-p1)·p2(1-p2)), clipped to Frechet
    bounds. Reproduces the memo's worked table exactly."""
    cov = rho * np.sqrt(p1 * (1 - p1) * p2 * (1 - p2))
    joint = p1 * p2 + cov
    lo, hi = max(0.0, p1 + p2 - 1.0), min(p1, p2)  # Frechet-Hoeffding
    return float(min(max(joint, lo), hi))


def _gaussian_thresholds(probs: np.ndarray) -> np.ndarray:
    """Latent-normal cut points c_i with P(X_i > c_i) = p_i."""
    return stats.norm.ppf(1.0 - np.clip(probs, 1e-9, 1 - 1e-9))


def joint_all_hit(probs, rho: float = 0.0) -> float:
    """P(all N legs hit) under equicorrelation rho. N=2 uses the exact Bernoulli
    form (memo parity); N>=3 uses a Gaussian-copula equicorrelation orthant
    probability — a principled joint the pick'em prices as if independent, so any
    positive rho is pure EV the venue did not charge for (bball-04 §3c)."""
    p = np.asarray(list(probs), dtype=float)
    n = len(p)
    if n == 0:
        return 1.0
    if n == 1:
        return float(p[0])
    rho = float(np.clip(rho, -0.999, RHO_CAP))  # never credit above the cap
    if n == 2:
        return joint_all_hit_bernoulli(p[0], p[1], rho)
    c = _gaussian_thresholds(p)
    cov = np.full((n, n), rho, dtype=float)
    np.fill_diagonal(cov, 1.0)
    # P(all X_i > c_i) = P(all -X_i < -c_i); -X ~ N(0, cov) by symmetry.
    mvn = stats.multivariate_normal(mean=np.zeros(n), cov=cov, allow_singular=True)
    return float(mvn.cdf(-c))


def poisson_binomial_pmf(probs) -> np.ndarray:
    """Exact P(exactly k of N legs hit) for INDEPENDENT legs (DP). Length N+1."""
    dist = np.array([1.0])
    for p in probs:
        dist = np.convolve(dist, [1.0 - p, p])
    return dist


def count_dist(probs, rho: float = 0.0, seed: int = 20260719, draws: int = 40000) -> np.ndarray:
    """P(exactly k of N hit). Independent (rho≈0) is exact via poisson_binomial;
    correlated uses a SEEDED Gaussian-copula Monte-Carlo (reproducible — flex EV
    must not be eyeballed, bball-04 §3b)."""
    p = np.asarray(list(probs), dtype=float)
    n = len(p)
    if n == 0:
        return np.array([1.0])
    if abs(rho) < 1e-9:
        return poisson_binomial_pmf(p)
    rho = float(np.clip(rho, -0.999, RHO_CAP))
    c = _gaussian_thresholds(p)
    cov = np.full((n, n), rho)
    np.fill_diagonal(cov, 1.0)
    rng = np.random.default_rng(seed)
    z = rng.multivariate_normal(np.zeros(n), cov, size=draws)
    hits = (z > c).sum(axis=1)
    pmf = np.bincount(hits, minlength=n + 1)[: n + 1]
    return pmf / pmf.sum()


# ---------------------------------------------------------------------------
# entry EV (power all-must-hit, and flex/insured)
# ---------------------------------------------------------------------------


def entry_ev_power(probs, mult: float, rho: float = 0.0) -> dict:
    """All-must-hit entry: EV = P_joint · M − 1 (bball-04 §3b)."""
    p_joint = joint_all_hit(probs, rho)
    ev = p_joint * mult - 1.0
    return {"p_joint": p_joint, "mult": mult, "rho_credited": float(np.clip(rho, -0.999, RHO_CAP)),
            "ev": ev, "n_legs": len(list(probs))}


def entry_ev_flex(probs, payout_by_hits: dict[int, float], rho: float = 0.0,
                  seed: int = 20260719) -> dict:
    """Flex/insured entry that pays on 1-2 misses: its payout is a RANDOM VARIABLE,
    so EV = Σ_k P(k of N hit)·pay(k) − 1 over the FULL distribution (bball-04 §3b —
    never eyeball flex EV). `payout_by_hits` maps hit-count → payout multiplier."""
    p = list(probs)
    n = len(p)
    pmf = count_dist(p, rho, seed=seed)
    ev = float(sum(pmf[k] * payout_by_hits.get(k, 0.0) for k in range(n + 1)) - 1.0)
    return {"pmf": pmf.tolist(), "ev": ev, "n_legs": n,
            "rho_credited": float(np.clip(rho, -0.999, RHO_CAP))}


# ---------------------------------------------------------------------------
# stake sizing — quarter-Kelly ON THE ENTRY (mirror valuebets.quarter_kelly_fraction)
# ---------------------------------------------------------------------------


def kelly_fraction_multiplier(p_joint: float, mult: float) -> float:
    """Full-Kelly fraction for a multiplier bet paying (M-1)-to-1 at win prob
    p_joint: f* = (p·M − 1)/(M − 1), floored at 0 (bball-04 §3e)."""
    if mult <= 1.0:
        return 0.0
    f = (p_joint * mult - 1.0) / (mult - 1.0)
    return max(f, 0.0)


def quarter_kelly_entry(p_joint: float, mult: float, kelly_multiplier: float,
                        stake_cap_pct: float) -> dict:
    """The entry stake as one auditable step — full Kelly × the profile's fraction
    (quarter), capped at max_stake_pct_bankroll. Returns every intermediate so the
    audit dict shows the whole derivation (identical shape to safepicks
    valuebets.quarter_kelly_fraction)."""
    full = kelly_fraction_multiplier(p_joint, mult)
    scaled = full * kelly_multiplier
    return {
        "kelly_full": full,
        "kelly_multiplier": kelly_multiplier,
        "kelly_scaled": scaled,
        "stake_cap_pct": stake_cap_pct,
        "cap_bound": scaled > stake_cap_pct,
        "stake_fraction": min(scaled, stake_cap_pct),
    }


def slate_exposure_cap(entries: list[dict], max_aggregate_pct: float) -> dict:
    """Cap AGGREGATE nightly exposure across entries that SHARE LEGS (bball-04 §3e:
    a naive per-entry Kelly over-bets the slate because leg outcomes are
    correlated). `entries` = [{"stake_fraction":.., "legs": {leg_id,...}}]. Scales
    all stakes down proportionally if the total exceeds the cap, and reports each
    leg's accumulated exposure so an over-concentrated leg is visible."""
    total = sum(e["stake_fraction"] for e in entries)
    scale = 1.0 if total <= max_aggregate_pct or total == 0 else max_aggregate_pct / total
    leg_exposure: dict = {}
    adjusted = []
    for e in entries:
        stake = e["stake_fraction"] * scale
        adjusted.append({**e, "stake_fraction_capped": stake})
        for leg in e["legs"]:
            leg_exposure[leg] = leg_exposure.get(leg, 0.0) + stake
    return {
        "requested_total": total,
        "scale_applied": scale,
        "capped_total": total * scale,
        "entries": adjusted,
        "leg_exposure": leg_exposure,
    }
