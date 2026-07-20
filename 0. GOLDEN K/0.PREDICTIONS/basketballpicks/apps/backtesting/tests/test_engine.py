"""Pure grading-kernel tests [bball-05 §3b/§3c] — no DB, no models. Uses a
duck-typed box so it validates the settlement vocabulary in isolation."""

from types import SimpleNamespace

import pytest

from apps.backtesting import engine


def _box(**kw):
    base = dict(pts=0, reb=0, ast=0, stl=0, blk=0, tov=0, tpm=0, fgm=0, ftm=0, dnp=False, minutes=30)
    base.update(kw)
    return SimpleNamespace(**base)


def test_over_under_win_lose_push():
    assert engine.grade_over_under(30, 24.5, engine.OVER) == engine.WIN
    assert engine.grade_over_under(20, 24.5, engine.OVER) == engine.LOSE
    assert engine.grade_over_under(20, 24.5, engine.UNDER) == engine.WIN
    # whole line exact hit -> PUSH; half line never pushes
    assert engine.grade_over_under(24, 24.0, engine.OVER) == engine.PUSH
    assert engine.grade_over_under(24, 24.0, engine.UNDER) == engine.PUSH


def test_market_aliases_and_combos():
    box = _box(pts=20, reb=10, ast=12, blk=1, stl=2, tpm=5)
    # uppercase bball-05 codes normalize to canonical keys
    assert engine.canon_market("PTS") == "points"
    assert engine.canon_market("PRA") == "pra"
    assert engine.canon_market("BLKSTL") == "blocks_steals"
    # PRA = 20+10+12 = 42
    assert engine.grade_prop("pra", engine.OVER, box, 41.5) == engine.WIN
    assert engine.grade_prop("PRA", engine.UNDER, box, 41.5) == engine.LOSE
    # blocks_steals = 3
    assert engine.grade_prop("blocks_steals", engine.OVER, box, 2.5) == engine.WIN


def test_double_and_triple_double():
    # pts/reb/ast all >= 10 -> triple-double
    td = _box(pts=25, reb=11, ast=10, blk=1, stl=2)
    assert engine.grade_prop("double_double", engine.YES, td, 0.5) == engine.WIN
    assert engine.grade_prop("triple_double", engine.YES, td, 0.5) == engine.WIN
    assert engine.grade_prop("triple_double", engine.NO, td, 0.5) == engine.LOSE
    # only two categories -> DD yes, TD no
    dd = _box(pts=25, reb=11, ast=4)
    assert engine.grade_prop("double_double", engine.YES, dd, 0.5) == engine.WIN
    assert engine.grade_prop("triple_double", engine.YES, dd, 0.5) == engine.LOSE


def test_first_basket_needs_pbp_flag():
    box = _box(pts=10)
    # no first_basket attribute -> not gradable from the box alone
    assert engine.grade_prop("first_basket", engine.YES, box, 0.5) is None
    box.first_basket = True
    assert engine.grade_prop("first_basket", engine.YES, box, 0.5) == engine.WIN


def test_team_markets():
    # ML never pushes (no ties)
    assert engine.grade_team("ML", engine.HOME, 110, 105, None) == engine.WIN
    assert engine.grade_team("ML", engine.AWAY, 110, 105, None) == engine.LOSE
    # SPREAD: HOME -4.5 with a 5-point win covers; push on exact
    assert engine.grade_team("SPREAD", engine.HOME, 110, 105, -4.5) == engine.WIN
    assert engine.grade_team("SPREAD", engine.HOME, 110, 105, -6.5) == engine.LOSE
    assert engine.grade_team("SPREAD", engine.HOME, 110, 105, -5.0) == engine.PUSH
    # TOTAL over/under incl. OT (full-game score)
    assert engine.grade_team("TOTAL", engine.OVER, 110, 105, 214.5) == engine.WIN
    assert engine.grade_team("TOTAL", engine.UNDER, 110, 105, 220.5) == engine.WIN


def test_pnl_per_unit():
    assert engine.pnl_per_unit(engine.WIN, 1.90) == pytest.approx(0.90)
    assert engine.pnl_per_unit(engine.LOSE, 1.90) == -1.0
    assert engine.pnl_per_unit(engine.PUSH, 1.90) == 0.0
    assert engine.pnl_per_unit(engine.VOID, 1.90) == 0.0
