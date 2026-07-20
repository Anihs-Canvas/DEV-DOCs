"""FORWARD-CLV gate tests [bball-05 §4].

The core flag/measure/verdict logic is tested PURELY (no DB, no props/edge
models) via the module internals, so it validates the honesty math in isolation
and runs even mid-parallel-build. A guarded end-to-end `compute_prop_clv`
smoke test runs once the props app is migrated.
"""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from apps.backtesting import engine, prop_clv
from apps.backtesting.prop_clv import _BookPair


def _game(gid=1):
    return SimpleNamespace(id=gid, tipoff_utc=datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc))


def _box(pts=30, **kw):
    b = SimpleNamespace(
        pts=pts, reb=0, ast=0, stl=0, blk=0, tov=0, tpm=0, fgm=0, ftm=0,
        dnp=False, minutes=30,
    )
    b._player_status = kw.get("status", "active")
    for k, v in kw.items():
        setattr(b, k, v)
    return b


# ---------------------------------------------------------------------------
# line-normalization (the #1 correctness hazard)
# ---------------------------------------------------------------------------


def test_fair_at_line_exact_and_side():
    ladder = {24.5: (0.60, "pinnacle")}
    p, anc = prop_clv._fair_at_line(ladder, 24.5, engine.OVER)
    assert p == 0.60 and anc == "pinnacle"
    p_u, _ = prop_clv._fair_at_line(ladder, 24.5, engine.UNDER)
    assert abs(p_u - 0.40) < 1e-9


def test_fair_at_line_interpolates():
    ladder = {24.5: (0.60, "a"), 25.5: (0.50, "b")}
    p, _ = prop_clv._fair_at_line(ladder, 25.0, engine.OVER)
    assert abs(p - 0.55) < 1e-9  # linear midpoint


def test_fair_at_line_no_bracket_skips():
    ladder = {24.5: (0.60, "a"), 25.5: (0.50, "b")}
    # a line outside the ladder cannot be honestly normalized -> None
    assert prop_clv._fair_at_line(ladder, 26.5, engine.OVER) == (None, None)


# ---------------------------------------------------------------------------
# soft-book flag + three CLV flavors + realized ROI
# ---------------------------------------------------------------------------


def test_softbook_flag_measures_three_clv_and_roi():
    pair = _BookPair(
        book="draftkings", is_dfs=False, open_line=24.5, close_line=24.5,
        open_over=1.90, open_under=1.95, close_over=1.80, close_under=2.05,
        payout_mult=None,
    )
    open_ladder = {24.5: (0.58, "consensus")}
    close_ladder = {24.5: (0.60, "consensus")}
    pick = prop_clv._measure_side(
        pair, engine.OVER, open_ladder, close_ladder, "NBA", "points", _game(),
        lambda: _box(pts=30),
    )
    assert pick is not None
    assert pick.venue == "SOFTBOOK"
    assert abs(pick.flag_edge - (1.90 * 0.58 - 1)) < 1e-4       # +EV vs open fair
    assert abs(pick.price_clv - (1.90 / 1.80 - 1)) < 1e-4        # (1) same-book price CLV
    assert pick.line_move_clv == 0.0                             # (2) line held
    assert abs(pick.sharp_beat_clv - (0.60 * 1.90 - 1)) < 1e-4   # (3) *** verdict metric ***
    assert pick.settled and pick.outcome == engine.WIN
    assert abs(pick.pnl - 0.90) < 1e-9                           # ROI at the taken price


def test_softbook_below_flag_min_not_flagged():
    pair = _BookPair(
        book="fanduel", is_dfs=False, open_line=24.5, close_line=24.5,
        open_over=1.50, open_under=2.60, close_over=1.50, close_under=2.60,
        payout_mult=None,
    )
    # 1.50 * 0.58 - 1 = -0.13 < FLAG_EDGE_MIN -> not in the pre-registered universe
    pick = prop_clv._measure_side(
        pair, engine.OVER, {24.5: (0.58, "consensus")}, {24.5: (0.60, "consensus")},
        "NBA", "points", _game(), lambda: None,
    )
    assert pick is None


# ---------------------------------------------------------------------------
# DFS: price-less, line-move is the honest measure; sharp-beat uses payout_mult
# ---------------------------------------------------------------------------


def test_dfs_flag_line_move_and_payout_sharp_beat():
    pair = _BookPair(
        book="underdog", is_dfs=True, open_line=24.5, close_line=25.5,
        open_over=None, open_under=None, close_over=None, close_under=None,
        payout_mult=1.90,
    )
    pick = prop_clv._measure_side(
        pair, engine.OVER, {24.5: (0.58, "consensus")}, {24.5: (0.61, "consensus")},
        "NBA", "points", _game(), lambda: None,
    )
    assert pick is not None and pick.venue == "DFS"
    assert abs(pick.flag_edge - (0.58 - prop_clv.BREAKEVEN_DFS)) < 1e-9  # line-disagreement
    assert pick.price_clv is None                                        # no same-book price
    assert pick.line_move_clv == pytest.approx(1.0)                      # line came UP toward OVER
    assert abs(pick.dfs_line_edge - 0.08) < 1e-9
    assert abs(pick.sharp_beat_clv - (0.61 * 1.90 - 1)) < 1e-4           # real payout, not fabricated


def test_dfs_without_payout_has_no_sharp_beat():
    pair = _BookPair(
        book="prizepicks", is_dfs=True, open_line=24.5, close_line=23.5,
        open_over=None, open_under=None, close_over=None, close_under=None,
        payout_mult=None,
    )
    pick = prop_clv._measure_side(
        pair, engine.UNDER, {24.5: (0.58, "consensus")}, {24.5: (0.61, "consensus")},
        "NBA", "points", _game(), lambda: None,
    )
    # UNDER flag: p_fair(UNDER)=0.42 -> 0.42-0.5=-0.08 < min -> not flagged
    assert pick is None


def test_void_settlement_does_not_inflate_roi():
    pair = _BookPair(
        book="draftkings", is_dfs=False, open_line=24.5, close_line=24.5,
        open_over=1.90, open_under=1.95, close_over=1.90, close_under=1.95,
        payout_mult=None,
    )
    # DNP -> VOID; counts as a flagged pick but pnl is 0 (never a win credit)
    pick = prop_clv._measure_side(
        pair, engine.OVER, {24.5: (0.58, "consensus")}, {24.5: (0.60, "consensus")},
        "NBA", "points", _game(), lambda: _box(pts=0, dnp=True, minutes=0),
    )
    assert pick.outcome == engine.VOID and pick.pnl == 0.0


# ---------------------------------------------------------------------------
# pre-registered verdict thresholds (frozen)
# ---------------------------------------------------------------------------


def _summary(**kw):
    base = dict(
        n=0, n_sharp_beat=0, sharp_beat_mean=None, sharp_beat_ci_lo=None,
        sharp_beat_ci_hi=None, roi_ci_lo=None, roi_ci_hi=None, n_settled=0, weeks=0,
    )
    base.update(kw)
    return base


def test_verdict_confirm():
    s = _summary(
        n=600, n_sharp_beat=600, sharp_beat_mean=0.03, sharp_beat_ci_lo=0.012,
        sharp_beat_ci_hi=0.05, weeks=10, n_settled=600, roi_ci_lo=0.0, roi_ci_hi=0.09,
    )
    assert prop_clv._verdict(s) == prop_clv.VERDICT_CONFIRM


def test_verdict_kill_on_flat_clv():
    s = _summary(
        n=400, n_sharp_beat=400, sharp_beat_mean=-0.005, sharp_beat_ci_lo=-0.02,
        sharp_beat_ci_hi=0.004, weeks=9, n_settled=400, roi_ci_lo=-0.02, roi_ci_hi=0.01,
    )
    assert prop_clv._verdict(s) == prop_clv.VERDICT_KILL


def test_verdict_kill_on_negative_roi_ci():
    s = _summary(
        n=400, n_sharp_beat=400, sharp_beat_mean=0.03, sharp_beat_ci_lo=0.01,
        sharp_beat_ci_hi=0.05, weeks=9, n_settled=400, roi_ci_lo=-0.05, roi_ci_hi=-0.01,
    )
    assert prop_clv._verdict(s) == prop_clv.VERDICT_KILL


def test_verdict_hold_when_thin():
    s = _summary(
        n=50, n_sharp_beat=50, sharp_beat_mean=0.03, sharp_beat_ci_lo=0.01,
        sharp_beat_ci_hi=0.05, weeks=3, n_settled=50, roi_ci_lo=0.0, roi_ci_hi=0.09,
    )
    assert prop_clv._verdict(s) == prop_clv.VERDICT_HOLD


def test_confirm_blocked_without_settled_roi_evidence():
    # sharp-beat clears but ROI CI is unknown (no settled picks) -> HOLD, not CONFIRM
    s = _summary(
        n=600, n_sharp_beat=600, sharp_beat_mean=0.03, sharp_beat_ci_lo=0.012,
        sharp_beat_ci_hi=0.05, weeks=10, n_settled=0, roi_ci_lo=None, roi_ci_hi=None,
    )
    assert prop_clv._verdict(s) == prop_clv.VERDICT_HOLD


# ---------------------------------------------------------------------------
# guarded end-to-end smoke test (runs once props app is migrated)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_compute_prop_clv_end_to_end():
    props = pytest.importorskip("apps.props.models")
    PropMarket = getattr(props, "PropMarket", None)
    PropLine = getattr(props, "PropLine", None)
    PropConsensus = getattr(props, "PropConsensus", None)
    if not all((PropMarket, PropLine, PropConsensus)):
        pytest.skip("props models not defined yet (parallel build)")

    from datetime import date, timedelta
    from decimal import Decimal

    from django.utils import timezone as dj_tz

    from apps.core.models import (
        Game, League, Player, PlayerBoxScore, Season, Team,
    )
    from apps.odds.models import Bookmaker

    league = League.objects.create(code="NBA", name="NBA", level="pro")
    season = Season.objects.create(league=league, name="2025-26")
    home = Team.objects.create(canonical_name="Boston", abbreviation="BOS", league=league)
    away = Team.objects.create(canonical_name="LA", abbreviation="LAL", league=league)
    tip = dj_tz.now().replace(hour=23, minute=0, second=0, microsecond=0)
    game = Game.objects.create(
        season=season, home_team=home, away_team=away, tipoff_utc=tip,
        status=Game.STATUS_FINAL, home_score=112, away_score=108,
        source="nba_api", external_id="clv-smoke-1",
    )
    player = Player.objects.create(canonical_name="Jayson Tatum", current_team=home)
    PlayerBoxScore.objects.create(
        game=game, player=player, team=home, started=True, minutes=Decimal("34.5"),
        pts=30, reb=8, ast=5, tpm=4,
    )
    market = PropMarket.objects.create(key="points", label="Points", settle_expr="pts")
    dk = Bookmaker.objects.create(name="draftkings", in_soft_consensus=True)

    t_open = tip - timedelta(hours=6)
    t_close = tip - timedelta(minutes=5)
    PropLine.objects.create(
        game=game, player=player, market=market, bookmaker=dk, line=Decimal("24.5"),
        over_price=Decimal("1.90"), under_price=Decimal("1.95"), is_closing=False,
        captured_at=t_open, source="the_odds_api",
    )
    PropLine.objects.create(
        game=game, player=player, market=market, bookmaker=dk, line=Decimal("24.5"),
        over_price=Decimal("1.80"), under_price=Decimal("2.05"), is_closing=True,
        captured_at=t_close, source="the_odds_api",
    )
    PropConsensus.objects.create(
        game=game, player=player, market=market, line=Decimal("24.5"),
        fair_prob_over=Decimal("0.58000"), anchor="consensus", is_closing=False,
        captured_at=t_open,
    )
    PropConsensus.objects.create(
        game=game, player=player, market=market, line=Decimal("24.5"),
        fair_prob_over=Decimal("0.60000"), anchor="consensus", is_closing=True,
        captured_at=t_close,
    )

    today = date.today()
    report = prop_clv.compute_prop_clv(today - timedelta(days=2), today + timedelta(days=2))
    assert report["n_flagged"] >= 1
    over_cell = report["by_cell"]["SOFTBOOK:points:NBA"]
    assert over_cell["n"] >= 1
    assert over_cell["sharp_beat_mean"] is not None
