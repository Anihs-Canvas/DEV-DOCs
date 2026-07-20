"""Settlement VOID-policy tests [bball-05 §3d].

`grade_pick` is the pure policy kernel (DNP/0-min/two-way/postponed VOID ->
engine grade). It is exercised here against REAL core box scores with
duck-typed pick/prop_line objects, so the load-bearing VOID rules are validated
without depending on apps.edge's not-yet-built EdgePick shape. A guarded
end-to-end `settle_edge_picks` smoke test runs once edge+props are migrated.
"""

from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.utils import timezone

from apps.backtesting import engine, settlement
from apps.core.models import Game, League, Player, PlayerBoxScore, Season, Team

pytestmark = pytest.mark.django_db


def _final_game(status=Game.STATUS_FINAL, tip=None):
    league = League.objects.create(code="NBA", name="NBA", level="pro")
    season = Season.objects.create(league=league, name="2025-26")
    home = Team.objects.create(canonical_name="Boston", abbreviation="BOS", league=league)
    away = Team.objects.create(canonical_name="LA", abbreviation="LAL", league=league)
    game = Game.objects.create(
        season=season, home_team=home, away_team=away,
        tipoff_utc=tip or timezone.now() - timedelta(hours=3),
        status=status, home_score=112, away_score=108,
        source="nba_api", external_id="settle-1",
    )
    player = Player.objects.create(canonical_name="Jayson Tatum", current_team=home)
    return game, player, home


def _prop_pick(game, player, side, line, market_key="points"):
    prop_line = SimpleNamespace(
        game=game, player=player, market=SimpleNamespace(key=market_key), line=line
    )
    return SimpleNamespace(
        prop_line_id=1, prop_line=prop_line, odds_snapshot_id=None, side=side, line=line
    )


def _team_pick(game, market, side, line):
    snap = SimpleNamespace(game=game, market=market)
    return SimpleNamespace(
        prop_line_id=None, odds_snapshot_id=1, odds_snapshot=snap, side=side, line=line
    )


def test_grade_prop_win_and_push():
    game, player, home = _final_game()
    PlayerBoxScore.objects.create(
        game=game, player=player, team=home, started=True, minutes=Decimal("34.5"), pts=30
    )
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 24.5)) == engine.WIN
    # whole-line exact hit -> PUSH
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 30.0)) == engine.PUSH


def test_dnp_and_zero_minutes_void():
    game, player, home = _final_game()
    PlayerBoxScore.objects.create(
        game=game, player=player, team=home, minutes=Decimal("0.00"), dnp=True, pts=0
    )
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 24.5)) == engine.VOID


def test_missing_boxscore_voids():
    game, player, home = _final_game()  # no PlayerBoxScore created
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 24.5)) == engine.VOID


def test_two_way_under_voids_but_over_grades():
    game, player, home = _final_game()
    player.status = Player.STATUS_TWO_WAY
    player.save(update_fields=["status"])
    PlayerBoxScore.objects.create(
        game=game, player=player, team=home, started=False, minutes=Decimal("18.0"), pts=8
    )
    # Porter rule: UNDER on a two-way player -> VOID
    assert settlement.grade_pick(_prop_pick(game, player, engine.UNDER, 12.5)) == engine.VOID
    # OVER is graded normally (8 < 12.5 -> LOSE)
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 12.5)) == engine.LOSE


def test_postponed_past_grace_voids_and_not_final_pending():
    tip = timezone.now() - timedelta(hours=24)
    game, player, home = _final_game(status=Game.STATUS_POSTPONED, tip=tip)
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 24.5)) == engine.VOID

    # a scheduled (not final) game is not yet gradable -> None
    game.status = Game.STATUS_SCHEDULED
    game.save(update_fields=["status"])
    assert settlement.grade_pick(_prop_pick(game, player, engine.OVER, 24.5)) is None


def test_team_total_grade():
    game, player, home = _final_game()  # 112 + 108 = 220
    assert settlement.grade_pick(_team_pick(game, "TOTAL", engine.OVER, 218.5)) == engine.WIN
    assert settlement.grade_pick(_team_pick(game, "TOTAL", engine.UNDER, 218.5)) == engine.LOSE
    assert settlement.grade_pick(_team_pick(game, "ML", engine.HOME, None)) == engine.WIN


def test_settle_edge_picks_end_to_end():
    """Guarded: exercises the idempotent, row-locked write path once the
    edge+props apps are migrated."""
    edge = pytest.importorskip("apps.edge.models")
    props = pytest.importorskip("apps.props.models")
    EdgePick = getattr(edge, "EdgePick", None)
    PropMarket = getattr(props, "PropMarket", None)
    PropLine = getattr(props, "PropLine", None)
    if not all((EdgePick, PropMarket, PropLine)):
        pytest.skip("edge/props models not defined yet (parallel build)")

    from apps.odds.models import Bookmaker

    game, player, home = _final_game()
    PlayerBoxScore.objects.create(
        game=game, player=player, team=home, started=True, minutes=Decimal("34.5"), pts=30
    )
    market = PropMarket.objects.create(key="points", label="Points", settle_expr="pts")
    dk = Bookmaker.objects.create(name="draftkings")
    line = PropLine.objects.create(
        game=game, player=player, market=market, bookmaker=dk, line=Decimal("24.5"),
        over_price=Decimal("1.90"), under_price=Decimal("1.95"), is_closing=False,
        captured_at=timezone.now() - timedelta(hours=6), source="the_odds_api",
    )
    pick = EdgePick.objects.create(
        prop_line=line, cell="SOFTBOOK:points:NBA", venue="SOFTBOOK", market_key="points",
        side=engine.OVER, line=Decimal("24.5"), sharp_fair_prob=Decimal("0.58000"),
        edge=Decimal("0.10000"), ev=Decimal("0.10000"),
        published_at=timezone.now() - timedelta(hours=6),
        expires_at=game.tipoff_utc, status="OPEN",
    )
    stats = settlement.settle_edge_picks()
    pick.refresh_from_db()
    assert pick.status == "WON"
    assert stats["settled"] == 1
    # idempotent: a second pass changes nothing
    stats2 = settlement.settle_edge_picks()
    assert stats2["settled"] == 0
