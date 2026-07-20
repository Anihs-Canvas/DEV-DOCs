"""Celery application — Beat drives all recurring work; no cron sprawl.

Every task no-ops with a `skipped` JobRun while API keys / sources are
missing, so this beat can run TODAY (ADR 007).

FOUNDATION NOTE (Agent 1): only the ingestion-OWNED beats are registered
below, so `celery -A config beat` runs cleanly against a fresh clone.
The full bball-01 §3 cadence (the 10-min prop loop, injuries, DFS poll,
ratings/predict/publish/settle, weekly forward-CLV) is documented as a
commented block at the bottom — each owning agent UNCOMMENTS its lines as
it lands the task. Cadences are tuned to NBA's overnight-heavy slate (US
tip-offs 23:00-04:00 UTC).
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("basketballpicks")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

_CORE = {"queue": "core"}
_INGEST = {"queue": "ingestion"}

# --- Active beats (ingestion-owned; safe on a fresh clone) -----------------
app.conf.beat_schedule = {
    # daily 09:00 UTC: unified ETL — anchor -> props -> enrich -> the blocking
    # data-quality gate (apps/ingestion/etl.py). Runs after the night's games
    # are FINAL (~06:00-08:00 UTC).
    "daily-etl-0900": {
        "task": "ingestion.run_daily_etl_beat",
        "schedule": crontab(minute=0, hour=9),
        "options": _CORE,
    },
    # every 15 min: nba_api results + box scores (live/final) on the slow
    # ingestion queue so it never delays the core prop loop.
    "results-boxscore-15min": {
        "task": "ingestion.sync_results_boxscore_beat",
        "schedule": crontab(minute="*/15"),
        "options": _INGEST,
    },
    # every 30 min: missed-beat watchdog.
    "watchdog-30min": {
        "task": "ingestion.watchdog_beat",
        "schedule": crontab(minute="7,37"),
        "options": _CORE,
    },
}

# --- Full cadence [bball-01 §3] — each owning agent uncomments its lines ----
# app.conf.beat_schedule.update({
#     # === apps.odds / apps.props (Agent owning odds+props) ===
#     "props-final90-10min": {          # THE line-shop money loop (T-90m)
#         "task": "odds.sync_final90_beat",
#         "schedule": crontab(minute="*/10"), "options": _CORE},
#     "props-t24-hourly": {
#         "task": "odds.sync_t24_beat",
#         "schedule": crontab(minute=5), "options": _CORE},
#     "props-t3d-6h": {
#         "task": "odds.sync_t3d_beat",
#         "schedule": crontab(minute=20, hour="*/6"), "options": _CORE},
#     "closing-capture-15min": {
#         "task": "odds.capture_closing_beat",
#         "schedule": crontab(minute="3-58/15"), "options": _CORE},
#     "dfs-lines-30min": {
#         "task": "odds.sync_dfs_lines_beat",
#         "schedule": crontab(minute="*/30"), "options": _CORE},
#     # === apps.ingestion (injuries — the usage-cascade trigger) ===
#     "injuries-15min": {
#         "task": "ingestion.sync_injuries_beat",
#         "schedule": crontab(minute="*/15"), "options": _CORE},
#     # === apps.features / apps.predictions / apps.edge ===
#     "ratings-form-daily-0930": {
#         "task": "features.rebuild_ratings_form_beat",
#         "schedule": crontab(minute=30, hour=9), "options": _CORE},
#     "predict-daily-1000": {
#         "task": "predictions.predict_daily_beat",
#         "schedule": crontab(minute=0, hour=10), "options": _CORE},
#     "publish-daily-1030": {
#         "task": "edge.publish_daily_beat",
#         "schedule": crontab(minute=30, hour=10), "options": _CORE},
#     # === apps.backtesting / apps.edge (settle + CLV) ===
#     "settle-15min": {
#         "task": "backtesting.settle_beat",
#         "schedule": crontab(minute="6-59/15"), "options": _CORE},
#     "paper-clv-weekly-mon-0745": {    # *** FORWARD-CLV gate (central here) ***
#         "task": "backtesting.paper_clv_weekly_beat",
#         "schedule": crontab(minute=45, hour=7, day_of_week=1), "options": _CORE},
#     "monthly-model-review-1st-0800": {
#         "task": "predictions.monthly_model_review_beat",
#         "schedule": crontab(minute=0, hour=8, day_of_month=1), "options": _CORE},
# })
