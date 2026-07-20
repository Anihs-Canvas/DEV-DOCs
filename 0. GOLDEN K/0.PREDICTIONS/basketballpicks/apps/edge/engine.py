"""Edge detection: reprice the fair distribution at each soft/DFS line and flag the
+EV side (bball-04 §2c/§3, bball-06 §7). PURE module — the ORM service (services.py)
builds the inputs and persists EdgePicks; all the decision math lives here so it is
unit-tested without a database.

Signal per prop per venue (identical in shape to safepicks sharp_anchor.edge_vs_fair,
ported from 1X2 to props):
    p_true   = de-vig(sharp/consensus) repriced to the venue's line (props devig_engine)
    soft:  EDGE = price · p_true − 1        (a soft book is +EV iff EDGE > 0)
    DFS:   leg qualifies iff p_true(side) >= breakeven(N) + margin (dfs.py)

*** THE ANCHOR-CONTAMINATION GUARDRAIL (bball-06 §7 — the single biggest $0 hazard).
With no independent sharp price, the "true" prob is a de-vig of the SAME soft market
we grade against, so the honesty gate can confirm a PHANTOM edge when the soft books
and the DFS line are wrong together. This module ENCODES that risk as a tier on every
candidate and refuses / down-weights accordingly:

  tier 0 PINNACLE_AUDITED   anchor=pinnacle (OddsPapi) — independent sharp truth. Clean.
  tier 1 CONSENSUS_VS_DFS   anchor=consensus, venue=DFS. DFS line is NOT in the soft
                            panel, so it is an independent target; the residual risk
                            is only the soft panel's own shared blind spots. Bankable.
  tier 2 CONSENSUS_LEAVE1OUT anchor=consensus, venue=soft book, leave-one-out applied
                            (the graded book was REMOVED from its own benchmark). The
                            structural mitigation worked; peers may still share error.
  tier 3 CONTAMINATED       anchor=consensus, venue=soft book, NO leave-one-out — the
                            book is INSIDE its own fair benchmark. Phantom-edge shaped.
                            REJECTED (never published).
  tier 4 MODEL_ANCHORED     no sharp AND no consensus (thin/neglected line). 2× edge
                            threshold, ½ stake, tracked as a SEPARATE cohort, and NEVER
                            trusted vs a well-quoted sharp line (bball-04 §4/§6b).

The OddsPapi Pinnacle audit (pinnacle_bias / audit_verdict) is the only independent
check on tiers 1-2; a SYSTEMATIC consensus-vs-Pinnacle bias fires kill-criterion K6.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from . import dfs

# Contamination tiers (lower = cleaner). tier 3 is auto-rejected.
TIER_PINNACLE_AUDITED = 0
TIER_CONSENSUS_VS_DFS = 1
TIER_CONSENSUS_LEAVE1OUT = 2
TIER_CONTAMINATED = 3
TIER_MODEL_ANCHORED = 4

TIER_LABELS = {
    0: "pinnacle_audited",
    1: "consensus_vs_dfs",
    2: "consensus_leave_one_out",
    3: "contaminated",
    4: "model_anchored",
}

# Per-tier discipline (bball-04 §6b): model-anchored candidates get 2× the edge
# threshold and ½ the stake; contaminated candidates are refused outright.
TIER_EDGE_MULT = {0: 1.0, 1: 1.0, 2: 1.0, 3: float("inf"), 4: 2.0}
TIER_STAKE_MULT = {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.0, 4: 0.5}

# K6 anti-contamination audit (bball-06 §5): a MEAN |consensus − pinnacle| bias
# beyond this on the same legs = systematic, not noise → kill.
PINNACLE_BIAS_KILL = 0.03


def edge_vs_fair(price: float, p_fair: float) -> float:
    """EV per unit staked when `price` is taken at fair probability `p_fair`
    (safepicks sharp_anchor.edge_vs_fair, verbatim shape)."""
    return price * p_fair - 1.0


# ---------------------------------------------------------------------------
# contamination assessment (the guardrail)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Contamination:
    tier: int
    label: str
    reason: str
    edge_mult: float  # multiply the base edge threshold by this
    stake_mult: float  # multiply the base stake by this
    rejected: bool
    needs_pinnacle_audit: bool


def assess_contamination(*, anchor: str, venue_is_dfs: bool, excluded_book: str | None,
                         venue_book: str, pinnacle_audited: bool = False) -> Contamination:
    """Classify a candidate's anchor-contamination risk into a tier (see module
    docstring). `excluded_book` is the leave-one-out book the consensus removed."""
    if anchor == "pinnacle" or pinnacle_audited:
        t = TIER_PINNACLE_AUDITED
        return Contamination(t, TIER_LABELS[t], "independent sharp (pinnacle) truth",
                             TIER_EDGE_MULT[t], TIER_STAKE_MULT[t], False, False)
    if anchor == "model":
        t = TIER_MODEL_ANCHORED
        return Contamination(t, TIER_LABELS[t], "no sharp/consensus cross-check — thin line",
                             TIER_EDGE_MULT[t], TIER_STAKE_MULT[t], False, False)
    # anchor == "consensus"
    if venue_is_dfs:
        t = TIER_CONSENSUS_VS_DFS
        return Contamination(t, TIER_LABELS[t], "DFS line independent of the soft panel",
                             TIER_EDGE_MULT[t], TIER_STAKE_MULT[t], False, True)
    # soft-book venue graded against a soft consensus
    if excluded_book and excluded_book.lower() == venue_book.lower():
        t = TIER_CONSENSUS_LEAVE1OUT
        return Contamination(t, TIER_LABELS[t], "graded book removed from its own benchmark",
                             TIER_EDGE_MULT[t], TIER_STAKE_MULT[t], False, True)
    t = TIER_CONTAMINATED
    reason = "book is inside its own fair benchmark — phantom-edge shaped"
    return Contamination(t, TIER_LABELS[t], reason,
                         TIER_EDGE_MULT[t], TIER_STAKE_MULT[t], True, True)


# ---------------------------------------------------------------------------
# candidate evaluation (soft + DFS)
# ---------------------------------------------------------------------------

OVER, UNDER = "OVER", "UNDER"


@dataclass(frozen=True, slots=True)
class EdgeCandidate:
    venue: str  # SOFTBOOK | DFS
    book: str
    market_key: str
    line: float
    side: str  # OVER | UNDER
    p_true: float  # fair prob of the chosen side
    edge: float  # price·p_true − 1 (soft) OR p_true − breakeven (DFS)
    price: float | None  # decimal (soft) / None (DFS)
    contamination: Contamination
    qualifies: bool
    audit: dict = field(default_factory=dict)


def evaluate_soft_line(*, book: str, market_key: str, line: float, over_price: float | None,
                       under_price: float | None, p_true_over: float, contamination: Contamination,
                       min_edge: float, within_cap: bool = True, method_spread: float = 0.0,
                       max_method_spread: float = 0.02) -> EdgeCandidate | None:
    """Flag the +EV side of a two-sided soft quote. Returns the better-EV side as a
    candidate (qualifies=True/False), or None if the anchor is contaminated/uncapped
    or method-fragile. Threshold is scaled by the contamination tier."""
    if contamination.rejected or not within_cap:
        return None
    if method_spread > max_method_spread:  # method-fragile edge is not real (bball-04 §2a)
        return None
    thr = min_edge * contamination.edge_mult
    best = None
    sides = ((OVER, over_price, p_true_over), (UNDER, under_price, 1.0 - p_true_over))
    for side, price, p in sides:
        if price is None or price <= 1.0:
            continue
        e = edge_vs_fair(price, p)
        cand = EdgeCandidate(
            venue="SOFTBOOK", book=book, market_key=market_key, line=line, side=side,
            p_true=p, edge=e, price=price, contamination=contamination,
            qualifies=e >= thr,
            audit={"threshold": thr, "method_spread": method_spread, "within_cap": within_cap},
        )
        if best is None or cand.edge > best.edge:
            best = cand
    return best


def evaluate_dfs_leg(*, book: str, market_key: str, line: float, side: str, p_true: float,
                     mult: float, n_legs: int, contamination: Contamination,
                     margin: float = dfs.DEFAULT_MARGIN, within_cap: bool = True,
                     dfs_odds_type: str = "standard") -> EdgeCandidate | None:
    """Evaluate ONE DFS pick'em leg vs the per-leg breakeven b(N)=M^(-1/N). The
    'price' is implicit in the multiplier + leg count, so the comparison is
    p_true vs a breakeven, not vs a decimal (bball-04 §3a)."""
    if contamination.rejected or not within_cap:
        return None
    be = dfs.breakeven_per_leg(mult, n_legs)
    eff_margin = margin * contamination.edge_mult
    # non-standard PrizePicks lines (demon/goblin) are shaded — demand more edge.
    if dfs_odds_type in ("demon", "goblin"):
        eff_margin += 0.02
    edge = p_true - be
    return EdgeCandidate(
        venue="DFS", book=book, market_key=market_key, line=line, side=side,
        p_true=p_true, edge=edge, price=None, contamination=contamination,
        qualifies=p_true >= be + eff_margin,
        audit={"breakeven": be, "margin": eff_margin, "mult": mult, "n_legs": n_legs,
               "dfs_odds_type": dfs_odds_type},
    )


# ---------------------------------------------------------------------------
# OddsPapi Pinnacle AUDIT hook (K6 anti-contamination)
# ---------------------------------------------------------------------------


def pinnacle_bias(consensus_p_over: float, pinnacle_p_over: float) -> float:
    """Signed bias of the soft-consensus fair prob vs the independent Pinnacle
    de-vig on the SAME leg. Positive => consensus over-states OVER vs the sharp."""
    return consensus_p_over - pinnacle_p_over


def audit_verdict(biases: list[float]) -> dict:
    """K6 (bball-06 §5): if the soft-consensus is SYSTEMATICALLY (not merely noisily)
    biased vs Pinnacle on the audited legs, the anchor is contaminated → KILL. Uses
    the ~8-boards/mo OddsPapi sample; reported as a bias check, never a volume gate."""
    if not biases:
        return {"n": 0, "mean_bias": None, "mean_abs_bias": None, "kill": False,
                "reason": "no pinnacle audit legs yet (empty-runs-clean)"}
    mean_bias = statistics.fmean(biases)
    mean_abs = statistics.fmean(abs(b) for b in biases)
    kill = abs(mean_bias) > PINNACLE_BIAS_KILL
    return {
        "n": len(biases),
        "mean_bias": mean_bias,
        "mean_abs_bias": mean_abs,
        "kill": kill,
        "reason": ("consensus systematically biased vs pinnacle — K6 kill"
                   if kill else "within noise of pinnacle"),
    }
