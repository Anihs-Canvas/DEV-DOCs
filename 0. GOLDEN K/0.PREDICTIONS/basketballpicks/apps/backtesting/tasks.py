"""Celery beat tasks — SETTLE + the FORWARD-CLV gate [bball-05 §5].

Task names match the (currently commented) config/celery.py beat_schedule that
Agent-01 scaffolded, so the owning agent only has to UNCOMMENT its lines:

    backtesting.settle_beat              settle-15min      (6-59/15)
    backtesting.paper_clv_weekly_beat    Mon 07:45         (the gate)

Both are DB-ONLY (no API key): settle re-reads box scores, the CLV gate reads
the accrued open/closing prop pairs. Every run leaves exactly one JobRun
"beat:<job>" (the safepicks never-crash-the-beat discipline via run_beat).
"""

from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="backtesting.settle_beat")
def settle_beat() -> dict:
    """Every 15 min: grade props + team markets from box scores (idempotent,
    row-locked, 48h re-grade). DB-only — runs and counts toward job success
    even before any API key lands (bball-05 §5)."""
    from apps.backtesting import settlement
    from apps.ingestion.tasks import run_beat

    return run_beat("beat:settle_props", settlement.settle_edge_picks)


@shared_task(name="backtesting.paper_clv_weekly_beat")
def paper_clv_weekly_beat() -> dict:
    """Weekly (Mon 07:45): log the trailing-90-day FORWARD-CLV read to a JobRun
    so the pre-registered CONFIRM/KILL/HOLD verdict accrues without manual runs
    (bball-05 §4/§5). DB-only. Thin now; meaningful once forward data builds."""
    from apps.backtesting import prop_clv
    from apps.ingestion.tasks import run_beat

    def _run() -> dict:
        today = timezone.now().date()
        result = prop_clv.compute_prop_clv(today - timedelta(days=90), today)
        # keep the JobRun row compact — drop the per-pick list.
        return {k: v for k, v in result.items() if k != "picks"}

    return run_beat("beat:prop_clv", _run)
