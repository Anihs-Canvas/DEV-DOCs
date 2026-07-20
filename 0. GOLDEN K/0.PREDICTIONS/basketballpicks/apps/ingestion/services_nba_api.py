"""nba_api persistence — NBA schedule + TEAM/PLAYER box into the core models
[bball-02 S1]. Parsing is pure (sources/nba_api.py); this owns the ORM writes.

Idempotent: games key on (source, external_id); teams/players resolve by their
nba_api id in ``source_ids`` (survives trades); box rows update_or_create on
(game, team) / (game, player). Network-tolerant like the safepicks ESPN stage —
a 429/blip on one game is counted + skipped, never a raised harvest failure;
a spent budget stops cleanly with a note.
"""

from __future__ import annotations

import logging
import urllib.error
from datetime import date, timedelta

from django.utils import timezone

from apps.ingestion import harvest
from apps.ingestion.http import BudgetedClient, BudgetExhausted, Priority, TransportError
from apps.ingestion.sources import nba_api

logger = logging.getLogger(__name__)

SOURCE = nba_api.SOURCE
_FETCH_ERRORS = (TransportError, urllib.error.HTTPError, urllib.error.URLError)


def _ensure_league():
    return harvest.ensure_league("NBA", "NBA", "pro", SOURCE, nba_api.LEAGUE_ID)


def _season_for(game_date: date):
    return harvest.season_name_split_year(game_date, start_month=8)


def harvest_slate(
    client: BudgetedClient,
    game_date: date,
    league,
    stats: harvest.HarvestStats,
    *,
    with_advanced: bool = False,
    max_games: int | None = None,
) -> None:
    """Harvest one calendar day: scoreboard -> games, then box for FINAL games."""
    try:
        payload = nba_api.fetch_scoreboard(client, game_date, priority=Priority.LOW)
    except BudgetExhausted as exc:
        stats.budget_note = str(exc)
        return
    except _FETCH_ERRORS as exc:
        stats.fetch_errors += 1
        logger.warning("nba_api: scoreboard %s failed (%r)", game_date, exc)
        return

    games = nba_api.parse_scoreboard(payload)
    day_key = game_date.isoformat()
    day_counts = {"games": 0, "player_box": 0}
    if not games:
        stats.empty_slates += 1

    season_name = _season_for(game_date)
    season = harvest.ensure_season(league, season_name)

    for pg in games:
        if max_games is not None and stats.games_seen >= max_games:
            break
        stats.games_seen += 1
        day_counts["games"] += 1

        home = harvest.resolve_team(league, SOURCE, pg.home_team_id, pg.home_name, pg.home_abbr)
        away = harvest.resolve_team(league, SOURCE, pg.away_team_id, pg.away_name, pg.away_abbr)
        game, created = harvest.upsert_game(
            SOURCE,
            pg.game_id,
            season,
            home,
            away,
            pg.tipoff_utc,
            pg.status,
            home_score=pg.home_score,
            away_score=pg.away_score,
            period_scores=pg.period_scores,
            num_ot=pg.num_ot,
            raw={"nba_api": pg.raw},
        )
        stats.games_created += int(created)
        stats.games_updated += int(not created)

        if pg.status != harvest.STATUS_FINAL:
            continue  # box scores only exist for completed games

        _harvest_box(client, game, league, pg, stats, day_counts, with_advanced=with_advanced)

    stats.per_day[day_key] = day_counts


def _harvest_box(client, game, league, pg, stats, day_counts, *, with_advanced):
    try:
        trad = nba_api.fetch_boxscore_traditional(client, pg.game_id, is_final=True)
    except BudgetExhausted as exc:
        stats.budget_note = str(exc)
        return
    except _FETCH_ERRORS as exc:
        stats.fetch_errors += 1
        logger.warning("nba_api: box %s failed (%r)", pg.game_id, exc)
        return

    adv_players: dict = {}
    adv_teams: dict = {}
    if with_advanced:
        try:
            adv = nba_api.fetch_boxscore_advanced(client, pg.game_id, is_final=True)
            adv_players, adv_teams = nba_api.parse_advanced(adv)
        except (BudgetExhausted, *_FETCH_ERRORS) as exc:
            logger.info("nba_api: advanced box %s skipped (%r)", pg.game_id, exc)

    for tb in nba_api.parse_team_boxscores(trad):
        team = harvest.resolve_team(league, SOURCE, tb.team_id, tb.team_name, tb.team_abbr)
        a = adv_teams.get(tb.team_id, {})
        created = harvest.upsert_team_boxscore(
            game,
            team,
            is_home=tb.team_id == pg.home_team_id,
            fields={
                "pts": tb.pts, "reb": tb.reb, "ast": tb.ast, "stl": tb.stl,
                "blk": tb.blk, "tov": tb.tov, "pf": tb.pf, "fgm": tb.fgm, "fga": tb.fga,
                "tpm": tb.tpm, "tpa": tb.tpa, "ftm": tb.ftm, "fta": tb.fta,
                "minutes": tb.minutes if tb.minutes is not None else harvest.team_minutes(pg.num_ot, 240),
                "pace": a.get("pace"),
                "off_rtg": a.get("off_rtg"), "def_rtg": a.get("def_rtg"),
                "raw": {"nba_api": tb.raw},
            },
        )
        stats.team_box_rows += 1
        _ = created

    for pb in nba_api.parse_player_boxscores(trad):
        team = harvest.resolve_team(league, SOURCE, pb.team_id, "", "")
        player = harvest.resolve_player(
            SOURCE, pb.player_id, pb.player_name, team, pb.start_position
        )
        stats.players_seen += 1
        a = adv_players.get(pb.player_id, {})
        harvest.upsert_player_boxscore(
            game,
            player,
            team,
            fields={
                "started": pb.started, "dnp": pb.dnp,
                "minutes": pb.minutes if pb.minutes is not None else 0,
                "pts": pb.pts, "oreb": pb.oreb, "dreb": pb.dreb, "reb": pb.reb,
                "ast": pb.ast, "stl": pb.stl, "blk": pb.blk, "tov": pb.tov, "pf": pb.pf,
                "fgm": pb.fgm, "fga": pb.fga, "tpm": pb.tpm, "tpa": pb.tpa,
                "ftm": pb.ftm, "fta": pb.fta, "plus_minus": pb.plus_minus,
                "usage_rate": a.get("usage_rate"),
                "raw": {"nba_api": pb.raw},
            },
        )
        stats.player_box_rows += 1
        day_counts["player_box"] += 1


def harvest_nba(
    client: BudgetedClient,
    date_from: date,
    date_to: date,
    *,
    with_advanced: bool = False,
    max_games: int | None = None,
) -> dict:
    """Harvest every day in [date_from, date_to] inclusive. Idempotent + resumable."""
    league = _ensure_league()
    stats = harvest.HarvestStats()
    cur = date_from
    while cur <= date_to:
        harvest_slate(
            client, cur, league, stats, with_advanced=with_advanced, max_games=max_games
        )
        if stats.budget_note:
            break
        cur += timedelta(days=1)
    stats.requests_made = getattr(client, "requests_made", 0)
    stats.cache_hits = getattr(client, "cache_hits", 0)
    return stats.as_dict()


def default_window(now=None) -> tuple[date, date]:
    """Default harvest window: yesterday's completed slate (NBA runs overnight
    ET, so the prior day is the freshly-finished one)."""
    now = now or timezone.now()
    y = (now - timedelta(days=1)).date()
    return y, y
