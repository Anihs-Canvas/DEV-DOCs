"""Harvest NCAA Men's D1 schedule + TEAM/PLAYER box scores from ESPN (hoopR)
[bball-02 S2 — biggest data volume, DFS-only soft prop tail; keyless].

Usage:
    python manage.py harvest_ncaam                     # yesterday's slate
    python manage.py harvest_ncaam --date 2026-01-15
    python manage.py harvest_ncaam --from 2026-01-01 --to 2026-01-03

NCAA slates are large (350+ D1 teams); use --max-games while soaking. Idempotent.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.ingestion import harvest, services_espn_basketball


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise CommandError(f"bad date {value!r} (want YYYY-MM-DD)") from exc


class Command(BaseCommand):
    help = "Harvest NCAA Men's D1 games + team/player box scores from ESPN/hoopR (keyless)"

    def add_arguments(self, parser):
        parser.add_argument("--date", help="single day YYYY-MM-DD")
        parser.add_argument("--from", dest="date_from", help="window start YYYY-MM-DD")
        parser.add_argument("--to", dest="date_to", help="window end YYYY-MM-DD")
        parser.add_argument("--max-games", type=int, help="stop after N games (soak guard)")

    def handle(self, *args, **opts):
        if opts["date"]:
            dfrom = dto = _parse_date(opts["date"])
        elif opts["date_from"] and opts["date_to"]:
            dfrom, dto = _parse_date(opts["date_from"]), _parse_date(opts["date_to"])
        elif opts["date_from"] or opts["date_to"]:
            raise CommandError("--from and --to must be given together")
        else:
            dfrom, dto = services_espn_basketball.default_window()

        client = harvest.espn_basketball_client()

        def _run():
            return services_espn_basketball.harvest_ncaam(
                client, dfrom, dto, max_games=opts["max_games"]
            )

        job = harvest.run_harvest_job("harvest_ncaam", _run)
        stats = job.stats
        self.stdout.write(
            self.style.SUCCESS(
                f"ncaam {dfrom}..{dto}: games={stats.get('games_seen', 0)} "
                f"(new={stats.get('games_created', 0)} upd={stats.get('games_updated', 0)}), "
                f"team-box={stats.get('team_box_rows', 0)} player-box={stats.get('player_box_rows', 0)}; "
                f"calls={stats.get('requests_made', 0)} errors={stats.get('fetch_errors', 0)}"
            )
        )
        if stats.get("budget_note"):
            self.stdout.write(self.style.WARNING(f"  stopped: {stats['budget_note']}"))
