"""Shared harvest-layer support for the basketballpicks player-box ingestion
[bball-02 §4 / bball-01 §2, §5].

This is the seam between the PURE source parsers (``sources/*.py`` — no ORM)
and Agent 1's core models + JobRun audit row. It owns three things every
harvester needs and nothing source-specific:

* CLIENT FACTORIES — a ``BudgetedClient`` per source (nba_api, espn_basketball,
  euroleague) built on Agent 1's ``ingestion/http.py`` infra so budget / rate /
  backoff / TTL-cache are owned centrally, NOT per source (bball-02 §4). All
  settings are read with ``getattr`` defaults so a source still stands up if the
  config block has not landed yet.
* IDEMPOTENT UPSERTS into the core models — ``League / Season / Team / Player /
  Game / TeamBoxScore / PlayerBoxScore``. Identity is by each source's own id
  carried in ``*.source_ids`` JSON (players survive trades) with the natural
  key as the fallback, so a re-run of a slate mutates rows in place and creates
  nothing new. FINAL games and stored scores are never downgraded / erased.
* ``run_harvest_job`` — plugs a harvest fn INTO Agent 1's ``JobRun`` audit row
  (we do NOT define JobRun; we import it). Mirrors ``services.run_job``.

CONTRACT (do not redefine): ``from apps.core.models import League, Season, Team,
Player, Game, TeamBoxScore, PlayerBoxScore``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.utils import timezone

from apps.core.models import (
    Game,
    League,
    Player,
    PlayerBoxScore,
    Season,
    Team,
    TeamBoxScore,
)
from apps.ingestion.http import BudgetedClient, DailyBudget, TokenBucket
from apps.ingestion.models import JobRun

logger = logging.getLogger(__name__)

# core.Game status values (mirror the Match.STATUS_* convention, bball-01 §2).
STATUS_SCHEDULED = "SCHEDULED"
STATUS_LIVE = "LIVE"
STATUS_FINAL = "FINAL"
STATUS_PP = "PP"

_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# client factories (one BudgetedClient per source; settings getattr-defaulted)
# ---------------------------------------------------------------------------


def nba_api_client() -> BudgetedClient:
    """stats.nba.com wrapper client. Keyless but IP/rate-limited: it needs
    browser-like headers (stats.nba.com 403s bots) and a gentle token bucket
    (~20/min). Treated exactly like a keyless source with network tolerance."""
    base = getattr(settings, "NBA_API_BASE_URL", "https://stats.nba.com/stats")
    ua = getattr(settings, "NBA_API_USER_AGENT", _BROWSER_UA)
    rate = getattr(settings, "NBA_API_RATE_PER_MIN", 20)
    budget = getattr(settings, "NBA_API_DAILY_BUDGET", 20000)
    return BudgetedClient(
        source="nba_api",
        base_url=base,
        headers={
            "User-Agent": ua,
            "Referer": "https://www.nba.com/",
            "Origin": "https://www.nba.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "x-nba-stats-origin": "stats",
            "x-nba-stats-token": "true",
        },
        budget=DailyBudget("nba_api", budget),
        bucket=TokenBucket(rate),
    )


def espn_basketball_client() -> BudgetedClient:
    """ESPN keyless basketball scoreboard/summary client (wehoop/hoopR wrap the
    same site.api.espn.com feed). Free, so the daily budget is a safety
    ceiling; a browser UA avoids the odd 403."""
    base = getattr(
        settings,
        "ESPN_BB_BASE_URL",
        "https://site.api.espn.com/apis/site/v2/sports/basketball",
    )
    ua = getattr(settings, "ESPN_BB_USER_AGENT", _BROWSER_UA)
    rate = getattr(settings, "ESPN_BB_RATE_PER_MIN", 60)
    budget = getattr(settings, "ESPN_BB_DAILY_BUDGET", 20000)
    return BudgetedClient(
        source="espn_basketball",
        base_url=base,
        headers={"User-Agent": ua},
        budget=DailyBudget("espn_basketball", budget),
        bucket=TokenBucket(rate),
    )


def euroleague_client() -> BudgetedClient:
    """EuroLeague official feeds client (the euroleague-api source). Cleanest
    international feed; low volume, gentle bucket."""
    base = getattr(settings, "EUROLEAGUE_BASE_URL", "https://live.euroleague.net/api")
    ua = getattr(settings, "EUROLEAGUE_USER_AGENT", _BROWSER_UA)
    rate = getattr(settings, "EUROLEAGUE_RATE_PER_MIN", 30)
    budget = getattr(settings, "EUROLEAGUE_DAILY_BUDGET", 5000)
    return BudgetedClient(
        source="euroleague",
        base_url=base,
        headers={"User-Agent": ua},
        budget=DailyBudget("euroleague", budget),
        bucket=TokenBucket(rate),
    )


# ---------------------------------------------------------------------------
# JobRun wrapper (plug INTO Agent 1's audit model — never redefined here)
# ---------------------------------------------------------------------------


def run_harvest_job(job_name: str, fn, **kwargs) -> JobRun:
    """Wrap a harvest in a JobRun audit row (mirrors services.run_job). A
    designed no-op (nothing to harvest) is still an OK run with stats; only a
    real exception marks the run FAILED and re-raises for the beat wrapper."""
    job = JobRun.objects.create(job_name=job_name)
    try:
        stats = fn(**kwargs)
        job.status = JobRun.STATUS_OK
        job.stats = stats if isinstance(stats, dict) else stats.as_dict()
    except Exception as exc:  # noqa: BLE001 — recorded on the row, then re-raised
        job.status = JobRun.STATUS_FAILED
        job.stats = {"error": repr(exc)}
        raise
    finally:
        job.finished_at = timezone.now()
        job.save()
    return job


# ---------------------------------------------------------------------------
# numeric coercion helpers (box columns are PositiveSmallInt / Decimal)
# ---------------------------------------------------------------------------


def as_int(value, default: int = 0) -> int:
    """Coerce a box-score cell to a non-negative int; blanks/None -> default."""
    if value is None or value == "":
        return default
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def as_decimal(value) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def as_signed_int(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# season helpers
# ---------------------------------------------------------------------------


def season_name_split_year(d: date, *, start_month: int = 8) -> str:
    """Winter-calendar season label 'YYYY-YY' (NBA/NCAA/EuroLeague run
    Oct->Jun). A game in Jan 2026 belongs to the 2025-26 season."""
    year = d.year if d.month >= start_month else d.year - 1
    return f"{year}-{(year + 1) % 100:02d}"


def season_name_single_year(d: date) -> str:
    """Single-calendar-year season label (WNBA plays May->Oct)."""
    return str(d.year)


def team_minutes(num_ot: int = 0, regulation: int = 240) -> Decimal:
    """Fallback team-minutes total when a feed omits it (TeamBoxScore.minutes is
    NOT NULL). 5 players x game length: NBA/ESPN 240 (+25/OT), EuroLeague 200."""
    return Decimal(int(regulation) + 25 * int(num_ot or 0))


# ---------------------------------------------------------------------------
# core-model resolution + upserts (idempotent; identity by source id)
# ---------------------------------------------------------------------------


def ensure_league(code: str, name: str, level: str, source: str, source_id) -> League:
    """get_or_create a League by its stable code and seed
    ``source_ids[source]`` (never overwrites a manually pinned id)."""
    league, _ = League.objects.get_or_create(
        code=code, defaults={"name": name, "level": level}
    )
    sid = str(source_id)
    if (league.source_ids or {}).get(source) != sid:
        league.source_ids = {**(league.source_ids or {}), source: sid}
        league.save(update_fields=["source_ids"])
    return league


def ensure_season(league: League, name: str) -> Season:
    season, _ = Season.objects.get_or_create(league=league, name=name)
    return season


def resolve_team(
    league: League,
    source: str,
    source_id,
    name: str,
    abbreviation: str = "",
    **defaults,
) -> Team:
    """Resolve a Team idempotently: by ``source_ids[source]`` first (stable id),
    then by (canonical_name, league), else create. Seeds the source id + keeps
    the abbreviation fresh. Distinct source ids stay distinct teams (never a
    fuzzy merge) — the Reggina/Reggiana safety, ADR 002.10."""
    sid = str(source_id) if source_id not in (None, "") else ""
    team = None
    if sid:
        team = Team.objects.filter(league=league, **{f"source_ids__{source}": sid}).first()
    if team is None:
        team = Team.objects.filter(canonical_name=name, league=league).first()
    if team is None:
        return Team.objects.create(
            canonical_name=name,
            abbreviation=(abbreviation or "")[:8],
            league=league,
            source_ids={source: sid} if sid else {},
            **defaults,
        )
    changed: list[str] = []
    if sid and (team.source_ids or {}).get(source) != sid:
        team.source_ids = {**(team.source_ids or {}), source: sid}
        changed.append("source_ids")
    if abbreviation and team.abbreviation != abbreviation[:8]:
        team.abbreviation = abbreviation[:8]
        changed.append("abbreviation")
    if changed:
        team.save(update_fields=changed)
    return team


def resolve_player(
    source: str,
    source_id,
    name: str,
    team: Team | None,
    primary_position: str = "",
) -> Player:
    """Resolve a Player idempotently: by ``source_ids[source]`` first (survives
    a mid-season trade), then by (canonical_name, current_team), else create.
    Refreshes current_team so the roster tracks the latest game."""
    sid = str(source_id) if source_id not in (None, "") else ""
    player = None
    if sid:
        player = Player.objects.filter(**{f"source_ids__{source}": sid}).first()
    if player is None:
        player = Player.objects.filter(canonical_name=name, current_team=team).first()
    if player is None:
        return Player.objects.create(
            canonical_name=name,
            current_team=team,
            primary_position=(primary_position or "")[:4],
            source_ids={source: sid} if sid else {},
        )
    changed: list[str] = []
    if sid and (player.source_ids or {}).get(source) != sid:
        player.source_ids = {**(player.source_ids or {}), source: sid}
        changed.append("source_ids")
    if team is not None and player.current_team_id != team.id:
        player.current_team = team
        changed.append("current_team")
    if primary_position and not player.primary_position:
        player.primary_position = primary_position[:4]
        changed.append("primary_position")
    if changed:
        player.save(update_fields=changed)
    return player


def _tipoff(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return timezone.now()


def upsert_game(
    source: str,
    external_id: str,
    season: Season,
    home_team: Team,
    away_team: Team,
    tipoff_utc: datetime,
    status: str,
    *,
    home_score: int | None = None,
    away_score: int | None = None,
    period_scores: dict | None = None,
    num_ot: int = 0,
    venue: str = "",
    raw: dict | None = None,
) -> tuple[Game, bool]:
    """Idempotent Game upsert keyed on (source, external_id). Guards: never
    downgrade a stored FINAL to a non-final status, never erase a stored score.
    Returns (game, created)."""
    existing = Game.objects.filter(source=source, external_id=str(external_id)).first()
    if existing is None:
        game = Game.objects.create(
            source=source,
            external_id=str(external_id),
            season=season,
            home_team=home_team,
            away_team=away_team,
            tipoff_utc=_tipoff(tipoff_utc),
            status=status,
            home_score=home_score,
            away_score=away_score,
            period_scores=period_scores or {},
            num_ot=num_ot or 0,
            venue=(venue or "")[:64],
            raw=raw or {},
        )
        return game, True

    changed: list[str] = []
    downgrade = existing.status == STATUS_FINAL and status != STATUS_FINAL
    if not downgrade and existing.status != status:
        existing.status = status
        changed.append("status")
    # scores/period only fill or improve — a feed blip never nulls a result
    if home_score is not None and existing.home_score != home_score:
        existing.home_score = home_score
        changed.append("home_score")
    if away_score is not None and existing.away_score != away_score:
        existing.away_score = away_score
        changed.append("away_score")
    if num_ot and existing.num_ot != num_ot:
        existing.num_ot = num_ot
        changed.append("num_ot")
    if period_scores and existing.period_scores != period_scores:
        existing.period_scores = period_scores
        changed.append("period_scores")
    # keep a still-SCHEDULED row's tipoff fresh (a TBD time can firm up)
    if existing.status == STATUS_SCHEDULED and tipoff_utc and existing.tipoff_utc != tipoff_utc:
        existing.tipoff_utc = _tipoff(tipoff_utc)
        changed.append("tipoff_utc")
    if venue and not existing.venue:
        existing.venue = venue[:64]
        changed.append("venue")
    if changed:
        existing.save(update_fields=changed)
    return existing, False


def upsert_team_boxscore(game: Game, team: Team, is_home: bool, fields: dict) -> bool:
    """update_or_create a TeamBoxScore on (game, team). Returns created?"""
    defaults = {"is_home": is_home, **fields}
    _, created = TeamBoxScore.objects.update_or_create(
        game=game, team=team, defaults=defaults
    )
    return created


def upsert_player_boxscore(game: Game, player: Player, team: Team, fields: dict) -> bool:
    """update_or_create a PlayerBoxScore on (game, player) — the props grain.
    Returns created?"""
    defaults = {"team": team, **fields}
    _, created = PlayerBoxScore.objects.update_or_create(
        game=game, player=player, defaults=defaults
    )
    return created


# ---------------------------------------------------------------------------
# shared stats accumulator
# ---------------------------------------------------------------------------


@dataclass
class HarvestStats:
    games_seen: int = 0
    games_created: int = 0
    games_updated: int = 0
    team_box_rows: int = 0
    player_box_rows: int = 0
    players_seen: int = 0
    fetch_errors: int = 0
    empty_slates: int = 0
    requests_made: int = 0
    cache_hits: int = 0
    per_day: dict = field(default_factory=dict)
    budget_note: str | None = None

    def as_dict(self) -> dict:
        d = self.__dict__.copy()
        if d.get("budget_note") is None:
            d.pop("budget_note", None)
        return d
