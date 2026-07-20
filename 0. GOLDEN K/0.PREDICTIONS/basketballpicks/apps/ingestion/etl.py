"""Unified daily ETL orchestrator [bball-01 §3 / ADR 007].

Mirrors the safepicks etl.py parent/child JobRun pattern and its
no-key-no-crash / no-data-no-crash contracts. This module ORCHESTRATES the
ingestion sources — it never re-parses or re-persists anything itself. The
stages run in a fixed order under one parent JobRun (`etl:daily`) whose stats
aggregate the child JobRuns:

    anchor   (keyless)    nba_api: schedule -> results (Game SCHEDULED->FINAL)
                          -> TeamBoxScore + PlayerBoxScore. nba_api needs no
                          key but is IP/rate-limited: a 429/blip is a
                          counted+skipped child, never a raised run failure.
    props    (key-gated)  *** the money stage *** The Odds API BUSINESS: team
                          markets -> OddsSnapshot, player props -> PropLine
                          (sharp + soft + DFS books in one pass).
    enrich   (mixed)      injuries (keyless -> InjuryReport; the 30-min-pre-tip
                          report is the highest-value poll) + DFS pick'em lines.
    validate (always)     the blocking data-quality gate (validation.py).

Contracts (carried from safepicks):
* NO KEY / NO SOURCE, NO CRASH — an empty key or a not-yet-wired source
  records a `skipped` child JobRun and moves on (ADR 007).
* every stage is wrapped in the run_job audit; one stage failing is recorded
  (FAILED child + Sentry alert) but does not corrupt earlier committed writes,
  and the validate gate still runs.
* a validate HARD FAIL, or any non-validate stage crash, marks the parent
  FAILED, alerts, and raises so the command exits non-zero.

======================================================================
AGENT 2 SEAM: the `_run_*` stage-body functions below are STUBS that return a
zeroed stats dict with a TODO note. Replace each body with a lazy import of
apps/ingestion/sources/* + the persistence call (see the docstrings). Do NOT
change the stage plumbing (_run_child / _skip_child / the parent aggregation)
— those are the shared contract this foundation guarantees.
======================================================================
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import date

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.ingestion import tasks, validation
from apps.ingestion.models import JobRun
from apps.ingestion.services import run_job

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# stage / source configuration (order + key-gating declared once, up top)
# ---------------------------------------------------------------------------

STAGE_ANCHOR = "anchor"
STAGE_PROPS = "props"
STAGE_ENRICH = "enrich"
STAGE_VALIDATE = "validate"

#: canonical execution order — also the valid `--only` choices.
STAGES: tuple[str, ...] = (STAGE_ANCHOR, STAGE_PROPS, STAGE_ENRICH, STAGE_VALIDATE)


@dataclass(frozen=True)
class KeyedSource:
    """A key-gated source: skipped with a `skipped` JobRun when its API-key
    setting is empty (the no-key-no-crash contract, ADR 007)."""

    name: str  # JobRun suffix + summary-row label
    setting_key: str  # settings attribute holding the API key

    @property
    def job_name(self) -> str:
        return f"etl:{self.name}"

    def key(self) -> str:
        return getattr(settings, self.setting_key, "") or ""


#: The Odds API BUSINESS props stage (team markets + player props).
PROPS_SOURCE = KeyedSource("props", "THE_ODDS_API_KEY")

#: keyless enrich sources (each ALWAYS runs; network-tolerant, so an outage is
#: a benign counted no-op, never a run failure).
ENRICH_KEYLESS = ("etl:enrich:injuries",)

#: enrich sources that carry payout-less DFS lines (keyless scraper).
ENRICH_DFS = "etl:enrich:dfs"

# summary-table metric buckets (best-effort human glance; the authoritative
# per-source numbers live untouched in each child JobRun.stats).
_INSERTED_KEYS = (
    "games_created", "team_boxscores", "player_boxscores", "snapshots_written",
    "prop_lines", "reports_written",
)
_UPDATED_KEYS = ("games_upgraded", "games_updated", "results_finalized", "games_adopted")
_SKIPPED_KEYS = ("games_existing", "skipped_already", "events_unmatched")


# ---------------------------------------------------------------------------
# result / error types
# ---------------------------------------------------------------------------


class ETLError(RuntimeError):
    """Base for daily-ETL failures that must produce a non-zero exit."""


class ETLValidationError(ETLError):
    """The data-quality gate hard-failed (or crashed): terminal."""

    def __init__(self, gate: "validation.GateResult | None"):
        self.gate = gate
        n = len(gate.hard_failures) if gate else "n/a"
        super().__init__(f"ETL data-quality gate hard-failed ({n} violation(s))")


class ETLStageError(ETLError):
    """At least one non-validate stage failed (gate itself passed)."""

    def __init__(self, failed: list[str]):
        self.failed = failed
        super().__init__(f"ETL stage(s) failed: {', '.join(failed)}")


@dataclass
class StageResult:
    """One row of the human summary + parent-stats aggregation."""

    name: str
    status: str
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    requests: int = 0
    duration_s: float = 0.0
    note: str = ""
    stats: dict = field(default_factory=dict)


@dataclass
class ETLRunResult:
    """Return value of :func:`run_daily_etl`."""

    parent: JobRun
    stages: list[StageResult]
    gate: "validation.GateResult | None"
    summary: str
    wall_s: float
    dry_run: bool
    hard_failed: bool
    stage_failed: list[str]


# ---------------------------------------------------------------------------
# stage bodies — each returns a plain dict (run_job stores it on the JobRun)
#   >>> AGENT 2 replaces the STUB bodies; keep the return-a-dict contract. <<<
# ---------------------------------------------------------------------------


def _run_anchor() -> dict:
    """KEYLESS nba_api anchor: schedule -> results (Game SCHEDULED->FINAL) ->
    TeamBoxScore + PlayerBoxScore.

    STUB. Replace with:
        from apps.ingestion.sources import nba_api
        ...persist schedule/results/boxscores via services helpers...
    Return a stats dict keyed like `_INSERTED_KEYS` (games_created,
    team_boxscores, player_boxscores, games_upgraded, requests_made)."""
    return {
        "note": "TODO(agent2): wire apps.ingestion.sources.nba_api",
        "games_created": 0,
        "team_boxscores": 0,
        "player_boxscores": 0,
        "requests_made": 0,
    }


def _run_props() -> dict:
    """KEY-GATED The Odds API BUSINESS: team markets -> odds.OddsSnapshot,
    player props -> props.PropLine (sharp + soft + DFS books in one pass).

    STUB. Replace with the odds/props source parse + persist (the odds+props
    agent typically owns the parser; this stage just invokes it)."""
    return {
        "note": "TODO(odds/props agent): wire the_odds_api team markets + props",
        "snapshots_written": 0,
        "prop_lines": 0,
        "events_matched": 0,
        "requests_made": 0,
    }


def _run_injuries() -> dict:
    """KEYLESS injury feed -> ingestion.InjuryReport (the usage-cascade
    trigger). STUB — replace with apps.ingestion.sources.injuries_espn."""
    return {
        "note": "TODO(agent2): wire apps.ingestion.sources.injuries_espn",
        "reports_written": 0,
        "requests_made": 0,
    }


def _run_dfs() -> dict:
    """KEYLESS DFS pick'em scrape -> props.PropLine (price-less, payout_mult).
    STUB — replace with apps.ingestion.sources.dfs_underdog."""
    return {
        "note": "TODO(agent2): wire apps.ingestion.sources.dfs_underdog",
        "prop_lines": 0,
        "requests_made": 0,
    }


_ENRICH_RUNNERS = {
    "etl:enrich:injuries": _run_injuries,
    ENRICH_DFS: _run_dfs,
}


# ---------------------------------------------------------------------------
# child-JobRun helpers (shared contract — do not change)
# ---------------------------------------------------------------------------


def _summarize_stats(stats: dict) -> tuple[int, int, int, int]:
    """(inserted, updated, skipped, requests) best-effort from a stats dict."""

    def _sum(keys) -> int:
        return sum(int(stats.get(k, 0) or 0) for k in keys)

    return (
        _sum(_INSERTED_KEYS),
        _sum(_UPDATED_KEYS),
        _sum(_SKIPPED_KEYS),
        int(stats.get("requests_made", 0) or 0),
    )


def _run_child(job_name: str, fn, aggregate: dict, *, network_tolerant: bool = False) -> StageResult:
    """Run one stage under the run_job audit; never raises. A network-tolerant
    stage (keyless nba_api / ESPN) downgrades an OSError to a `skipped` child
    rather than failing the whole run (the ADR 007 no-data-no-crash rule)."""
    start = time.monotonic()
    try:
        job = run_job(job_name, fn)
    except OSError as exc:
        if network_tolerant:
            duration = time.monotonic() - start
            reason = f"network unavailable: {exc}"
            stale = JobRun.objects.filter(job_name=job_name).latest("started_at")
            stale.status = JobRun.STATUS_SKIPPED
            stale.stats = {"reason": reason}
            stale.save(update_fields=["status", "stats"])
            aggregate[job_name] = {"reason": reason}
            logger.info("ETL stage %s skipped: %s", job_name, reason)
            return StageResult(
                name=job_name, status=JobRun.STATUS_SKIPPED, duration_s=duration,
                note=reason, stats={"reason": reason},
            )
        return _fail_child(job_name, exc, aggregate, start)
    except Exception as exc:  # run_job already wrote a FAILED JobRun
        return _fail_child(job_name, exc, aggregate, start)

    duration = time.monotonic() - start
    inserted, updated, skipped, requests = _summarize_stats(job.stats)
    aggregate[job_name] = job.stats
    logger.info(
        "ETL stage %s %s in %.1fs (ins~%d upd~%d skp~%d req=%d)",
        job_name, job.status, duration, inserted, updated, skipped, requests,
    )
    return StageResult(
        name=job_name, status=job.status, inserted=inserted, updated=updated,
        skipped=skipped, requests=requests, duration_s=duration, stats=job.stats,
    )


def _fail_child(job_name: str, exc: Exception, aggregate: dict, start: float) -> StageResult:
    duration = time.monotonic() - start
    logger.exception("ETL stage %s failed", job_name)
    tasks.alert(f"{job_name} failed: {exc!r}", exc=exc)
    aggregate[job_name] = {"error": repr(exc)}
    return StageResult(
        name=job_name, status=JobRun.STATUS_FAILED, errors=1, duration_s=duration,
        note=repr(exc), stats={"error": repr(exc)},
    )


def _skip_child(job_name: str, reason: str, aggregate: dict) -> StageResult:
    """Record a designed `skipped` JobRun (reuses tasks.skip_job)."""
    tasks.skip_job(job_name, reason)
    aggregate[job_name] = {"reason": reason}
    return StageResult(
        name=job_name, status=JobRun.STATUS_SKIPPED, note=reason, stats={"reason": reason}
    )


# ---------------------------------------------------------------------------
# stages
# ---------------------------------------------------------------------------


def _stage_anchor(aggregate: dict) -> StageResult:
    """Keyless nba_api anchor — always runs, network-tolerant."""
    return _run_child("etl:anchor", _run_anchor, aggregate, network_tolerant=True)


def _stage_props(aggregate: dict) -> StageResult:
    if not PROPS_SOURCE.key():
        return _skip_child(
            PROPS_SOURCE.job_name, f"missing {PROPS_SOURCE.setting_key}", aggregate
        )
    return _run_child(PROPS_SOURCE.job_name, _run_props, aggregate)


def _stage_enrich(aggregate: dict) -> list[StageResult]:
    results: list[StageResult] = []
    # keyless enrich (injuries) — always runs, network-tolerant.
    for job_name in ENRICH_KEYLESS:
        results.append(
            _run_child(job_name, _ENRICH_RUNNERS[job_name], aggregate, network_tolerant=True)
        )
    # DFS pick'em scrape — keyless, network-tolerant.
    results.append(
        _run_child(ENRICH_DFS, _ENRICH_RUNNERS[ENRICH_DFS], aggregate, network_tolerant=True)
    )
    return results


def _stage_validate(
    since: date | None, aggregate: dict
) -> "tuple[validation.GateResult | None, StageResult]":
    """The blocking gate. The child JobRun is marked FAILED when the gate
    hard-fails (keeping its stats) so the audit trail is honest; a gate crash
    is a failed stage + Sentry alert."""
    job_name = "etl:validate"
    job = JobRun.objects.create(job_name=job_name)
    start = time.monotonic()
    try:
        gate = validation.validate_etl(since=since)
    except Exception as exc:
        duration = time.monotonic() - start
        logger.exception("ETL stage %s crashed", job_name)
        tasks.alert(f"{job_name} crashed: {exc!r}", exc=exc)
        job.status = JobRun.STATUS_FAILED
        job.stats = {"error": repr(exc)}
        job.finished_at = timezone.now()
        job.save()
        aggregate[job_name] = {"error": repr(exc)}
        return None, StageResult(
            name=job_name, status=JobRun.STATUS_FAILED, errors=1, duration_s=duration,
            note=repr(exc), stats={"error": repr(exc)},
        )
    duration = time.monotonic() - start
    stats = gate.as_dict()
    job.stats = stats
    job.status = JobRun.STATUS_FAILED if not gate.ok else JobRun.STATUS_OK
    job.finished_at = timezone.now()
    job.save()
    aggregate[job_name] = stats
    return gate, StageResult(
        name=job_name, status=job.status, errors=len(gate.hard_failures), duration_s=duration,
        note=f"{len(gate.hard_failures)} hard / {len(gate.warnings)} warn", stats=stats,
    )


# ---------------------------------------------------------------------------
# parent stats + human summary
# ---------------------------------------------------------------------------


def _build_parent_stats(stages, aggregate, gate, wall_s, *, dry_run, only) -> dict:
    return {
        "dry_run": dry_run,
        "only": only,
        "wall_seconds": round(wall_s, 2),
        "stages": {
            sr.name: {
                "status": sr.status,
                "inserted": sr.inserted,
                "updated": sr.updated,
                "skipped": sr.skipped,
                "errors": sr.errors,
                "requests_made": sr.requests,
                "duration_s": round(sr.duration_s, 2),
            }
            for sr in stages
        },
        "gate": gate.as_dict() if gate is not None else None,
        "gate_hard_failures": len(gate.hard_failures) if gate else 0,
        "gate_warnings": len(gate.warnings) if gate else 0,
        "children": aggregate,
    }


def _render_summary(stages, gate, wall_s, *, dry_run) -> str:
    header = "== basketballpicks daily ETL{} ==".format("  [DRY RUN]" if dry_run else "")
    cols = f"{'stage':24} {'status':8} {'ins':>6} {'upd':>6} {'skp':>6} {'err':>4} {'dur':>7}"
    rule = "-" * len(cols)
    lines = [header, cols, rule]
    for sr in stages:
        if sr.name == "etl:validate":
            ins = upd = skp = "-"
        else:
            ins, upd, skp = str(sr.inserted), str(sr.updated), str(sr.skipped)
        lines.append(
            f"{sr.name:24} {sr.status:8} {ins:>6} {upd:>6} {skp:>6} "
            f"{sr.errors:>4} {sr.duration_s:>6.1f}s"
        )
    lines.append(rule)
    if gate is None:
        lines.append("gate: NOT RUN (skipped or crashed)")
    elif gate.ok:
        lines.append(f"gate: PASS  ({len(gate.hard_failures)} hard, {len(gate.warnings)} warnings)")
    else:
        lines.append(
            f"gate: FAIL  ({len(gate.hard_failures)} HARD FAILURES, {len(gate.warnings)} warnings)"
        )
        for hf in gate.hard_failures[:20]:
            lines.append(f"  HARD: {hf}")
    if gate is not None and gate.warnings:
        for w in gate.warnings[:10]:
            lines.append(f"  warn: {w}")
    lines.append(f"total wall time: {wall_s:.1f}s")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def _do_run(*, only, skip_validate, since, dry_run) -> ETLRunResult:
    """Create the parent JobRun, run the requested stages, finalize and return
    a result. Never raises for a gate/stage failure — the caller decides how to
    surface a non-zero exit (so the summary always prints first)."""
    t0 = time.monotonic()
    parent = JobRun.objects.create(job_name="etl:daily")
    aggregate: dict = {}
    stages: list[StageResult] = []
    gate = None
    stages_to_run = (only,) if only else STAGES

    for stage in stages_to_run:
        if stage == STAGE_ANCHOR:
            stages.append(_stage_anchor(aggregate))
        elif stage == STAGE_PROPS:
            stages.append(_stage_props(aggregate))
        elif stage == STAGE_ENRICH:
            stages.extend(_stage_enrich(aggregate))
        elif stage == STAGE_VALIDATE:
            if skip_validate:
                logger.info("ETL validate stage skipped (--skip-validate)")
                continue
            gate, sr = _stage_validate(since, aggregate)
            stages.append(sr)

    stage_failed = [
        sr.name for sr in stages
        if sr.status == JobRun.STATUS_FAILED and sr.name != "etl:validate"
    ]
    gate_hard_failed = gate is not None and not gate.ok
    gate_crashed = (not skip_validate) and (STAGE_VALIDATE in stages_to_run) and gate is None
    run_failed = bool(stage_failed) or gate_hard_failed or gate_crashed

    wall_s = time.monotonic() - t0
    parent.stats = _build_parent_stats(stages, aggregate, gate, wall_s, dry_run=dry_run, only=only)
    parent.status = JobRun.STATUS_FAILED if run_failed else JobRun.STATUS_OK
    parent.finished_at = timezone.now()
    parent.save()

    summary = _render_summary(stages, gate, wall_s, dry_run=dry_run)
    logger.info("ETL daily finished in %.1fs status=%s", wall_s, parent.status)
    return ETLRunResult(
        parent=parent, stages=stages, gate=gate, summary=summary, wall_s=wall_s,
        dry_run=dry_run, hard_failed=gate_hard_failed or gate_crashed, stage_failed=stage_failed,
    )


def run_daily_etl(
    *,
    only: str | None = None,
    dry_run: bool = False,
    skip_validate: bool = False,
    since: date | None = None,
    stdout=None,
) -> ETLRunResult:
    """Run the unified daily ETL.

    Args:
        only: run a single stage (one of :data:`STAGES`); None runs them all.
        dry_run: perform NO writes — the whole run executes inside a
            transaction that is rolled back, so row counts are unchanged.
        skip_validate: do not run the blocking gate (diagnostic use only).
        since: date scoping the gate's per-game checks.
        stdout: optional stream the human summary is written to.

    Raises:
        ValueError: `only` is not a known stage.
        ETLValidationError: the gate hard-failed (or crashed) — terminal.
        ETLStageError: a non-validate stage failed (gate itself passed).
    """
    if only is not None and only not in STAGES:
        raise ValueError(f"unknown stage {only!r}; choose from {STAGES}")

    logger.info(
        "ETL daily start (only=%s dry_run=%s skip_validate=%s since=%s)",
        only, dry_run, skip_validate, since,
    )

    if dry_run:
        with transaction.atomic():
            result = _do_run(only=only, skip_validate=skip_validate, since=since, dry_run=True)
            transaction.set_rollback(True)  # NO writes persist
    else:
        result = _do_run(only=only, skip_validate=skip_validate, since=since, dry_run=False)

    if stdout is not None:
        stdout.write(result.summary)

    if result.hard_failed:
        tasks.alert(
            "etl:daily gate HARD FAIL — publication blocked "
            f"({len(result.gate.hard_failures) if result.gate else 'n/a'} violation(s))"
        )
        raise ETLValidationError(result.gate)
    if result.stage_failed:
        raise ETLStageError(result.stage_failed)
    return result
