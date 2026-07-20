"""API v1 contract tests [bball-01 §1]. Read-only surface; the CLV-gate and
edge endpoints degrade to a clean empty/designed state before data accrues."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.core.models import Game, League, Player, Season, Team
from apps.predictions.models import ModelVersion, Prediction, PropPrediction

pytestmark = pytest.mark.django_db


def _game(status=Game.STATUS_SCHEDULED, tip=None):
    league = League.objects.create(code="NBA", name="NBA", level="pro")
    season = Season.objects.create(league=league, name="2025-26")
    home = Team.objects.create(canonical_name="Boston", abbreviation="BOS", league=league)
    away = Team.objects.create(canonical_name="LA", abbreviation="LAL", league=league)
    game = Game.objects.create(
        season=season, home_team=home, away_team=away,
        tipoff_utc=tip or timezone.now(), status=status,
        source="nba_api", external_id="api-1",
    )
    return game, home


def test_predictions_today_empty(client):
    resp = client.get(reverse("api:predictions-today"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["n_games"] == 0
    assert body["team_predictions"] == [] and body["prop_predictions"] == []


def test_predictions_today_with_rows(client):
    game, home = _game()
    mv = ModelVersion.objects.create(name="core-v1", algo="ridge_gaussian", is_active=True)
    Prediction.objects.create(
        game=game, model_version=mv, market=Prediction.MARKET_CORE,
        prob_vector={"ML": {"HOME": 0.62, "AWAY": 0.38}, "TOTAL": {"line": 224.5, "OVER": 0.51}},
    )
    player = Player.objects.create(canonical_name="Jayson Tatum", current_team=home)
    PropPrediction.objects.create(
        game=game, player=player, market_key="points", model_version=mv,
        proj_minutes=Decimal("34.5"), mean=Decimal("27.500"), dist="normal",
        calibration_gate=True,
    )
    resp = client.get(reverse("api:predictions-today"))
    body = resp.json()
    assert body["n_games"] == 1
    assert body["team_predictions"][0]["market"] == "CORE"
    assert body["team_predictions"][0]["fixture"] == "LAL @ BOS"
    assert body["prop_predictions"][0]["market_key"] == "points"
    assert body["prop_predictions"][0]["calibration_gate"] is True


def test_clv_gate_empty_is_clean(client):
    resp = client.get(reverse("api:clv-gate"), {"days": 30})
    assert resp.status_code == 200
    body = resp.json()
    assert body["n_flagged"] == 0
    assert body["overall"]["verdict"] == "HOLD"
    # frozen pre-registered thresholds are echoed for auditability
    assert body["thresholds"]["confirm_min_n"] == 500
    assert body["thresholds"]["confirm_min_sharp_beat"] == 0.02
    assert body["thresholds"]["all_cells_start_disabled"] is True
    assert "picks" not in body  # payload kept compact


def test_edge_today_designed_state(client):
    resp = client.get(reverse("api:edge-today"))
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 0  # empty whether or not the edge app is migrated


def test_edge_cells_ok(client):
    resp = client.get(reverse("api:edge-cells"))
    assert resp.status_code == 200
    assert "cells" in resp.json()


def test_game_prediction_and_props(client):
    game, home = _game()
    resp = client.get(reverse("api:game-prediction", args=[game.id]))
    assert resp.status_code == 200
    assert resp.json()["prediction"] is None  # none yet
    resp2 = client.get(reverse("api:game-props", args=[game.id]))
    assert resp2.status_code == 200
    assert resp2.json()["prop_predictions"] == []
