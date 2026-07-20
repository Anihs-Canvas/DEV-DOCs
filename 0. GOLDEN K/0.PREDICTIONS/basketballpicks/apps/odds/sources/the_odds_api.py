"""The Odds API v4 parser — FREE Starter tier usage only (bball-06 §1.A2).

Two roles at $0:
  * TEAM markets (h2h/spreads/totals) + the Betfair-exchange near-zero-vig team
    anchor — cheap, reliable (bball-06 §1.C2).
  * SPOT single-event player props — the free tier technically returns them per
    /events/{id}/odds; use SPARINGLY (credits are scarce, props are credit-heavy).

Cost model (billing awareness only — the BudgetedClient charges it): bulk team
call = markets x regions; per-event props = UNIQUE-MARKETS-RETURNED x regions;
/events enumeration is FREE. We never touch the paid Business/historical tiers.

Outcome payload (verified 2026-07-19): name=Over/Under, description=player name,
point=line, price=DECIMAL odds already.
"""

from __future__ import annotations

from .common import ParsedPropQuote, normalize_market

# Books The Odds API labels that we treat as SHARP-ish anchors on the free tier
# (Pinnacle is GONE post-2025-07-23; Betfair Exchange is the closest free proxy).
SHARP_BOOK_KEYS = frozenset({"betfair_ex_eu", "betfair_ex_uk", "betfair", "lowvig"})
CREDITS_TEAM_PER_REGION_MARKET = 1  # bull cost: markets x regions
HISTORICAL_MULTIPLIER = 10  # paid-only; we DO NOT use it — recorded to forbid it


def parse_event_props(payload: dict) -> list[ParsedPropQuote]:
    """One /events/{id}/odds response → two-sided prop quotes."""
    quotes: list[ParsedPropQuote] = []
    for bm in payload.get("bookmakers") or []:
        book = (bm.get("key") or "").lower()
        for mk in bm.get("markets") or []:
            market = normalize_market(mk.get("key"))
            if market is None:
                continue
            # group Over/Under outcomes by (player, line)
            pairs: dict[tuple, dict] = {}
            for oc in mk.get("outcomes") or []:
                player = oc.get("description")
                line = oc.get("point")
                price = oc.get("price")
                if not player or line is None or price is None:
                    continue
                slot = pairs.setdefault((player, float(line)), {"over": None, "under": None})
                name = (oc.get("name") or "").lower()
                if name.startswith("over") or name == "yes":
                    slot["over"] = float(price)
                elif name.startswith("under") or name == "no":
                    slot["under"] = float(price)
            for (player, line), slot in pairs.items():
                if slot["over"] is None and slot["under"] is None:
                    continue
                quotes.append(
                    ParsedPropQuote(
                        source="the_odds_api",
                        book=book,
                        player_name=player,
                        market=market,
                        line=line,
                        over_price=slot["over"],
                        under_price=slot["under"],
                        raw={"market_key": mk.get("key")},
                    )
                )
    return quotes


def parse_event_ids(events_payload: list[dict]) -> list[str]:
    """FREE /events response → game IDs to enumerate before spending credits."""
    return [e["id"] for e in (events_payload or []) if isinstance(e, dict) and e.get("id")]
