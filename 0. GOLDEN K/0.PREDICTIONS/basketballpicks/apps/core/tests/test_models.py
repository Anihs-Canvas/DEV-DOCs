"""Contract tests for the canonical core models [bball-01 §2].

These exercise the shared models every other agent imports. They need the
ASSEMBLED project (all 12 apps present so `config.settings` imports) plus
migrations — run with `pytest` (pytest-django) once the orchestrator has run
`makemigrations`. Kept pure-ORM so they touch no network and no live source.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.core.models import (
    Game,
    League,
    Player,
    PlayerBoxScore,
    Season,
    Team,
    TeamBoxScore,
)

pytestmark = pytest.mark.django_db


def _league() -> League:
    return League.objects.create(code="NBA", name="National Basketball Association", level="pro")


def _team(league: League, name: str, abbr: str, home=True) -> Team:
    return Team.objects.create(
        canonical_name=name, abbreviation=abbr, league=league, conference="East"
    )


def _game(season: Season, home: Team, away: Team) -> Game:
    return Game.objects.create(
        season=season,
        home_team=home,
        away_team=away,
        tipoff_utc=timezone.now(),
        status=Game.STATUS_SCHEDULED,
        source="nba_api",
        external_id="0022500001",
    )


def test_reference_chain_and_str():
    league = _league()
    season = Season.objects.create(league=league, name="2025-26")
    home = _team(league, "Boston Celtics", "BOS")
    away = _team(league, "Los Angeles Lakers", "LAL", home=False)
    game = _game(season, home, away)

    assert str(league) == "National Basketball Association (NBA)"
    assert str(season) == "NBA 2025-26"
    assert str(home) == "Boston Celtics"
    assert "LAL @ BOS" in str(game)


def test_game_source_unique():
    league = _league()
    season = Season.objects.create(league=league, name="2025-26")
    home = _team(league, "Boston Celtics", "BOS")
    away = _team(league, "Los Angeles Lakers", "LAL")
    _game(season, home, away)
    with pytest.raises(IntegrityError):
        # same (source, external_id) must collide
        Game.objects.create(
            season=season,
            home_team=home,
            away_team=away,
            tipoff_utc=timezone.now(),
            source="nba_api",
            external_id="0022500001",
        )


def test_team_name_unique_per_league():
    league = _league()
    _team(league, "Boston Celtics", "BOS")
    with pytest.raises(IntegrityError):
        _team(league, "Boston Celtics", "BOS2")


def test_player_first_class_and_boxscore_grain():
    league = _league()
    season = Season.objects.create(league=league, name="2025-26")
    home = _team(league, "Boston Celtics", "BOS")
    away = _team(league, "Los Angeles Lakers", "LAL")
    game = _game(season, home, away)

    player = Player.objects.create(
        canonical_name="Jayson Tatum",
        current_team=home,
        primary_position="F",
        birthdate=date(1998, 3, 3),
        source_ids={"nba_api": 1628369},
    )
    assert player.status == Player.STATUS_ACTIVE

    box = PlayerBoxScore.objects.create(
        game=game,
        player=player,
        team=home,
        started=True,
        minutes=Decimal("34.50"),
        pts=30,
        reb=8,
        ast=5,
        tpm=4,
        usage_rate=Decimal("29.30"),
    )
    # minutes is the master driver; combos are derived, never stored
    assert box.minutes == Decimal("34.50")
    assert box.pts + box.reb + box.ast == 43  # PRA derived at settle time

    # (game, player) is unique
    with pytest.raises(IntegrityError):
        PlayerBoxScore.objects.create(
            game=game, player=player, team=home, minutes=Decimal("0.00"), dnp=True
        )


def test_team_boxscore_unique_and_minutes():
    league = _league()
    season = Season.objects.create(league=league, name="2025-26")
    home = _team(league, "Boston Celtics", "BOS")
    away = _team(league, "Los Angeles Lakers", "LAL")
    game = _game(season, home, away)

    tbs = TeamBoxScore.objects.create(
        game=game, team=home, is_home=True, pts=112, reb=44, ast=26, minutes=Decimal("240.0")
    )
    assert tbs.minutes == Decimal("240.0")
    with pytest.raises(IntegrityError):
        TeamBoxScore.objects.create(
            game=game, team=home, is_home=True, minutes=Decimal("240.0")
        )
