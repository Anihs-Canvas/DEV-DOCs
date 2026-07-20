"""Minutes projection + the usage/opportunity layer (bball-03 §4a/§4b) — the
ceiling on everything, pure numpy/scipy (no ORM).

"Minutes is the ceiling on everything else" — no counting stat can exceed the
opportunity minutes provide. We model minutes as a DISTRIBUTION, not a number,
because its UNCERTAINTY is the dominant driver of prop variance (bball-03 §4a):

  * baseline mean/sd from decayed recent minutes (role), lineup-state conditioned;
  * a BLOWOUT (garbage-time) haircut whose probability comes from the CORE
    model's margin distribution — the real team->player linkage (favorites'
    starters have a left tail);
  * a DNP / injury-exit gate `p_active` (mass at 0 minutes).

The usage layer then turns the minutes distribution into per-stat PARAMETERS for
`prop_stats`, propagating minutes VARIANCE into the stat overdispersion via the
law of total variance — so "we don't know the minutes" honestly WIDENS every
prop, it does not bluff a tight number.
"""

from dataclasses import dataclass, field

import numpy as np


def blowout_prob_from_core(core_dist, threshold: float = 18.0) -> float:
    """P(|margin| > threshold) from the CORE MarginTotalDistribution — the
    garbage-time linkage (bball-03 §4a). A wider/one-sided margin => more
    starter-rest risk on both benches."""
    m = core_dist._margin()
    return float(m.sf(threshold) + m.cdf(-threshold))


@dataclass
class MinutesDistribution:
    """A two-component minutes mixture gated by availability. With prob
    `p_active` the player plays; conditional on playing, with prob `blowout_prob`
    minutes are haircut by `blowout_haircut` (garbage time / rest) at slightly
    wider sd. Truncated to [0, cap]."""

    mean: float  # baseline (normal-game) projected minutes
    sd: float = 6.0
    p_active: float = 1.0  # 1 - P(DNP / injury scratch)
    blowout_prob: float = 0.0
    blowout_haircut: float = 6.0  # minutes shaved in a blowout
    blowout_sd_mult: float = 1.3
    cap: float = 48.0

    def _components(self):
        """(weight, mu, sigma) tuples for the play-conditional mixture."""
        base_w = 1.0 - self.blowout_prob
        return [
            (base_w, self.mean, self.sd),
            (self.blowout_prob, max(self.mean - self.blowout_haircut, 0.0), self.sd * self.blowout_sd_mult),
        ]

    def conditional_moments(self) -> tuple[float, float]:
        """(E[M], Var[M]) GIVEN the player is active (mixture, pre-availability)."""
        comps = self._components()
        mu = sum(w * m for w, m, _ in comps)
        second = sum(w * (s * s + m * m) for w, m, s in comps)
        return float(mu), float(max(second - mu * mu, 1e-9))

    def effective_moments(self) -> tuple[float, float]:
        """(E[M], Var[M]) INCLUDING the DNP gate at 0 (law of total variance over
        the active/inactive Bernoulli). This is what the stat layer integrates."""
        mu_c, var_c = self.conditional_moments()
        p = float(np.clip(self.p_active, 0.0, 1.0))
        mean = p * mu_c
        var = p * (var_c + mu_c * mu_c) - mean * mean
        return float(mean), float(max(var, 1e-9))

    def sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        comps = self._components()
        weights = np.array([w for w, _, _ in comps])
        weights = weights / weights.sum()
        pick = rng.choice(len(comps), size=n, p=weights)
        out = np.empty(n)
        for i, (_, mu, sd) in enumerate(comps):
            mask = pick == i
            out[mask] = rng.normal(mu, sd, size=int(mask.sum()))
        out = np.clip(out, 0.0, self.cap)
        active = rng.random(n) < self.p_active
        return out * active

    def to_params(self) -> dict:
        return {
            "mean": round(self.mean, 3),
            "sd": round(self.sd, 3),
            "p_active": round(float(self.p_active), 4),
            "blowout_prob": round(self.blowout_prob, 4),
            "blowout_haircut": round(self.blowout_haircut, 3),
        }


@dataclass
class UsageProjection:
    """Given a minutes distribution + per-minute rates + team pace, produce the
    parameters each `prop_stats` constructor needs, with minutes variance folded
    into the stat overdispersion (bball-03 §4b). Rates are per-minute (from
    decayed PlayerForm); shooting-make rates split points into 2P/3P/FT."""

    minutes: MinutesDistribution
    reb_per_min: float = 0.0
    ast_per_min: float = 0.0
    tpm_per_min: float = 0.0  # threes MADE per minute
    tpa_per_min: float = 0.0  # threes ATTEMPTED per minute
    three_pct: float = 0.36
    fg2_makes_per_min: float = 0.0  # 2P makes per minute
    ft_makes_per_min: float = 0.0
    stl_per_min: float = 0.0
    blk_per_min: float = 0.0
    base_overdisp: float = 1.15  # role/opponent overdispersion floor
    meta: dict = field(default_factory=dict)

    def _count_moments(self, rate: float) -> tuple[float, float]:
        """(mean, vmr) for a per-minute-rate counting stat, minutes variance
        propagated (Var = within-minutes Poisson-ish + rate^2 * Var[M])."""
        m, v = self.minutes.effective_moments()
        mean = rate * m
        if mean <= 1e-9:
            return 0.0, 1.0
        var = mean * self.base_overdisp + (rate ** 2) * v
        return float(mean), float(max(var / mean, 1.0))

    def rebounds(self):
        from apps.predictions.engines.prop_stats import neg_binom

        mean, vmr = self._count_moments(self.reb_per_min)
        return neg_binom(mean, vmr)

    def assists(self):
        from apps.predictions.engines.prop_stats import neg_binom

        mean, vmr = self._count_moments(self.ast_per_min)
        return neg_binom(mean, vmr)

    def steals(self):
        from apps.predictions.engines.prop_stats import poisson_stat

        mean, _ = self._count_moments(self.stl_per_min)
        return poisson_stat(mean)

    def blocks(self):
        from apps.predictions.engines.prop_stats import poisson_stat

        mean, _ = self._count_moments(self.blk_per_min)
        return poisson_stat(mean)

    def threes(self):
        from apps.predictions.engines.prop_stats import threes_made

        m, _ = self.minutes.effective_moments()
        return threes_made(self.tpa_per_min * m, self.three_pct)

    def points(self):
        from apps.predictions.engines.prop_stats import points_compound

        m, _ = self.minutes.effective_moments()
        return points_compound(
            lam2=self.fg2_makes_per_min * m,
            lam3=self.tpm_per_min * m,
            lam_ft=self.ft_makes_per_min * m,
        )

    def combo(self, components: list[str], corr=None):
        """A copula-summed combo (PRA / P+R / P+A / R+A). `components` names the
        marginals to sum, e.g. ["points", "rebounds", "assists"]."""
        from apps.predictions.engines.prop_stats import combine_copula

        builders = {
            "points": self.points,
            "rebounds": self.rebounds,
            "assists": self.assists,
            "threes": self.threes,
        }
        marginals = [builders[c]() for c in components]
        return combine_copula(marginals, corr=corr)
