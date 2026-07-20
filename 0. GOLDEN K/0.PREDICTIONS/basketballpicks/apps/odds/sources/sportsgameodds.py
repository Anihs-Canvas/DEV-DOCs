"""SportsGameOdds free "Amateur" tier parser (bball-06 §1.A1) — the backbone.

Structured JSON, 9 soft books (FanDuel, DraftKings, BetMGM, Caesars, ESPN BET,
Bovada, Unibet, PointsBet, William Hill) + a pre-computed "Fair Odds" / "Book
Consensus" field on the free tier. We PARSE the raw two-sided book prices and
recompute our own de-vig anyway (bball-06 §1.D2: control the method + log method-
sensitivity), but we surface SGO's consensus as a zero-effort cross-check.

SCHEMA CAVEAT (ADR-007): SGO's exact field names must be verified on the first
real key. This parser targets the documented v2 shape
    {"data": [ {"odds": { oddID: {statID, playerID/statEntityID, betTypeID:"ou",
      sideID:"over"|"under", byBookmaker: {book: {odds, overUnder}}, fairOdds,
      bookOddsAvailable} } , "players": {playerID: {name}} } ]}
and is DEFENSIVE: any record missing a field is skipped, never guessed.
"""

from __future__ import annotations

from collections.abc import Iterable

from .common import ParsedPropQuote, american_to_decimal, normalize_market

_SIDE_OVER = {"over", "o", "ou-over"}
_SIDE_UNDER = {"under", "u", "ou-under"}


def _dec(v):
    """SGO reports American odds as strings/ints; tolerate decimal already."""
    if v in (None, ""):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f > 1.0 and abs(f) < 100 and "." in str(v) else american_to_decimal(v)


def parse_events(payload: dict) -> list[ParsedPropQuote]:
    quotes: list[ParsedPropQuote] = []
    for event in payload.get("data") or []:
        players = event.get("players") or {}
        odds = event.get("odds") or {}
        # Pair over/under sides that share (player, statID, book, line).
        pairs: dict[tuple, dict] = {}
        for od in odds.values() if isinstance(odds, dict) else odds:
            if not isinstance(od, dict):
                continue
            if (od.get("betTypeID") or od.get("betType")) not in ("ou", "over_under", None):
                continue
            market = normalize_market(od.get("statID") or od.get("statEntityID_stat"))
            if market is None:
                continue
            pid = od.get("playerID") or od.get("statEntityID")
            pname = (players.get(pid) or {}).get("name") if pid else None
            pname = pname or od.get("playerName")
            if not pname:
                continue
            side = (od.get("sideID") or od.get("side") or "").lower()
            by_book = od.get("byBookmaker") or {}
            for book, bd in by_book.items():
                if not isinstance(bd, dict):
                    continue
                line = bd.get("overUnder", od.get("overUnder"))
                price = _dec(bd.get("odds"))
                if line is None or price is None:
                    continue
                key = (pname, market, book, float(line))
                slot = pairs.setdefault(key, {"over": None, "under": None, "raw": bd})
                if side in _SIDE_OVER:
                    slot["over"] = price
                elif side in _SIDE_UNDER:
                    slot["under"] = price
        for (pname, market, book, line), slot in pairs.items():
            if slot["over"] is None and slot["under"] is None:
                continue
            quotes.append(
                ParsedPropQuote(
                    source="sportsgameodds",
                    book=str(book).lower(),
                    player_name=pname,
                    market=market,
                    line=line,
                    over_price=slot["over"],
                    under_price=slot["under"],
                    raw=slot["raw"],
                )
            )
    return quotes


def parse(payload: dict) -> list[ParsedPropQuote]:
    return parse_events(payload)


def iter_quotes(payloads: Iterable[dict]) -> list[ParsedPropQuote]:
    out: list[ParsedPropQuote] = []
    for p in payloads:
        out.extend(parse_events(p))
    return out
