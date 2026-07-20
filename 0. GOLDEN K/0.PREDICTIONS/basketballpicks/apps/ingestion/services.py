"""Ingestion services — the JobRun audit wrapper the ETL + beats share.

Copied from safepicks (`run_job`). Agent 2 adds the persistence helpers
(ensure_league / resolve_team / resolve_player / persist_games /
persist_boxscores) here as it wires apps/ingestion/sources/. Keep parsing
PURE in sources/*; this module owns the ORM writes.
"""

from django.utils import timezone

from apps.ingestion.models import JobRun


def run_job(job_name: str, fn, **kwargs) -> JobRun:
    """Wrap an ingest in a JobRun audit row. `fn` returns a stats dict (or an
    object with `.as_dict()`); on exception the row is marked FAILED and the
    exception re-raised for the caller (beat/ETL) to handle."""
    job = JobRun.objects.create(job_name=job_name)
    try:
        stats = fn(**kwargs)
        job.status = JobRun.STATUS_OK
        job.stats = stats if isinstance(stats, dict) else stats.as_dict()
    except Exception as exc:
        job.status = JobRun.STATUS_FAILED
        job.stats = {"error": repr(exc)}
        raise
    finally:
        job.finished_at = timezone.now()
        job.save()
    return job
