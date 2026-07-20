"""EuroLeague persistence — schedule + TEAM/PLAYER box into the core models
[bball-02 S3]. Parsing is pure (sources/euroleague.py); this owns the ORM writes.

Idempotent + net-tolerant: games key on (source, external_id) where external_id
= 'E2025:GAMECODE'; teams resolve by their EuroLeague team code, players by
their EuroLeague player id in ``source_ids``. A played game's box is fetched
once (immutable-final TTL); a blip on one game is counted and skipped.
"""

from __future__ import annotations

import logging
import urllib.error

from django.utils import timezone

from apps.ingestion import harvest
from apps.ingestion.http import BudgetedClient, BudgetExhausted, Priority, TransportError
from apps.ingestion.sources import euroleague

logger = logging.getLogger(__name__)

SOURCE = euroleague.SOURCE
_FETCH_ERRORS = (TransportError, urllib.error.HTTPError, urllib.error.URLError)


def _ensure_league():
    return harvest.ensure_league("EURO", "EuroLeague", "intl", SOURCE, euroleague.COMPETITION)


def _external_id(scode: str, game_code: str) -> str:
    return f"{scode}:{game_code}"


def harvest_season(
    client: BudgetedClient,
    start_year: int,
    *,
    only_played: bool = True,
    max_games: int | None = None,
) -> dict:
    """Harvest one EuroLeague season: schedule -> games, then box for played
    games. Idempotent + resumable (a re-run re-adopts every game via its ref)."""
    scode = euroleague.season_code(start_year)
    league = _ensure_league()
    season = harvest.ensure_season(league, euroleague.season_name(start_year))
    stats = harvest.HarvestStats()

    try:
        sched_payload = euroleague.fetch_schedule(client, scode, priority=Priority.LOW)
    except BudgetExhausted as exc:
        stats.budget_note = str(exc)
        return stats.as_dict()
    except _FETCH_ERRORS as exc:
        stats.fetch_errors += 1
        logger.warning("euroleague: schedule %s failed (%r)", scode, exc)
        return stats.as_dict()

    games = euroleague.parse_schedule(sched_payload, scode)
    if not games:
        stats.empty_slates += 1

    for pg in games:
        if max_games is not None and stats.games_seen >= max_games:
            break
        stats.games_seen += 1

        home = harvest.resolve_team(league, SOURCE, pg.home_code, pg.home_name or pg.home_code)
        away = harvest.resolve_team(league, SOURCE, pg.away_code, pg.away_name or pg.away_code)
        game, created = harvest.upsert_game(
            SOURCE,
            _external_id(scode, pg.game_code),
            season,
            home,
            away,
            pg.tipoff_utc or timezone.now(),
            pg.status,
            home_score=pg.home_score,
            away_score=pg.away_score,
            raw={"euroleague": pg.raw},
        )
        stats.games_created += int(created)
        stats.games_updated += int(not created)

        if only_played and not pg.played:
            continue
        _harvest_box(client, scode, game, league, pg, stats)
        if stats.budget_note:
            break

    stats.requests_made = getattr(client, "requests_made", 0)
    stats.cache_hits = getattr(client, "cache_hits", 0)
    return stats.as_dict()


def _harvest_box(client, scode, game, league, pg, stats) -> None:
    try:
        box_payload = euroleague.fetch_boxscore(client, scode, pg.game_code, is_final=pg.played)
    except BudgetExhausted as exc:
        stats.budget_note = str(exc)
        return
    except _FETCH_ERRORS as exc:
        stats.fetch_errors += 1
        logger.warning("euroleague: box %s/%s failed (%r)", scode, pg.game_code, exc)
        return

    team_rows, player_rows = euroleague.parse_boxscore(
        box_payload, pg.game_code, pg.home_code, pg.away_code
    )

    for tb in team_rows:
        team = harvest.resolve_team(league, SOURCE, tb.team_code, tb.team_name or tb.team_code)
        harvest.upsert_team_boxscore(
            game,
            team,
            is_home=tb.is_home,
            fields={
                "pts": tb.pts, "reb": tb.reb, "ast": tb.ast, "stl": tb.stl,
                "blk": tb.blk, "tov": tb.tov, "pf": tb.pf, "fgm": tb.fgm, "fga": tb.fga,
                "tpm": tb.tpm, "tpa": tb.tpa, "ftm": tb.ftm, "fta": tb.fta,
                "minutes": tb.minutes if tb.minutes is not None else harvest.team_minutes(0, 200),
                "raw": {"euroleague": tb.raw},
            },
        )
        stats.team_box_rows += 1

    for pb in player_rows:
        if not pb.player_name and not pb.player_id:
            continue
        team = harvest.resolve_team(league, SOURCE, pb.team_code, pb.team_code)
        player = harvest.resolve_player(SOURCE, pb.player_id, pb.player_name, team)
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
                "ftm": pb.ftm, "fta": pb.fta, "plus_minus": None,
                "raw": {"euroleague": pb.raw, "valuation": pb.valuation},
            },
        )
        stats.player_box_rows += 1
