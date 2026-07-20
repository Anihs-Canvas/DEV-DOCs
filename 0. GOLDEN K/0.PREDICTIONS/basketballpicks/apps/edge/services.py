"""Publish beat: PropLine + consensus + (secondary) PropPrediction → EdgePick rows
(bball-01 §3 publish stage). ORM glue only — every decision delegates to the PURE
engine (edge.engine), DFS math (edge.dfs) and consensus builder (props.consensus),
so this module is thin and the logic is unit-tested without a database.

Contract consumed (never mutated): apps.core.Game/Player, apps.props.PropLine/
PropMarket/PropConsensus, apps.predictions.PropPrediction. Candidates that fail any
gate write NO row (the audit lives on the published row + the publishing JobRun).
"""

from __future__ import annotations

import logging

from django.utils import timezone

from apps.props import consensus as consensus_mod
from apps.props import devig_engine as de

from . import dfs, engine
from .models import EdgePick, RiskProfile

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# consume the SECONDARY model layer (predictions.PropPrediction) for thin lines
# ---------------------------------------------------------------------------


def model_p_over(game, player_id: int, market_key: str, line: float):
    """p_true(over line) from the calibrated PropPrediction, or None. Prefers the
    materialized pmf (works for every family incl. compound/copula); falls back to
    the closed-form dist. Returns None unless the market cleared the calibration
    gate (bball-03 §5: blocks/steals/threes/first-basket are display/devig-only,
    NEVER a model edge)."""
    try:
        from apps.predictions.models import PropPrediction
    except Exception:  # predictions app not wired in this context
        return None
    pp = (
        PropPrediction.objects.filter(game=game, player_id=player_id, market_key=market_key)
        .order_by("-created_at")
        .first()
    )
    if pp is None or not pp.calibration_gate:
        return None
    if pp.pmf:
        return de.prob_over_from_pmf(pp.pmf, pp.support_start, line), pp
    try:
        return de.prob_over_from_dist(pp.dist, pp.dist_params, line), pp
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# per-line anchor: consensus first, model fallback on thin lines
# ---------------------------------------------------------------------------


def _anchor_for_line(game, player_id, market_key, target_line, panel_quotes, *,
                     venue_is_dfs, venue_book):
    """Return (p_true_over, anchor_label, meta) for one target line. Consensus is
    primary; when the panel is too thin (<2 books) OR the reprice extrapolates past
    the cap, fall back to the model (thin/neglected cohort)."""
    exclude = None if venue_is_dfs else venue_book
    res = consensus_mod.build_consensus_at(
        panel_quotes, market_key, target_line, exclude_book=exclude
    )
    if res.p_over is not None and res.n_books >= 2 and res.within_cap:
        return res.p_over, "consensus", {"consensus": res, "excluded_book": exclude}

    model = model_p_over(game, player_id, market_key, target_line)
    if model is not None:
        p, pp = model
        return p, "model", {"prop_prediction": pp, "consensus": res}
    # consensus exists but thin/uncapped — still usable, flagged by tier + within_cap
    if res.p_over is not None:
        return res.p_over, "consensus", {"consensus": res, "excluded_book": exclude, "thin": True}
    return None, None, {}


# ---------------------------------------------------------------------------
# the publish entry point
# ---------------------------------------------------------------------------


def publish_edges(game, *, profile: RiskProfile | None = None, at=None, is_closing=False) -> dict:
    """Scan a game's soft + DFS prop lines, flag +EV candidates that clear their
    cell gate + rails + the contamination guardrail, and write EdgePick rows.
    Idempotent by EdgePick's unique key. Empty-runs-clean. Returns a counters dict
    for the publishing JobRun."""
    from collections import defaultdict

    from apps.props.models import PropLine

    at = at or timezone.now()
    profile = profile or RiskProfile.objects.filter(name="default").first() or RiskProfile()
    counters = {"scanned": 0, "published": 0, "rejected_contaminated": 0,
                "below_edge": 0, "model_anchored": 0, "no_anchor": 0}

    lines = list(
        PropLine.objects.filter(game=game, is_closing=is_closing)
        .select_related("player", "market", "bookmaker")
    )
    if not lines:
        return counters

    # all quotes per (player, market) → the consensus panel; iterate targets over
    # the DFS + soft lines actually on offer.
    panels: dict[tuple, list] = defaultdict(list)
    for pl in lines:
        panels[(pl.player_id, pl.market_id)].append(
            consensus_mod._Quote(pl.bookmaker.name, float(pl.line),
                                 _f(pl.over_price), _f(pl.under_price), pl.bookmaker.is_dfs)
        )

    for pl in lines:
        counters["scanned"] += 1
        market_key = pl.market.key
        panel = panels[(pl.player_id, pl.market_id)]
        venue_is_dfs = pl.bookmaker.is_dfs
        p_over, anchor_label, meta = _anchor_for_line(
            game, pl.player_id, market_key, float(pl.line), panel,
            venue_is_dfs=venue_is_dfs, venue_book=pl.bookmaker.name,
        )
        if p_over is None:
            counters["no_anchor"] += 1
            continue

        cons = meta.get("consensus")
        within_cap = cons.within_cap if cons is not None else True
        excluded = meta.get("excluded_book")
        method_spread = cons.method_spread if cons is not None else 0.0

        cont = engine.assess_contamination(
            anchor=anchor_label, venue_is_dfs=venue_is_dfs, excluded_book=excluded,
            venue_book=pl.bookmaker.name,
        )
        if cont.rejected:
            counters["rejected_contaminated"] += 1
            continue
        if cont.tier == engine.TIER_MODEL_ANCHORED:
            counters["model_anchored"] += 1

        cand = _evaluate(pl, market_key, p_over, cont, profile, within_cap,
                         method_spread, venue_is_dfs)
        if cand is None or not cand.qualifies:
            counters["below_edge"] += 1
            continue

        _write_pick(game, pl, cand, anchor_label, excluded, profile, at, meta, counters)

    return counters


def _evaluate(pl, market_key, p_over, cont, profile, within_cap, method_spread, venue_is_dfs):
    if venue_is_dfs:
        mult = float(pl.payout_mult) if pl.payout_mult else None
        if mult is None:
            return None  # a bare pick'em leg needs its entry's multiplier — priced at entry build
        # a DFS leg is evaluated per side; pick the +EV side vs breakeven.
        # n_legs is a per-entry property; use the profile's typical odd-leg power play (3).
        best = None
        for side, p in (("OVER", p_over), ("UNDER", 1.0 - p_over)):
            c = engine.evaluate_dfs_leg(
                book=pl.bookmaker.name, market_key=market_key, line=float(pl.line), side=side,
                p_true=p, mult=mult, n_legs=3, contamination=cont,
                margin=float(profile.min_edge), within_cap=within_cap,
                dfs_odds_type=pl.dfs_odds_type or "standard",
            )
            if c and (best is None or c.edge > best.edge):
                best = c
        return best
    return engine.evaluate_soft_line(
        book=pl.bookmaker.name, market_key=market_key, line=float(pl.line),
        over_price=_f(pl.over_price), under_price=_f(pl.under_price), p_true_over=p_over,
        contamination=cont, min_edge=float(profile.min_edge), within_cap=within_cap,
        method_spread=method_spread,
    )


def _write_pick(game, pl, cand, anchor_label, excluded, profile, at, meta, counters):
    # stake: quarter-Kelly on the (single-leg) price; DFS entries re-stake at entry
    # build time (dfs.quarter_kelly_entry over the joint), so a leg's stake here is
    # a placeholder single-leg sizing.
    price = cand.price if cand.price else 1.0 / max(cand.p_true, 1e-6)
    kelly = dfs.quarter_kelly_entry(
        cand.p_true, price, float(profile.kelly_fraction), float(profile.max_stake_pct_bankroll)
    )
    stake = kelly["stake_fraction"] * cand.contamination.stake_mult
    min_acc = (1.0 + float(profile.min_edge)) / cand.p_true if cand.venue == "SOFTBOOK" else None
    pp = meta.get("prop_prediction")

    EdgePick.objects.update_or_create(
        prop_line=pl, cell=_cell_for(cand),
        defaults=dict(
            prop_prediction=pp,
            venue=cand.venue, market_key=cand.market_key, side=cand.side, line=cand.line,
            sharp_fair_prob=round(cand.p_true, 5),
            model_prob=round(cand.p_true, 5) if anchor_label == "model" else None,
            edge=round(cand.edge, 5), ev=round(cand.edge, 5),
            stake_fraction=round(stake, 5),
            min_acceptable_price=round(min_acc, 3) if min_acc else None,
            anchor=anchor_label, contamination_tier=cand.contamination.tier,
            excluded_book=excluded or "",
            published_at=at, expires_at=game.tipoff_utc,
            audit={**cand.audit, "contamination": cand.contamination.label, "kelly": kelly},
        ),
    )
    counters["published"] += 1


def _cell_for(cand) -> str:
    return f"{cand.venue[:1]}-{cand.market_key}-t{cand.contamination.tier}"


def _f(v):
    return float(v) if v is not None else None
