"""Print the FORWARD-CLV gate table over a date window [bball-05 §4].

Measures the three CLV flavors on every FLAGGED soft/DFS +EV selection whose
open->closing prop pair has landed, and renders the per-cell CONFIRM/KILL/HOLD
verdict against the frozen pre-registered thresholds. Forward-only: an empty
table is the correct output today, not an error.
"""

import datetime as dt

from django.core.management.base import BaseCommand, CommandError

from apps.backtesting import prop_clv


def _pct(value) -> str:
    return "    n/a" if value is None else f"{value * 100:+6.2f}%"


def _pts(value) -> str:
    return "  n/a" if value is None else f"{value:+5.2f}"


def _row(label: str, summ: dict, verdict: bool = True) -> str:
    v = f"  [{summ.get('verdict', '-')}]" if verdict else ""
    return (
        f"  {label:<22} n={summ['n']:<4} "
        f"sharpCLV={_pct(summ['sharp_beat_mean'])} "
        f"CI[{_pct(summ['sharp_beat_ci_lo'])},{_pct(summ['sharp_beat_ci_hi'])}] "
        f"lineMv={_pts(summ['line_move_mean'])} "
        f"ROI={_pct(summ['roi_mean'])} "
        f"wk={summ['weeks']}{v}"
    )


class Command(BaseCommand):
    help = (
        "Measure the FORWARD prop-CLV gate (three CLV flavors + pre-registered "
        "CONFIRM/KILL/HOLD verdicts). Forward-only; empty until captures accrue."
    )

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="date_from", required=True, help="start YYYY-MM-DD")
        parser.add_argument("--to", dest="date_to", required=True, help="end YYYY-MM-DD (inclusive)")

    def handle(self, *args, **opts):
        try:
            date_from = dt.date.fromisoformat(opts["date_from"])
            date_to = dt.date.fromisoformat(opts["date_to"])
        except ValueError as exc:
            raise CommandError(f"bad date (expected YYYY-MM-DD): {exc}") from exc
        if date_to < date_from:
            raise CommandError("--to must not precede --from")

        report = prop_clv.compute_prop_clv(date_from, date_to)
        w = report["window"]
        self.stdout.write(
            f"PROP-CLV GATE  {w['from']} .. {w['to']}  "
            f"(sharpCLV = p_fair_close * O_taken - 1; the verdict metric)"
        )
        self.stdout.write(
            f"  games scanned={report['n_games_scanned']}  with pairs="
            f"{report['n_games_with_pairs']}  flagged={report['n_flagged']}"
        )
        self.stdout.write(_row("OVERALL", report["overall"]))
        for section, verdict in (
            ("by_venue", True),
            ("by_market", True),
            ("by_league", True),
            ("by_cell", True),
            ("by_book", False),
            ("by_anchor", False),
        ):
            cells = report[section]
            if not cells:
                continue
            self.stdout.write(f"  -- {section} --")
            for key, summ in cells.items():
                self.stdout.write(_row(key, summ, verdict))
        if report["n_flagged"] == 0:
            self.stdout.write(
                "  (no flagged open->closing pairs yet — forward-only; accrues as "
                "prop open lines + closing captures land)"
            )
        self.stdout.write(self.style.SUCCESS("prop_clv_report done"))
