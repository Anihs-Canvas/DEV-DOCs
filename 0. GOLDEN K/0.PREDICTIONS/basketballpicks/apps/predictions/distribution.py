"""The predictive MARGIN + TOTAL distribution (bball-03 §2d/§2e) — the core
deliverable, pure scipy/numpy (no ORM).

By the CLT a basketball game is ~100 near-independent possessions, so the margin
and total are ~Gaussian (bball-03 §1). We wrap the two point estimates in a
predictive distribution and derive EVERY listed market from it:

    MARGIN ~ Family(mu_m, sigma_m)      spread / moneyline
    TOTAL  ~ Family(mu_t, sigma_t)      total
    home pts ~ Normal((mu_t+mu_m)/2, sigma_tt)   team total

`Family` is Normal by default, with two documented refinements that earn their
place ONLY under the CRPS/PIT gate (bball-03 §2d/§6b):
  * Student-t (dof ~8-10) for fatter blowout/OT tails;
  * skew-normal for the mild asymmetry blowouts create.
Both are re-parameterized so `mu`/`sigma` stay the true mean/SD — the refinement
changes only the SHAPE, so a calibration comparison is apples-to-apples.

sigma_m (~11-13 NBA) is EMPIRICAL — our features explain only ~21% of MOV
variance, the residual IS sigma_m (bball-03 §2d). It is passed in (estimated
per-league from our own residuals) and WIDENS under lineup uncertainty — honest
doubt, never a bluffed tight number.

Integer lines get a continuity-corrected PUSH mass (the "key points / hook"
density fix, bball-03 §2d) so win/push/lose is honest on whole numbers.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.stats import norm, skewnorm, t as student_t

FAMILY_NORMAL = "normal"
FAMILY_T = "t"
FAMILY_SKEWNORM = "skewnorm"


def _frozen(mu: float, sigma: float, family: str, dof: float | None, skew: float):
    """A scipy frozen distribution with mean==mu and SD==sigma regardless of
    family — the shape refinement never moves the first two moments."""
    sigma = max(float(sigma), 1e-6)
    if family == FAMILY_T:
        df = float(dof if dof and dof > 2 else 8.0)
        scale = sigma * np.sqrt((df - 2.0) / df)  # so Var == sigma^2
        return student_t(df, loc=mu, scale=scale)
    if family == FAMILY_SKEWNORM and abs(skew) > 1e-9:
        a = float(skew)
        delta = a / np.sqrt(1.0 + a * a)
        scale = sigma / np.sqrt(1.0 - 2.0 * delta * delta / np.pi)
        loc = mu - scale * delta * np.sqrt(2.0 / np.pi)
        return skewnorm(a, loc=loc, scale=scale)
    return norm(loc=mu, scale=sigma)


def _is_integer_line(line: float) -> bool:
    return abs(line - round(line)) < 1e-9


def _win_push_lose(dist, threshold: float, greater: bool) -> tuple[float, float, float]:
    """(win, push, lose) for an over/cover bet whose realized quantity is
    integer-valued. Half-lines never push; integer lines get a continuity-
    corrected push band of width 1 centered on the line."""
    if _is_integer_line(threshold):
        lo = dist.cdf(threshold - 0.5)
        hi = dist.cdf(threshold + 0.5)
        push = float(max(hi - lo, 0.0))
        win_hi = 1.0 - hi  # strictly beyond the push band
        lose_lo = lo
        win, lose = (float(win_hi), float(lose_lo)) if greater else (float(lose_lo), float(win_hi))
        return win, push, lose
    p_gt = float(dist.sf(threshold))
    return (p_gt, 0.0, 1.0 - p_gt) if greater else (1.0 - p_gt, 0.0, p_gt)


@dataclass
class MarginTotalDistribution:
    """The full predictive object for one game. `sigma_teamtotal` defaults to the
    principled sqrt(sigma_t^2 + sigma_m^2)/2 (home pts = (total+margin)/2 with
    margin/total ~uncorrelated, bball-03 §2d)."""

    mu_margin: float  # home - away expected points (positive = home favored)
    sigma_margin: float
    mu_total: float
    sigma_total: float
    margin_family: str = FAMILY_NORMAL
    total_family: str = FAMILY_NORMAL
    dof: float | None = None  # Student-t degrees of freedom (both marginals)
    skew: float = 0.0  # skew-normal shape (margin only)
    sigma_teamtotal: float | None = None
    meta: dict = field(default_factory=dict)

    # ---- frozen marginals -------------------------------------------------
    def _margin(self):
        return _frozen(self.mu_margin, self.sigma_margin, self.margin_family, self.dof, self.skew)

    def _total(self):
        return _frozen(self.mu_total, self.sigma_total, self.total_family, self.dof, 0.0)

    def _team(self, home: bool):
        mu = (self.mu_total + (self.mu_margin if home else -self.mu_margin)) / 2.0
        sig = self.sigma_teamtotal
        if sig is None:
            sig = np.sqrt(self.sigma_total**2 + self.sigma_margin**2) / 2.0
        return _frozen(mu, sig, FAMILY_NORMAL, None, 0.0)

    # ---- market probabilities (bball-03 §2e) ------------------------------
    def prob_home_ml(self) -> float:
        """P(home wins) = P(margin > 0). Basketball has no draws (OT resolves
        ties), so the continuous survival is exact."""
        return float(self._margin().sf(0.0))

    def spread(self, home_line: float) -> dict:
        """Home covers `home_line` (e.g. -4.5 favored, +3.5 dog) iff
        margin > -home_line. Returns WIN/PUSH/LOSE for the HOME side; AWAY is the
        mirror."""
        threshold = -float(home_line)
        win, push, lose = _win_push_lose(self._margin(), threshold, greater=True)
        return {
            "line": float(home_line),
            "HOME": win,
            "AWAY": lose,
            "PUSH": push,
        }

    def total(self, line: float) -> dict:
        """Over/under `line` on the game total."""
        over, push, under = _win_push_lose(self._total(), float(line), greater=True)
        return {"line": float(line), "OVER": over, "UNDER": under, "PUSH": push}

    def team_total(self, line: float, home: bool) -> dict:
        over, push, under = _win_push_lose(self._team(home), float(line), greater=True)
        return {"line": float(line), "side": "HOME" if home else "AWAY",
                "OVER": over, "UNDER": under, "PUSH": push}

    def moneyline(self) -> dict:
        p = self.prob_home_ml()
        return {"HOME": p, "AWAY": 1.0 - p}

    # ---- distributional scoring (bball-03 §6b) ----------------------------
    def pit_margin(self, actual_margin: float) -> float:
        return float(self._margin().cdf(float(actual_margin)))

    def pit_total(self, actual_total: float) -> float:
        return float(self._total().cdf(float(actual_total)))

    def crps_margin(self, actual_margin: float) -> float:
        from apps.predictions.metrics import crps_gaussian, crps_ensemble

        if self.margin_family == FAMILY_NORMAL:
            return float(crps_gaussian(self.mu_margin, self.sigma_margin, actual_margin))
        samples = self._margin().rvs(size=4000, random_state=0)
        return crps_ensemble(samples, actual_margin)

    def crps_total(self, actual_total: float) -> float:
        from apps.predictions.metrics import crps_gaussian, crps_ensemble

        if self.total_family == FAMILY_NORMAL:
            return float(crps_gaussian(self.mu_total, self.sigma_total, actual_total))
        samples = self._total().rvs(size=4000, random_state=0)
        return crps_ensemble(samples, actual_total)

    # ---- serialization (the Prediction.prob_vector `dist` block) ----------
    def dist_block(self) -> dict:
        return {
            "margin": {
                "mu": round(float(self.mu_margin), 4),
                "sigma": round(float(self.sigma_margin), 4),
                "family": self.margin_family,
                "dof": self.dof,
                "skew": round(float(self.skew), 4),
            },
            "total": {
                "mu": round(float(self.mu_total), 4),
                "sigma": round(float(self.sigma_total), 4),
                "family": self.total_family,
                "dof": self.dof,
            },
        }

    @classmethod
    def from_dist_block(cls, block: dict) -> "MarginTotalDistribution":
        m, t = block["margin"], block["total"]
        return cls(
            mu_margin=m["mu"], sigma_margin=m["sigma"], margin_family=m.get("family", FAMILY_NORMAL),
            dof=m.get("dof"), skew=m.get("skew", 0.0),
            mu_total=t["mu"], sigma_total=t["sigma"], total_family=t.get("family", FAMILY_NORMAL),
        )


def estimate_sigma(residuals, floor: float = 8.0, ceil: float = 16.0) -> float:
    """Empirical sigma from OUR OWN model residuals (bball-03 §2d): sigma is not
    fitted from features (they explain ~21% of MOV variance) — it IS the residual
    spread. Clamped to a sane NBA-ish band so a thin/degenerate sample can't
    produce an absurd width."""
    r = np.asarray(residuals, dtype=float)
    if len(r) < 2:
        return float(np.clip(12.0, floor, ceil))
    return float(np.clip(np.std(r, ddof=1), floor, ceil))
