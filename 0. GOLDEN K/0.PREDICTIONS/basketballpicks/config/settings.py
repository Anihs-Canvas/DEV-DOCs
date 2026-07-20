"""
Django settings — basketballpicks (player-props / DFS line-shop platform).

Mirrors the safepicks Django/Postgres/Celery stack; the schema is
PLAYER-FIRST and the hero engine is DEVIG + LINE-SHOP, not a forecasting
model. Everything is environment-driven; see .env.example. Plan references
are to _planning/bball-00-BUILD-PLAN.md [§n] and bball-01-architecture-
scaffold.txt.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "insecure-dev-only-key-change-me",  # overridden in every real deployment
)
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = [
    h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",  # token auth for /api/v1
    # basketballpicks apps — one per concern [bball-01 §1]. ALL 12 are
    # registered up front so the project imports; the apps other agents own
    # ship as empty-but-valid stubs until they fill them.
    "apps.core",  # reference + results; Player + box scores (the differentiator)
    "apps.ingestion",  # JobRun audit, source-refs, ETL orchestrator, sources/
    "apps.features",  # TeamRating(+pace); PlayerForm + MinutesProjection
    "apps.odds",  # TEAM markets (spread/ML/total) + devig + sharp_anchor
    "apps.props",  # HERO DATA APP: PropMarket/PropLine/PropConsensus/PropPrediction
    "apps.predictions",  # ModelVersion/Prediction (team, market-grade)
    "apps.edge",  # HERO PUBLISHER: EdgeRule/EdgePick/ProductionModel/PipelineState
    "apps.secondary",  # SecondaryModule flag registry
    "apps.backtesting",  # settle/pnl/CLV engine; forward paper-CLV emphasis
    "apps.portfolio",  # Bankroll/Bet (singles) + DFSEntry (pick'em parlays)
    "apps.dashboard",  # Django ops templates
    "apps.api",  # DRF v1 read surface
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Database -----------------------------------------------------------
# PostgreSQL 16 is the single source of truth. Compose/CI set POSTGRES_HOST;
# without it (bare local dev) we fall back to SQLite so a fresh clone can
# still run the test suite with zero services.
if os.environ.get("POSTGRES_HOST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "basketballpicks"),
            "USER": os.environ.get("POSTGRES_USER", "basketballpicks"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "basketballpicks"),
            "HOST": os.environ["POSTGRES_HOST"],
            "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "dev.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- I18N / TZ -----------------------------------------------------------
# Everything is stored and computed in UTC.
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF -----------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "60/hour",
        "user": "1000/hour",
    },
}

# --- Notifications -------------------------------------------------------
# Pluggable digest/retraction backends: CSV of console|email|telegram.
NOTIFY_BACKENDS = os.environ.get("NOTIFY_BACKENDS", "console")
NOTIFY_EMAIL_TO = os.environ.get("NOTIFY_EMAIL_TO", "")
NOTIFY_EMAIL_FROM = os.environ.get("NOTIFY_EMAIL_FROM", "basketballpicks@localhost")
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# --- Live data sources [bball-01 §4] --------------------------------------
# Empty keys are legal: every beat task no-ops with a `skipped` JobRun until
# keys land in .env — the pipeline can be deployed TODAY (ADR 007).

# nba_api / stats.nba.com — KEYLESS but IP/rate-limited. Needs a browser UA
# (stats.nba.com 403s bots); the token bucket keeps the request rate polite.
NBA_API_BASE_URL = os.environ.get("NBA_API_BASE_URL", "https://stats.nba.com/stats")
NBA_API_USER_AGENT = os.environ.get(
    "NBA_API_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
)
NBA_API_RATE_PER_MIN = int(os.environ.get("NBA_API_RATE_PER_MIN", "20"))

# The Odds API — BUSINESS tier REQUIRED for player props + Pinnacle + history.
# Team markets on bulk /odds; props on per-event /events/{id}/odds (enumerate
# game ids on the free /events first). Business is credit-generous.
THE_ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY", "")
THE_ODDS_API_BASE_URL = os.environ.get("THE_ODDS_API_BASE_URL", "https://api.the-odds-api.com")
THE_ODDS_API_DAILY_BUDGET = int(os.environ.get("THE_ODDS_API_DAILY_BUDGET", "5000"))
THE_ODDS_API_RATE_PER_MIN = int(os.environ.get("THE_ODDS_API_RATE_PER_MIN", "30"))
THE_ODDS_API_PROP_MARKETS = os.environ.get(
    "THE_ODDS_API_PROP_MARKETS",
    "player_points,player_rebounds,player_assists,"
    "player_points_rebounds_assists,player_threes,player_blocks,player_steals",
)

# Optional real-time EV feeds (sharp-fair cross-check). Both no-op when unset.
ODDSJAM_API_KEY = os.environ.get("ODDSJAM_API_KEY", "")
STATSBENCH_API_KEY = os.environ.get("STATSBENCH_API_KEY", "")

# DFS pick'em scraper knobs (Underdog / PrizePicks reverse-engineered JSON).
UNDERDOG_BASE_URL = os.environ.get("UNDERDOG_BASE_URL", "")
UNDERDOG_USER_AGENT = os.environ.get(
    "UNDERDOG_USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
)

# Sport keys + book taxonomy + devig/edge knobs (shared by odds/props/edge).
SPORT_KEYS = {
    "NBA": "basketball_nba",
    "WNBA": "basketball_wnba",
    "NCAAB": "basketball_ncaab",
    "EURO": "basketball_euroleague",
}
SHARP_BOOKS = ["pinnacle", "circa"]  # the devig anchors
DFS_BOOKS = ["underdog", "prizepicks", "pick6"]
DEVIG_METHOD = os.environ.get("DEVIG_METHOD", "shin")  # reuse odds.devig math
MIN_EDGE = float(os.environ.get("MIN_EDGE", "0.03"))  # publish floor (EV vs fair)
MAX_PROP_ODDS = float(os.environ.get("MAX_PROP_ODDS", "3.0"))  # props hold 6-10%

# --- Error monitoring (ADR 010) -------------------------------------------
# Log-based always; Sentry wired when a DSN is set. Unset (default) => no-op.
SENTRY_DSN = os.environ.get("SENTRY_DSN", "")
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "dev")

from config.sentry import init_sentry  # noqa: E402 — needs SENTRY_* above

init_sentry(SENTRY_DSN, SENTRY_ENVIRONMENT)

# --- Celery [bball-01 §3] --------------------------------------------------
# Queues split so slow keyless nba_api pulls (ingestion) never delay the
# 10-min prop loop (core); secondary modules may never starve core.
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_TIMEZONE = "UTC"
CELERY_TASK_DEFAULT_QUEUE = "core"
CELERY_TASK_QUEUES = {
    "core": {},  # devig/line-shop loop, prop capture, settlement, publishing
    "ingestion": {},  # slow keyless nba_api box-score / PBP pulls
    "secondary": {},  # secondary modules; may never starve `core`
}

# --- Caching: the frontend response (page) cache --------------------------
# Read-only /api/v1/frontend/* GET payloads are a pure function of their query
# params (no per-user data), so one global short-TTL Redis entry per
# (path+querystring) is safe. Mirrors safepicks; retargeted key prefix.
TESTING = "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))

FRONTEND_CACHE_TTL = int(os.environ.get("FRONTEND_CACHE_TTL", "300"))  # seconds
FRONTEND_CACHE_ENABLED = os.environ.get(
    "FRONTEND_CACHE_ENABLED", "1" if TESTING else "0"
) not in ("0", "false", "False")


def _redis_on_db(url: str, db: int) -> str:
    """Same Redis server as Celery, DIFFERENT logical DB (Celery is on /0),
    so frontend cache keys can never collide with the Celery broker."""
    base, sep, tail = url.rpartition("/")
    if sep and tail.isdigit():
        return f"{base}/{db}"
    return f"{url.rstrip('/')}/{db}"


FRONTEND_CACHE_URL = os.environ.get("FRONTEND_CACHE_URL") or _redis_on_db(REDIS_URL, 1)

try:
    import redis as _redis_client  # noqa: F401

    _REDIS_CACHE_BACKEND = "django.core.cache.backends.redis.RedisCache"
except Exception:  # pragma: no cover - redis client missing
    _REDIS_CACHE_BACKEND = None

if TESTING:
    _FRONTEND_CACHE = {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}
elif _REDIS_CACHE_BACKEND:
    _FRONTEND_CACHE = {
        "BACKEND": _REDIS_CACHE_BACKEND,
        "LOCATION": FRONTEND_CACHE_URL,  # redis://…/1 — never the Celery DB (/0)
        "KEY_PREFIX": "basketballpicks_fe",
        "TIMEOUT": FRONTEND_CACHE_TTL,
    }
else:  # redis client unavailable — degrade to an in-process cache, still works
    _FRONTEND_CACHE = {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "frontend-cache-fallback",
        "TIMEOUT": FRONTEND_CACHE_TTL,
    }

CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "frontend": _FRONTEND_CACHE,
}
