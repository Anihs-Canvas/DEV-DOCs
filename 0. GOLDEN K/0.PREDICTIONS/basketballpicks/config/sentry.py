"""Sentry wiring [ADR 010], copied verbatim from safepicks.

Initialised from settings.py at import time, STRICTLY behind SENTRY_DSN:
with the env var unset (the default) nothing is imported and nothing is
initialised — zero behavior change. With a DSN set, `sentry_sdk.init`
runs with the Django + Celery integrations, so unhandled web/task
exceptions are captured automatically.

Kept in its own module so the init path is unit-testable without
re-importing settings (tests inject a fake sentry_sdk).
"""

import logging

logger = logging.getLogger(__name__)


def init_sentry(dsn: str, environment: str = "dev", sdk=None) -> bool:
    """Initialise Sentry when `dsn` is non-empty. Returns True when the
    SDK was initialised. `sdk` is injectable for tests; the import only
    happens when a DSN exists (no DSN -> no import -> no behavior)."""
    if not dsn:
        return False
    if sdk is None:
        try:
            import sentry_sdk as sdk  # noqa: PLC0415 — deliberate lazy import
        except ImportError:
            logger.warning("SENTRY_DSN set but sentry-sdk is not installed — log-only alerts")
            return False
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        # Error monitoring only — no performance tracing, no PII.
        traces_sample_rate=0.0,
        send_default_pii=False,
    )
    logger.info("Sentry initialised (environment=%s)", environment)
    return True
