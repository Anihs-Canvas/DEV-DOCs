"""Harvest EuroLeague schedule + TEAM/PLAYER box scores from the official feeds
(euroleague-api) [bball-02 S3 — cleanest international free data, PIR model].

Usage:
    python manage.py harvest_euroleague                    # current season, played games
    python manage.py harvest_euroleague --season 2025      # the 2025-26 season
    python manage.py harvest_euroleague --season 2025 --include-scheduled
    python manage.py harvest_euroleague --season 2025 --max-games 5   # soak guard

Idempotent: a re-run upserts every game/box row in place and creates nothing new.
"""

from datetime import date

from django.core.management.base import BaseCommand

from apps.ingestion import harvest, services_euroleague


def _current_start_year(today: date | None = None) -> int:
    today = today or date.today()
    # EuroLeague runs Oct->May; before August the current season started last year.
    return today.year if today.month >= 8 else today.year - 1


class Command(BaseCommand):
    help = "Harvest EuroLeague games + team/player box scores from the official feeds (keyless)"

    def add_arguments(self, parser):
        parser.add_argument("--season", type=int, help="season start year, e.g. 2025 (=2025-26)")
        parser.add_argument(
            "--include-scheduled", action="store_true",
            help="also harvest not-yet-played games (schedule only; no box)",
        )
        parser.add_argument("--max-games", type=int, help="stop after N games (soak guard)")

    def handle(self, *args, **opts):
        start_year = opts["season"] or _current_start_year()
        client = harvest.euroleague_client()

        def _run():
            return services_euroleague.harvest_season(
                client, start_year,
                only_played=not opts["include_scheduled"],
                max_games=opts["max_games"],
            )

        job = harvest.run_harvest_job("harvest_euroleague", _run)
        stats = job.stats
        self.stdout.write(
            self.style.SUCCESS(
                f"euroleague E{start_year}: games={stats.get('games_seen', 0)} "
                f"(new={stats.get('games_created', 0)} upd={stats.get('games_updated', 0)}), "
                f"team-box={stats.get('team_box_rows', 0)} player-box={stats.get('player_box_rows', 0)}; "
                f"calls={stats.get('requests_made', 0)} errors={stats.get('fetch_errors', 0)}"
            )
        )
        if stats.get("budget_note"):
            self.stdout.write(self.style.WARNING(f"  stopped: {stats['budget_note']}"))
