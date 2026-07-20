"""Per-stat prop DISTRIBUTIONS (bball-03 §4c) — the differentiator, pure
numpy/scipy (no ORM). We output a full distribution per stat, never a point, so
ANY line and alt-line is priceable and devig-able (bball-03 §4).

The right distribution per stat (bball-03 §4c):
  * POINTS  -> a COMPOUND distribution: points = 2*(2P made) + 3*(3P made) + FT.
    Makes are modeled as (thinned) Poisson arrivals and the three components are
    CONVOLVED, giving the approximately-normal-but-lumpy shape with the discrete
    3-point jumps and fat right tail. Points variance is shooting-luck dominated
    — the least modelable of the big three (books price it most carefully).
  * REBOUNDS -> NEGATIVE BINOMIAL: counts are overdispersed vs Poisson (VMR>1)
    from role volatility; rebounds are the single best-calibrating prop (minutes+
    position+opponent-rate driven). The prime target.
  * ASSISTS  -> NEGATIVE BINOMIAL, mean = f(minutes, usage, teammate FG%);
    honest-wide intervals (teammate shooting luck is irreducible).
  * THREES MADE -> Binomial(3PA, 3P%): modelable mean, make/miss luck dominates
    the OUTCOME (§5 noise — devig only).
  * BLOCKS/STEALS -> low-rate Poisson: nearly all mass is noise (§5 devig only).
  * PRA / P+R / P+A / R+A -> SUM of CORRELATED marginals via a Gaussian COPULA
    (minutes is the shared driver -> positive correlation; a big-minutes night
    lifts all three). Combos have LOWER relative variance than components — a
    favored, more-calibratable target.

Every distribution exposes a materialized pmf + `support_start` so the stored
PropPrediction prices the whole ladder downstream WITHOUT this module.
"""

import numpy as np
from scipy.stats import binom, nbinom, norm, poisson

MAX_SUPPORT = 120  # ceiling on any counting-stat pmf length


def _is_integer_line(line: float) -> bool:
    return abs(line - round(line)) < 1e-9


class StatDistribution:
    """A discrete distribution over non-negative integer stat values.
    `pmf[i] = P(X == support_start + i)`. All prop pricing flows through here."""

    def __init__(self, pmf, support_start: int = 0, family: str = "empirical", params: dict | None = None):
        pmf = np.asarray(pmf, dtype=float)
        s = pmf.sum()
        self.pmf = pmf / s if s > 0 else pmf
        self.support_start = int(support_start)
        self.family = family
        self.params = params or {}

    # ---- support helpers --------------------------------------------------
    def values(self) -> np.ndarray:
        return self.support_start + np.arange(len(self.pmf))

    def mean(self) -> float:
        return float(np.sum(self.values() * self.pmf))

    def var(self) -> float:
        v = self.values()
        m = self.mean()
        return float(np.sum((v - m) ** 2 * self.pmf))

    def cdf(self, x: float) -> float:
        """P(X <= x)."""
        return float(self.pmf[self.values() <= x].sum())

    def prob_over(self, line: float) -> float:
        """P(X > line) — the OVER probability at a book/DFS line."""
        return float(self.pmf[self.values() > line].sum())

    def over_under(self, line: float) -> dict:
        """OVER/UNDER/PUSH. Half-lines never push; an integer line pushes on an
        exact hit (the whole-number push, bball-03 §2d analog for props)."""
        v = self.values()
        if _is_integer_line(line):
            k = int(round(line))
            push = float(self.pmf[v == k].sum())
            over = float(self.pmf[v > k].sum())
            under = float(self.pmf[v < k].sum())
        else:
            over = float(self.pmf[v > line].sum())
            push = 0.0
            under = 1.0 - over
        return {"line": float(line), "OVER": over, "UNDER": under, "PUSH": push}

    def materialize(self) -> dict:
        """The PropPrediction storage payload: a trimmed pmf + support_start so
        any line prices downstream. Trailing ~0 tail is dropped for compactness."""
        pmf = self.pmf
        nz = np.nonzero(pmf > 1e-6)[0]
        if len(nz) == 0:
            return {"pmf": [], "support_start": self.support_start}
        lo, hi = int(nz[0]), int(nz[-1])
        return {
            "pmf": [round(float(x), 6) for x in pmf[lo : hi + 1]],
            "support_start": self.support_start + lo,
        }

    def sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        return self.support_start + rng.choice(len(self.pmf), size=n, p=self.pmf)


# ---------------------------------------------------------------------------
# constructors per stat (bball-03 §4c)
# ---------------------------------------------------------------------------


def neg_binom(mean: float, vmr: float, family: str = "neg_binom") -> StatDistribution:
    """Rebounds / assists (bball-03 §4c). `vmr` = variance-to-mean ratio (>1 =
    overdispersed). Falls back to Poisson when vmr<=1 (no overdispersion to
    model). NB(r, p): var = mean/p, so p = 1/vmr, r = mean/(vmr-1)."""
    mean = max(float(mean), 1e-6)
    if vmr <= 1.0 + 1e-6:
        return poisson_stat(mean)
    p = 1.0 / vmr
    r = mean / (vmr - 1.0)
    hi = int(min(MAX_SUPPORT, mean + 10.0 * np.sqrt(vmr * mean) + 5))
    ks = np.arange(0, hi + 1)
    return StatDistribution(nbinom.pmf(ks, r, p), 0, family, {"r": float(r), "p": float(p)})


def poisson_stat(mean: float, family: str = "poisson") -> StatDistribution:
    """Blocks / steals — low-rate, variance-dominated noise (bball-03 §5 devig
    only). Also the vmr<=1 fallback for NB stats."""
    mean = max(float(mean), 1e-6)
    hi = int(min(MAX_SUPPORT, mean + 8.0 * np.sqrt(mean) + 5))
    ks = np.arange(0, hi + 1)
    return StatDistribution(poisson.pmf(ks, mean), 0, family, {"lam": float(mean)})


def threes_made(attempts_mean: float, three_pct: float) -> StatDistribution:
    """Threes made ~ Binomial(round(3PA), 3P%) (bball-03 §4c). Modelable mean,
    make/miss luck dominates the outcome (§5 noise)."""
    n = max(int(round(attempts_mean)), 0)
    p = float(np.clip(three_pct, 1e-6, 1 - 1e-6))
    ks = np.arange(0, n + 1)
    return StatDistribution(binom.pmf(ks, n, p), 0, "binom", {"n": n, "p": p})


def points_compound(lam2: float, lam3: float, lam_ft: float) -> StatDistribution:
    """POINTS as a compound convolution (bball-03 §4c): expected 2P makes `lam2`,
    3P makes `lam3`, FT makes `lam_ft`, each ~Poisson; points = 2*P2 + 3*P3 + FT.
    Convolving the three scaled-Poisson pmfs yields the lumpy, fat-right-tailed
    points distribution the 3-pointer creates."""
    lam2, lam3, lam_ft = max(lam2, 1e-9), max(lam3, 1e-9), max(lam_ft, 1e-9)
    mean = 2 * lam2 + 3 * lam3 + lam_ft
    var = 4 * lam2 + 9 * lam3 + lam_ft
    max_pts = int(min(MAX_SUPPORT, mean + 6.0 * np.sqrt(var) + 10))

    def scaled_poisson_pmf(lam: float, mult: int) -> np.ndarray:
        arr = np.zeros(max_pts + 1)
        ks = np.arange(0, max_pts // mult + 1)
        arr[ks * mult] = poisson.pmf(ks, lam)
        return arr

    conv = np.convolve(scaled_poisson_pmf(lam2, 2), scaled_poisson_pmf(lam3, 3))
    conv = np.convolve(conv, scaled_poisson_pmf(lam_ft, 1))[: max_pts + 1]
    return StatDistribution(
        conv, 0, "compound", {"lam2": float(lam2), "lam3": float(lam3), "lam_ft": float(lam_ft)}
    )


def combine_copula(
    marginals: list[StatDistribution],
    corr: np.ndarray | None = None,
    n: int = 40000,
    seed: int = 0,
) -> StatDistribution:
    """PRA / P+R / P+A / R+A (bball-03 §4c): the SUM of correlated marginals via a
    Gaussian copula. Minutes is the shared driver, so components are positively
    correlated; we simulate correlated normals -> uniforms -> each marginal's
    inverse CDF -> sum, then build the empirical pmf. Deterministic (seeded).
    Default correlation 0.3 pairwise (a big-minutes night lifts all components)."""
    k = len(marginals)
    if k == 1:
        return marginals[0]
    if corr is None:
        corr = np.full((k, k), 0.3)
        np.fill_diagonal(corr, 1.0)
    rng = np.random.default_rng(seed)
    z = rng.multivariate_normal(np.zeros(k), corr, size=n)
    u = norm.cdf(z)
    total = np.zeros(n, dtype=np.int64)
    for i, m in enumerate(marginals):
        cdf = np.cumsum(m.pmf)
        idx = np.searchsorted(cdf, u[:, i], side="left")
        idx = np.clip(idx, 0, len(m.pmf) - 1)
        total += m.support_start + idx
    hi = int(total.max())
    pmf = np.bincount(total, minlength=hi + 1).astype(float) / n
    return StatDistribution(pmf, 0, "copula", {"n_marginals": k, "corr": np.asarray(corr).tolist()})
