"""PrizePicks pick'em parser (bball-06 §1.B1) — DFS venue #2 (P2P, lower priority).

Endpoint: GET /projections?league_id={id}&per_page=250&single_stat=true. Cloudflare
gates datacenter IPs (403) — live with a residential IP + browser UA. PrizePicks
converted ALL contests to peer-to-peer "Arena" (bball-04 §3d), so its vs-house edge
has decayed; treat NBA-star props as near-dead (sharp field), keep for obscure legs.

`odds_type` demon/goblin are SHADED lines (worse/better payout) — we record it so
the edge engine can down-weight non-standard legs. league_id drifts → resolve at
runtime via /leagues, never hard-code (bball-06 §1.B1).

Shape: {"data":[{"type":"projection","attributes":{"line_score":24.5,"stat_type":
"Points","odds_type":"standard"},"relationships":{"new_player":{"data":{"id":"123",
"type":"new_player"}}}}], "included":[{"type":"new_player","id":"123","attributes":
{"name":"..."}}]}.
"""

from __future__ import annotations

from .common import ParsedPropQuote, normalize_market


def _player_index(payload: dict) -> dict[str, str]:
    idx = {}
    for inc in payload.get("included") or []:
        if inc.get("type") == "new_player" and inc.get("id"):
            name = (inc.get("attributes") or {}).get("name")
            if name:
                idx[str(inc["id"])] = name
    return idx


def parse(payload: dict) -> list[ParsedPropQuote]:
    players = _player_index(payload)
    quotes: list[ParsedPropQuote] = []
    for proj in payload.get("data") or []:
        if proj.get("type") != "projection":
            continue
        attrs = proj.get("attributes") or {}
        market = normalize_market(attrs.get("stat_type"))
        if market is None:
            continue
        try:
            line = float(attrs.get("line_score"))
        except (TypeError, ValueError):
            continue
        pdata = ((proj.get("relationships") or {}).get("new_player") or {}).get("data") or {}
        player = players.get(str(pdata.get("id")))
        if not player:
            continue
        quotes.append(
            ParsedPropQuote(
                source="prizepicks",
                book="prizepicks",
                player_name=player,
                market=market,
                line=line,
                is_dfs=True,
                dfs_odds_type=(attrs.get("odds_type") or "standard").lower(),
            )
        )
    return quotes
