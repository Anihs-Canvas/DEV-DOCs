"""Pure tests for prop settlement (apps.props.settle). No Django/DB."""

from dataclasses import dataclass

import pytest

from apps.props import settle


@dataclass
class Box:
    pts: int = 0
    reb: int = 0
    ast: int = 0
    tpm: int = 0
    blk: int = 0
    stl: int = 0
    tov: int = 0
    fgm: int = 0
    ftm: int = 0
    minutes: float = 30.0
    dnp: bool = False


def test_derived_combos():
    b = Box(pts=20, reb=8, ast=6)
    assert settle.stat_value("pra", b) == 34
    assert settle.stat_value("pr", b) == 28
    assert settle.stat_value("ra", b) == 14


def test_over_under_and_push():
    b = Box(pts=26)
    assert settle.grade("points", "OVER", 24.5, b) == settle.WIN
    assert settle.grade("points", "UNDER", 24.5, b) == settle.LOSE
    assert settle.grade("points", "OVER", 26.0, b) == settle.PUSH  # exact integer hit


def test_dnp_and_zero_minutes_void():
    assert settle.grade("points", "OVER", 24.5, Box(pts=0, dnp=True)) == settle.VOID
    assert settle.grade("points", "OVER", 24.5, Box(pts=0, minutes=0.0)) == settle.VOID


def test_porter_rule_voids_two_way_unders():
    b = Box(pts=10, minutes=20)
    assert settle.grade("points", "UNDER", 24.5, b, is_two_way=True) == settle.VOID
    # the OVER side is still graded normally
    assert settle.grade("points", "OVER", 24.5, b, is_two_way=True) == settle.LOSE


def test_double_double_yes_no():
    dd = Box(pts=12, reb=11, ast=4)
    assert settle.grade("double_double", "YES", 0.5, dd) == settle.WIN
    assert settle.grade("double_double", "NO", 0.5, dd) == settle.LOSE
    single = Box(pts=12, reb=4)
    assert settle.grade("double_double", "YES", 0.5, single) == settle.LOSE


def test_threes_uses_tpm_column():
    assert settle.grade("threes", "OVER", 2.5, Box(tpm=3)) == settle.WIN


def test_pnl_per_unit():
    assert settle.pnl_per_unit(settle.WIN, 1.90) == pytest.approx(0.90)
    assert settle.pnl_per_unit(settle.LOSE, 1.90) == -1.0
    assert settle.pnl_per_unit(settle.VOID, 1.90) == 0.0
    assert settle.pnl_per_unit(settle.PUSH, 1.90) == 0.0
