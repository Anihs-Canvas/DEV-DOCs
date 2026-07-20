"""Underdog Fantasy pick'em parser (bball-06 §1.B2) — DFS venue #1 (the target).

Underdog CLASSIC vs-house advertises NO limiting → the PRIME durable venue we bet
against (bball-04 §3d). Endpoint: GET /beta/v5/over_under_lines with a browser UA
+ Referer. A pick'em leg has NO two-way price — we store the payout multiplier and
leave over/under prices None (bball-05 §1: never fabricate a DFS price).

Shape (from aidanhall21/underdog-fantasy-pickem-scraper): {"over_under_lines":
[{"stat_value": "24.5", "over_under": {"appearance_stat": {"stat":"points",
"appearance_id": "..."}, "title":"..."}, "options": [{"choice":"higher",
"payout_multiplier":"1"}, {"choice":"lower", ...}]}], "appearances": [{"id":...,
"player_id":...}], "players": [{"id":..., "first_name":.., "last_name":..}]}.
"""

from __future__ import annotations

from .common import ParsedPropQuote, normalize_market


def _player_index(payload: dict) -> dict[str, str]:
    """appearance_id -> player full name via appearances→players join."""
    players = {}
    for p in payload.get("players") or []:
        name = " ".join(x for x in (p.get("first_name"), p.get("last_name")) if x).strip()
        if p.get("id") and name:
            players[str(p["id"])] = name
    apps = {}
    for a in payload.get("appearances") or []:
        pid = a.get("player_id")
        if a.get("id") and pid is not None and str(pid) in players:
            apps[str(a["id"])] = players[str(pid)]
    return apps


def parse(payload: dict) -> list[ParsedPropQuote]:
    apps = _player_index(payload)
    quotes: list[ParsedPropQuote] = []
    for line_obj in payload.get("over_under_lines") or []:
        ou = line_obj.get("over_under") or {}
        astat = ou.get("appearance_stat") or {}
        market = normalize_market(astat.get("stat") or astat.get("display_stat"))
        if market is None:
            continue
        app_id = astat.get("appearance_id") or ou.get("appearance_id")
        player = apps.get(str(app_id)) if app_id is not None else ou.get("title")
        if not player:
            continue
        try:
            line = float(line_obj.get("stat_value"))
        except (TypeError, ValueError):
            continue
        # Underdog classic standard payout is the entry-level multiplier; a
        # per-option multiplier != 1 signals a "boosted"/insured leg — keep it.
        mult = None
        for opt in line_obj.get("options") or []:
            try:
                m = float(opt.get("payout_multiplier"))
            except (TypeError, ValueError):
                continue
            if m and m != 1.0:
                mult = m
        quotes.append(
            ParsedPropQuote(
                source="underdog",
                book="underdog",
                player_name=player,
                market=market,
                line=line,
                payout_mult=mult,
                is_dfs=True,
                dfs_odds_type="standard",
            )
        )
    return quotes
