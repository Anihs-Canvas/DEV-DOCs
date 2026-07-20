"""Bovada public-JSON parser (bball-06 §1.A3) — the datacenter-reachable backbone.

Bovada is the ONE book whose public JSON WebFetch reached from a datacenter IP
without a 403, so it is the reliability backbone of the soft panel (works where
DK/FD scrapers get blocked). Team markets live under marketFilterId=def; player
props live under the per-EVENT coupon path with a props filter.

Shape (verified live 2026-07-19 for team; props Betstamp-confirmed): the response
is a list of groups, each with `events[]`, each event with `displayGroups[]`,
each group with `markets[]`, each market with `outcomes[]` carrying
`price.decimal` / `price.american` and (for props) a `description` = player and a
handicap on the outcome. Defensive: anything malformed is skipped.
"""

from __future__ import annotations

from .common import ParsedPropQuote, american_to_decimal, normalize_market

_OVER = {"over", "o"}
_UNDER = {"under", "u"}


def _price(outcome: dict) -> float | None:
    p = outcome.get("price") or {}
    dec = p.get("decimal")
    if dec is not None:
        try:
            f = float(dec)
            if f > 1.0:
                return f
        except (TypeError, ValueError):
            pass
    return american_to_decimal(p.get("american"))


def parse(payload) -> list[ParsedPropQuote]:
    quotes: list[ParsedPropQuote] = []
    groups = payload if isinstance(payload, list) else [payload]
    for grp in groups:
        for event in (grp or {}).get("events") or []:
            for dg in event.get("displayGroups") or []:
                for mk in dg.get("markets") or []:
                    market = normalize_market(
                        mk.get("statType") or mk.get("key") or mk.get("description")
                    )
                    if market is None:
                        continue
                    pairs: dict[tuple, dict] = {}
                    for oc in mk.get("outcomes") or []:
                        player = oc.get("description") or mk.get("playerName")
                        line = (oc.get("price") or {}).get("handicap")
                        if line is None:
                            line = mk.get("line")
                        price = _price(oc)
                        if not player or line is None or price is None:
                            continue
                        slot = pairs.setdefault((player, float(line)),
                                                {"over": None, "under": None})
                        side = (oc.get("type") or oc.get("description") or "").lower()
                        if any(side.startswith(s) for s in _OVER):
                            slot["over"] = price
                        elif any(side.startswith(s) for s in _UNDER):
                            slot["under"] = price
                    for (player, line), slot in pairs.items():
                        if slot["over"] is None and slot["under"] is None:
                            continue
                        quotes.append(
                            ParsedPropQuote(
                                source="bovada",
                                book="bovada",
                                player_name=player,
                                market=market,
                                line=line,
                                over_price=slot["over"],
                                under_price=slot["under"],
                            )
                        )
    return quotes
