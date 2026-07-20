"""Pure parse primitives shared by every free odds source (bball-05 §2b).

NO ORM, NO network — each source module turns an already-decoded JSON payload into
a list[ParsedPropQuote]; the ingestion service owns Player/Bookmaker resolution +
persistence. Keeping the parsers pure is what lets the whole layer be unit-tested
without a database or a key (safepicks the_odds_api.py discipline).

The MARKET vocabulary is the stable settlement-oriented key set from bball-05 §1;
`normalize_market()` maps every source's idiosyncratic stat label onto it. Anything
unmapped returns None and is COUNTED-and-skipped by the caller (never guessed — a
silently-misclassified market corrupts settlement).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ---- MARKET vocabulary -----------------------------------------------------
# Stable lowercase-word keys that MATCH props.PropMarket.key AND
# predictions.PropPrediction.market_key (bball-01 §2; the predictions contract) —
# a single vocabulary across props/predictions/edge so a PropPrediction joins a
# PropLine by market key with no translation layer.
PTS, REB, AST = "points", "rebounds", "assists"
THREES, BLK, STL, TOV = "threes", "blocks", "steals", "turnovers"
FGM, FTM = "fgm", "ftm"
PRA, PR, PA, RA, BLKSTL = "pra", "pr", "pa", "ra", "blocks_steals"
DD, TD, FIRST_BASKET = "double_double", "triple_double", "first_basket"

MARKETS = (PTS, REB, AST, THREES, BLK, STL, TOV, FGM, FTM, PRA, PR, PA, RA, BLKSTL,
           DD, TD, FIRST_BASKET)

# Count-family stats are low-count / right-skew (rebounds, assists, 3PM, blocks,
# steals, TOV) → the props CDF reprice fits Neg-Binom/Poisson; continuous-ish
# families (points, PRA, combos) fit (skew-)Normal (bball-04 §2b).
COUNT_FAMILY = frozenset({REB, AST, THREES, BLK, STL, TOV, FGM, FTM, BLKSTL})
CONTINUOUS_FAMILY = frozenset({PTS, PRA, PR, PA, RA})
YESNO_FAMILY = frozenset({DD, TD, FIRST_BASKET})

# The Odds API market keys (bball-05 §2b, verified 2026-07-19).
_ODDS_API_MAP = {
    "player_points": PTS,
    "player_rebounds": REB,
    "player_assists": AST,
    "player_threes": THREES,
    "player_blocks": BLK,
    "player_steals": STL,
    "player_turnovers": TOV,
    "player_blocks_steals": BLKSTL,
    "player_field_goals": FGM,
    "player_frees_made": FTM,
    "player_points_rebounds_assists": PRA,
    "player_points_rebounds": PR,
    "player_points_assists": PA,
    "player_rebounds_assists": RA,
    "player_double_double": DD,
    "player_triple_double": TD,
    "player_first_basket": FIRST_BASKET,
}

# Free-text stat labels used by SGO / Bovada / DFS apps (lower-cased, punctuation
# stripped). DFS apps use "Pts+Rebs+Asts"-style; SGO uses "points"/"rebounds".
_LABEL_MAP = {
    "points": PTS, "pts": PTS,
    "rebounds": REB, "rebs": REB, "reb": REB, "total rebounds": REB,
    "assists": AST, "asts": AST, "ast": AST,
    "3-pt made": THREES, "threes": THREES, "three pointers made": THREES,
    "3 point fg": THREES, "made threes": THREES, "3pt made": THREES,
    "blocks": BLK, "blocked shots": BLK,
    "steals": STL,
    "turnovers": TOV,
    "blocks+steals": BLKSTL, "blks+stls": BLKSTL, "steals+blocks": BLKSTL,
    "fg made": FGM, "field goals made": FGM,
    "ft made": FTM, "free throws made": FTM,
    "pts+rebs+asts": PRA, "points+rebounds+assists": PRA, "pra": PRA, "pts rebs asts": PRA,
    "pts+rebs": PR, "points+rebounds": PR, "pts rebs": PR,
    "pts+asts": PA, "points+assists": PA, "pts asts": PA,
    "rebs+asts": RA, "rebounds+assists": RA, "rebs asts": RA,
    "double double": DD, "double-double": DD,
    "triple double": TD, "triple-double": TD,
    "first basket": FIRST_BASKET, "first field goal": FIRST_BASKET,
}


def normalize_market(raw: str | None) -> str | None:
    """Map a source market key/label to the stable MARKET vocab, else None."""
    if not raw:
        return None
    key = raw.strip()
    if key in _ODDS_API_MAP:
        return _ODDS_API_MAP[key]
    label = key.lower().replace("_", " ").replace("  ", " ").strip()
    return _LABEL_MAP.get(label)


def american_to_decimal(american: float | int | str | None) -> float | None:
    """+150 -> 2.50 ; -120 -> 1.8333. Returns None on missing/zero."""
    if american in (None, "", 0):
        return None
    a = float(american)
    if a == 0:
        return None
    return 1.0 + (a / 100.0 if a > 0 else 100.0 / -a)


@dataclass(frozen=True, slots=True)
class ParsedPropQuote:
    """One source's quote for one player's one market at one line. Two-sided books
    fill over_price/under_price; DFS pick'em fills payout_mult and leaves prices
    None (a pick'em leg has no two-way price — bball-05 §1: never fabricate one)."""

    source: str
    book: str  # bookmaker key: draftkings|fanduel|bovada|pinnacle|underdog|prizepicks|...
    player_name: str
    market: str  # MARKET vocab
    line: float
    over_price: float | None = None  # decimal
    under_price: float | None = None  # decimal
    payout_mult: float | None = None  # DFS leg payout multiplier (no vig)
    is_dfs: bool = False
    dfs_odds_type: str | None = None  # standard|demon|goblin (PrizePicks) — non-standard = shaded
    raw: dict = field(default_factory=dict)

    def two_sided(self) -> bool:
        return self.over_price is not None and self.under_price is not None
