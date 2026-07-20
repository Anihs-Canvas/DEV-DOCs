"""Harvest NBA schedule + TEAM/PLAYER box scores from stats.nba.com (nba_api)
[bball-02 S1 — the props-eligible core league; keyless].

Usage:
    python manage.py harvest_nba                       # yesterday's slate
    python manage.py harvest_nba --date 2026-01-15
    python manage.py harvest_nba --from 2026-01-01 --to 2026-01-07
    python manage.py harvest_nba --date 2026-01-15 --with-advanced   # + USG%/pace
    python manage.py harvest_nba --date 2026-01-15 --max-games 3      # soak guard

Idempotent: a re-run upserts every game/box row in place and creates nothing new.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.ingestion import harvest, services_nba_api


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CommandError(f"bad date {value!r} (want YYYY-MM-DD)") from exc


class Command(BaseCommand):
    help = "Harvest NBA games + team/player box scores from nba_api (keyless)"

    def add_arguments(self, parser):
        parser.add_argument("--date", help="single day YYYY-MM-DD")
        parser.add_argument("--from", dest="date_from", help="window start YYYY-MM-DD")
        parser.add_argument("--to", dest="date_to", help="window end YYYY-MM-DD")
        parser.add_argument(
            "--with-advanced", action="store_true",
            help="also fetch advanced box (USG%%/pace/off-def rating) — the props signal",
        )
        parser.add_argument("--max-games", type=int, help="stop after N games (soak guard)")

    def handle(self, *args, **opts):
        if opts["date"]:
            dfrom = dto = _parse_date(opts["date"])
        elif opts["date_from"] and opts["date_to"]:
            dfrom, dto = _parse_date(opts["date_from"]), _parse_date(opts["date_to"])
        elif opts["date_from"] or opts["date_to"]:
            raise CommandError("--from and --to must be given together")
        else:
            dfrom, dto = services_nba_api.default_window()

        client = harvest.nba_api_client()

        def _run():
            return services_nba_api.harvest_nba(
                client, dfrom, dto,
                with_advanced=opts["with_advanced"], max_games=opts["max_games"],
            )

        job = harvest.run_harvest_job("harvest_nba", _run)
        self._report(job.stats, dfrom, dto)

    def _report(self, stats: dict, dfrom, dto) -> None:
        self.stdout.write(
            self.style.SUCCESS(
                f"nba_api {dfrom}..{dto}: games seen={stats.get('games_seen', 0)} "
                f"(new={stats.get('games_created', 0)} upd={stats.get('games_updated', 0)}), "
                f"team-box={stats.get('team_box_rows', 0)} player-box={stats.get('player_box_rows', 0)}; "
                f"calls={stats.get('requests_made', 0)} cache={stats.get('cache_hits', 0)} "
                f"errors={stats.get('fetch_errors', 0)}"
            )
        )
        if stats.get("budget_note"):
            self.stdout.write(self.style.WARNING(f"  stopped: {stats['budget_note']}"))
