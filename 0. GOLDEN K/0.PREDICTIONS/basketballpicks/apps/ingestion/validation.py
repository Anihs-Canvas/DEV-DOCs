"""Blocking data-quality gate for the daily ETL [bball-01 §3, gate G0].

WRONG DATA IN THE DB IS THE WORST OUTCOME, so the daily ETL ends on a
pure-READ gate that can veto the whole run. The gate never writes; it returns
a structured :class:`GateResult` the orchestrator turns into a FAILED parent
JobRun + a Sentry alert + a non-zero exit.

FOUNDATION NOTE (Agent 1): the two structural HARD checks below (duplicate
games; FINAL-score integrity) are real and run today against apps.core.Game.
The domain-specific checks bball-01 §3 calls for are left as clearly-marked
TODO seams for the data agents to fill:
    * prop-line coverage per slate (>= X% of the slate has lines)
    * sharp-anchor presence (>= X% of prop lines have a Pinnacle/Circa peer)
    * box-score minutes conservation (sum player minutes ~= 240 + 25*num_ot
      per team)
    * stale-injury freshness (final report captured < N min pre-tip)
Those import from apps.props / apps.odds (other agents' apps), so they are
added once those models exist — keeping this gate importable on a fresh clone.
"""

import logging
from dataclasses import dataclass, field
from datetime import date

from django.db.models import Count, Q, QuerySet

from apps.core.models import Game, TeamBoxScore

logger = logging.getLogger(__name__)


@dataclass
class GateResult:
    """Structured verdict of :func:`validate_etl`. `ok` is False iff there is
    at least one hard failure; warnings never affect `ok`."""

    ok: bool
    hard_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "hard_failures": self.hard_failures,
            "warnings": self.warnings,
            "hard_failure_count": len(self.hard_failures),
            "warning_count": len(self.warnings),
            "stats": self.stats,
        }


# ---------------------------------------------------------------------------
# hard checks (structural; source-agnostic)
# ---------------------------------------------------------------------------


def _duplicate_games(game_qs: QuerySet) -> list[str]:
    """Two+ Game rows sharing (season, tipoff date, home, away) — the same real
    game stored twice. The adopt-not-duplicate design exists to prevent this; a
    survivor means adoption failed and must block publication."""
    groups = (
        game_qs.values("season", "tipoff_utc__date", "home_team", "away_team")
        .annotate(c=Count("id"))
        .filter(c__gt=1)
        .order_by("season", "tipoff_utc__date")
    )
    problems: list[str] = []
    for g in groups:
        ids = list(
            game_qs.filter(
                season=g["season"],
                tipoff_utc__date=g["tipoff_utc__date"],
                home_team=g["home_team"],
                away_team=g["away_team"],
            )
            .order_by("id")
            .values_list("id", flat=True)
        )
        problems.append(
            f"duplicate game: season_id={g['season']} date={g['tipoff_utc__date']} "
            f"home_id={g['home_team']} away_id={g['away_team']} count={g['c']} ids={ids}"
        )
    return problems


def _final_integrity(game_qs: QuerySet) -> list[str]:
    """A FINAL Game must carry both scores."""
    rows = (
        game_qs.filter(status=Game.STATUS_FINAL)
        .filter(Q(home_score__isnull=True) | Q(away_score__isnull=True))
        .values_list("id", "source", "external_id")
    )
    return [
        f"FINAL game {gid} ({src}:{ext}) has a null score" for gid, src, ext in rows
    ]


# ---------------------------------------------------------------------------
# warnings (surfaced, never block)
# ---------------------------------------------------------------------------


def _boxscore_coverage(game_qs: QuerySet) -> list[str]:
    """FINAL games with no TeamBoxScore — a coverage gap, not a corruption."""
    missing = (
        game_qs.filter(status=Game.STATUS_FINAL)
        .annotate(n=Count("team_boxscores"))
        .filter(n=0)
        .count()
    )
    if missing:
        return [f"{missing} FINAL game(s) have no TeamBoxScore yet"]
    return []


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def validate_etl(since: date | None = None) -> GateResult:
    """Run the blocking gate. `since` scopes the per-game checks to games
    tipping off on/after that date (a full-history sweep when None)."""
    game_qs = Game.objects.all()
    if since is not None:
        game_qs = game_qs.filter(tipoff_utc__date__gte=since)

    hard: list[str] = []
    hard += _duplicate_games(game_qs)
    hard += _final_integrity(game_qs)

    warnings: list[str] = []
    warnings += _boxscore_coverage(game_qs)

    stats = {
        "games_checked": game_qs.count(),
        "final_games": game_qs.filter(status=Game.STATUS_FINAL).count(),
        "team_boxscores": TeamBoxScore.objects.count(),
        "since": since.isoformat() if since else None,
    }
    ok = not hard
    result = GateResult(ok=ok, hard_failures=hard, warnings=warnings, stats=stats)
    logger.info(
        "ETL gate: ok=%s hard=%d warn=%d (%s games checked)",
        ok, len(hard), len(warnings), stats["games_checked"],
    )
    return result
