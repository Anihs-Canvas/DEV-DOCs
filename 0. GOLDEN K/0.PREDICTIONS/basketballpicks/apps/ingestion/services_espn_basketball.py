"""ESPN basketball persistence — the wehoop (WNBA) + hoopR (NCAA Men's D1)
harvester into the core models [bball-02 S2].

One generic ``harvest_espn`` drives every basketball slug; ``harvest_wnba`` and
``harvest_ncaam`` are thin wrappers pinning slug + core League code + the season
convention (WNBA = single calendar year, NCAA = split-year). Idempotent + net-
tolerant exactly like services_nba_api: scoreboard -> games, summary -> box for
FINAL games; a per-game blip is counted and skipped.
"""

from __future__ import annotations

import logging
import urllib.error
from datetime import date, timedelta

from django.utils import timezone

from apps.ingestion import harvest
from apps.ingestion.http import BudgetedClient, BudgetExhausted, Priority, TransportError
from apps.ingestion.sources import espn_basketball as espn

logger = logging.getLogger(__name__)

SOURCE = espn.SOURCE
_FETCH_ERRORS = (TransportError, urllib.error.HTTPError, urllib.error.URLError)

# (League code) -> (name, level, single-calendar-year season?)
LEAGUE_META = {
    "WNBA": ("WNBA", "pro", True),
    "NCAAB": ("NCAA Men's D1", "college", False),
    "NCAAW": ("NCAA Women's D1", "college", False),
    "NBA": ("NBA", "pro", False),
}


def _ensure_league(code: str):
    name, level, _single = LEAGUE_META[code]
    return harvest.ensure_league(code, name, level, SOURCE, espn.LEAGUE_SLUGS[code])


def _season_name(code: str, game_date: date) -> str:
    _n, _l, single = LEAGUE_META[code]
    if single:
        return harvest.season_name_single_year(game_date)
    return harvest.season_name_split_year(game_date, start_month=8)


def harvest_slate(
    client: BudgetedClient,
    slug: str,
    code: str,
    game_date: date,
    league,
    stats: harvest.HarvestStats,
    *,
    max_games: int | None = None,
) -> None:
    try:
        payload = espn.fetch_scoreboard(client, slug, game_date, priority=Priority.LOW)
    except BudgetExhausted as exc:
        stats.budget_note = str(exc)
        return
    except _FETCH_ERRORS as exc:
        stats.fetch_errors += 1
        logger.warning("espn_basketball: %s scoreboard %s failed (%r)", slug, game_date, exc)
        return

    games = espn.parse_scoreboard(payload)
    day_key = game_date.isoformat()
    day_counts = {"games": 0, "player_box": 0}
    if not games:
        stats.empty_slates += 1

    season = harvest.ensure_season(league, _season_name(code, game_date))

    for pg in games:
        if max_games is not None and stats.games_seen >= max_games:
            break
        stats.games_seen += 1
        day_counts["games"] += 1

        home = harvest.resolve_team(league, SOURCE, pg.home_team_id, pg.home_name, pg.home_abbr)
        away = harvest.resolve_team(league, SOURCE, pg.away_team_id, pg.away_name, pg.away_abbr)
        game, created = harvest.upsert_game(
            SOURCE,
            pg.event_id,
            season,
            home,
            away,
            pg.tipoff_utc,
            pg.status,
            home_score=pg.home_score,
            away_score=pg.away_score,
            num_ot=pg.num_ot,
            venue=pg.venue,
            raw={"espn": pg.raw},
        )
        stats.games_created += int(created)
        stats.games_updated += int(not created)

        if pg.status != harvest.STATUS_FINAL:
            continue

        _harvest_box(client, slug, game, league, pg, stats, day_counts)

    stats.per_day[day_key] = day_counts


def _harvest_box(client, slug, game, league, pg, stats, day_counts) -> None:
    try:
        summary = espn.fetch_summary(client, slug, pg.event_id, is_final=True)
    except BudgetExhausted as exc:
        stats.budget_note = str(exc)
        return
    except _FETCH_ERRORS as exc:
        stats.fetch_errors += 1
        logger.warning("espn_basketball: summary %s failed (%r)", pg.event_id, exc)
        return

    team_rows, player_rows = espn.parse_boxscore(summary)
    home_id = pg.home_team_id

    for tb in team_rows:
        team = harvest.resolve_team(league, SOURCE, tb.team_id, tb.team_name, tb.team_abbr)
        harvest.upsert_team_boxscore(
            game,
            team,
            is_home=(tb.team_id == home_id) if home_id else tb.is_home,
            fields={
                "pts": tb.pts, "reb": tb.reb, "ast": tb.ast, "stl": tb.stl,
                "blk": tb.blk, "tov": tb.tov, "pf": tb.pf, "fgm": tb.fgm, "fga": tb.fga,
                "tpm": tb.tpm, "tpa": tb.tpa, "ftm": tb.ftm, "fta": tb.fta,
                "minutes": harvest.team_minutes(pg.num_ot, 240),
                "raw": {"espn": tb.raw},
            },
        )
        stats.team_box_rows += 1

    for pb in player_rows:
        if not pb.player_id:
            continue
        team = harvest.resolve_team(league, SOURCE, pb.team_id, "", "")
        player = harvest.resolve_player(SOURCE, pb.player_id, pb.player_name, team, pb.position)
        stats.players_seen += 1
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
                "raw": {"espn": pb.raw},
            },
        )
        stats.player_box_rows += 1
        day_counts["player_box"] += 1


def harvest_espn(
    client: BudgetedClient,
    code: str,
    date_from: date,
    date_to: date,
    *,
    max_games: int | None = None,
) -> dict:
    slug = espn.LEAGUE_SLUGS[code]
    league = _ensure_league(code)
    stats = harvest.HarvestStats()
    cur = date_from
    while cur <= date_to:
        harvest_slate(client, slug, code, cur, league, stats, max_games=max_games)
        if stats.budget_note:
            break
        cur += timedelta(days=1)
    stats.requests_made = getattr(client, "requests_made", 0)
    stats.cache_hits = getattr(client, "cache_hits", 0)
    return stats.as_dict()


def harvest_wnba(client, date_from, date_to, *, max_games=None) -> dict:
    return harvest_espn(client, "WNBA", date_from, date_to, max_games=max_games)


def harvest_ncaam(client, date_from, date_to, *, max_games=None) -> dict:
    return harvest_espn(client, "NCAAB", date_from, date_to, max_games=max_games)


def default_window(now=None) -> tuple[date, date]:
    now = now or timezone.now()
    y = (now - timedelta(days=1)).date()
    return y, y
