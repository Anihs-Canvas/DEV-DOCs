"""Calibration metrics (bball-03 §6) — ported from safepicks, EXTENDED with the
distributional scores basketball's continuous outputs need.

Two families:

* PROBABILITY calibration (each binary market side): band-ECE / band-bias in the
  operating band [0.80, 0.98) — THE gate scalar. A model can look globally
  calibrated and still be 3 pts optimistic at 0.90, which at prop odds is the
  whole margin (safepicks ADR 004). Equal-mass ECE estimator (band samples are
  small; equal-width bins have a noise floor above the 0.02 gate).

* DISTRIBUTIONAL calibration (the Gaussian core + player distributions, NET-NEW
  for basketball, bball-03 §6b):
    - PIT (probability-integral-transform): F_pred(actual) is Uniform(0,1) iff
      the predictive distribution is honest. A U-shaped PIT = OVERCONFIDENT
      (sigma too small — the exact failure the feasibility memo warns about); a
      hump = underconfident. The continuous analog of a reliability curve.
    - CRPS (continuous ranked probability score): the proper-scoring
      generalization of Brier to a full predictive distribution; the primary
      score for comparing sigma models and the skew/t refinements, and for
      scoring us vs the market-implied distribution.

Pure numpy/scipy — no ORM.
"""

from dataclasses import dataclass

import numpy as np

BAND = (0.80, 0.98)
BIN_WIDTH = 0.02


@dataclass
class ReliabilityBin:
    lo: float
    hi: float
    n: int
    confidence: float  # mean predicted prob in bin
    accuracy: float  # observed hit rate in bin

    def as_dict(self) -> dict:
        return {
            "lo": round(self.lo, 4),
            "hi": round(self.hi, 4),
            "n": self.n,
            "confidence": round(self.confidence, 4),
            "accuracy": round(self.accuracy, 4),
        }


def reliability_curve(probs, outcomes, lo=0.0, hi=1.0, bin_width=BIN_WIDTH):
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    edges = np.arange(lo, hi + 1e-9, bin_width)
    bins: list[ReliabilityBin] = []
    for i in range(len(edges) - 1):
        mask = (probs >= edges[i]) & (probs < edges[i + 1])
        n = int(mask.sum())
        if n == 0:
            continue
        bins.append(
            ReliabilityBin(
                lo=float(edges[i]),
                hi=float(edges[i + 1]),
                n=n,
                confidence=float(probs[mask].mean()),
                accuracy=float(outcomes[mask].mean()),
            )
        )
    return bins


def ece(probs, outcomes, lo=0.0, hi=1.0) -> float:
    """Occupancy-weighted ECE over [lo, hi), equal-WIDTH bins."""
    bins = reliability_curve(probs, outcomes, lo, hi)
    total = sum(b.n for b in bins)
    if total == 0:
        return float("nan")
    return float(sum(b.n * abs(b.accuracy - b.confidence) for b in bins) / total)


def ece_equal_mass(probs, outcomes, k: int = 5) -> float:
    """Equal-mass (quantile-binned) ECE — the low-variance estimator (ADR 004)."""
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    n = len(probs)
    if n == 0:
        return float("nan")
    order = np.argsort(probs)
    p, y = probs[order], outcomes[order]
    edges = np.linspace(0, n, min(k, n) + 1).astype(int)
    total = 0.0
    for i in range(len(edges) - 1):
        seg_p = p[edges[i] : edges[i + 1]]
        seg_y = y[edges[i] : edges[i + 1]]
        if len(seg_p) == 0:
            continue
        total += len(seg_p) * abs(seg_y.mean() - seg_p.mean())
    return float(total / n)


def band_ece(probs, outcomes, k: int = 5) -> tuple[float, int]:
    """(equal-mass ECE inside [0.80, 0.98), n inside band)."""
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    mask = (probs >= BAND[0]) & (probs < BAND[1])
    n = int(mask.sum())
    if n == 0:
        return float("nan"), 0
    return ece_equal_mass(probs[mask], outcomes[mask], k=k), n


def band_bias(probs, outcomes) -> tuple[float, int]:
    """(mean claimed prob - mean outcome inside the band, n). THE gate scalar:
    signed bias directly corrupts EV. Positive = overconfident."""
    probs = np.asarray(probs, dtype=float)
    outcomes = np.asarray(outcomes, dtype=float)
    mask = (probs >= BAND[0]) & (probs < BAND[1])
    n = int(mask.sum())
    if n == 0:
        return float("nan"), 0
    return float(probs[mask].mean() - outcomes[mask].mean()), n


def brier(probs, outcomes) -> float:
    return float(np.mean((np.asarray(probs, float) - np.asarray(outcomes, float)) ** 2))


def logloss(probs, outcomes, eps: float = 1e-15) -> float:
    p = np.clip(np.asarray(probs, dtype=float), eps, 1 - eps)
    y = np.asarray(outcomes, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


# ---------------------------------------------------------------------------
# distributional calibration (bball-03 §6b) — NET-NEW vs safepicks
# ---------------------------------------------------------------------------


def crps_gaussian(mu, sigma, y) -> np.ndarray:
    """Closed-form CRPS of a Normal predictive distribution (Gneiting & Raftery
    2007):  CRPS = sigma*[ z*(2*Phi(z)-1) + 2*phi(z) - 1/sqrt(pi) ],
    z = (y - mu)/sigma. Lower is better. Vectorized."""
    from scipy.stats import norm

    mu = np.asarray(mu, dtype=float)
    sigma = np.clip(np.asarray(sigma, dtype=float), 1e-9, None)
    y = np.asarray(y, dtype=float)
    z = (y - mu) / sigma
    return sigma * (z * (2.0 * norm.cdf(z) - 1.0) + 2.0 * norm.pdf(z) - 1.0 / np.sqrt(np.pi))


def crps_ensemble(forecast_samples, y) -> float:
    """Sample-based CRPS (energy form) for a single observation against an
    ensemble of forecast draws — the fallback for non-Gaussian predictive
    distributions (skew-t, copula-summed props). O(n log n)."""
    x = np.sort(np.asarray(forecast_samples, dtype=float))
    n = len(x)
    if n == 0:
        return float("nan")
    y = float(y)
    term1 = float(np.mean(np.abs(x - y)))
    # E|X - X'| via the sorted-array identity sum_i (2i - n + 1) x_i * 2 / n^2
    i = np.arange(1, n + 1)
    term2 = float(np.sum((2 * i - n - 1) * x) * 2.0 / (n * n))
    return term1 - 0.5 * term2


def pit_values(cdf_at_actual) -> np.ndarray:
    """The PIT sample: F_pred(actual) for each realized outcome. Uniform(0,1)
    under an honest predictive distribution."""
    return np.clip(np.asarray(cdf_at_actual, dtype=float), 0.0, 1.0)


def pit_histogram(pits, bins: int = 10) -> list[dict]:
    pits = pit_values(pits)
    counts, edges = np.histogram(pits, bins=bins, range=(0.0, 1.0))
    exp = len(pits) / bins if len(pits) else 0.0
    return [
        {"lo": float(edges[i]), "hi": float(edges[i + 1]), "n": int(counts[i]), "expected": exp}
        for i in range(bins)
    ]


def pit_calibration_error(pits, bins: int = 10) -> float:
    """Mean absolute deviation of the PIT histogram from uniform, as a share of
    the sample — 0 for a perfectly calibrated distribution. A compact scalar to
    gate sigma choices (complements the visual PIT histogram)."""
    pits = pit_values(pits)
    n = len(pits)
    if n == 0:
        return float("nan")
    counts, _ = np.histogram(pits, bins=bins, range=(0.0, 1.0))
    exp = n / bins
    return float(np.sum(np.abs(counts - exp)) / n)


def pit_slope(pits) -> float:
    """Signed over/underconfidence summary: variance of the PIT minus the uniform
    variance (1/12). NEGATIVE => PIT concentrated in the middle (hump =
    UNDERconfident, sigma too wide); POSITIVE => U-shaped (OVERconfident, sigma
    too small — the dangerous direction, bball-03 §6b)."""
    pits = pit_values(pits)
    if len(pits) == 0:
        return float("nan")
    return float(np.var(pits) - 1.0 / 12.0)
