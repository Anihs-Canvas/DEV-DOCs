"""Manually run the prop/team settlement pass [bball-05 §3].

Grades every settleable EdgePick from box scores (idempotent, row-locked, 48h
re-grade). The same pass the `backtesting.settle_beat` runs on a 15-min cadence.
"""

from django.core.management.base import BaseCommand

from apps.backtesting import settlement


class Command(BaseCommand):
    help = "Grade props + team markets from box scores (idempotent, 48h re-grade)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--regrade-window-h",
            type=int,
            default=settlement.REGRADE_WINDOW_H,
            help="hours a terminal pick stays open to stat-correction re-grade",
        )

    def handle(self, *args, **opts):
        stats = settlement.settle_edge_picks(regrade_window_h=opts["regrade_window_h"])
        for key, val in stats.items():
            self.stdout.write(f"  {key:<12} {val}")
        self.stdout.write(self.style.SUCCESS("settle_props done"))
