"""REST API v1 [bball-01 §1] — a MINIMAL read surface over the three product
objects: model predictions, published edge picks, and the forward-CLV gate
state. AllowAny + read-only (local paper product; the DRF default throttles
still apply). Nothing here writes — PAPER-ONLY by construction.

Endpoints:
    GET /api/v1/predictions/today[?date=YYYY-MM-DD]   team + prop model rows
    GET /api/v1/edge/today                            open published EdgePicks
    GET /api/v1/edge/cells                            EdgeRule grid (+ enabled)
    GET /api/v1/clv/gate[?days=90]                    the forward-CLV verdict grid
    GET /api/v1/games/<id>/prediction                 one game's team prediction
    GET /api/v1/games/<id>/props                      one game's prop board
"""

from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api import serializers as ser
from apps.core.models import Game
from apps.predictions.models import Prediction, PropPrediction


def _parse_date(request):
    raw = request.query_params.get("date")
    if raw:
        from datetime import date

        return date.fromisoformat(raw)
    return timezone.now().date()


@api_view(["GET"])
@permission_classes([AllowAny])
def predictions_today(request):
    """Team CORE predictions + player-prop projections for games tipping on
    `date` (default today). Zero rows is a designed state, not an error."""
    day = _parse_date(request)
    games = Game.objects.filter(tipoff_utc__date=day)
    team = (
        Prediction.objects.filter(game__in=games, market=Prediction.MARKET_CORE)
        .select_related("game__season__league", "game__home_team", "game__away_team", "model_version")
        .order_by("game__tipoff_utc")
    )
    props = (
        PropPrediction.objects.filter(game__in=games)
        .select_related("player", "model_version")
        .order_by("game__tipoff_utc", "player__canonical_name", "market_key")
    )
    return Response(
        {
            "date": day.isoformat(),
            "n_games": games.count(),
            "team_predictions": ser.PredictionSerializer(team, many=True).data,
            "prop_predictions": ser.PropPredictionSerializer(props, many=True).data,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def edge_today(request):
    """Currently OPEN published edge picks (the +EV line-shop product)."""
    EdgePick = _edge_pick()
    if EdgePick is None:
        return Response({"count": 0, "picks": [], "detail": "edge app not migrated yet"})
    picks = (
        EdgePick.objects.filter(status="OPEN")
        .select_related(
            "prop_line__game__season__league",
            "prop_line__game__home_team",
            "prop_line__game__away_team",
            "prop_line__player",
            "prop_line__bookmaker",
            "odds_snapshot__game__season__league",
            "odds_snapshot__game__home_team",
            "odds_snapshot__game__away_team",
            "odds_snapshot__bookmaker",
        )
        .order_by("expires_at")
    )
    data = ser.EdgePickSerializer(picks, many=True).data
    return Response(
        {
            "at": timezone.now().isoformat(),
            "count": len(data),
            "paper_only": True,
            "picks": data,
            "zero_picks_designed_state": not data,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def edge_cells(request):
    """The EdgeRule (venue x market x league) grid + its enabled flag. Every
    cell starts DISABLED and earns ON only via the forward-CLV gate."""
    rows = _edge_rules()
    return Response({"count": len(rows), "cells": rows})


@api_view(["GET"])
@permission_classes([AllowAny])
def clv_gate(request):
    """The FORWARD-CLV gate state (bball-05 §4): per-cell three-flavor CLV +
    seeded-bootstrap CI + pre-registered CONFIRM/KILL/HOLD verdict, joined to
    each cell's live EdgeRule.enabled flag. `days` = trailing window (default
    90). Forward-only: empty until open->closing pairs accrue."""
    from apps.backtesting import prop_clv

    try:
        days = max(1, int(request.query_params.get("days", "90")))
    except ValueError:
        days = 90
    today = timezone.now().date()
    report = prop_clv.compute_prop_clv(today - timedelta(days=days), today)
    enabled = _enabled_by_cell()
    for cell_key, summ in report["by_cell"].items():
        summ["edge_rule_enabled"] = enabled.get(cell_key)
    report.pop("picks", None)  # keep the API payload compact
    return Response(report)


@api_view(["GET"])
@permission_classes([AllowAny])
def game_prediction(request, game_id: int):
    game = get_object_or_404(Game.objects.select_related("season__league"), pk=game_id)
    pred = (
        Prediction.objects.filter(game=game, market=Prediction.MARKET_CORE)
        .select_related("game__home_team", "game__away_team", "model_version")
        .first()
    )
    return Response(
        {
            "game_id": game.id,
            "status": game.status,
            "tipoff_utc": game.tipoff_utc,
            "prediction": ser.PredictionSerializer(pred).data if pred else None,
        }
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def game_props(request, game_id: int):
    """One game's prop board: model projections + book lines + the devigged
    consensus fair, optionally ?market= filtered."""
    game = get_object_or_404(Game, pk=game_id)
    market = request.query_params.get("market")

    props = PropPrediction.objects.filter(game=game).select_related("player", "model_version")
    if market:
        props = props.filter(market_key=market)

    lines_data, cons_data = [], []
    PropLine, PropConsensus = _prop_models()
    if PropLine is not None:
        lines = PropLine.objects.filter(game=game).select_related(
            "bookmaker", "market", "player"
        )
        if market:
            lines = lines.filter(market__key=market)
        lines_data = ser.PropLineSerializer(lines.order_by("player__canonical_name"), many=True).data
    if PropConsensus is not None:
        cons = PropConsensus.objects.filter(game=game).select_related("market", "player")
        if market:
            cons = cons.filter(market__key=market)
        cons_data = ser.PropConsensusSerializer(cons, many=True).data

    return Response(
        {
            "game_id": game.id,
            "market": market,
            "prop_predictions": ser.PropPredictionSerializer(props, many=True).data,
            "lines": lines_data,
            "consensus": cons_data,
        }
    )


# ---------------------------------------------------------------------------
# defensive model loaders (parallel build: edge/props may migrate after this)
# ---------------------------------------------------------------------------


def _edge_pick():
    try:
        from apps.edge.models import EdgePick

        return EdgePick
    except Exception:  # app not migrated / model not defined yet
        return None


def _prop_models():
    try:
        from apps.props.models import PropConsensus, PropLine

        return PropLine, PropConsensus
    except Exception:
        return None, None


def _edge_rules():
    try:
        from apps.edge.models import EdgeRule
    except Exception:
        return []
    out = []
    for r in EdgeRule.objects.all().order_by("cell"):
        out.append(
            {
                "cell": r.cell,
                "venue": r.venue,
                "market": getattr(r.prop_market, "key", None),
                "league_level": r.league_level,
                "min_edge": r.min_edge,
                "enabled": r.enabled,
            }
        )
    return out


def _enabled_by_cell():
    """Map the prop_clv cell key 'VENUE:market:LEAGUE' -> EdgeRule.enabled."""
    try:
        from apps.edge.models import EdgeRule
    except Exception:
        return {}
    mapping = {}
    for r in EdgeRule.objects.select_related("prop_market").all():
        mkt = getattr(r.prop_market, "key", None)
        if mkt is None:
            continue
        mapping[f"{r.venue}:{mkt}:{r.league_level}"] = r.enabled
    return mapping
