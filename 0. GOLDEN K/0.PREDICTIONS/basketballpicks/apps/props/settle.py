"""Prop settlement: PlayerBoxScore → W/L/PUSH/VOID (bball-05 §3).

ONE grader over the MARKET vocabulary — no per-market reimplementation. Pure
grade() is unit-tested against a box duck-type; the ORM settle helper reads
core.PlayerBoxScore. VOID policy is pre-committed (bball-05 §3d): DNP / 0-min →
VOID; the post-Jontay-Porter two-way UNDER ban → VOID; exact-line hit → PUSH.
"""

from __future__ import annotations

WIN, LOSE, PUSH, VOID = "WON", "LOST", "PUSH", "VOID"

OVER, UNDER, YES, NO = "OVER", "UNDER", "YES", "NO"

_DD_CATS = ("pts", "reb", "ast", "stl", "blk")


def stat_value(market_key: str, box) -> float | int | None:
    """Compute the settlement statistic from a PlayerBoxScore-like object. Combos
    are DERIVED here (never stored — one source of truth, bball-01 §2)."""
    g = lambda a: getattr(box, a, 0) or 0  # noqa: E731
    table = {
        "points": lambda: g("pts"),
        "rebounds": lambda: g("reb"),
        "assists": lambda: g("ast"),
        "threes": lambda: g("tpm"),  # three-pointers made (core column is tpm)
        "blocks": lambda: g("blk"),
        "steals": lambda: g("stl"),
        "turnovers": lambda: g("tov"),
        "fgm": lambda: g("fgm"),
        "ftm": lambda: g("ftm"),
        "pra": lambda: g("pts") + g("reb") + g("ast"),
        "pr": lambda: g("pts") + g("reb"),
        "pa": lambda: g("pts") + g("ast"),
        "ra": lambda: g("reb") + g("ast"),
        "blocks_steals": lambda: g("blk") + g("stl"),
        "double_double": lambda: sum(1 for c in _DD_CATS if g(c) >= 10),  # # of double-digit cats
        "triple_double": lambda: sum(1 for c in _DD_CATS if g(c) >= 10),
    }
    fn = table.get(market_key)
    return fn() if fn else None


def grade(market_key: str, side: str, line: float, box, *, is_two_way: bool = False) -> str:
    """Grade one prop selection. Returns WON|LOST|PUSH|VOID."""
    # DNP / inactive / 0 minutes → VOID (universal book rule, bball-05 §3d).
    mins = getattr(box, "minutes", None)
    if getattr(box, "dnp", False) or (mins is not None and float(mins) == 0.0):
        return VOID
    # Porter-rule: books void UNDER (often all) props on two-way / 10-day players.
    if is_two_way and side == UNDER:
        return VOID

    # YES/NO markets (double-double / triple-double)
    if market_key in ("double_double", "triple_double"):
        need = 2 if market_key == "double_double" else 3
        got = stat_value(market_key, box) >= need
        want = side == YES
        return WIN if got == want else LOSE

    stat = stat_value(market_key, box)
    if stat is None:
        return VOID
    if stat == line:  # exact hit → PUSH (only possible on whole-number lines)
        return PUSH
    over_wins = stat > line
    if side == OVER:
        return WIN if over_wins else LOSE
    if side == UNDER:
        return WIN if not over_wins else LOSE
    raise ValueError(f"unknown side: {side}")


def pnl_per_unit(outcome: str, decimal_price: float) -> float:
    """Realized P&L per unit staked at the taken price. PUSH/VOID = stake back (0);
    settlement never lets a VOID inflate ROI (bball-05 §7)."""
    if outcome == WIN:
        return decimal_price - 1.0
    if outcome == LOSE:
        return -1.0
    return 0.0  # PUSH / VOID
