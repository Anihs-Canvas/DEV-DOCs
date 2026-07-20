"""De-vig: recover true implied probabilities from bookmaker odds.

*** COPIED VERBATIM from safepicks apps/odds/devig.py (bball-01 §5 COPY-VERBATIM
list) — the Shin method is pure, portable, zero soccer coupling. Do not fork it;
props devigging (apps/props/devig_engine.py) imports shin() from here so the two
sports share one audited de-vig implementation. ***

Shin's method [PLAN 5 de-vig note / ODDS 1.4] models an insider fraction
z and corrects the favourite-longshot bias that plain multiplicative
normalization leaves in. It matters MOST at odds-on prices — and on props,
where two-way holds run 6-10%+, method choice matters even more than on 1X2
(bball-04 §2a: an edge that survives only ONE de-vig method is not real).
Multiplicative kept as the MVP fallback.

Inverse recovery, given implied probs pi_i (sum = booksum B > 1):
    p_i(z) = (sqrt(z^2 + 4(1-z) * pi_i^2 / B) - z) / (2(1-z))
with z in [0, 0.5) solved by bisection so that sum(p_i) = 1.
z = 0 collapses to multiplicative. Pure module, no ORM.
"""

import numpy as np

MAX_Z = 0.5
TOL = 1e-12


def implied(odds: list[float] | np.ndarray) -> np.ndarray:
    o = np.asarray(odds, dtype=float)
    if (o <= 1.0).any():
        raise ValueError("decimal odds must be > 1.0")
    return 1.0 / o


def multiplicative(odds: list[float] | np.ndarray) -> np.ndarray:
    pi = implied(odds)
    return pi / pi.sum()


def _shin_probs(pi: np.ndarray, booksum: float, z: float) -> np.ndarray:
    return (np.sqrt(z * z + 4.0 * (1.0 - z) * pi * pi / booksum) - z) / (2.0 * (1.0 - z))


def shin(odds: list[float] | np.ndarray) -> tuple[np.ndarray, float]:
    """Returns (probabilities summing to 1, fitted z)."""
    pi = implied(odds)
    booksum = float(pi.sum())
    if booksum <= 1.0 + 1e-9:  # fair or arb book: nothing to remove
        return pi / booksum, 0.0

    lo, hi = 0.0, MAX_Z
    # sum(p) decreases monotonically in z; find z where it hits 1
    for _ in range(200):
        mid = (lo + hi) / 2.0
        s = _shin_probs(pi, booksum, mid).sum()
        if s > 1.0:
            lo = mid
        else:
            hi = mid
        if hi - lo < TOL:
            break
    z = (lo + hi) / 2.0
    p = _shin_probs(pi, booksum, z)
    return p / p.sum(), z


def devig(odds: list[float] | np.ndarray, method: str = "shin") -> np.ndarray:
    if method == "shin":
        return shin(odds)[0]
    if method == "multiplicative":
        return multiplicative(odds)
    raise ValueError(f"unknown de-vig method: {method}")
