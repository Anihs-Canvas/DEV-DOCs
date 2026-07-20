"""OddsPapi parser (bball-06 §1.D1) — the free-Pinnacle SHARP AUDIT feed.

250 req/mo (~8 full boards/mo): each request returns the entire board for one
fixture across ~370 bookmakers INCLUDING Pinnacle + Betfair Exchange, with player
props (playerName field). This is NOT a volume anchor — it is spent surgically at
CLOSING on flagged marquee games to give a low-n but REAL sharp cross-check that
soft-consensus alone cannot (the anti-contamination guardrail, bball-06 §7 / K6).

We extract ONLY the Pinnacle two-sided prop quotes here; the edge layer de-vigs
them and compares to the soft-consensus fair prob on the SAME leg (audit, never a
bet-vs price). VERIFY the schema on the first real key (longevity/ToS risk).

Shape: {"odds":[{"bookmaker":"pinnacle","market":"player_points","playerName":
"...","line":24.5,"over":1.90,"under":1.95}]} (decimal odds assumed; defensive).
"""

from __future__ import annotations

from .common import ParsedPropQuote, american_to_decimal, normalize_market

AUDIT_BOOK = "pinnacle"


def _dec(v):
    if v in (None, ""):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f > 1.0 else american_to_decimal(v)


def parse(payload: dict, book: str = AUDIT_BOOK) -> list[ParsedPropQuote]:
    """Return only `book` (default pinnacle) two-sided prop quotes from a board."""
    quotes: list[ParsedPropQuote] = []
    rows = payload.get("odds") if isinstance(payload, dict) else payload
    for od in rows or []:
        if (od.get("bookmaker") or "").lower() != book:
            continue
        market = normalize_market(od.get("market") or od.get("statID"))
        player = od.get("playerName") or od.get("player")
        line = od.get("line") or od.get("point")
        if market is None or not player or line is None:
            continue
        over, under = _dec(od.get("over")), _dec(od.get("under"))
        if over is None and under is None:
            continue
        quotes.append(
            ParsedPropQuote(
                source="oddspapi",
                book=book,
                player_name=player,
                market=market,
                line=float(line),
                over_price=over,
                under_price=under,
                raw={"audit": True},
            )
        )
    return quotes
