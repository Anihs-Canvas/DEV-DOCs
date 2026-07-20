"""ORM tests for props models + the consensus materialiser (apps.props). Django/DB
— runs post-integration (needs the assembled project + migrations; the props/edge
agent does not run makemigrations, bball task constraint)."""

import datetime as dt

import pytest
from django.utils import timezone

pytestmark = pytest.mark.django_db


def _slate():
    from apps.core.models import Game, League, Player, Season, Team
    from apps.odds.models import Bookmaker
    from apps.props.models import PropMarket

    lg = League.objects.create(code="NBA", name="NBA", level="pro")
    season = Season.objects.create(league=lg, name="2025-26")
    home = Team.objects.create(canonical_name="Denver Nuggets", abbreviation="DEN", league=lg)
    away = Team.objects.create(canonical_name="LA Lakers", abbreviation="LAL", league=lg)
    game = Game.objects.create(
        season=season, home_team=home, away_team=away,
        tipoff_utc=timezone.now() + dt.timedelta(hours=3),
        source="nba_api", external_id="G1",
    )
    player = Player.objects.create(canonical_name="Nikola Jokic", current_team=home)
    market = PropMarket.objects.create(key="points", label="Points", settle_expr="pts",
                                       stat_family="continuous")
    dk = Bookmaker.objects.create(name="draftkings", in_soft_consensus=True)
    fd = Bookmaker.objects.create(name="fanduel", in_soft_consensus=True)
    bov = Bookmaker.objects.create(name="bovada", in_soft_consensus=True)
    ud = Bookmaker.objects.create(name="underdog", is_dfs=True, limits_winners=False)
    return dict(game=game, player=player, market=market, dk=dk, fd=fd, bov=bov, ud=ud)


def test_prop_line_two_sided_and_dfs_rows():
    from apps.props.models import PropLine

    s = _slate()
    now = timezone.now()
    # a two-sided soft quote
    soft = PropLine.objects.create(
        game=s["game"], player=s["player"], market=s["market"], bookmaker=s["dk"],
        line=24.5, over_price=1.90, under_price=1.95, captured_at=now, source="the_odds_api",
    )
    # a DFS pick'em leg: no two-way price, payout multiplier instead
    dfs = PropLine.objects.create(
        game=s["game"], player=s["player"], market=s["market"], bookmaker=s["ud"],
        line=21.5, payout_mult=1.0, dfs_odds_type="standard", captured_at=now, source="underdog",
    )
    assert soft.over_price is not None and dfs.over_price is None
    assert soft.bookmaker.is_dfs is False and dfs.bookmaker.is_dfs is True


def test_materialise_consensus_writes_rows():
    from apps.props import consensus
    from apps.props.models import PropConsensus, PropLine

    s = _slate()
    now = timezone.now()
    for bk, ov, un in ((s["dk"], 1.90, 1.95), (s["fd"], 1.88, 1.97), (s["bov"], 1.91, 1.93)):
        PropLine.objects.create(
            game=s["game"], player=s["player"], market=s["market"], bookmaker=bk,
            line=24.5, over_price=ov, under_price=un, captured_at=now, source="test",
        )
    written = consensus.materialise_consensus(s["game"], at=now)
    assert written >= 1
    row = PropConsensus.objects.get(game=s["game"], line=24.5)
    assert row.anchor == "consensus" and row.n_books == 3
    assert 0.45 < float(row.fair_prob_over) < 0.55


def test_materialise_consensus_empty_runs_clean():
    from apps.props import consensus

    s = _slate()  # no PropLine rows
    assert consensus.materialise_consensus(s["game"]) == 0
