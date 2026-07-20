"""Prop + team-market GRADING vocabulary — pure math, no ORM [bball-05 §3b/§3c].

One grader, no per-market reimplementation (the safepicks `engine.settle`
discipline). Every market maps a PlayerBoxScore (or a final score) to an
Over/Under/Yes-No outcome against a line:

    OVER  wins if stat >  line   |  UNDER wins if stat <  line
    PUSH (VOID, stake back) if stat == line
    half-point lines (24.5) never push; whole lines (24.0) can.

`market_key` is the stable string shared by props.PropMarket.key and
predictions.PropPrediction.market_key (points|rebounds|assists|pra|...); the
uppercase bball-05 codes (PTS/REB/...) are accepted as aliases so a settle
call never has to know which vocabulary the caller used.

This module is import-safe with no Django app loaded: it only reaches for
attributes on the box-score object it is handed. DNP / two-way / postponement
VOID *policy* lives in settlement.py (it needs the ORM row); this file is the
pure stat-vs-line kernel that policy falls through to.
"""

from __future__ import annotations

# outcome vocabulary (mirrors backtesting.engine WIN/LOSE/PUSH/VOID)
WIN = "WIN"
LOSE = "LOSE"
PUSH = "PUSH"
VOID = "VOID"

# selection vocabulary
OVER = "OVER"
UNDER = "UNDER"
YES = "YES"
NO = "NO"
HOME = "HOME"
AWAY = "AWAY"

EPS = 1e-9


# ---------------------------------------------------------------------------
# market -> statistic extractor (over/under markets)
# ---------------------------------------------------------------------------

# canonical key -> callable(box) -> int stat. `tpm` is threes-made on the box.
_STAT = {
    "points": lambda b: b.pts,
    "rebounds": lambda b: b.reb,
    "assists": lambda b: b.ast,
    "threes": lambda b: b.tpm,
    "blocks": lambda b: b.blk,
    "steals": lambda b: b.stl,
    "turnovers": lambda b: b.tov,
    "fgm": lambda b: b.fgm,
    "ftm": lambda b: b.ftm,
    "pra": lambda b: b.pts + b.reb + b.ast,
    "pr": lambda b: b.pts + b.reb,
    "pa": lambda b: b.pts + b.ast,
    "ra": lambda b: b.reb + b.ast,
    "blocks_steals": lambda b: b.blk + b.stl,
}

# yes/no (milestone) markets — count-of-categories or a PBP flag.
_YESNO = {"double_double", "triple_double", "first_basket"}

# accept the settlement-oriented uppercase vocabulary (bball-05 §1) as aliases.
_ALIAS = {
    "PTS": "points",
    "REB": "rebounds",
    "AST": "assists",
    "THREES": "threes",
    "BLK": "blocks",
    "STL": "steals",
    "TOV": "turnovers",
    "FGM": "fgm",
    "FTM": "ftm",
    "PRA": "pra",
    "PR": "pr",
    "PA": "pa",
    "RA": "ra",
    "BLKSTL": "blocks_steals",
    "BLK_STL": "blocks_steals",
    "DD": "double_double",
    "TD": "triple_double",
    "FIRST_BASKET": "first_basket",
}


def canon_market(market_key: str) -> str:
    """Normalize any accepted spelling to the canonical lower-case key."""
    if market_key in _STAT or market_key in _YESNO:
        return market_key
    if market_key in _ALIAS:
        return _ALIAS[market_key]
    upper = market_key.upper()
    if upper in _ALIAS:
        return _ALIAS[upper]
    return market_key.lower()


def is_gradable_market(market_key: str) -> bool:
    m = canon_market(market_key)
    return m in _STAT or m in _YESNO


# ---------------------------------------------------------------------------
# double / triple double + stat value
# ---------------------------------------------------------------------------


def _double_categories(box) -> int:
    """Count of the five box categories (pts/reb/ast/blk/stl) reaching >= 10."""
    return sum(1 for v in (box.pts, box.reb, box.ast, box.blk, box.stl) if v >= 10)


def stat_value(market_key: str, box):
    """The numeric statistic for an over/under market, or None if the market
    is not a stat-vs-line market (dd/td/first_basket) or is unknown."""
    fn = _STAT.get(canon_market(market_key))
    return None if fn is None else fn(box)


# ---------------------------------------------------------------------------
# settlement kernels
# ---------------------------------------------------------------------------


def grade_over_under(stat: float, line: float, side: str) -> str:
    """OVER/UNDER vs a line. Exact hit = PUSH (whole lines only; half lines
    can never equal an integer stat)."""
    if abs(stat - line) < EPS:
        return PUSH
    over_wins = stat > line
    if side == OVER:
        return WIN if over_wins else LOSE
    if side == UNDER:
        return LOSE if over_wins else WIN
    raise ValueError(f"over/under market needs OVER|UNDER, got {side!r}")


def grade_yes_no(condition: bool, side: str) -> str:
    """YES/NO milestone (double-double, triple-double, first-basket). No push."""
    if side == YES:
        return WIN if condition else LOSE
    if side == NO:
        return LOSE if condition else WIN
    raise ValueError(f"yes/no market needs YES|NO, got {side!r}")


def grade_prop(market_key: str, side: str, box, line) -> str | None:
    """Grade one player-prop selection from a PlayerBoxScore.

    Returns WIN|LOSE|PUSH, or None when the market cannot be settled from the
    box alone (unknown market, or first_basket without the PBP flag). OT is
    already inside the full-game box (bball-05 §3c). DNP/0-min/two-way VOID
    policy is applied by the caller BEFORE this kernel (bball-05 §3d)."""
    m = canon_market(market_key)
    if m == "double_double":
        return grade_yes_no(_double_categories(box) >= 2, side)
    if m == "triple_double":
        return grade_yes_no(_double_categories(box) >= 3, side)
    if m == "first_basket":
        flag = getattr(box, "first_basket", None)  # PBP-derived; absent on the base box
        return None if flag is None else grade_yes_no(bool(flag), side)
    stat = stat_value(m, box)
    if stat is None:
        return None
    return grade_over_under(float(stat), float(line), side)


def grade_team(market: str, side: str, home_score: int, away_score: int, line) -> str | None:
    """Grade a team market (ML|SPREAD|TOTAL) from the final score. OT included
    (full-game score). Basketball ML never pushes (no ties). SPREAD line is the
    selection's OWN handicap (HOME -4.5 -> line=-4.5, AWAY +4.5 -> line=+4.5)."""
    mk = market.upper()
    if mk == "ML":
        if side == HOME:
            return WIN if home_score > away_score else LOSE
        if side == AWAY:
            return WIN if away_score > home_score else LOSE
        raise ValueError(f"ML needs HOME|AWAY, got {side!r}")
    if mk == "SPREAD":
        if line is None:
            return None
        margin = (home_score - away_score) if side == HOME else (away_score - home_score)
        cover = margin + float(line)
        if abs(cover) < EPS:
            return PUSH
        return WIN if cover > 0 else LOSE
    if mk == "TOTAL":
        if line is None:
            return None
        return grade_over_under(home_score + away_score, float(line), side)
    return None


def pnl_per_unit(outcome: str, taken_odds: float) -> float:
    """P&L per unit staked: WIN pays odds-1, PUSH/VOID returns the stake,
    LOSE loses the unit (backtesting.engine.pnl_per_unit convention)."""
    if outcome == WIN:
        return taken_odds - 1.0
    if outcome in (PUSH, VOID):
        return 0.0
    return -1.0
