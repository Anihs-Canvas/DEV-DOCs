"""Celery beat tasks + the shared alert / skip / never-crash helpers.

Design rules (ADR 007), carried from safepicks:
* every beat run leaves exactly one JobRun named "beat:<job>";
* NO KEY / NO SOURCE, NO CRASH: a missing key or not-yet-wired source
  records a `skipped` JobRun and returns — the beat can run today;
* unexpected exceptions mark the JobRun failed, alert, and are swallowed
  so celery never crash-loops a beat.

FOUNDATION NOTE (Agent 1): the results/watchdog beats below are runnable
STUBS. `run_daily_etl_beat` already drives the real orchestrator shell
(etl.run_daily_etl); the others record a `skipped` JobRun until Agent 2
wires apps/ingestion/sources/.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.ingestion.models import JobRun
from apps.ingestion.services import run_job

logger = logging.getLogger(__name__)


def alert(message: str, exc: BaseException | None = None) -> None:
    """Log-based alert, mirrored to Sentry when SENTRY_DSN is set. `exc` ships
    the exception with a real traceback (beat failures never propagate — the
    ADR 007 never-crash-the-beat rule — so the Celery integration alone would
    miss them)."""
    logger.error("PIPELINE ALERT: %s", message)
    dsn = getattr(settings, "SENTRY_DSN", "")
    if not dsn:
        return
    try:
        import sentry_sdk

        sentry_sdk.capture_message(message, level="error")
        if exc is not None:
            sentry_sdk.capture_exception(exc)
    except ImportError:
        logger.warning("SENTRY_DSN set but sentry-sdk is not installed — log-only alerts")


def skip_job(job_name: str, reason: str) -> dict:
    JobRun.objects.create(
        job_name=job_name,
        status=JobRun.STATUS_SKIPPED,
        finished_at=timezone.now(),
        stats={"reason": reason},
    )
    logger.info("%s skipped: %s", job_name, reason)
    return {"skipped": reason}


def run_beat(job_name: str, fn) -> dict:
    """run_job + never-crash-the-beat semantics."""
    try:
        return run_job(job_name, fn).stats
    except Exception as exc:  # JobRun row is already marked failed
        alert(f"{job_name} failed: {exc!r}", exc=exc)
        return {"error": repr(exc)}


@shared_task(name="ingestion.run_daily_etl_beat")
def run_daily_etl_beat() -> dict:
    """Daily unified ETL: anchor -> props -> enrich -> the blocking gate.

    Drives the real orchestrator (etl.run_daily_etl). A gate HARD FAIL or a
    stage crash raises ETLError inside run_daily_etl (which already alerted);
    the beat swallows it so celery never crash-loops, returning the parent
    JobRun stats either way."""
    from apps.ingestion import etl

    try:
        result = etl.run_daily_etl()
        return result.parent.stats
    except etl.ETLError as exc:
        # run_daily_etl already fired the Sentry alert + wrote a FAILED parent.
        logger.warning("daily ETL finished with failure: %r", exc)
        latest = JobRun.objects.filter(job_name="etl:daily").latest("started_at")
        return latest.stats


@shared_task(name="ingestion.sync_results_boxscore_beat")
def sync_results_boxscore_beat() -> dict:
    """15-min nba_api results + box-score poll [bball-01 §3].

    STUB: nba_api is keyless, so there is no key to gate on — this records a
    `skipped` JobRun until Agent 2 wires apps/ingestion/sources/nba_api.py.
    Replace the body with `run_beat("beat:sync_results_boxscore", _run)` where
    `_run` calls the nba_api results + box-score persistence."""
    return skip_job("beat:sync_results_boxscore", "nba_api source not wired yet (Agent 2)")


@shared_task(name="ingestion.sync_injuries_beat")
def sync_injuries_beat() -> dict:
    """15-min injury feed [bball-01 §3] — the pre-tip final report triggers the
    usage-cascade repricing. STUB until Agent 2 wires injuries_espn.py."""
    return skip_job("beat:sync_injuries", "injury source not wired yet (Agent 2)")


@shared_task(name="ingestion.watchdog_beat")
def watchdog_beat() -> dict:
    """Missed-beat watchdog [bball-01 §3]. STUB: records its own heartbeat
    JobRun. Agent (ops) replaces this with the real staleness scan over
    JobRun rows (alert when an expected beat has not run within its window)."""
    JobRun.objects.create(
        job_name="beat:watchdog",
        status=JobRun.STATUS_OK,
        finished_at=timezone.now(),
        stats={"note": "heartbeat stub — real missed-beat scan TODO"},
    )
    return {"ok": True}
