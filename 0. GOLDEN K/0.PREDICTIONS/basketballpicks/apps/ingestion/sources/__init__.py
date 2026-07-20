"""Ingestion sources — OWNED BY AGENT 2.

This package is the plug-in point for the per-source clients + parsers the
ETL orchestrator (apps/ingestion/etl.py) calls into. Expected modules
[bball-01 §5]:

    nba_api.py        keyless schedule / results / TeamBoxScore + PlayerBoxScore
                      + (optional) PlayByPlay. IP/rate-limited: a 429/blip is a
                      counted+skipped child, never a raised failure.
    the_odds_api.py   BUSINESS tier: team markets (h2h/spreads/totals) + player
                      props (player_points/rebounds/assists/pra/threes/...),
                      capturing sharp (pinnacle/circa) + soft + DFS books.
    dfs_underdog.py   Underdog / PrizePicks pick'em (price-less PropLine rows
                      with payout_mult).
    injuries_espn.py  keyless InjuryReport feed (the 30-min-pre-tip final
                      report is the highest-value poll — the usage cascade).

The orchestrator imports these LAZILY inside each stage body, so this package
staying empty for now does not break project import or the test suite. Wire
real clients on apps/ingestion/http.BudgetedClient (copy from safepicks) to
reuse the token-bucket / daily-budget audit.
"""
