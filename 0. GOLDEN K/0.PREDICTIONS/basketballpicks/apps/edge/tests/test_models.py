"""ORM tests for the edge publisher + the publish_edges flow (apps.edge). Django/DB
— runs post-integration (needs the assembled project + migrations)."""

import datetime as dt

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _slate_with_edge():
    """A stale DFS line vs a tight soft consensus → a real +EV DFS leg."""
    from apps.core.models import Game, League, Player, Season, Team
    from apps.odds.models import Bookmaker
    from apps.props.models import PropLine, PropMarket

    lg = League.objects.create(code="NBA", name="NBA", level="pro")
    season = Season.objects.create(league=lg, name="2025-26")
    home = Team.objects.create(canonical_name="Denver", abbreviation="DEN", league=lg)
    away = Team.objects.create(canonical_name="Lakers", abbreviation="LAL", league=lg)
    game = Game.objects.create(season=season, home_team=home, away_team=away,
                               tipoff_utc=timezone.now() + dt.timedelta(hours=2),
                               source="nba_api", external_id="G1")
    player = Player.objects.create(canonical_name="Nikola Jokic", current_team=home)
    market = PropMarket.objects.create(key="points", label="Points",
                                       settle_expr="pts", stat_family="continuous")
    dk = Bookmaker.objects.create(name="draftkings", in_soft_consensus=True)
    fd = Bookmaker.objects.create(name="fanduel", in_soft_consensus=True)
    bov = Bookmaker.objects.create(name="bovada", in_soft_consensus=True)
    ud = Bookmaker.objects.create(name="underdog", is_dfs=True, limits_winners=False)
    now = timezone.now()
    # tight soft consensus around ~24.5 (fair over ≈ 0.5)
    for bk, ov, un in ((dk, 1.90, 1.95), (fd, 1.90, 1.92), (bov, 1.88, 1.96)):
        PropLine.objects.create(game=game, player=player, market=market, bookmaker=bk,
                                line=24.5, over_price=ov, under_price=un,
                                captured_at=now, source="t")
    # a STALE DFS over line 2 points lower (within the 2-unit reprice cap) → the
    # repriced p_over (~0.59) clears the 3-pick breakeven+margin → a real +EV leg.
    PropLine.objects.create(game=game, player=player, market=market, bookmaker=ud,
                            line=22.5, payout_mult=6.0, dfs_odds_type="standard",
                            captured_at=now, source="underdog")
    return game


def test_publish_edges_flags_stale_dfs_line():
    from apps.edge.models import EdgePick
    from apps.edge.services import publish_edges

    game = _slate_with_edge()
    counters = publish_edges(game)
    assert counters["scanned"] >= 4
    # the DFS over should publish; contamination tier 1 (consensus vs DFS), not rejected
    dfs_picks = EdgePick.objects.filter(venue="DFS")
    assert dfs_picks.exists()
    p = dfs_picks.first()
    assert p.side == "OVER" and p.contamination_tier == 1 and p.anchor == "consensus"
    assert float(p.edge) > 0


def test_publish_edges_empty_runs_clean():
    from apps.core.models import Game, League, Season, Team
    from apps.edge.services import publish_edges

    lg = League.objects.create(code="NBA", name="NBA", level="pro")
    season = Season.objects.create(league=lg, name="2025-26")
    h = Team.objects.create(canonical_name="A", abbreviation="A", league=lg)
    a = Team.objects.create(canonical_name="B", abbreviation="B", league=lg)
    game = Game.objects.create(season=season, home_team=h, away_team=a,
                               tipoff_utc=timezone.now(), source="s", external_id="E")
    assert publish_edges(game)["scanned"] == 0


def test_edgepick_carries_contamination_audit_trail():
    from apps.edge.models import EdgePick
    from apps.edge.services import publish_edges

    game = _slate_with_edge()
    publish_edges(game)
    p = EdgePick.objects.filter(venue="DFS").first()
    assert "contamination" in p.audit and "breakeven" in p.audit
