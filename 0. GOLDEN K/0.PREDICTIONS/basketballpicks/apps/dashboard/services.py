"""Dashboard context assembly [bball-01 §1] — read-only (ADR 009 discipline).

Thin views render these contexts; all ORM reads live here. Three product pages:
predictions (model output), edge (published +EV picks), and the forward-CLV
gate (the honesty verdict grid). No writes anywhere.
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.core.models import Game
from apps.predictions.models import Prediction, PropPrediction


def base_context() -> dict:
    now = timezone.now()
    return {"now": now, "today": now.date()}


# ---------------------------------------------------------------------------
# predictions page
# ---------------------------------------------------------------------------


def predictions_context(day=None) -> dict:
    ctx = base_context()
    day = day or ctx["today"]
    games = list(
        Game.objects.filter(tipoff_utc__date=day)
        .select_related("season__league", "home_team", "away_team")
        .order_by("tipoff_utc")
    )
    preds = {
        p.game_id: p
        for p in Prediction.objects.filter(
            game__in=games, market=Prediction.MARKET_CORE
        ).select_related("model_version")
    }
    props_by_game: dict[int, list] = {}
    for pp in (
        PropPrediction.objects.filter(game__in=games)
        .select_related("player", "model_version")
        .order_by("player__canonical_name", "market_key")
    ):
        props_by_game.setdefault(pp.game_id, []).append(pp)

    rows = []
    for g in games:
        pv = preds[g.id].prob_vector if g.id in preds else {}
        rows.append(
            {
                "game": g,
                "league": g.season.league.code,
                "prob_vector": pv,
                "ml": (pv or {}).get("ML"),
                "spread": (pv or {}).get("SPREAD"),
                "total": (pv or {}).get("TOTAL"),
                "props": props_by_game.get(g.id, []),
            }
        )
    ctx.update({"day": day, "rows": rows, "n_games": len(games)})
    return ctx


# ---------------------------------------------------------------------------
# edge page
# ---------------------------------------------------------------------------


def edge_context() -> dict:
    ctx = base_context()
    picks = []
    try:
        from apps.edge.models import EdgePick

        for p in (
            EdgePick.objects.filter(status="OPEN")
            .select_related(
                "prop_line__game__home_team",
                "prop_line__game__away_team",
                "prop_line__game__season__league",
                "prop_line__player",
                "prop_line__bookmaker",
                "odds_snapshot__game__home_team",
                "odds_snapshot__game__away_team",
                "odds_snapshot__bookmaker",
            )
            .order_by("expires_at")
        ):
            picks.append(_edge_row(p))
    except Exception:
        ctx["edge_unavailable"] = True
    ctx.update({"picks": picks, "n_picks": len(picks)})
    return ctx


def _edge_row(p) -> dict:
    if p.prop_line_id:
        g = p.prop_line.game
        player = p.prop_line.player.canonical_name
        book = p.prop_line.bookmaker.name
    elif p.odds_snapshot_id:
        g = p.odds_snapshot.game
        player = None
        book = p.odds_snapshot.bookmaker.name
    else:
        g, player, book = None, None, None
    return {
        "cell": p.cell,
        "venue": p.venue,
        "fixture": f"{g.away_team.abbreviation} @ {g.home_team.abbreviation}" if g else "-",
        "league": g.season.league.code if g else None,
        "player": player,
        "book": book,
        "market_key": p.market_key,
        "side": p.side,
        "line": p.line,
        "sharp_fair_prob": p.sharp_fair_prob,
        "model_prob": p.model_prob,
        "edge": p.edge,
        "ev": p.ev,
        "min_price": p.min_acceptable_price,
        "expires_at": p.expires_at,
    }


# ---------------------------------------------------------------------------
# forward-CLV gate page
# ---------------------------------------------------------------------------


def clv_gate_context(days: int = 90) -> dict:
    from apps.backtesting import prop_clv

    ctx = base_context()
    today = ctx["today"]
    report = prop_clv.compute_prop_clv(today - timedelta(days=days), today)
    enabled = _enabled_by_cell()
    cells = []
    for key, summ in report["by_cell"].items():
        row = dict(summ)
        row["cell"] = key
        row["edge_rule_enabled"] = enabled.get(key)
        cells.append(row)
    cells.sort(key=lambda r: (r["verdict"] != "CONFIRM", r["verdict"] != "KILL", -r["n"]))
    ctx.update(
        {
            "days": days,
            "report": report,
            "overall": report["overall"],
            "thresholds": report["thresholds"],
            "cells": cells,
            "by_venue": report["by_venue"],
            "by_market": report["by_market"],
        }
    )
    return ctx


def _enabled_by_cell() -> dict:
    try:
        from apps.edge.models import EdgeRule
    except Exception:
        return {}
    out = {}
    for r in EdgeRule.objects.select_related("prop_market").all():
        mkt = getattr(r.prop_market, "key", None)
        if mkt:
            out[f"{r.venue}:{mkt}:{r.league_level}"] = r.enabled
    return out
